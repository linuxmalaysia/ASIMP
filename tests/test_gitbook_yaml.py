#!/usr/bin/env python3
"""
Regression tests for the newly added .gitbook.yaml GitBook configuration file.

.gitbook.yaml declares the GitBook content root and maps the repository's
README.md/SUMMARY.md files as the canonical readme/summary structural files.
These tests parse the file with a real YAML loader and verify:
  1. The file loads as valid YAML (a basic sanity check for the whole file).
  2. It declares the expected top-level keys (version, root, structure) with
     the documented values.
  3. The readme/summary files it points at actually exist in the repository,
     so GitBook builds do not silently break due to a stale mapping.

Run with:
    python3 -m unittest tests/test_gitbook_yaml.py -v
"""
import os
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITBOOK_YAML_PATH = os.path.join(REPO_ROOT, ".gitbook.yaml")


class TestGitbookYaml(unittest.TestCase):
    """Verify .gitbook.yaml is syntactically valid and semantically correct."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(GITBOOK_YAML_PATH, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()
        cls.data = yaml.safe_load(cls.raw_content)

    def test_file_exists(self) -> None:
        self.assertTrue(
            os.path.isfile(GITBOOK_YAML_PATH),
            ".gitbook.yaml must exist at the repository root",
        )

    def test_file_is_valid_yaml_mapping(self) -> None:
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(f".gitbook.yaml must be valid YAML, but failed to parse: {exc}")
        self.assertIsInstance(data, dict)

    def test_declares_expected_version(self) -> None:
        self.assertIn("version", self.data)
        self.assertEqual(self.data["version"], "1.0.0")

    def test_declares_root_as_repository_root(self) -> None:
        self.assertIn("root", self.data)
        self.assertEqual(self.data["root"], "./")

    def test_declares_structure_mapping_with_readme_and_summary(self) -> None:
        self.assertIn("structure", self.data)
        structure = self.data["structure"]
        self.assertIsInstance(structure, dict)
        self.assertEqual(structure.get("readme"), "README.md")
        self.assertEqual(structure.get("summary"), "SUMMARY.md")

    def test_referenced_readme_and_summary_files_exist_in_repo(self) -> None:
        structure = self.data["structure"]
        root = self.data["root"]
        readme_path = os.path.join(REPO_ROOT, root, structure["readme"])
        summary_path = os.path.join(REPO_ROOT, root, structure["summary"])
        self.assertTrue(
            os.path.isfile(readme_path),
            f"structure.readme points at {structure['readme']!r}, but no such file exists at {readme_path}",
        )
        self.assertTrue(
            os.path.isfile(summary_path),
            f"structure.summary points at {structure['summary']!r}, but no such file exists at {summary_path}",
        )

    def test_no_unexpected_top_level_keys(self) -> None:
        # Guards against accidental/unintended additions to the GitBook config
        # surface that would silently change build behavior.
        self.assertEqual(set(self.data.keys()), {"version", "root", "structure"})


if __name__ == "__main__":
    unittest.main()