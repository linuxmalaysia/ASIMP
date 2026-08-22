#!/usr/bin/env python3
"""
Unit tests for scripts/verify_sitemap_links.py (Sitemap and Link Integrity Verification Script).

These tests verify host validation, scheme validation, URL checks, GitHub Pages link verification,
sitemap file comparison, and concurrent execution in isolation.

Run with:
    python3 -m unittest tests/test_verify_sitemap_links.py -v
"""
import os
import sys
import tempfile
import unittest
import random
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import verify_sitemap_links  # noqa: E402


class TestVerifySitemapLinks(unittest.TestCase):
    """Test case for verify_sitemap_links.py functions."""

    def setUp(self) -> None:
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self) -> None:
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    def test_check_url_invalid_scheme(self) -> None:
        is_ok, failure_type = verify_sitemap_links.check_url("ftp://linuxmalaysia.github.io/ASIMP/")
        self.assertFalse(is_ok)
        self.assertEqual(failure_type, "InvalidScheme:ftp")

    def test_check_url_disallowed_host(self) -> None:
        is_ok, failure_type = verify_sitemap_links.check_url("https://malicious-domain.com/test")
        self.assertFalse(is_ok)
        self.assertEqual(failure_type, "DisallowedHost:malicious-domain.com")

    @patch("urllib.request.build_opener")
    def test_check_url_success_200(self, mock_build_opener: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_opener = MagicMock()
        mock_opener.open.return_value.__enter__.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        is_ok, failure_type = verify_sitemap_links.check_url("https://linuxmalaysia.github.io/ASIMP/")
        self.assertTrue(is_ok)
        self.assertEqual(failure_type, "OK")

    def test_verify_github_pages_url_invalid_host(self) -> None:
        result = verify_sitemap_links.verify_github_pages_url("https://example.com/ASIMP/")
        self.assertFalse(result)

    @patch("verify_sitemap_links.check_url")
    def test_verify_github_pages_url_live_success(self, mock_check_url: MagicMock) -> None:
        mock_check_url.return_value = (True, "OK")
        result = verify_sitemap_links.verify_github_pages_url("https://linuxmalaysia.github.io/ASIMP/architecture.html")
        self.assertTrue(result)

    @patch("verify_sitemap_links.check_url")
    def test_verify_github_pages_url_disk_fallback(self, mock_check_url: MagicMock) -> None:
        mock_check_url.return_value = (False, "HTTPError:404")
        os.makedirs("docs", exist_ok=True)
        with open("docs/architecture.md", "w") as f:
            f.write("# Architecture")

        result = verify_sitemap_links.verify_github_pages_url("https://linuxmalaysia.github.io/ASIMP/architecture.html")
        self.assertTrue(result)

    def test_compare_file_contents_success(self) -> None:
        with open("file_a.txt", "w") as fa, open("file_b.txt", "w") as fb:
            fa.write("same content")
            fb.write("same content")

        try:
            verify_sitemap_links.compare_file_contents("file_a.txt", "file_b.txt", "test")
        except SystemExit:
            self.fail("compare_file_contents exited unexpectedly on matching files")

    @patch("verify_sitemap_links.check_url")
    def test_main_success(self, mock_check_url: MagicMock) -> None:
        mock_check_url.return_value = (True, "OK")
        os.makedirs("docs", exist_ok=True)
        sitemap_txt = "https://linuxmalaysia.github.io/ASIMP/\n"
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://linuxmalaysia.github.io/ASIMP/</loc></url></urlset>'

        with open("sitemap.txt", "w") as f:
            f.write(sitemap_txt)
        with open("docs/sitemap.txt", "w") as f:
            f.write(sitemap_txt)
        with open("sitemap.xml", "w") as f:
            f.write(sitemap_xml)
        with open("docs/sitemap.xml", "w") as f:
            f.write(sitemap_xml)

        try:
            verify_sitemap_links.main()
        except SystemExit as exc:
            self.fail(f"verify_sitemap_links.main() exited unexpectedly with code {exc.code}")

    @patch("verify_sitemap_links.check_url")
    def test_main_failure_nonzero_exit(self, mock_check_url: MagicMock) -> None:
        mock_check_url.return_value = (False, "HTTPError:500")
        os.makedirs("docs", exist_ok=True)
        sitemap_txt = "https://linuxmalaysia.github.io/ASIMP/broken.html\n"
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://linuxmalaysia.github.io/ASIMP/broken.html</loc></url></urlset>'

        with open("sitemap.txt", "w") as f:
            f.write(sitemap_txt)
        with open("docs/sitemap.txt", "w") as f:
            f.write(sitemap_txt)
        with open("sitemap.xml", "w") as f:
            f.write(sitemap_xml)
        with open("docs/sitemap.xml", "w") as f:
            f.write(sitemap_xml)

        with self.assertRaises(SystemExit) as cm:
            verify_sitemap_links.main()
        self.assertNotEqual(cm.exception.code, 0)

class TestMainConcurrentVerification(unittest.TestCase):
    """Tests for main()'s use of ThreadPoolExecutor to verify URLs concurrently.

    This class targets the behavior introduced in this PR: replacing the
    sequential for-loops over gh_pages_urls and the sampled GitBook URLs with
    ThreadPoolExecutor(max_workers=5).map(...) calls, while preserving
    result-to-URL ordering and overall success/failure semantics.
    """

    def setUp(self) -> None:
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self) -> None:
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    def _write_sitemap_files(self, urls) -> None:
        """Writes matching root/docs sitemap.txt and sitemap.xml files for the given URLs."""
        os.makedirs("docs", exist_ok=True)

        txt_content = "\n".join(urls) + ("\n" if urls else "")
        with open("sitemap.txt", "w") as f:
            f.write(txt_content)
        with open("docs/sitemap.txt", "w") as f:
            f.write(txt_content)

        url_entries = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{url_entries}</urlset>"
        )
        with open("sitemap.xml", "w") as f:
            f.write(xml_content)
        with open("docs/sitemap.xml", "w") as f:
            f.write(xml_content)

    @patch("verify_sitemap_links.check_url")
    @patch("verify_sitemap_links.verify_github_pages_url")
    def test_main_success_all_checks_pass(self, mock_verify_gh: MagicMock, mock_check_url: MagicMock) -> None:
        urls = [
            "https://linuxmalaysia.github.io/ASIMP/architecture.html",
            "https://linuxmalaysia.github.io/ASIMP/readme.html",
        ]
        self._write_sitemap_files(urls)
        mock_verify_gh.return_value = True
        mock_check_url.return_value = (True, "OK")

        try:
            verify_sitemap_links.main()
        except SystemExit as e:
            self.fail(f"main() exited unexpectedly with code {e.code}")

        self.assertEqual(mock_verify_gh.call_count, len(urls))
        self.assertEqual(mock_check_url.call_count, 5)  # deterministic GitBook sample size

    @patch("verify_sitemap_links.check_url")
    @patch("verify_sitemap_links.verify_github_pages_url")
    def test_main_exits_nonzero_on_gh_pages_failure(
        self, mock_verify_gh: MagicMock, mock_check_url: MagicMock
    ) -> None:
        urls = [
            "https://linuxmalaysia.github.io/ASIMP/architecture.html",
            "https://linuxmalaysia.github.io/ASIMP/broken.html",
        ]
        self._write_sitemap_files(urls)
        mock_verify_gh.side_effect = lambda u: "broken" not in u
        mock_check_url.return_value = (True, "OK")

        with self.assertRaises(SystemExit) as cm:
            verify_sitemap_links.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("verify_sitemap_links.check_url")
    @patch("verify_sitemap_links.verify_github_pages_url")
    def test_main_exits_nonzero_on_gitbook_failure(
        self, mock_verify_gh: MagicMock, mock_check_url: MagicMock
    ) -> None:
        urls = ["https://linuxmalaysia.github.io/ASIMP/architecture.html"]
        self._write_sitemap_files(urls)
        mock_verify_gh.return_value = True
        mock_check_url.return_value = (False, "HTTPError:404")

        with self.assertRaises(SystemExit) as cm:
            verify_sitemap_links.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("verify_sitemap_links.check_url")
    @patch("verify_sitemap_links.verify_github_pages_url")
    def test_main_uses_thread_pool_executor_with_max_workers_five(
        self, mock_verify_gh: MagicMock, mock_check_url: MagicMock
    ) -> None:
        urls = ["https://linuxmalaysia.github.io/ASIMP/architecture.html"]
        self._write_sitemap_files(urls)
        mock_verify_gh.return_value = True
        mock_check_url.return_value = (True, "OK")

        with patch("verify_sitemap_links.ThreadPoolExecutor", wraps=ThreadPoolExecutor) as mock_executor:
            try:
                verify_sitemap_links.main()
            except SystemExit as e:
                self.fail(f"main() exited unexpectedly with code {e.code}")

        # One executor for gh_pages_urls, one for the GitBook sample.
        self.assertEqual(mock_executor.call_count, 2)
        for call in mock_executor.call_args_list:
            self.assertEqual(call.kwargs.get("max_workers"), 5)

    @patch("verify_sitemap_links.check_url")
    @patch("verify_sitemap_links.verify_github_pages_url")
    def test_main_preserves_url_result_order_for_gitbook_sample(
        self, mock_verify_gh: MagicMock, mock_check_url: MagicMock
    ) -> None:
        """The zip(sample_gitbook, gb_results) pairing must stay aligned per-URL
        even though results are produced by a thread pool."""
        urls = ["https://linuxmalaysia.github.io/ASIMP/architecture.html"]
        self._write_sitemap_files(urls)
        mock_verify_gh.return_value = True

        random.seed(42)
        expected_sample = random.sample(
            verify_sitemap_links.GITBOOK_URLS, min(5, len(verify_sitemap_links.GITBOOK_URLS))
        )
        failing_url = expected_sample[2]

        def fake_check_url(u: str) -> tuple:
            if u == failing_url:
                return False, "HTTPError:404"
            return True, "OK"

        mock_check_url.side_effect = fake_check_url

        with self.assertRaises(SystemExit) as cm:
            verify_sitemap_links.main()
        self.assertEqual(cm.exception.code, 1)

        # Every URL in the sample must have been checked exactly once, in order.
        called_urls = [c.args[0] for c in mock_check_url.call_args_list]
        self.assertEqual(called_urls, expected_sample)

    @patch("verify_sitemap_links.check_url")
    def test_main_handles_empty_gh_pages_url_list(self, mock_check_url: MagicMock) -> None:
        """ThreadPoolExecutor.map over an empty gh_pages_urls list must not fail,
        and all([]) must be treated as success."""
        self._write_sitemap_files([])
        mock_check_url.return_value = (True, "OK")

        try:
            verify_sitemap_links.main()
        except SystemExit as e:
            self.fail(f"main() exited unexpectedly with code {e.code}")


if __name__ == "__main__":
    unittest.main()
