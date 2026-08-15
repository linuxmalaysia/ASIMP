#!/usr/bin/env python3
"""
Unit tests for OKF v0.1 frontmatter and ASIMP footer standards validation.
Checks all markdown files inside the repository to ensure complete compliance.
"""

from datetime import datetime
import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestOKFFrontmatterAndFooters(unittest.TestCase):
    """Validate OKF v0.1 frontmatter metadata and standard footers across docs."""

    def test_repository_markdown_okf_frontmatter(self) -> None:
        """Verify that all markdown files in the repository have valid OKF v0.1 frontmatter."""
        exclude_dirs = {".git", "node_modules", "venv", ".venv", ".pytest_cache", "asimp_mock"}
        target_files = []

        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, file), REPO_ROOT)
                    if rel_path.startswith("roles/lynis-ansible") or "data/asimp_mock" in rel_path:
                        continue
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

            # Assert okf_version
            self.assertIn("okf_version", fm_data, f"{rel_path} missing 'okf_version'")
            self.assertEqual(str(fm_data["okf_version"]), "0.1", f"{rel_path} okf_version must be '0.1'")

            # Assert nonempty string type and title
            self.assertIn("type", fm_data, f"{rel_path} missing 'type'")
            self.assertIsInstance(fm_data["type"], str, f"{rel_path} 'type' must be a string")
            self.assertTrue(bool(fm_data["type"].strip()), f"{rel_path} 'type' must not be empty")

            self.assertIn("title", fm_data, f"{rel_path} missing 'title'")
            self.assertIsInstance(fm_data["title"], str, f"{rel_path} 'title' must be a string")
            self.assertTrue(bool(fm_data["title"].strip()), f"{rel_path} 'title' must not be empty")

            # Assert ISO-8601 parsable timestamp
            self.assertIn("timestamp", fm_data, f"{rel_path} missing 'timestamp'")
            ts_str = str(fm_data["timestamp"])
            try:
                datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except ValueError as e:
                self.fail(f"{rel_path} 'timestamp' ({ts_str}) is not valid ISO-8601: {e}")

            # Assert non-empty topics list containing valid topic strings
            self.assertIn("topics", fm_data, f"{rel_path} missing 'topics'")
            self.assertIsInstance(fm_data["topics"], list, f"{rel_path} 'topics' must be a list")
            self.assertTrue(len(fm_data["topics"]) > 0, f"{rel_path} 'topics' list must not be empty")
            for topic in fm_data["topics"]:
                self.assertIsInstance(topic, str, f"{rel_path} topic element must be a string")
                self.assertTrue(bool(topic.strip()), f"{rel_path} topic element must not be empty")

    def test_markdown_code_block_blank_lines(self) -> None:
        """Verify that markdown files in docs/how-to/ and docs/tutorials/ have blank lines around code blocks."""
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
                                    if i + 1 < len(lines):
                                        next_line = lines[i + 1].strip()
                                        if next_line and not next_line.startswith("---"):
                                            self.assertEqual(
                                                next_line,
                                                "",
                                                f"{rel_path}:{i+1} closing code block fence should be followed by a blank line"
                                            )


if __name__ == "__main__":
    unittest.main()
