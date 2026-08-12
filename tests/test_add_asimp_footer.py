#!/usr/bin/env python3
"""
Unit tests for scripts/add_asimp_footer.py (ASIMP Standard Footer Patcher).

These tests verify the footer-presence check, footer-append formatting, and
the directory/file exclusion logic used when walking the repository in
isolation against temporary fixtures.

Run with:
    python3 -m unittest tests/test_add_asimp_footer.py -v
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

import add_asimp_footer  # noqa: E402


class TestAddAsimpFooter(unittest.TestCase):
    """Test case for add_asimp_footer.py functions."""

    EXPECTED_FOOTER_TEXT = (
        "ASIMP (Ansible System Integrity Management Platform) | "
        "Deep State of Mind (DSOM) For My AI Protocol | "
        "Harisfazillah Jamel (LinuxMalaysia) | "
        "2026-07-12 Standard: UK English | "
        "DBP-standard Bahasa Melayu Malaysia (Piawai) | "
        "GNU General Public License v3.0 | "
        "[Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)"
    )

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

    # -- FOOTER_TEXT constant ------------------------------------------------

    def test_footer_text_constant_matches_expected_standard(self) -> None:
        # Guard against accidental drift of the literal footer string, since
        # every changed documentation file in the repo depends on this exact
        # wording matching verbatim.
        self.assertEqual(add_asimp_footer.FOOTER_TEXT, self.EXPECTED_FOOTER_TEXT)

    # -- patch_markdown_file ---------------------------------------------------

    def test_patch_markdown_file_appends_footer_when_absent(self) -> None:
        path = "README.md"
        content = "# ASIMP\nSome content."
        self._write(path, content)

        add_asimp_footer.patch_markdown_file(path)

        res = self._read(path)
        expected = content + "\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        self.assertEqual(res, expected)

    def test_patch_markdown_file_strips_trailing_whitespace_before_appending(self) -> None:
        path = "docs/page.md"
        content = "# Heading\nBody text.\n\n\n   \n"
        self._write(path, content)

        add_asimp_footer.patch_markdown_file(path)

        res = self._read(path)
        expected = "# Heading\nBody text." + "\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        self.assertEqual(res, expected)

    def test_patch_markdown_file_noop_when_footer_already_present(self) -> None:
        path = "AGENTS.md"
        original = (
            "# Agents\nSome instructions.\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        )
        self._write(path, original)

        add_asimp_footer.patch_markdown_file(path)

        # File must be byte-for-byte unchanged (idempotent, no duplicate footer).
        self.assertEqual(self._read(path), original)

    def test_patch_markdown_file_noop_when_footer_embedded_mid_document(self) -> None:
        path = "docs/weird.md"
        original = (
            "# Title\n" + add_asimp_footer.FOOTER_TEXT + "\nMore content below.\n"
        )
        self._write(path, original)

        add_asimp_footer.patch_markdown_file(path)

        # It should append the footer to the end since the mid-document footer is not the canonical trailing block.
        expected = original.rstrip() + "\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        self.assertEqual(self._read(path), expected)

    def test_patch_markdown_file_on_empty_file(self) -> None:
        path = "EMPTY.md"
        self._write(path, "")

        add_asimp_footer.patch_markdown_file(path)

        res = self._read(path)
        expected = "\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        self.assertEqual(res, expected)

    def test_patch_markdown_file_preserves_unicode_content(self) -> None:
        path = "docs/unicode.md"
        content = "# Piawai DBP\nBahasa Melayu Malaysia: café, naïve, 日本語.\n"
        self._write(path, content)

        add_asimp_footer.patch_markdown_file(path)

        res = self._read(path)
        self.assertTrue(res.startswith(content.rstrip()))
        self.assertIn(add_asimp_footer.FOOTER_TEXT, res)

    def test_patch_markdown_file_prints_noop_message(self) -> None:
        path = "README.md"
        original = "Body\n\n---\n\n" + add_asimp_footer.FOOTER_TEXT + "\n"
        self._write(path, original)

        with patch("builtins.print") as mock_print:
            add_asimp_footer.patch_markdown_file(path)
            mock_print.assert_called_once_with(
                f"No update needed (already has footer): {path}"
            )

    def test_patch_markdown_file_prints_success_message(self) -> None:
        path = "README.md"
        self._write(path, "Body")

        with patch("builtins.print") as mock_print:
            add_asimp_footer.patch_markdown_file(path)
            mock_print.assert_called_once_with(
                f"Successfully appended standard footer to: {path}"
            )

    # -- main() directory/file traversal ---------------------------------------

    def test_main_walking_excludes_standard_dirs(self) -> None:
        os.makedirs("docs", exist_ok=True)
        os.makedirs("other_docs", exist_ok=True)
        os.makedirs(".git", exist_ok=True)
        os.makedirs("node_modules", exist_ok=True)
        os.makedirs("venv", exist_ok=True)
        os.makedirs(".venv", exist_ok=True)

        self._write("docs/test.md", "# Doc title\nContent")
        self._write("other_docs/test.md", "# Other Doc title\nContent")
        self._write(".git/test.md", "# Git title\nContent")
        self._write("node_modules/test.md", "# Node title\nContent")
        self._write("venv/test.md", "# Venv title\nContent")
        self._write(".venv/test.md", "# Dotvenv title\nContent")
        self._write("README.md", "# Main title\nContent")

        with patch("add_asimp_footer.patch_markdown_file") as mock_patch:
            add_asimp_footer.main()
            processed_paths = [os.path.normpath(call[0][0]) for call in mock_patch.call_args_list]
            self.assertIn(os.path.normpath("README.md"), processed_paths)
            self.assertIn(os.path.normpath("other_docs/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath("docs/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath(".git/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath("node_modules/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath("venv/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath(".venv/test.md"), processed_paths)

    def test_main_excludes_lynis_ansible_dir_anywhere_in_tree(self) -> None:
        # A directory literally named 'lynis-ansible' must be pruned, whether
        # it lives under roles/ or anywhere else in the tree.
        os.makedirs("roles/lynis-ansible/nested", exist_ok=True)
        os.makedirs("other/lynis-ansible", exist_ok=True)

        self._write("roles/lynis-ansible/README.md", "# Third-party\nContent")
        self._write("roles/lynis-ansible/nested/deep.md", "# Deep\nContent")
        self._write("other/lynis-ansible/README.md", "# Other\nContent")
        self._write("roles/own-role.md", "# Own role\nContent")

        with patch("add_asimp_footer.patch_markdown_file") as mock_patch:
            add_asimp_footer.main()
            processed_paths = [os.path.normpath(call[0][0]) for call in mock_patch.call_args_list]
            self.assertNotIn(os.path.normpath("roles/lynis-ansible/README.md"), processed_paths)
            self.assertNotIn(os.path.normpath("roles/lynis-ansible/nested/deep.md"), processed_paths)
            self.assertNotIn(os.path.normpath("other/lynis-ansible/README.md"), processed_paths)
            self.assertIn(os.path.normpath("roles/own-role.md"), processed_paths)

    def test_main_ignores_non_markdown_files(self) -> None:
        self._write("notes.txt", "not markdown")
        self._write("README.md", "# Real doc\nContent")

        with patch("add_asimp_footer.patch_markdown_file") as mock_patch:
            add_asimp_footer.main()
            processed_paths = [os.path.normpath(call[0][0]) for call in mock_patch.call_args_list]
            self.assertNotIn(os.path.normpath("notes.txt"), processed_paths)
            self.assertIn(os.path.normpath("README.md"), processed_paths)

    def test_main_end_to_end_appends_footer_to_real_files(self) -> None:
        # Exercise main() without mocking patch_markdown_file to confirm the
        # full walk-and-patch pipeline actually mutates matching files on disk.
        os.makedirs("docs", exist_ok=True)
        os.makedirs("other_docs", exist_ok=True)
        os.makedirs("roles/lynis-ansible", exist_ok=True)

        self._write("README.md", "# Root readme\nBody.")
        self._write("docs/page.md", "# Page\nBody.")
        self._write("other_docs/page.md", "# Other Page\nBody.")
        self._write("roles/lynis-ansible/README.md", "# Vendored\nBody.")

        add_asimp_footer.main()

        self.assertIn(add_asimp_footer.FOOTER_TEXT, self._read("README.md"))
        self.assertIn(add_asimp_footer.FOOTER_TEXT, self._read("other_docs/page.md"))
        # Excluded docs directory should be left completely untouched.
        self.assertEqual(self._read("docs/page.md"), "# Page\nBody.")
        # Vendored third-party file must be left completely untouched.
        self.assertEqual(self._read("roles/lynis-ansible/README.md"), "# Vendored\nBody.")


if __name__ == "__main__":
    unittest.main()