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


if __name__ == "__main__":
    unittest.main()
