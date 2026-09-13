"""Unit tests for the Ubuntu LTS, Debian, and openSUSE playbooks."""

import ast
import os
import re
import unittest

import yaml


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAYBOOKS = (
    "ubuntu_lts_hardening.yml",
    "debian_hardening.yml",
    "opensuse_hardening.yml",
)
TASK_KEYWORDS = {
    "any_errors_fatal",
    "args",
    "async",
    "block",
    "become",
    "become_exe",
    "become_flags",
    "become_method",
    "become_user",
    "changed_when",
    "check_mode",
    "collections",
    "connection",
    "debugger",
    "delegate_facts",
    "delegate_to",
    "diff",
    "environment",
    "failed_when",
    "ignore_errors",
    "loop",
    "loop_control",
    "module_defaults",
    "name",
    "no_log",
    "notify",
    "poll",
    "port",
    "register",
    "remote_user",
    "retries",
    "run_once",
    "tags",
    "throttle",
    "timeout",
    "until",
    "vars",
    "when",
}


class TestDistroPlaybooks(unittest.TestCase):
    """Verify the safety and hardening contracts of each distro playbook."""

    @classmethod
    def setUpClass(cls):
        """Load all three playbooks once for the test class."""
        cls.plays = {}
        for filename in PLAYBOOKS:
            path = os.path.join(REPO_ROOT, "playbooks", filename)
            with open(path, "r", encoding="utf-8") as playbook_file:
                data = yaml.safe_load(playbook_file)
            if not isinstance(data, list) or len(data) != 1:
                raise AssertionError(f"{filename} must contain exactly one play")
            cls.plays[filename] = data[0]

    def _tasks(self, filename):
        """Return the top-level tasks for a named playbook."""
        return self.plays[filename].get("tasks", [])

    def _task(self, filename, name_snippet, *, nested=False):
        """Find one task by name, optionally descending into block tasks."""
        tasks = self._tasks(filename)
        if nested:
            tasks = [task for parent in tasks for task in parent.get("block", [])]
        matches = [task for task in tasks if name_snippet in task.get("name", "")]
        self.assertEqual(
            len(matches),
            1,
            f"Expected exactly one task containing {name_snippet!r} in {filename}",
        )
        return matches[0]

    def _mode_block(self, filename, mode):
        """Return the report or remediation block for a playbook."""
        return self._task(filename, f"Mode {mode} -")

    def _assertion_conditions(self, filename, name_snippet):
        """Return the conditions from a named assert task."""
        task = self._task(filename, name_snippet)
        conditions = task.get("ansible.builtin.assert", {}).get("that", [])
        self.assertIsInstance(conditions, list)
        self.assertTrue(conditions, f"{task['name']} must contain assertions")
        return conditions

    def _literal_list(self, expression):
        """Extract and safely parse the first list literal in an expression."""
        match = re.search(r"\[[^]]*\]", expression)
        self.assertIsNotNone(match, f"No list literal found in {expression!r}")
        return ast.literal_eval(match.group(0))

    def test_playbook_defaults_are_safe_and_consistent(self):
        """Default every playbook to report mode with the shared report path."""
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                play = self.plays[filename]
                self.assertEqual(play.get("hosts"), "all")
                self.assertIs(play.get("become"), True)
                self.assertEqual(play.get("vars", {}).get("execution_mode"), "report")
                self.assertEqual(
                    play.get("vars", {}).get("openscap_report_dir"),
                    "/opt/report/openscap",
                )
                directory_task = self._task(filename, "Ensure Report Directory Exists")
                self.assertEqual(
                    directory_task.get("ansible.builtin.file"),
                    {
                        "path": "{{ openscap_report_dir }}",
                        "state": "directory",
                        "mode": "0755",
                    },
                )

    def test_execution_mode_allowlist_rejects_unknown_and_empty_values(self):
        """Accept only report/remediate and reject representative invalid modes."""
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                conditions = self._assertion_conditions(
                    filename, "Validate execution_mode parameter"
                )
                self.assertEqual(len(conditions), 1)
                allowed_modes = self._literal_list(conditions[0])
                self.assertEqual(allowed_modes, ["report", "remediate"])
                for invalid_mode in ("", "audit", "apply", "REPORT", None):
                    self.assertNotIn(invalid_mode, allowed_modes)

    def test_ubuntu_lts_os_allowlist_is_exact(self):
        """Allow only Ubuntu 24.04 and 26.04, excluding adjacent releases."""
        conditions = self._assertion_conditions(
            "ubuntu_lts_hardening.yml", "Validate supported OS"
        )
        self.assertIn("ansible_distribution == 'Ubuntu'", conditions)
        version_condition = next(
            condition
            for condition in conditions
            if "ansible_distribution_version" in condition
        )
        allowed_versions = self._literal_list(version_condition)
        self.assertEqual(allowed_versions, ["24.04", "26.04"])
        for unsupported_version in ("22.04", "25.10", "26.10", "24.04.1", ""):
            self.assertNotIn(unsupported_version, allowed_versions)

    def test_debian_os_allowlist_is_exact(self):
        """Require Debian family/distribution and major versions 11 through 13."""
        conditions = self._assertion_conditions(
            "debian_hardening.yml", "Validate supported OS"
        )
        self.assertIn("ansible_os_family == 'Debian'", conditions)
        self.assertIn("ansible_distribution == 'Debian'", conditions)
        version_condition = next(
            condition
            for condition in conditions
            if "ansible_distribution_major_version" in condition
        )
        self.assertIn("| string", version_condition)
        allowed_versions = self._literal_list(version_condition)
        self.assertEqual(allowed_versions, ["11", "12", "13"])
        for unsupported_version in ("10", "14", "testing", ""):
            self.assertNotIn(unsupported_version, allowed_versions)

    def test_opensuse_os_check_has_known_distributions_and_family_fallback(self):
        """Cover named SUSE distributions while retaining the Suse family fallback."""
        conditions = self._assertion_conditions(
            "opensuse_hardening.yml", "Validate supported OS"
        )
        self.assertEqual(len(conditions), 1)
        condition = conditions[0]
        self.assertEqual(
            self._literal_list(condition),
            [
                "SUSE",
                "SLES",
                "SLED",
                "openSUSE",
                "opensuse-leap",
                "opensuse-tumbleweed",
            ],
        )
        self.assertIn("or (ansible_os_family == 'Suse')", condition)
        self.assertNotIn("RedHat", condition)
        self.assertNotIn("Debian", condition)

    def test_sandbox_detection_is_present_before_mode_blocks(self):
        """Detect /home/jules and derive the safe sandbox fact before mode work."""
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                tasks = self._tasks(filename)
                check = self._task(filename, "Check Sandbox Mode")
                fact = self._task(filename, "Set Sandbox Fact")
                self.assertEqual(
                    check.get("ansible.builtin.stat", {}).get("path"), "/home/jules"
                )
                self.assertEqual(check.get("register"), "jules_sandbox_stat")
                self.assertEqual(
                    fact.get("ansible.builtin.set_fact", {}).get("is_sandbox_jules"),
                    "{{ jules_sandbox_stat.stat.exists | default(false) }}",
                )
                self.assertLess(tasks.index(check), tasks.index(self._mode_block(filename, 1)))
                self.assertLess(tasks.index(fact), tasks.index(self._mode_block(filename, 1)))

    def test_report_and_remediation_blocks_are_mutually_exclusive(self):
        """Gate report and remediation blocks on their exact execution modes."""
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                report = self._mode_block(filename, 1)
                remediation = self._mode_block(filename, 2)
                self.assertEqual(report.get("when"), 'execution_mode == "report"')
                self.assertEqual(remediation.get("when"), 'execution_mode == "remediate"')

                report_tasks = report.get("block", [])
                self.assertEqual(len(report_tasks), 2)
                self.assertEqual(
                    report_tasks[0]
                    .get("ansible.builtin.include_role", {})
                    .get("name"),
                    "reporting-ASIMP",
                )
                self.assertEqual(
                    report_tasks[0].get("vars", {}).get("execution_mode"), "dev"
                )
                self.assertIn("ansible.builtin.debug", report_tasks[1])

    def test_remediation_role_sequence_and_distro_specific_options(self):
        """Preserve measure/harden/re-measure ordering and distro role options."""
        expectations = {
            "ubuntu_lts_hardening.yml": (
                [
                    "reporting-ASIMP",
                    "update-ubuntu-ASIMP",
                    "lynis-ansible",
                    "reporting-ASIMP",
                ],
                "update-ubuntu-ASIMP",
                {"debsums_ubuntu_check": True, "upgrade_ubuntu_check": True},
            ),
            "debian_hardening.yml": (
                [
                    "reporting-ASIMP",
                    "update-ubuntu-ASIMP",
                    "lynis-ansible",
                    "reporting-ASIMP",
                ],
                "update-ubuntu-ASIMP",
                {"debsums_ubuntu_check": True, "upgrade_ubuntu_check": False},
            ),
            "opensuse_hardening.yml": (
                [
                    "reporting-ASIMP",
                    "sysctl-suse-ASIMP",
                    "lynis-ansible",
                    "reporting-ASIMP",
                ],
                "sysctl-suse-ASIMP",
                {"suse_sysctl_auto_calc_resources": True},
            ),
        }
        for filename, (expected_roles, distro_role, expected_vars) in expectations.items():
            with self.subTest(playbook=filename):
                block = self._mode_block(filename, 2).get("block", [])
                role_tasks = [
                    task for task in block if "ansible.builtin.include_role" in task
                ]
                roles = [
                    task["ansible.builtin.include_role"]["name"] for task in role_tasks
                ]
                self.assertEqual(roles, expected_roles)
                selected_task = next(
                    task
                    for task in role_tasks
                    if task["ansible.builtin.include_role"]["name"] == distro_role
                )
                self.assertEqual(selected_task.get("vars"), expected_vars)
                self.assertEqual(
                    role_tasks[0].get("vars", {}).get("execution_mode"), "dev"
                )
                self.assertEqual(
                    role_tasks[-1].get("vars", {}).get("execution_mode"), "dev"
                )

    def test_sensitive_file_permissions_are_complete(self):
        """Apply the exact owner, group, and permission matrix on every distro."""
        expected_permissions = {
            "/etc/passwd": "0644",
            "/etc/shadow": "0000",
            "/etc/group": "0644",
            "/etc/gshadow": "0000",
        }
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                task = self._task(filename, "Apply System File Permissions", nested=True)
                module = task.get("ansible.builtin.file", {})
                self.assertEqual(module.get("owner"), "root")
                self.assertEqual(module.get("group"), "root")
                self.assertEqual(module.get("mode"), "{{ item.mode }}")
                self.assertEqual(
                    {item["path"]: item["mode"] for item in task.get("loop", [])},
                    expected_permissions,
                )
                self.assertEqual(task.get("register"), "file_perm_res")

    def test_ssh_hardening_validates_before_safely_reloading(self):
        """Validate changed SSH config and reload only off-sandbox after success."""
        expected_lines = {
            "PermitRootLogin no",
            "PasswordAuthentication no",
            "MaxAuthTries 4",
            "ClientAliveInterval 300",
            "ClientAliveCountMax 0",
        }
        expected_services = {
            "ubuntu_lts_hardening.yml": "ssh",
            "debian_hardening.yml": "ssh",
            "opensuse_hardening.yml": "sshd",
        }
        for filename, service_name in expected_services.items():
            with self.subTest(playbook=filename):
                hardening = self._task(
                    filename, "Apply SSH Daemon Hardening", nested=True
                )
                self.assertEqual(
                    {item["line"] for item in hardening.get("loop", [])},
                    expected_lines,
                )
                self.assertEqual(hardening.get("register"), "sshd_config_res")

                validation = self._task(
                    filename, "Validate SSH Configuration", nested=True
                )
                self.assertEqual(validation.get("ansible.builtin.command"), "sshd -t")
                self.assertIs(validation.get("changed_when"), False)
                self.assertIs(validation.get("failed_when"), False)
                self.assertEqual(
                    validation.get("when"),
                    "sshd_config_res.changed | default(false)",
                )
                self.assertEqual(validation.get("register"), "sshd_validate_res")

                reload_task = self._task(filename, "Reload SSH Service", nested=True)
                self.assertEqual(
                    reload_task.get("ansible.builtin.service"),
                    {"name": service_name, "state": "reloaded"},
                )
                self.assertEqual(
                    reload_task.get("when"),
                    [
                        "not is_sandbox_jules",
                        "sshd_config_res.changed | default(false)",
                        "sshd_validate_res.rc | default(1) == 0",
                    ],
                )
                self.assertEqual(reload_task.get("register"), "sshd_reload_res")

    def test_pam_password_policy_is_consistently_hardened(self):
        """Require the same strong PAM password-quality controls on each distro."""
        expected_lines = {"minlen = 14", "minclass = 4"}
        for filename in PLAYBOOKS:
            with self.subTest(playbook=filename):
                task = self._task(
                    filename, "Apply PAM Password Quality Hardening", nested=True
                )
                module = task.get("ansible.builtin.lineinfile", {})
                self.assertEqual(module.get("path"), "/etc/security/pwquality.conf")
                self.assertEqual(module.get("state"), "present")
                self.assertEqual(module.get("line"), "{{ item.line }}")
                self.assertEqual(
                    {item["line"] for item in task.get("loop", [])}, expected_lines
                )
                self.assertNotIn("minlen = 8", expected_lines)
                self.assertEqual(task.get("register"), "pam_pwquality_res")

    def test_kernel_hardening_uses_platform_specific_safe_path(self):
        """Guard Debian-family sysctls in sandboxes and use the SUSE role."""
        expected_sysctls = {
            "net.ipv4.ip_forward": "0",
            "net.ipv4.conf.all.accept_redirects": "0",
            "net.ipv4.conf.all.send_redirects": "0",
            "net.ipv4.conf.all.rp_filter": "1",
            "net.ipv4.tcp_syncookies": "1",
        }
        for filename in ("ubuntu_lts_hardening.yml", "debian_hardening.yml"):
            with self.subTest(playbook=filename):
                task = self._task(
                    filename, "Apply Kernel Sysctl Hardening", nested=True
                )
                self.assertEqual(task.get("when"), "not is_sandbox_jules")
                self.assertEqual(task.get("register"), "sysctl_res")
                self.assertEqual(
                    {item["key"]: item["value"] for item in task.get("loop", [])},
                    expected_sysctls,
                )
                self.assertEqual(
                    task.get("ansible.posix.sysctl"),
                    {
                        "name": "{{ item.key }}",
                        "value": "{{ item.value }}",
                        "state": "present",
                        "reload": True,
                    },
                )

        opensuse_task = self._task(
            "opensuse_hardening.yml",
            "Apply openSUSE Network Sysctl Hardening",
            nested=True,
        )
        self.assertEqual(
            opensuse_task.get("ansible.builtin.include_role", {}).get("name"),
            "sysctl-suse-ASIMP",
        )
        self.assertIs(
            opensuse_task.get("vars", {}).get("suse_sysctl_auto_calc_resources"),
            True,
        )

    def test_failure_summary_aggregates_every_local_remediation_result(self):
        """Ensure partial failures cannot be reported as fully verified."""
        expected_registers = {
            "ubuntu_lts_hardening.yml": {
                "file_perm_res",
                "sshd_config_res",
                "pam_pwquality_res",
                "sysctl_res",
            },
            "debian_hardening.yml": {
                "file_perm_res",
                "sshd_config_res",
                "pam_pwquality_res",
                "sysctl_res",
            },
            "opensuse_hardening.yml": {
                "file_perm_res",
                "sshd_config_res",
                "pam_pwquality_res",
            },
        }
        for filename, registers in expected_registers.items():
            with self.subTest(playbook=filename):
                task = self._task(filename, "Evaluate Remediation", nested=True)
                expression = task.get("ansible.builtin.set_fact", {}).get(
                    "phase2_remediation_success", ""
                )
                for register in registers:
                    self.assertIn(
                        f"{register}.failed | default(false)", expression
                    )
                self.assertEqual(
                    expression.count(".failed | default(false)"), len(registers)
                )
                self.assertIn("{{ not (", expression)

                summary = self._task(filename, "Display Comparative", nested=True)
                messages = summary.get("ansible.builtin.debug", {}).get("msg", [])
                state_message = next(
                    msg for msg in messages if "System Configuration State" in msg
                )
                self.assertIn("phase2_remediation_success", state_message)
                self.assertIn("ENFORCED & VERIFIED", state_message)
                self.assertIn("PARTIAL / ERRORS DETECTED", state_message)

    def test_all_tasks_use_fully_qualified_module_names(self):
        """Require FQCN module keys for top-level and nested tasks."""
        for filename in PLAYBOOKS:
            top_level_tasks = self._tasks(filename)
            tasks = top_level_tasks + [
                task
                for parent in top_level_tasks
                for task in parent.get("block", [])
            ]
            for task in tasks:
                with self.subTest(playbook=filename, task=task.get("name")):
                    module_keys = [key for key in task if key not in TASK_KEYWORDS]
                    if "block" in task:
                        self.assertEqual(module_keys, [])
                        continue
                    self.assertEqual(
                        len(module_keys), 1, f"Task must have exactly one module: {task}"
                    )
                    self.assertIn(".", module_keys[0], f"Module must use FQCN: {task}")


if __name__ == "__main__":
    unittest.main()
