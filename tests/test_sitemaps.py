#!/usr/bin/env python3
"""
Tests for sitemap.txt / sitemap.xml at the repository root and their
deployed copies under docs/.

This PR:
  * Added four new URLs (output_asimp.html, output_lynis.html,
    output_openscap.html, security_posture_assessment.html) to both
    sitemap.txt and sitemap.xml, in both the root and docs/ locations.
  * Bumped every <lastmod> date in sitemap.xml (root and docs/) from
    2026-08-08 to 2026-08-11.
  * Kept the root and docs/ copies of each sitemap file byte-for-byte
    identical, matching the invariant enforced by
    scripts/verify_sitemap_links.py's compare_file_contents() check.

Run with:
    python3 -m unittest tests/test_sitemaps.py -v
"""
import os
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_SITEMAP_TXT = os.path.join(REPO_ROOT, "sitemap.txt")
ROOT_SITEMAP_XML = os.path.join(REPO_ROOT, "sitemap.xml")
DOCS_SITEMAP_TXT = os.path.join(REPO_ROOT, "docs", "sitemap.txt")
DOCS_SITEMAP_XML = os.path.join(REPO_ROOT, "docs", "sitemap.xml")

XML_NAMESPACE = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

NEW_URLS = [
    "https://linuxmalaysia.github.io/ASIMP/output_asimp.html",
    "https://linuxmalaysia.github.io/ASIMP/output_lynis.html",
    "https://linuxmalaysia.github.io/ASIMP/output_openscap.html",
    "https://linuxmalaysia.github.io/ASIMP/security_posture_assessment.html",
]

EXPECTED_LASTMOD = "2026-08-11"


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _txt_urls(path: str):
    return [line.strip() for line in _read(path).splitlines() if line.strip()]


def _xml_url_elements(path: str):
    tree = ET.parse(path)
    return tree.getroot().findall(".//ns:url", XML_NAMESPACE)


class TestSitemapRootDocsSynchronization(unittest.TestCase):
    """Root and docs/ copies of each sitemap file must be identical."""

    def test_all_sitemap_files_exist(self) -> None:
        for path in (ROOT_SITEMAP_TXT, ROOT_SITEMAP_XML, DOCS_SITEMAP_TXT, DOCS_SITEMAP_XML):
            with self.subTest(path=path):
                self.assertTrue(os.path.isfile(path))

    def test_sitemap_txt_root_and_docs_are_identical(self) -> None:
        self.assertEqual(_read(ROOT_SITEMAP_TXT), _read(DOCS_SITEMAP_TXT))

    def test_sitemap_xml_root_and_docs_are_identical(self) -> None:
        self.assertEqual(_read(ROOT_SITEMAP_XML), _read(DOCS_SITEMAP_XML))


class TestSitemapTxtContent(unittest.TestCase):
    """Content checks for sitemap.txt (identical assertions apply to both copies)."""

    def test_new_urls_present_in_root_and_docs_txt(self) -> None:
        for path in (ROOT_SITEMAP_TXT, DOCS_SITEMAP_TXT):
            urls = _txt_urls(path)
            for new_url in NEW_URLS:
                with self.subTest(path=path, url=new_url):
                    self.assertIn(new_url, urls)

    def test_no_duplicate_urls_in_txt(self) -> None:
        for path in (ROOT_SITEMAP_TXT, DOCS_SITEMAP_TXT):
            urls = _txt_urls(path)
            with self.subTest(path=path):
                self.assertEqual(len(urls), len(set(urls)))

    def test_all_txt_urls_use_expected_domain(self) -> None:
        for path in (ROOT_SITEMAP_TXT, DOCS_SITEMAP_TXT):
            for url in _txt_urls(path):
                with self.subTest(path=path, url=url):
                    parsed = urlparse(url)
                    self.assertEqual(parsed.scheme, "https")
                    self.assertEqual(parsed.netloc, "linuxmalaysia.github.io")
                    self.assertTrue(url.startswith("https://linuxmalaysia.github.io/ASIMP/"))

    def test_new_urls_appear_between_openscap_and_troubleshooting(self) -> None:
        # The new report/checklist pages were inserted alphabetically after
        # openscap.html and before troubleshooting.html.
        urls = _txt_urls(ROOT_SITEMAP_TXT)
        openscap_idx = urls.index("https://linuxmalaysia.github.io/ASIMP/openscap.html")
        troubleshooting_idx = urls.index(
            "https://linuxmalaysia.github.io/ASIMP/troubleshooting.html"
        )
        for new_url in NEW_URLS:
            with self.subTest(url=new_url):
                new_idx = urls.index(new_url)
                self.assertGreater(new_idx, openscap_idx)
                self.assertLess(new_idx, troubleshooting_idx)


