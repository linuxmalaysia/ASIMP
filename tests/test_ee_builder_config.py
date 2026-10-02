#!/usr/bin/env python3
"""
Unit tests for Ansible Execution Environment (EE) builder configuration
and build script integrity.
"""

import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestEEBuilderConfig(unittest.TestCase):
    """Validate execution-environment files and build_ee.sh script."""

    def test_execution_environment_yml(self) -> None:
        """Verify execution-environment/execution-environment.yml schema and uv steps."""
        ee_yml_path = os.path.join(REPO_ROOT, "execution-environment", "execution-environment.yml")
        self.assertTrue(os.path.isfile(ee_yml_path), "execution-environment.yml must exist")

        with open(ee_yml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "EE definition must be a YAML mapping")
        self.assertEqual(data.get("version"), 3, "EE definition version must be 3")
        self.assertIn("images", data, "EE definition must specify images")
        self.assertEqual(
            data["images"]["base_image"]["name"],
            "quay.io/ansible/ansible-runner@sha256:0d531a89c9d1df52341d087b7a6270d4f24301548e65738805f63901b0f5b9d3"
        )

        steps = data.get("additional_build_steps", {})
        prepend_base = steps.get("prepend_base", [])
        self.assertTrue(
            any("uv" in step for step in prepend_base),
            "prepend_base build steps must contain uv installation"
        )

    def test_ee_dependencies_files(self) -> None:
        """Verify presence and validity of requirements.yml, requirements.txt, and bindep.txt."""
        ee_dir = os.path.join(REPO_ROOT, "execution-environment")
        req_yml = os.path.join(ee_dir, "requirements.yml")
        req_txt = os.path.join(ee_dir, "requirements.txt")
        bindep_txt = os.path.join(ee_dir, "bindep.txt")

        self.assertTrue(os.path.isfile(req_yml), "requirements.yml must exist")
        self.assertTrue(os.path.isfile(req_txt), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(bindep_txt), "bindep.txt must exist")

        with open(req_yml, "r", encoding="utf-8") as f:
            req_data = yaml.safe_load(f)
        self.assertIn("collections", req_data)
        self.assertIn("roles", req_data)

    def test_build_ee_script(self) -> None:
        """Verify scripts/build_ee.sh exists and is executable."""
        script_path = os.path.join(REPO_ROOT, "scripts", "build_ee.sh")
        self.assertTrue(os.path.isfile(script_path), "scripts/build_ee.sh must exist")
        self.assertTrue(os.access(script_path, os.X_OK), "scripts/build_ee.sh must be executable")


if __name__ == "__main__":
    unittest.main()
