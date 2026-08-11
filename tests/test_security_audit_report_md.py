#!/usr/bin/env python3
"""
Regression tests for data/asimp_mock/opt/report/openscap/SECURITY_AUDIT_REPORT.md.

This PR changed the mock Security Audit Report fixture in several ways:
  1. Quoted the 'okf_version' front matter value ("0.1" instead of the bare
     float 0.1), and removed the 'description' field entirely.
  2. Bumped the 'timestamp' front matter field and the corresponding
     '**Report Timestamp**' body line from 2026-08-05 23:54:50 to
     2026-08-10 23:50:01.
  3. Replaced the 'Mock Environment' / 'Kernel Simulation' overview lines
     with a single 'Execution Environment' line reflecting a
     limited/sandboxed privilege model.
  4. Annotated both Lynis and OpenSCAP baseline/after scores with
     "(Simulated Fallback)".
  5. Collapsed the previous itemized 'Executed Mock Controls & Remediation'
     section (THP, SSH hardening, compiler constraints, sysctl tuning,
     OpenSCAP compliant status, OVAL non-vulnerable) into a renamed
     'Executed Controls & Remediation' section stating that no
     remediations were applied and that the OVAL scan was not executed.
  6. Bumped the footer attribution date to 2026-08-10.

Run with:
    python3 -m unittest tests/test_security_audit_report_md.py -v
"""
import os
import re
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_MD_PATH = os.path.join(
    REPO_ROOT, "data", "asimp_mock", "opt", "report", "openscap", "SECURITY_AUDIT_REPORT.md"
)


class TestSecurityAuditReportMd(unittest.TestCase):
    """Verify the mock SECURITY_AUDIT_REPORT.md fixture front matter and body content."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(REPORT_MD_PATH, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()

        # Front matter is delimited by the first two '---' lines.
        parts = cls.raw_content.split("---", 2)
        cls.frontmatter = yaml.safe_load(parts[1])
        cls.body = parts[2]

    def test_file_exists(self) -> None:
        self.assertTrue(os.path.isfile(REPORT_MD_PATH))

    def test_frontmatter_okf_version_is_quoted_string(self) -> None:
        self.assertIsInstance(self.frontmatter["okf_version"], str)
        self.assertEqual(self.frontmatter["okf_version"], "0.1")

    def test_frontmatter_okf_version_literal_is_quoted_in_source(self) -> None:
        # Guard against regressing to the bare/unquoted float form, which
        # would silently change the parsed type from str to float.
        self.assertIn('okf_version: "0.1"', self.raw_content)
        self.assertNotIn("okf_version: 0.1\n", self.raw_content)

    def test_frontmatter_description_field_removed(self) -> None:
        self.assertNotIn("description", self.frontmatter)
        self.assertNotIn("description:", self.raw_content)

    def test_frontmatter_timestamp_bumped(self) -> None:
        self.assertEqual(self.frontmatter["timestamp"], "2026-08-10T23:50:01Z")

    def test_frontmatter_timestamp_is_iso8601_utc(self) -> None:
        self.assertRegex(
            self.frontmatter["timestamp"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        )

    def test_frontmatter_type_and_title_unchanged(self) -> None:
        self.assertEqual(self.frontmatter["type"], "report")
        self.assertEqual(
            self.frontmatter["title"],
            "Google Jules Sovereign OS Security Hardening & Compliance Report",
        )

    def test_frontmatter_topics_unchanged(self) -> None:
        self.assertEqual(
            self.frontmatter["topics"],
            ["security", "compliance", "audit", "report", "sandbox"],
        )

    def test_body_execution_environment_line_replaces_mock_environment(self) -> None:
        self.assertIn(
            "**Execution Environment**: Google Jules Sandbox (Privilege: limited)",
            self.body,
        )
        self.assertNotIn("Mock Environment", self.raw_content)
        self.assertNotIn("Kernel Simulation", self.raw_content)

    def test_body_report_timestamp_line_matches_frontmatter(self) -> None:
        expected_line = "**Report Timestamp**: 2026-08-10 23:50:01"
        self.assertIn(expected_line, self.body)

    def test_body_hardening_scores_annotated_as_simulated_fallback(self) -> None:
        self.assertEqual(
            self.body.count("(Simulated Fallback)"),
            4,
            "Expected all 4 Lynis/OpenSCAP baseline & after-hardening scores to be "
            "annotated with '(Simulated Fallback)'",
        )
        self.assertIn("Baseline: 62 / 100 (Simulated Fallback)", self.body)
        self.assertIn("After Hardening: 88 / 100 (Simulated Fallback)", self.body)
        self.assertIn("Baseline: 58.4% (Simulated Fallback)", self.body)
        self.assertIn("After Hardening: 91.2% (Simulated Fallback)", self.body)

    def test_section_renamed_from_executed_mock_controls(self) -> None:
        self.assertIn("## Executed Controls & Remediation", self.body)
        self.assertNotIn("## Executed Mock Controls & Remediation", self.raw_content)

    def test_body_no_longer_lists_removed_mock_controls(self) -> None:
        removed_snippets = [
            "Transparent Huge Pages (THP)",
            "SSH Server Hardening",
            "Compiler Constraints",
            "Network Sysctl Tuning",
            "OpenSCAP Evaluation Status**: Compliant",
        ]
        for snippet in removed_snippets:
            with self.subTest(snippet=snippet):
                self.assertNotIn(snippet, self.raw_content)

    def test_body_states_no_remediations_applied(self) -> None:
        self.assertIn(
            "**Remediation Status**: No remediations applied "
            "(Skipped in limited/sandboxed privilege environment)",
            self.body,
        )

    def test_body_states_oval_scan_not_executed(self) -> None:
        self.assertIn(
            "**OVAL Vulnerability Scan**: Not executed "
            "(Unsupported or failed in limited/sandboxed environment)",
            self.body,
        )
        self.assertNotIn("Non-vulnerable (Fully patched packages simulation)", self.raw_content)

    def test_footer_attribution_date_bumped(self) -> None:
        self.assertIn(
            "*Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-08-10*",
            self.raw_content,
        )
        self.assertNotIn("2026-08-05", self.raw_content)

    def test_document_starts_with_frontmatter_delimiter(self) -> None:
        self.assertTrue(self.raw_content.startswith("---\n"))

    def test_body_still_contains_target_hardening_index_and_target_compliance(self) -> None:
        self.assertIn("Target: 85+ (Sovereign Level)", self.body)
        self.assertIn("Target: 90%+", self.body)


if __name__ == "__main__":
    unittest.main()