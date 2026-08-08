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

    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self):
        """Restore the original working directory and clean up the temporary test directory."""
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    def _write(self, filepath, content):
        """
        Write text content to a UTF-8-encoded file, creating its parent directory when needed.
        
        Parameters:
            filepath: The path of the file to write.
            content: The text to write to the file.
        """
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _read(self, filepath):
        """Read and return the UTF-8 text content of a file.
        
        Parameters:
        	filepath: Path to the file to read.
        
        Returns:
        	str: The file's text content.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def test_process_markdown_no_front_matter_with_heading(self):
        # File has no front matter, has a clear markdown heading
        path = "docs/test_page.md"
        content = "# My Sample Title\nThis is some body text."
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertTrue(result.startswith("---"))
        self.assertIn('title: "My Sample Title"', result)
        self.assertIn("# My Sample Title\nThis is some body text.", result)

    def test_process_markdown_no_front_matter_fallback_title(self):
        # File has no front matter, has no markdown heading. Falls back to capitalized filename.
        path = "docs/some-test_doc.md"
        content = "Just some content without headings."
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertTrue(result.startswith("---"))
        self.assertIn('title: "Some Test Doc"', result)
        self.assertIn("Just some content without headings.", result)

    def test_process_markdown_already_has_front_matter(self):
        # File already has front matter. It should skip layout/front matter injection.
        path = "docs/already_has.md"
        original = "---\ntitle: \"Existing Title\"\n---\n# My Heading\nBody text."
        self._write(path, original)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertEqual(result, original)

    def test_main_scans_docs_directory_correctly(self):
        # Create a mock docs directory inside our temp directory
        os.makedirs("docs", exist_ok=True)
        self._write("docs/doc1.md", "# First Doc\nContent")
        self._write("docs/doc2.md", "---\ntitle: \"Second\"\n---\nContent")
        self._write("docs/ignored.txt", "Should not be touched")

        # Mock os.path.abspath to return the path under our temp directory for 'docs'
        real_docs_path = os.path.abspath(os.path.join(REPO_ROOT, "docs"))
        temp_docs_path = os.path.abspath("docs")

        orig_abspath = os.path.abspath

        def mock_abspath(path):
            """
            Redirect the repository docs path to the temporary test directory.
            """
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

        # ignored.txt should not be touched
        self.assertEqual(self._read("docs/ignored.txt"), "Should not be touched")

    def test_main_error_docs_not_exists(self):
        # When docs does not exist, prepare_docs.main should print error and return without raising
        with patch("os.path.exists", return_value=False):
            try:
                prepare_docs.main()
            except Exception as exc:
                self.fail(f"prepare_docs.main() raised unexpectedly: {exc}")

    def test_main_error_docs_not_exists_prints_message(self):
        # The error message should mention the missing docs path and must not
        # attempt to walk/process any files.
        import io
        from contextlib import redirect_stdout

        captured = io.StringIO()
        with patch("os.path.exists", return_value=False), \
                patch("os.walk") as mock_walk, \
                redirect_stdout(captured):
            prepare_docs.main()

        self.assertIn("does not exist", captured.getvalue())
        mock_walk.assert_not_called()

    def test_process_markdown_file_first_heading_wins_with_leading_text(self):
        # The first '#'-style heading anywhere in the content (in reading order)
        # should be used as the title, even if preceded by non-heading text.
        path = "docs/multi_heading.md"
        content = "Some intro text.\n## Second Level Heading\nMore text\n# Another Heading"
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertIn('title: "Second Level Heading"', result)

    def test_process_markdown_file_skips_when_leading_blank_lines_precede_front_matter(self):
        # Leading whitespace before an existing '---' front matter block must still
        # be recognized as "has front matter" (content is stripped before the check),
        # and the file must be left completely untouched.
        path = "docs/leading_blank.md"
        original = "\n\n---\ntitle: \"Existing\"\n---\n# Heading\nBody"
        self._write(path, original)

        prepare_docs.process_markdown_file(path)

        self.assertEqual(self._read(path), original)

    def test_process_markdown_file_fallback_title_formatting(self):
        # Underscores and hyphens in the filename should become spaces, and the
        # result should be title-cased, including alphanumeric tokens like 'v2'.
        path = "docs/2024-report_v2.md"
        content = "Just body text, no heading."
        self._write(path, content)

        prepare_docs.process_markdown_file(path)

        result = self._read(path)
        self.assertIn('title: "2024 Report V2"', result)

    def test_main_recurses_into_nested_subdirectories(self):
        # os.walk should traverse arbitrarily nested subdirectories under docs/.
        os.makedirs("docs/a/b/c", exist_ok=True)
        self._write("docs/a/b/c/deep.md", "# Deep Doc\nContent")

        real_docs_path = os.path.abspath(os.path.join(REPO_ROOT, "docs"))
        temp_docs_path = os.path.abspath("docs")
        orig_abspath = os.path.abspath

        def mock_abspath(path):
            """Redirect the repository docs path to the temporary test directory."""
            abs_path = orig_abspath(path)
            if abs_path == real_docs_path:
                return temp_docs_path
            return abs_path

        with patch("os.path.abspath", side_effect=mock_abspath):
            prepare_docs.main()

        deep_content = self._read("docs/a/b/c/deep.md")
        self.assertTrue(deep_content.startswith("---"))
        self.assertIn('title: "Deep Doc"', deep_content)


if __name__ == "__main__":
    unittest.main()
