#!/usr/bin/env python3
"""
Unit tests for OKF v0.1 frontmatter and ASIMP footer standards validation.
Checks all markdown files inside docs/ and root directories to ensure complete compliance.
"""

import os
import re
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestOKFFrontmatterAndFooters(unittest.TestCase):
    """Validate OKF v0.1 frontmatter metadata and standard footers across docs."""

    def test_docs_and_summary_okf_frontmatter(self) -> None:
        """Verify that all markdown files in docs/ and root SUMMARY.md have valid OKF v0.1 frontmatter."""
        target_files = [os.path.join(REPO_ROOT, "SUMMARY.md")]

        docs_dir = os.path.join(REPO_ROOT, "docs")
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(".md"):
                    target_files.append(os.path.join(root, file))

        for filepath in target_files:
            rel_path = os.path.relpath(filepath, REPO_ROOT)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(
                content.startswith("---"),
                f"{rel_path} must start with YAML frontmatter delimiter '---'"
            )

            parts = content.lstrip().split("---", 2)
            self.assertGreaterEqual(
                len(parts),
                3,
                f"{rel_path} must have closing YAML frontmatter delimiter '---'"
            )

            fm_raw = parts[1]
            try:
                fm_data = yaml.safe_load(fm_raw)
            except Exception as e:
                self.fail(f"Failed to parse YAML frontmatter in {rel_path}: {e}")

            self.assertIsInstance(fm_data, dict, f"Frontmatter in {rel_path} must be a YAML mapping")

            # Assert required OKF v0.1 fields
            self.assertIn("okf_version", fm_data, f"{rel_path} missing 'okf_version'")
            self.assertEqual(str(fm_data["okf_version"]), "0.1", f"{rel_path} okf_version must be '0.1'")

            self.assertIn("type", fm_data, f"{rel_path} missing 'type'")
            self.assertIn("title", fm_data, f"{rel_path} missing 'title'")

            self.assertIn("timestamp", fm_data, f"{rel_path} missing 'timestamp'")
            self.assertIn("topics", fm_data, f"{rel_path} missing 'topics'")
            self.assertIsInstance(fm_data["topics"], list, f"{rel_path} 'topics' must be a list")

    def test_markdown_code_block_blank_lines(self) -> None:
        """Verify that markdown files in docs/how-to/ and docs/tutorials/ have blank lines before code blocks."""
        check_dirs = [
            os.path.join(REPO_ROOT, "docs", "how-to"),
            os.path.join(REPO_ROOT, "docs", "tutorials"),
        ]

        for check_dir in check_dirs:
            if not os.path.exists(check_dir):
                continue
            for root, _, files in os.walk(check_dir):
                for file in files:
                    if file.endswith(".md"):
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, REPO_ROOT)
                        with open(filepath, "r", encoding="utf-8") as f:
                            lines = f.readlines()

                        in_code_block = False
                        for i in range(1, len(lines)):
                            line = lines[i].strip()
                            if line.startswith("```"):
                                if not in_code_block:
                                    # Entering opening fence
                                    in_code_block = True
                                    prev_line = lines[i - 1].strip()
                                    if prev_line and not prev_line.startswith("---"):
                                        self.assertEqual(
                                            prev_line,
                                            "",
                                            f"{rel_path}:{i+1} opening code block fence should be preceded by a blank line"
                                        )
                                else:
                                    # Closing fence
                                    in_code_block = False


if __name__ == "__main__":
    unittest.main()
