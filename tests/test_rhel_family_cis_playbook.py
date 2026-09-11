#!/usr/bin/env python3
"""Unit tests for the Enterprise Linux CIS Level 2 playbook added in PR 81.

The suite parses the shipped playbook and exercises its Jinja expressions and
embedded score parser directly.  It intentionally does not execute the
remediation play, which would alter the test host.

Run with:
    python3 -m unittest tests/test_rhel_family_cis_playbook.py -v
"""

import contextlib
import io
import os
import tempfile
import unittest

import yaml
from jinja2 import Environment

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYBOOK_PATH = os.path.join(REPO_ROOT, "playbooks", "rhel_family_cis.yml")


def _ansible_bool(value):
    """Implement the common values needed by Ansible's ``bool`` filter."""
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


class RhelFamilyCisPlaybookTestCase(unittest.TestCase):
    """Verify branching, safety gates, and hardening task configuration."""

    @classmethod
    def setUpClass(cls):
        with open(PLAYBOOK_PATH, "r", encoding="utf-8") as playbook_file:
            cls.plays = yaml.safe_load(playbook_file)

        cls.play = cls.plays[0]
        cls.tasks = cls.play["tasks"]
        cls.jinja = Environment(autoescape=False)
        cls.jinja.filters["bool"] = _ansible_bool

    def _task(self, name, tasks=None):
        matches = [task for task in tasks or self.tasks if task.get("name") == name]
        self.assertEqual(len(matches), 1, f"Expected exactly one task named {name!r}")
        return matches[0]

    def _evaluate_when(self, conditions, **variables):
        if isinstance(conditions, str):
            conditions = [conditions]
        return all(
            self.jinja.compile_expression(condition)(**variables)
            for condition in conditions
        )

    def test_play_has_safe_reporting_defaults(self):
        self.assertEqual(len(self.plays), 1)
        self.assertEqual(self.play["hosts"], "all")
        self.assertIs(self.play["become"], True)
        self.assertEqual(self.play["vars"]["execution_mode"], "report")
        self.assertEqual(
            self.play["vars"]["openscap_report_dir"], "/opt/report/openscap"
        )
        self.assertEqual(
            self.play["vars"]["openscap_profile"],
            "xccdf_org.ssgproject.content_profile_cis",
        )

    def test_execution_mode_validation_accepts_only_supported_modes(self):
        task = self._task("Enterprise Linux - Validate execution_mode parameter")
        condition = task["ansible.builtin.assert"]["that"][0]

        for valid_mode in ("report", "remediate"):
            with self.subTest(mode=valid_mode):
                self.assertTrue(
                    self.jinja.compile_expression(condition)(execution_mode=valid_mode)
                )

        for invalid_mode in ("", "audit", "REPORT", None):
            with self.subTest(mode=invalid_mode):
                self.assertFalse(
                    self.jinja.compile_expression(condition)(
                        execution_mode=invalid_mode
                    )
                )

    def test_preferred_datastream_maps_every_supported_distribution_version(self):
        task = self._task("Enterprise Linux - Compute Preferred DataStream Path")
        template = self.jinja.from_string(
            task["ansible.builtin.set_fact"]["preferred_datastream_path"]
        )
        distribution_prefixes = {
            "RedHat": "rhel",
            "AlmaLinux": "almalinux",
            "Rocky": "rocky",
            "OracleLinux": "ol",
        }

        for distribution, prefix in distribution_prefixes.items():
            for major_version in ("8", "9", "10"):
                with self.subTest(
                    distribution=distribution, major_version=major_version
                ):
                    rendered = template.render(
                        ansible_distribution=distribution,
                        ansible_distribution_major_version=major_version,
                    )
                    self.assertEqual(
                        rendered,
                        "/usr/share/xml/scap/ssg/content/"
                        f"ssg-{prefix}{major_version}-ds.xml",
                    )

    def test_oracle_ol_alias_and_unknown_distribution_fallback(self):
        task = self._task("Enterprise Linux - Compute Preferred DataStream Path")
        template = self.jinja.from_string(
            task["ansible.builtin.set_fact"]["preferred_datastream_path"]
        )

        self.assertEqual(
            template.render(
                ansible_distribution="OL",
                ansible_distribution_major_version="9",
            ),
            "/usr/share/xml/scap/ssg/content/ssg-ol9-ds.xml",
        )
        self.assertEqual(
            template.render(
                ansible_distribution="CentOS",
                ansible_distribution_major_version="9",
            ),
            "/usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml",
        )

    def test_active_datastream_prefers_native_then_rhel_then_empty(self):
        task = self._task("Enterprise Linux - Select Active SCAP DataStream")
        expression = task["ansible.builtin.set_fact"]["openscap_datastream"]
        template = self.jinja.from_string(expression)
        scenarios = (
            (True, True, "/native.xml"),
            (False, True, "/rhel.xml"),
            (False, False, ""),
        )

        for preferred_exists, fallback_exists, expected in scenarios:
            with self.subTest(
                preferred_exists=preferred_exists,
                fallback_exists=fallback_exists,
            ):
                rendered = template.render(
                    preferred_datastream_path="/native.xml",
                    rhel_fallback_datastream_path="/rhel.xml",
                    preferred_ds_stat={"stat": {"exists": preferred_exists}},
                    rhel_fallback_ds_stat={"stat": {"exists": fallback_exists}},
                )
                self.assertEqual(rendered, expected)

    def test_missing_datastream_is_tolerated_only_in_sandbox(self):
        task = self._task("Enterprise Linux - Assert Valid SCAP DataStream Path Exists")
        condition = task["ansible.builtin.assert"]["that"][0]
        evaluate = self.jinja.compile_expression(condition)

        self.assertTrue(
            evaluate(openscap_datastream="/native.xml", is_sandbox_jules=False)
        )
        self.assertTrue(evaluate(openscap_datastream="", is_sandbox_jules=True))
        self.assertFalse(evaluate(openscap_datastream="", is_sandbox_jules=False))

    def test_package_installation_gate_covers_mode_opt_in_os_and_sandbox(self):
        task = self._task(
            "Enterprise Linux - Install OpenSCAP and SSG packages via DNF"
        )
        conditions = task["when"]
        scenarios = (
            ({"execution_mode": "report"}, False),
            ({"execution_mode": "report", "install_packages": True}, True),
            ({"execution_mode": "report", "install_packages": "yes"}, True),
            ({"execution_mode": "remediate"}, True),
            ({"execution_mode": "remediate", "ansible_os_family": "Debian"}, False),
            ({"execution_mode": "remediate", "is_sandbox_jules": True}, False),
        )

        defaults = {
            "ansible_os_family": "RedHat",
            "is_sandbox_jules": False,
        }
        for overrides, expected in scenarios:
            variables = {**defaults, **overrides}
            with self.subTest(variables=variables):
                self.assertIs(self._evaluate_when(conditions, **variables), expected)

    def test_reporting_block_is_read_only_and_fix_generation_is_guarded(self):
        block = self._task("Enterprise Linux - Mode 1 - Reporting Only")
        self.assertEqual(block["when"], 'execution_mode == "report"')
        nested = block["block"]

        scan = self._task("Mode 1 - Execute OpenSCAP Evaluation Scan", nested)
        self.assertIs(scan["changed_when"], False)
        self.assertIs(scan["failed_when"], False)

        for name in (
            "Mode 1 - Generate Standalone Bash Remediation Script",
            "Mode 1 - Generate Standalone Ansible Remediation Playbook",
        ):
            with self.subTest(task=name):
                task = self._task(name, nested)
                self.assertEqual(task["when"], "openscap_datastream | length > 0")
                self.assertIs(task["failed_when"], False)

        mutating_modules = {
            "ansible.builtin.dnf",
            "ansible.builtin.file",
            "ansible.builtin.lineinfile",
            "ansible.builtin.service",
            "ansible.posix.mount",
            "ansible.posix.sysctl",
        }
        self.assertFalse(any(mutating_modules.intersection(task) for task in nested))

    def test_remediation_block_follows_measure_harden_remeasure_order(self):
        block = self._task(
            "Enterprise Linux - Mode 2 - Doing (Remediation and Hardening)"
        )
        self.assertEqual(block["when"], 'execution_mode == "remediate"')
        names = [task["name"] for task in block["block"]]

        baseline_index = names.index("Mode 2 - Phase 1 - Baseline Assessment Scan")
        hardening_index = names.index(
            "Mode 2 - Phase 2 - Apply CIS Level 2 System File Permissions"
        )
        verification_index = names.index(
            "Mode 2 - Phase 3 - Post-Hardening Verification Scan"
        )
        self.assertLess(baseline_index, hardening_index)
        self.assertLess(hardening_index, verification_index)

    def test_remediation_controls_match_documented_cis_settings(self):
        nested = self._task(
            "Enterprise Linux - Mode 2 - Doing (Remediation and Hardening)"
        )["block"]

        file_task = self._task(
            "Mode 2 - Phase 2 - Apply CIS Level 2 System File Permissions",
            nested,
        )
        self.assertEqual(
            file_task["loop"],
            [
                {"path": "/etc/passwd", "mode": "0644"},
                {"path": "/etc/shadow", "mode": "0000"},
                {"path": "/etc/group", "mode": "0644"},
                {"path": "/etc/gshadow", "mode": "0000"},
            ],
        )

        mount_task = self._task(
            "Mode 2 - Phase 2 - Enforce CIS Level 2 Storage Partition Mount Options",
            nested,
        )
        self.assertEqual(mount_task["loop"], ["/tmp", "/var/tmp", "/dev/shm"])
        self.assertEqual(
            mount_task["ansible.posix.mount"]["opts"],
            "defaults,nodev,nosuid,noexec",
        )

        ssh_task = self._task(
            "Mode 2 - Phase 2 - Apply CIS Level 2 SSH Daemon Hardening", nested
        )
        self.assertEqual(
            {item["line"] for item in ssh_task["loop"]},
            {
                "PermitRootLogin no",
                "PasswordAuthentication no",
                "MaxAuthTries 4",
                "ClientAliveInterval 300",
                "ClientAliveCountMax 0",
            },
        )

        password_task = self._task(
            "Mode 2 - Phase 2 - Apply CIS Level 2 PAM Password Complexity Policy",
            nested,
        )
        self.assertEqual(
            {item["line"] for item in password_task["loop"]},
            {"minlen = 14", "minclass = 4"},
        )

        sysctl_task = self._task(
            "Mode 2 - Phase 2 - Apply CIS Level 2 Kernel Sysctl Hardening", nested
        )
        self.assertEqual(
            {item["key"]: item["value"] for item in sysctl_task["loop"]},
            {
                "net.ipv4.ip_forward": "0",
                "net.ipv4.conf.all.accept_redirects": "0",
                "net.ipv4.conf.all.send_redirects": "0",
                "net.ipv4.conf.all.rp_filter": "1",
                "net.ipv4.tcp_syncookies": "1",
            },
        )

    def test_host_level_controls_are_skipped_in_sandbox(self):
        nested = self._task(
            "Enterprise Linux - Mode 2 - Doing (Remediation and Hardening)"
        )["block"]
        guarded_tasks = (
            "Mode 2 - Phase 2 - Enforce CIS Level 2 Storage Partition Mount Options",
            "Mode 2 - Phase 2 - Apply CIS Level 2 Crypto Policy",
            "Mode 2 - Phase 2 - Apply CIS Level 2 Kernel Sysctl Hardening",
            "Mode 2 - Phase 2 - Ensure Auditd Service is Enabled and Active",
        )

        for name in guarded_tasks:
            with self.subTest(task=name):
                task = self._task(name, nested)
                self.assertFalse(
                    self._evaluate_when(task["when"], is_sandbox_jules=True)
                )
                self.assertTrue(
                    self._evaluate_when(task["when"], is_sandbox_jules=False)
                )

    def test_all_command_tasks_declare_change_semantics(self):
        def walk(tasks):
            for task in tasks:
                yield task
                if "block" in task:
                    yield from walk(task["block"])

        command_modules = {"ansible.builtin.command", "ansible.builtin.shell"}
        for task in walk(self.tasks):
            if command_modules.intersection(task):
                with self.subTest(task=task["name"]):
                    self.assertIn("changed_when", task)


