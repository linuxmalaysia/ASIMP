#!/usr/bin/env python3
"""
Unit tests for Google Jules Session History & Google Antigravity Migration Archive.
Verifies structure, JSON validity, OKF frontmatter, and DSOM compliance.
"""

import json
import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN_DIR = os.path.join(REPO_ROOT, ".agents", "brain")
JULES_DIR = os.path.join(BRAIN_DIR, "jules_history")


class TestJulesHistoryExport(unittest.TestCase):
    """Test suite for Jules export artifacts in .agents/brain/."""

    def test_jules_history_files_exist(self) -> None:
        """Verify that mandatory JSON files exist in jules_history directory."""
        mandatory_files = [
            "user-settings.json",
            "env-variables.json",
            "scheduled-tasks.json",
            "sources.json",
            "sessions.json",
        ]
        for filename in mandatory_files:
            filepath = os.path.join(JULES_DIR, filename)
            self.assertTrue(os.path.isfile(filepath), f"{filename} must exist in {JULES_DIR}")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIsNotNone(data)

    def test_jules_history_repo_data(self) -> None:
        """Verify that repository memories and setup/test scripts are present."""
        repo_dir = os.path.join(JULES_DIR, "repos", "linuxmalaysia_ASIMP")
        self.assertTrue(os.path.isdir(repo_dir), f"Repository directory {repo_dir} must exist")
        self.assertTrue(os.path.isfile(os.path.join(repo_dir, "setup.sh")))
        self.assertTrue(os.path.isfile(os.path.join(repo_dir, "test-command.txt")))
        self.assertTrue(os.path.isfile(os.path.join(repo_dir, "memories.json")))
        self.assertTrue(os.path.isfile(os.path.join(repo_dir, "memories.md")))

    def test_jules_history_session_data(self) -> None:
        """Verify session artifacts: session.json, activities.json, summary.md, patch."""
        sess_dir = os.path.join(JULES_DIR, "sessions", "13663164952111193775")
        self.assertTrue(os.path.isdir(sess_dir), f"Session directory {sess_dir} must exist")

        session_file = os.path.join(sess_dir, "session.json")
        self.assertTrue(os.path.isfile(session_file))
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            self.assertIsInstance(session_data, dict)

        activities_file = os.path.join(sess_dir, "activities.json")
        self.assertTrue(os.path.isfile(activities_file))
        with open(activities_file, "r", encoding="utf-8") as f:
            activities_data = json.load(f)
            self.assertIsInstance(activities_data, list)

        self.assertTrue(os.path.isfile(os.path.join(sess_dir, "summary.md")))
        self.assertTrue(os.path.isfile(os.path.join(sess_dir, "patch-1.diff")))

    def test_jules_history_archive_frontmatter_and_footer(self) -> None:
        """Verify that jules_history_archive.md conforms to OKF v0.2 and ASIMP footer."""
        archive_path = os.path.join(BRAIN_DIR, "jules_history_archive.md")
        self.assertTrue(os.path.isfile(archive_path), "jules_history_archive.md must exist")
        with open(archive_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(content.startswith("---\n"), "Archive must start with YAML frontmatter")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "Frontmatter must be enclosed by ---")
        meta = yaml.safe_load(parts[1])
        self.assertEqual(meta.get("okf_version"), "0.2")
        self.assertEqual(meta.get("type"), "archive")
        self.assertIn("trust_level", meta)
        self.assertIn("jules", meta.get("topics", []))
        self.assertIn("antigravity", meta.get("topics", []))

        non_empty_lines = [line.strip() for line in content.splitlines() if line.strip()]
        self.assertTrue(non_empty_lines, "Archive must have non-empty content")
        expected_footer_prefix = "ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol"
        self.assertTrue(
            non_empty_lines[-1].startswith(expected_footer_prefix),
            f"Final non-empty line must start with ASIMP footer, got: {non_empty_lines[-1]}"
        )


if __name__ == "__main__":
    unittest.main()
