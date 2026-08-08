#!/usr/bin/env python3
"""
Unit tests for scripts/add_okf_frontmatter.py (OKF Frontmatter Patcher).

These tests verify semantic categorization, list extraction, title extraction,
and frontmatter injection/updating in isolation against temporary fixtures.

Run with:
    python3 -m unittest tests/test_add_okf_frontmatter.py -v
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

import add_okf_frontmatter  # noqa: E402


class TestAddOkfFrontmatter(unittest.TestCase):
    """Test case for add_okf_frontmatter.py functions."""

    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self):
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    def _write(self, filepath, content):
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _read(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def test_guess_type_and_topics(self):
        # test mapping logic for various filenames and paths
        cases = [
            ("CHANGELOG.md", "meta", ["asimp", "changelog", "history", "releases"]),
            ("CLAUDE.md", "instructions", ["ai", "agents", "guidelines", "rules", "conventions"]),
            ("AGENTS.md", "instructions", ["ai", "agents", "guidelines", "rules", "conventions"]),
            (".agents/skills/my_skill/SKILL.md", "skill", ["ai", "agents", "skills", "antigravity", "jules"]),
            ("docs/some_manual.md", "documentation", ["asimp", "docs", "manual", "security"]),
            ("SECURITY_AUDIT_REPORT.md", "report", ["security", "compliance", "audit", "report", "sandbox"]),
            ("roles/some-role/README.md", "role-documentation", ["ansible", "role", "asimp", "hardening"]),
            ("README.md", "documentation", ["asimp", "readme", "security", "baseline", "hardening"]),
            ("unclassified.md", "documentation", ["asimp", "general"]),
        ]
        for filepath, expected_type, expected_topics in cases:
            # guess_type_and_topics checks rel_path relative to current working directory,
            # so we should write the file or construct filepath relative to tmpcwd.
            t, top = add_okf_frontmatter.guess_type_and_topics(filepath, "dummy content")
            self.assertEqual(t, expected_type, f"Failed for {filepath}")
            self.assertEqual(top, expected_topics, f"Failed for {filepath}")

    def test_extract_list_inline_bracket(self):
        # test parsing inline brackets tags: [val1, val2]
        fm_str = "type: documentation\ntags: [apple, orange, 'banana']\n"
        topics = add_okf_frontmatter.extract_list("tags", fm_str)
        self.assertEqual(topics, ["apple", "orange", "banana"])

    def test_extract_list_indented_block(self):
        # test parsing YAML list block format
        fm_str = "type: documentation\ntags:\n  - apple\n  - 'orange'\n  - \"banana\"\n"
        topics = add_okf_frontmatter.extract_list("tags", fm_str)
        self.assertEqual(topics, ["apple", "orange", "banana"])

    def test_extract_list_empty_or_none(self):
        fm_str = "type: documentation\ntags:\n"
        topics = add_okf_frontmatter.extract_list("tags", fm_str)
        self.assertEqual(topics, [])

        fm_str_missing = "type: documentation\n"
        topics_missing = add_okf_frontmatter.extract_list("tags", fm_str_missing)
        self.assertEqual(topics_missing, [])

    def test_extract_title_from_content(self):
        # markdown title
        content = "\n\n# Dynamic Title\nSome content"
        title = add_okf_frontmatter.extract_title_from_content(content, "docs/foo.md")
        self.assertEqual(title, "Dynamic Title")

        # fallback capitalized filename
        content_no_heading = "Some content without heading"
        title_fallback = add_okf_frontmatter.extract_title_from_content(content_no_heading, "docs/my-awesome-doc.md")
        self.assertEqual(title_fallback, "My Awesome Doc")

    def test_process_file_no_frontmatter(self):
        # Brand new file with no frontmatter should get full OKF block
        path = "README.md"
        content = "# ASIMP Main Readme\nWelcome."
        self._write(path, content)

        add_okf_frontmatter.process_file(path)

        res = self._read(path)
        self.assertTrue(res.startswith("---"))
        self.assertIn('okf_version: "0.1"', res)
        self.assertIn('type: documentation', res)
        self.assertIn('title: "ASIMP Main Readme"', res)
        self.assertIn('timestamp: "2026-08-05T12:00:00Z"', res)
        self.assertIn('topics: [asimp, readme, security, baseline, hardening]', res)

    def test_process_file_partial_frontmatter(self):
        # Existing frontmatter missing some fields
        path = "docs/page.md"
        # Has title, but missing okf_version, type, timestamp, topics
        original = "---\ntitle: \"Existing Title\"\n---\n# My Heading\nBody"
        self._write(path, original)

        add_okf_frontmatter.process_file(path)

        res = self._read(path)
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Existing Title"', res) # Kept original
        self.assertIn('okf_version: "0.1"', res)
        self.assertIn('type: documentation', res)
        self.assertIn('timestamp: "2026-08-05T12:00:00Z"', res)
        self.assertIn('topics: [asimp, docs, manual, security]', res)

    def test_process_file_partial_frontmatter_with_tags_mapping(self):
        # Existing frontmatter has tags, should map them to topics
        path = "docs/page.md"
        original = "---\ntags: [custom1, custom2]\n---\n# My Heading\nBody"
        self._write(path, original)

        add_okf_frontmatter.process_file(path)

        res = self._read(path)
        self.assertTrue(res.startswith("---"))
        self.assertIn('okf_version: "0.1"', res)
        self.assertIn('topics: [custom1, custom2]', res)

    def test_process_file_complete_frontmatter(self):
        # Has all fields, should be unmodified
        path = "docs/page.md"
        original = (
            "---\n"
            'okf_version: "0.1"\n'
            "type: documentation\n"
            'title: "Full Title"\n'
            'timestamp: "2026-08-05T12:00:00Z"\n'
            "topics: [a, b]\n"
            "---\n"
            "# Heading\n"
            "Body"
        )
        self._write(path, original)

        add_okf_frontmatter.process_file(path)

        self.assertEqual(self._read(path), original)

    def test_main_walking(self):
        # Create folder structure under current temp directory (which is self._tmp_dir.name)
        os.makedirs("docs", exist_ok=True)
        os.makedirs(".git", exist_ok=True)
        self._write("docs/test.md", "# Doc title\nContent")
        self._write(".git/test.md", "# Git title\nContent") # Should be excluded
        self._write("README.md", "# Main title\nContent")

        # Mock process_file to check what gets processed
        with patch("add_okf_frontmatter.process_file") as mock_process:
            add_okf_frontmatter.main()
            # Should process README.md and docs/test.md, but NOT .git/test.md
            processed_paths = [os.path.normpath(call[0][0]) for call in mock_process.call_args_list]
            self.assertIn(os.path.normpath("README.md"), processed_paths)
            self.assertIn(os.path.normpath("docs/test.md"), processed_paths)
            self.assertNotIn(os.path.normpath(".git/test.md"), processed_paths)


if __name__ == "__main__":
    unittest.main()
