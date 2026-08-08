#!/usr/bin/env python3
"""
Unit tests for scripts/prepare_docs.py (Jekyll Documentation Pre-processing Script).

These tests verify the markdown header parsing, Jekyll front matter injection,
and skip behaviors in isolation against temporary fixtures.

Run with:
    python3 -m unittest tests/test_prepare_docs.py -v
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import prepare_docs  # noqa: E402


class TestPrepareDocs(unittest.TestCase):
    """Test case for prepare_docs.py functions."""

    def setUp(self) -> None:
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self) -> None:
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    def _write(self, filepath: str, content: str) -> None:
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _read(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def test_process_markdown_no_front_matter_with_heading(self) -> None:
        # File has no front matter, has a clear markdown heading
        path = "docs/test_page.md"
        content = "# My Sample Title\nThis is some body text."
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertTrue(result.startswith("---"))
        self.assertIn('title: "My Sample Title"', result)
        self.assertIn("# My Sample Title\nThis is some body text.", result)

    def test_process_markdown_no_front_matter_fallback_title(self) -> None:
        # File has no front matter, has no markdown heading. Falls back to capitalized filename.
        path = "docs/some-test_doc.md"
        content = "Just some content without headings."
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertTrue(result.startswith("---"))
        self.assertIn('title: "Some Test Doc"', result)
        self.assertIn("Just some content without headings.", result)

    def test_process_markdown_already_has_front_matter(self) -> None:
        # File already has front matter. It should skip layout/front matter injection.
        path = "docs/already_has.md"
        original = "---\ntitle: \"Existing Title\"\n---\n# My Heading\nBody text."
        self._write(path, original)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertEqual(result, original)

    def test_main_scans_docs_directory_correctly(self) -> None:
        # Create a mock docs directory inside our temp directory
        os.makedirs("docs", exist_ok=True)
        self._write("docs/doc1.md", "# First Doc\nContent")
        self._write("docs/doc2.md", "---\ntitle: \"Second\"\n---\nContent")
        self._write("docs/nested/doc3.md", "# Third Nested Doc\nContent")
        self._write("docs/ignored.txt", "Should not be touched")

        # Mock os.path.abspath to return the path under our temp directory for 'docs'
        real_docs_path = os.path.abspath(os.path.join(REPO_ROOT, "docs"))
        temp_docs_path = os.path.abspath("docs")

        orig_abspath = os.path.abspath

        def mock_abspath(path):
            abs_path = orig_abspath(path)
            if abs_path == real_docs_path:
                return temp_docs_path
            return abs_path

        with patch("os.path.abspath", side_effect=mock_abspath):
            prepare_docs.main()

        # Doc1 should be updated (it had no front matter)
        doc1_content = self._read("docs/doc1.md")
        self.assertTrue(doc1_content.startswith("---"))
        self.assertIn('title: "First Doc"', doc1_content)

        # Doc2 should not be modified
        doc2_content = self._read("docs/doc2.md")
        self.assertTrue(doc2_content.startswith("---"))
        self.assertIn('title: "Second"', doc2_content)

        # doc3.md should be updated (nested without front matter)
        doc3_content = self._read("docs/nested/doc3.md")
        self.assertTrue(doc3_content.startswith("---"))
        self.assertIn('title: "Third Nested Doc"', doc3_content)

        # ignored.txt should not be touched
        self.assertEqual(self._read("docs/ignored.txt"), "Should not be touched")

    def test_main_error_docs_not_exists(self) -> None:
        # When docs does not exist, prepare_docs.main should print error and return without raising
        with patch("os.path.exists", return_value=False):
            try:
                prepare_docs.main()
            except Exception as exc:
                self.fail(f"prepare_docs.main() raised unexpectedly: {exc}")


if __name__ == "__main__":
    unittest.main()