class TestSitemapXmlContent(unittest.TestCase):
    """Content checks for sitemap.xml (identical assertions apply to both copies)."""

    def test_xml_is_well_formed(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            with self.subTest(path=path):
                try:
                    ET.parse(path)
                except ET.ParseError as exc:
                    self.fail(f"{path} is not well-formed XML: {exc}")

    def test_new_urls_present_as_loc_entries(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            locs = [
                url_el.find("ns:loc", XML_NAMESPACE).text
                for url_el in _xml_url_elements(path)
            ]
            for new_url in NEW_URLS:
                with self.subTest(path=path, url=new_url):
                    self.assertIn(new_url, locs)

    def test_all_lastmod_dates_bumped_to_expected_date(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            for url_el in _xml_url_elements(path):
                loc = url_el.find("ns:loc", XML_NAMESPACE).text
                lastmod = url_el.find("ns:lastmod", XML_NAMESPACE).text
                with self.subTest(path=path, url=loc):
                    self.assertEqual(lastmod, EXPECTED_LASTMOD)

    def test_new_url_entries_have_weekly_changefreq_and_expected_priority(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            url_elements_by_loc = {
                url_el.find("ns:loc", XML_NAMESPACE).text: url_el
                for url_el in _xml_url_elements(path)
            }
            for new_url in NEW_URLS:
                with self.subTest(path=path, url=new_url):
                    url_el = url_elements_by_loc[new_url]
                    changefreq = url_el.find("ns:changefreq", XML_NAMESPACE).text
                    priority = url_el.find("ns:priority", XML_NAMESPACE).text
                    self.assertEqual(changefreq, "weekly")
                    self.assertEqual(priority, "0.8")

    def test_homepage_entry_retains_daily_changefreq_and_top_priority(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            url_elements_by_loc = {
                url_el.find("ns:loc", XML_NAMESPACE).text: url_el
                for url_el in _xml_url_elements(path)
            }
            homepage = url_elements_by_loc["https://linuxmalaysia.github.io/ASIMP/"]
            with self.subTest(path=path):
                self.assertEqual(
                    homepage.find("ns:changefreq", XML_NAMESPACE).text, "daily"
                )
                self.assertEqual(homepage.find("ns:priority", XML_NAMESPACE).text, "1.0")

    def test_no_duplicate_loc_entries_in_xml(self) -> None:
        for path in (ROOT_SITEMAP_XML, DOCS_SITEMAP_XML):
            locs = [
                url_el.find("ns:loc", XML_NAMESPACE).text
                for url_el in _xml_url_elements(path)
            ]
            with self.subTest(path=path):
                self.assertEqual(len(locs), len(set(locs)))


class TestSitemapTxtXmlCrossConsistency(unittest.TestCase):
    """sitemap.txt and sitemap.xml must describe exactly the same URL set."""

    def test_txt_and_xml_url_sets_match(self) -> None:
        for txt_path, xml_path in (
            (ROOT_SITEMAP_TXT, ROOT_SITEMAP_XML),
            (DOCS_SITEMAP_TXT, DOCS_SITEMAP_XML),
        ):
            txt_urls = set(_txt_urls(txt_path))
            xml_urls = {
                url_el.find("ns:loc", XML_NAMESPACE).text
                for url_el in _xml_url_elements(xml_path)
            }
            with self.subTest(txt_path=txt_path, xml_path=xml_path):
                self.assertEqual(txt_urls, xml_urls)

    def test_txt_and_xml_url_counts_match(self) -> None:
        for txt_path, xml_path in (
            (ROOT_SITEMAP_TXT, ROOT_SITEMAP_XML),
            (DOCS_SITEMAP_TXT, DOCS_SITEMAP_XML),
        ):
            with self.subTest(txt_path=txt_path, xml_path=xml_path):
                self.assertEqual(len(_txt_urls(txt_path)), len(_xml_url_elements(xml_path)))


if __name__ == "__main__":
    unittest.main()