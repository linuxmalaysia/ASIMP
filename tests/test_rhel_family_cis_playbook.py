"""
Unit tests for playbooks/rhel_family_cis.yml structure and task configurations.
"""

import os
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAYBOOK_PATH = os.path.join(REPO_ROOT, "playbooks", "rhel_family_cis.yml")


class TestRhelFamilyCisPlaybook(unittest.TestCase):
    """Test suite verifying structural correctness of playbooks/rhel_family_cis.yml."""

    @classmethod
    def setUpClass(cls):
        with open(PLAYBOOK_PATH, "r", encoding="utf-8") as f:
            cls.playbook_data = yaml.safe_load(f)
        cls.play = cls.playbook_data[0]
        cls.tasks = cls.play.get("tasks", [])

    def _task(self, name_snippet):
        """Helper to retrieve a task by name substring."""
        for t in self.tasks:
            if name_snippet in t.get("name", ""):
                return t
            if "block" in t:
                for bt in t["block"]:
                    if name_snippet in bt.get("name", ""):
                        return bt
        return None

    def test_os_validation_rejects_centos(self):
        """Assert OS validation requires RedHat family and explicitly excludes CentOS."""
        os_task = self._task("Validate supported OS distribution and major version")
        self.assertIsNotNone(os_task, "OS validation task must exist")
        assert_block = os_task.get("ansible.builtin.assert", {})
        that_list = assert_block.get("that", [])
        dist_check = [stmt for stmt in that_list if "ansible_distribution" in stmt and "in [" in stmt][0]
        self.assertNotIn("centos", dist_check.lower(), "CentOS must be rejected in OS allowlist")
        self.assertIn("redhat", dist_check.lower())
        self.assertIn("almalinux", dist_check.lower())
        self.assertIn("rocky", dist_check.lower())
        self.assertIn("oraclelinux", dist_check.lower())

    def test_remediation_artifact_opt_in_guard(self):
        """Assert oscap generate fix tasks require generate_remediation_artifacts opt-in."""
        bash_fix_task = self._task("Mode 1 - Generate Standalone Bash Remediation Script")
        self.assertIsNotNone(bash_fix_task)
        when_clause = bash_fix_task.get("when", [])
        when_str = str(when_clause)
        self.assertIn("generate_remediation_artifacts", when_str)

        ansible_fix_task = self._task("Mode 1 - Generate Standalone Ansible Remediation Playbook")
        self.assertIsNotNone(ansible_fix_task)
        when_clause_ans = ansible_fix_task.get("when", [])
        when_str_ans = str(when_clause_ans)
        self.assertIn("generate_remediation_artifacts", when_str_ans)

    def test_mount_persist_task_name_lookup(self):
        """Assert task 'Mode 2 - Phase 2 - Persist CIS Level 2 Mount Options in /etc/fstab' exists."""
        mount_task = self._task("Mode 2 - Phase 2 - Persist CIS Level 2 Mount Options in /etc/fstab")
        self.assertIsNotNone(mount_task, "Mount persist task must exist with exact name")
        self.assertEqual(mount_task.get("ansible.posix.mount", {}).get("state"), "present")


if __name__ == "__main__":
    unittest.main()
