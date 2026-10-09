"""Publication regression tests for the OpenSCAP guide introduced in PR #91.

These checks read documentation fixtures; they never execute hardening examples.
"""

import json
import re
import unittest
from pathlib import Path

from tools.build_mintlify_mdx import convert_md_to_mdx, parse_frontmatter


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE = "openscap_operational_guide"
# Only pages whose generated bodies changed in PR #91 are fixtures here.
CONVERTED_PAGES = (
    GUIDE,
    "knowledge_portal_testbed_openscap_va_report",
    "lynis",
    "openscap",
    "rhel_family_cis",
)


class TestOpenSCAPOperationalGuide(unittest.TestCase):
    def test_changed_mdx_pages_match_source_conversion(self):
        for page in CONVERTED_PAGES:
            with self.subTest(page=page):
                source = (REPO_ROOT / "docs" / (page + ".md")).read_text(encoding="utf-8")
                published = (REPO_ROOT / "docs-source" / (page + ".mdx")).read_text(encoding="utf-8")
                fm, body = parse_frontmatter(source)
                fallback = page.replace("_", " ").title()
                self.assertEqual(published, convert_md_to_mdx(fm, body, fallback))

    def test_changed_mdx_pages_remove_wrappers_and_preserve_code_examples(self):
        for page in CONVERTED_PAGES:
            with self.subTest(page=page):
                source = (REPO_ROOT / "docs" / (page + ".md")).read_text(encoding="utf-8")
                published = (REPO_ROOT / "docs-source" / (page + ".mdx")).read_text(encoding="utf-8")
                # Assert independently of the converter to catch a regression in
                # both the converter and regenerated checked-in output.
                self.assertIn("{% raw %}", source)
                self.assertNotRegex(published, r"\{%\s*(?:raw|endraw)\s*%\}")
                examples = re.findall(r"^```[^\n]*\n.*?^```[ \t]*$", source, re.MULTILINE | re.DOTALL)
                self.assertTrue(examples, "Fixture must contain fenced code examples")
                self.assertEqual(
                    re.findall(r"^```[^\n]*\n.*?^```[ \t]*$", published, re.MULTILINE | re.DOTALL),
                    examples,
                )

    def test_guide_metadata_survives_publication(self):
        source = (REPO_ROOT / "docs" / (GUIDE + ".md")).read_text(encoding="utf-8")
        published = (REPO_ROOT / "docs-source" / (GUIDE + ".mdx")).read_text(encoding="utf-8")
        fm, body = parse_frontmatter(source)
        published_fm, _ = parse_frontmatter(published)
        self.assertEqual(fm["okf_version"], "0.2")
        self.assertEqual(fm["type"], "documentation")
        self.assertEqual(fm["sidebarTitle"], "OpenSCAP Operational Guide")
        self.assertTrue(body.startswith("# " + fm["title"] + "\n"))
        for field in ("title", "sidebarTitle", "description"):
            with self.subTest(field=field):
                self.assertTrue(fm[field])
                self.assertEqual(published_fm[field], fm[field])

    def test_guide_is_registered_once_in_mintlify_navigation(self):
        config = json.loads((REPO_ROOT / "docs-source/docs.json").read_text(encoding="utf-8"))
        pages = [
            page
            for tab in config["navigation"]["tabs"]
            for group in tab["groups"]
            for page in group["pages"]
        ]
        self.assertEqual(pages.count(GUIDE), 1)
        self.assertTrue((REPO_ROOT / "docs-source" / (GUIDE + ".mdx")).is_file())

    def test_new_guide_links_use_each_index_publication_path(self):
        for index, target in (
            ("SUMMARY.md", "docs/" + GUIDE + ".md"),
            ("docs/SUMMARY.md", GUIDE + ".md"),
            ("docs/index.md", GUIDE + ".html"),
            ("docs-source/SUMMARY.mdx", GUIDE + ".md"),
            ("docs-source/index.mdx", GUIDE + ".html"),
            ("llms.txt", "docs/" + GUIDE + ".md"),
        ):
            with self.subTest(index=index):
                content = (REPO_ROOT / index).read_text(encoding="utf-8")
                links = re.findall(r"\[OpenSCAP Operational Guide\]\(([^)]+)\)", content)
                self.assertEqual(links, [target], "Guide must have one correctly resolved link")


if __name__ == "__main__":
    unittest.main()