class EmbeddedScoreParserTestCase(unittest.TestCase):
    """Exercise the exact Python score parser embedded in the playbook."""

    @classmethod
    def setUpClass(cls):
        with open(PLAYBOOK_PATH, "r", encoding="utf-8") as playbook_file:
            play = yaml.safe_load(playbook_file)[0]
        parser_task = next(
            task
            for task in play["tasks"]
            if task.get("name")
            == "Enterprise Linux - Deploy Score Parser Helper Script"
        )
        cls.script_source = parser_task["ansible.builtin.copy"]["content"]
        namespace = {"__name__": "embedded_score_parser_under_test"}
        exec(compile(cls.script_source, "parse_score.py", "exec"), namespace)
        cls.parse_score = staticmethod(namespace["parse_score"])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, content, filename="results.xml"):
        path = os.path.join(self.temp_dir.name, filename)
        with open(path, "w", encoding="utf-8") as xml_file:
            xml_file.write(content)
        return path

    def _output_for(self, path):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.parse_score(path)
        return output.getvalue().strip()

    def test_formats_xccdf_12_score_to_two_decimal_places(self):
        path = self._write(
            '<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2">'
            "<TestResult><score>83.456</score></TestResult>"
            "</Benchmark>"
        )
        self.assertEqual(self._output_for(path), "83.46")

    def test_zero_score_is_available(self):
        path = self._write(
            '<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2">'
            "<TestResult><score>0</score></TestResult>"
            "</Benchmark>"
        )
        self.assertEqual(self._output_for(path), "0.00")

    def test_unavailable_cases_do_not_raise(self):
        cases = {
            "missing file": os.path.join(self.temp_dir.name, "missing.xml"),
            "malformed XML": self._write("<not-closed>", "malformed.xml"),
            "missing score": self._write(
                '<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2"/>',
                "missing-score.xml",
            ),
            "blank score": self._write(
                '<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2">'
                "<score></score></Benchmark>",
                "blank-score.xml",
            ),
            "non-numeric score": self._write(
                '<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2">'
                "<score>not-a-number</score></Benchmark>",
                "invalid-score.xml",
            ),
            "wrong namespace": self._write(
                "<Benchmark><score>91.2</score></Benchmark>",
                "wrong-namespace.xml",
            ),
        }

        for case, path in cases.items():
            with self.subTest(case=case):
                self.assertEqual(self._output_for(path), "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
