"""
Unit tests for distro-specific playbooks (Ubuntu LTS, Debian, openSUSE).
"""

import os
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestDistroPlaybooks(unittest.TestCase):
    """Test suite verifying structural correctness of distro-specific playbooks."""

    def _load_playbook(self, filename):
        path = os.path.join(REPO_ROOT, "playbooks", filename)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data[0], data[0].get("tasks", [])

    def test_ubuntu_lts_playbook_assertions(self):
        """Assert Ubuntu LTS playbook validates Ubuntu 24.04 and 26.04."""
        play, tasks = self._load_playbook("ubuntu_lts_hardening.yml")
        os_task = next(t for t in tasks if "Validate supported OS" in t.get("name", ""))
        assert_block = os_task.get("ansible.builtin.assert", {})
        that_list = assert_block.get("that", [])
        version_stmt = [s for s in that_list if "ansible_distribution_version" in s][0]
        self.assertIn("24.04", version_stmt)
        self.assertIn("26.04", version_stmt)

    def test_debian_playbook_assertions(self):
        """Assert Debian playbook validates Debian major versions 11, 12, 13."""
        play, tasks = self._load_playbook("debian_hardening.yml")
        os_task = next(t for t in tasks if "Validate supported OS" in t.get("name", ""))
        assert_block = os_task.get("ansible.builtin.assert", {})
        that_list = assert_block.get("that", [])
        version_stmt = [s for s in that_list if "ansible_distribution_major_version" in s][0]
        self.assertIn("11", version_stmt)
        self.assertIn("12", version_stmt)
        self.assertIn("13", version_stmt)

    def test_opensuse_playbook_sysctl_role(self):
        """Assert openSUSE playbook includes sysctl-suse-ASIMP role."""
        play, tasks = self._load_playbook("opensuse_hardening.yml")
        mode2_block = next(t for t in tasks if "Mode 2" in t.get("name", ""))
        block_tasks = mode2_block.get("block", [])
        sysctl_task = next(t for t in block_tasks if "sysctl-suse-ASIMP" in str(t))
        self.assertIsNotNone(sysctl_task)


if __name__ == "__main__":
    unittest.main()
