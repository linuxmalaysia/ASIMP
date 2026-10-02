#!/usr/bin/env python3
"""
Unit test module for scripts/install_all.sh installer script and INSTALL.md documentation.

Tests that scripts/install_all.sh exists, is executable, contains necessary error checks,
and that INSTALL.md exists with required OKF v0.2 frontmatter and ASIMP/DSOM footer.
"""

import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestInstallScriptAndDoc(unittest.TestCase):
    """Test suite validating installation script and documentation artifacts."""

    def test_install_script_exists_and_executable(self) -> None:
        """Verify scripts/install_all.sh exists and is executable."""
        script_path = os.path.join(REPO_ROOT, "scripts", "install_all.sh")
        self.assertTrue(os.path.isfile(script_path), "scripts/install_all.sh must exist")
        self.assertTrue(os.access(script_path, os.X_OK), "scripts/install_all.sh must be executable")

    def test_install_script_contents(self) -> None:
        """Verify scripts/install_all.sh includes set -e, uv setup, and galaxy install."""
        script_path = os.path.join(REPO_ROOT, "scripts", "install_all.sh")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("set -e", content, "install_all.sh must use set -e")
        self.assertIn("python3 -m pip install --user uv", content, "install_all.sh must install uv via pip")
        self.assertIn("ansible-galaxy install -r", content, "install_all.sh must run ansible-galaxy install")
        self.assertNotIn("--ignore-errors", content, "install_all.sh must not pass --ignore-errors")

    def test_install_md_frontmatter_and_footer(self) -> None:
        """Verify INSTALL.md exists, has valid OKF frontmatter and ASIMP footer."""
        install_md_path = os.path.join(REPO_ROOT, "INSTALL.md")
        self.assertTrue(os.path.isfile(install_md_path), "INSTALL.md must exist")

        with open(install_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        self.assertTrue(lines and lines[0].strip() == "---", "INSTALL.md must start with ---")

        closing_idx = -1
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                closing_idx = idx
                break

        self.assertNotEqual(closing_idx, -1, "INSTALL.md must have closing --- frontmatter line")

        fm_raw = "\n".join(lines[1:closing_idx])
        fm_data = yaml.safe_load(fm_raw)

        self.assertIsInstance(fm_data, dict, "INSTALL.md frontmatter must be a YAML dict")
        self.assertEqual(str(fm_data.get("okf_version")), "0.2", "okf_version must be '0.2'")
        self.assertEqual(fm_data.get("type"), "documentation", "type must be 'documentation'")
        self.assertTrue(bool(fm_data.get("title")), "title must not be empty")

        self.assertIn("ASIMP (Ansible System Integrity Management Platform)", content, "INSTALL.md must include standard ASIMP footer")


if __name__ == "__main__":
    unittest.main()
