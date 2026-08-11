#!/usr/bin/env python3
"""
Tests for the new documentation/report pages added by this PR:
  - docs/output_asimp.md
  - docs/output_lynis.md
  - docs/output_openscap.md
  - docs/security_posture_assessment.md

These are brand-new static Jekyll markdown pages (each carrying its own OKF
front matter block) that are surfaced via the new "Reports & SPA" navigation
block in docs/_layouts/default.html and referenced by both sitemap.txt and
sitemap.xml. These tests verify that each page:
  * exists on disk,
  * has a syntactically valid, OKF-compliant front matter block,
  * declares the expected title/type/topics,
  * retains the expected key content sections and footer attribution.

Run with:
    python3 -m unittest tests/test_new_report_docs.py -v
"""
import os
import re
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

OUTPUT_ASIMP = os.path.join(DOCS_DIR, "output_asimp.md")
OUTPUT_LYNIS = os.path.join(DOCS_DIR, "output_lynis.md")
OUTPUT_OPENSCAP = os.path.join(DOCS_DIR, "output_openscap.md")
SECURITY_POSTURE_ASSESSMENT = os.path.join(DOCS_DIR, "security_posture_assessment.md")

ALL_NEW_DOCS = [OUTPUT_ASIMP, OUTPUT_LYNIS, OUTPUT_OPENSCAP, SECURITY_POSTURE_ASSESSMENT]


def _load(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    parts = raw.split("---", 2)
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2]
    return raw, frontmatter, body


class TestNewReportDocsCommonStructure(unittest.TestCase):
    """Shared front-matter/structure checks applied to all four new pages."""

    def test_all_new_doc_files_exist(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                self.assertTrue(os.path.isfile(path), f"Expected new doc file to exist: {path}")

    def test_all_new_docs_start_with_frontmatter_delimiter(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read()
                self.assertTrue(raw.startswith("---\n"))

    def test_all_new_docs_have_valid_yaml_frontmatter(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, frontmatter, _ = _load(path)
                self.assertIsInstance(frontmatter, dict)

    def test_all_new_docs_declare_okf_version_as_quoted_string(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, frontmatter, _ = _load(path)
                self.assertIn("okf_version", frontmatter)
                self.assertIsInstance(frontmatter["okf_version"], str)
                self.assertEqual(frontmatter["okf_version"], "0.1")

    def test_all_new_docs_declare_required_okf_fields(self) -> None:
        required_fields = {"okf_version", "type", "title", "timestamp", "topics"}
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, frontmatter, _ = _load(path)
                self.assertTrue(
                    required_fields.issubset(frontmatter.keys()),
                    f"Missing required OKF fields in {path}: "
                    f"{required_fields - frontmatter.keys()}",
                )

    def test_all_new_docs_have_iso8601_timestamp(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, frontmatter, _ = _load(path)
                self.assertRegex(
                    frontmatter["timestamp"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
                )

    def test_all_new_docs_have_dsom_footer_attribution(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, _, body = _load(path)
                self.assertIn(
                    "*Deep State of Mind (DSOM) For My AI Protocol | "
                    "Harisfazillah Jamel (LinuxMalaysia) | 2026-08-11*",
                    body,
                )

    def test_all_new_docs_topics_are_nonempty_lists(self) -> None:
        for path in ALL_NEW_DOCS:
            with self.subTest(path=path):
                _, frontmatter, _ = _load(path)
                self.assertIsInstance(frontmatter["topics"], list)
                self.assertGreater(len(frontmatter["topics"]), 0)


class TestOutputAsimpDoc(unittest.TestCase):
    """Content checks specific to docs/output_asimp.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw, cls.frontmatter, cls.body = _load(OUTPUT_ASIMP)

    def test_frontmatter_title_and_type(self) -> None:
        self.assertEqual(self.frontmatter["title"], "Output of ASIMP Example Report")
        self.assertEqual(self.frontmatter["type"], "report")

    def test_frontmatter_topics_include_asimp(self) -> None:
        self.assertIn("asimp", self.frontmatter["topics"])

    def test_h1_heading_matches_title(self) -> None:
        self.assertIn("# Output of ASIMP Example Report", self.body)

    def test_scorecard_table_contains_lynis_and_openscap_rows(self) -> None:
        self.assertIn("Lynis HI", self.body)
        self.assertIn("OpenSCAP %", self.body)
        self.assertIn("62", self.body)
        self.assertIn("88", self.body)
        self.assertIn("58.4%", self.body)
        self.assertIn("91.2%", self.body)

    def test_mitigations_section_lists_six_items(self) -> None:
        mitigation_items = re.findall(r"^\d+\.\s+\*\*", self.body, flags=re.MULTILINE)
        self.assertEqual(len(mitigation_items), 6)

    def test_artifact_locations_section_present(self) -> None:
        self.assertIn("/var/log/asimp-baseline-scores.json", self.body)
        self.assertIn("/var/log/openscap-before-report.html", self.body)
        self.assertIn("/var/log/openscap-after-report.html", self.body)


class TestOutputLynisDoc(unittest.TestCase):
    """Content checks specific to docs/output_lynis.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw, cls.frontmatter, cls.body = _load(OUTPUT_LYNIS)

    def test_frontmatter_title_and_type(self) -> None:
        self.assertEqual(self.frontmatter["title"], "Output of Lynis Auditing Report")
        self.assertEqual(self.frontmatter["type"], "report")

    def test_frontmatter_topics_include_lynis(self) -> None:
        self.assertIn("lynis", self.frontmatter["topics"])

    def test_hardening_index_scores_present(self) -> None:
        self.assertIn("**Before Hardening Score**: **62 / 100**", self.body)
        self.assertIn("**After Hardening Score**: **88 / 100**", self.body)
        self.assertIn("**Target Threshold**: **85+**", self.body)

    def test_console_output_example_present(self) -> None:
        self.assertIn("[+] Boot and services", self.body)
        self.assertIn("[+] SSH Support", self.body)

    def test_all_three_asimp_mitigations_listed(self) -> None:
        self.assertEqual(self.body.count("**ASIMP Mitigation**:"), 3)
        self.assertIn("### 1. SSH Server Security", self.body)
        self.assertIn("### 2. File Integrity Checking", self.body)
        self.assertIn("### 3. Compiler Restriction", self.body)

    def test_report_files_section_present(self) -> None:
        self.assertIn("/var/log/lynis.log", self.body)
        self.assertIn("/var/log/lynis-report.dat", self.body)


class TestOutputOpenscapDoc(unittest.TestCase):
    """Content checks specific to docs/output_openscap.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw, cls.frontmatter, cls.body = _load(OUTPUT_OPENSCAP)

    def test_frontmatter_title_and_type(self) -> None:
        self.assertEqual(self.frontmatter["title"], "Output of OpenSCAP Evaluation Report")
        self.assertEqual(self.frontmatter["type"], "report")

    def test_frontmatter_topics_include_openscap_and_cis(self) -> None:
        self.assertIn("openscap", self.frontmatter["topics"])
        self.assertIn("cis", self.frontmatter["topics"])

    def test_compliance_score_progression_present(self) -> None:
        self.assertIn("**Before Hardening Score**: **58.4%**", self.body)
        self.assertIn("**After Hardening Score**: **91.2%**", self.body)
        self.assertIn("**Target Compliance Threshold**: **90.0%+**", self.body)

    def test_rule_compliance_table_has_expected_header(self) -> None:
        self.assertIn(
            "| Policy Rule ID | Description | Before Hardening | After Hardening "
            "| Remediation Status |",
            self.body,
        )

    def test_rule_compliance_table_has_six_data_rows(self) -> None:
        # 1 header row + 1 separator row + 6 data rows = 8 table lines total.
        table_lines = [line for line in self.body.splitlines() if line.strip().startswith("|")]
        self.assertEqual(len(table_lines), 8)

    def test_report_artifacts_section_present(self) -> None:
        self.assertIn("/var/log/openscap-before-report.html", self.body)
        self.assertIn("/var/log/openscap-after-report.html", self.body)
        self.assertIn("/var/log/openscap-before-results.xml", self.body)
        self.assertIn("/var/log/openscap-after-results.xml", self.body)


class TestSecurityPostureAssessmentDoc(unittest.TestCase):
    """Content checks specific to docs/security_posture_assessment.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw, cls.frontmatter, cls.body = _load(SECURITY_POSTURE_ASSESSMENT)

    def test_frontmatter_title_and_type(self) -> None:
        self.assertEqual(
            self.frontmatter["title"],
            "Security Posture Assessment (SPA) Requirement Checklist",
        )
        self.assertEqual(self.frontmatter["type"], "documentation")

    def test_frontmatter_topics_include_checklist(self) -> None:
        self.assertIn("checklist", self.frontmatter["topics"])
        self.assertIn("assessment", self.frontmatter["topics"])

    def test_executive_summary_and_scope_sections_present(self) -> None:
        self.assertIn("## 1. Executive Security Blueprint Summary", self.body)
        self.assertIn("## 2. SPA Requirement Checklist", self.body)
        self.assertIn("## 3. Tiered Security Control Specifications", self.body)

    def test_all_six_tiers_present(self) -> None:
        for tier_num in range(1, 7):
            with self.subTest(tier=tier_num):
                self.assertIn(f"### Tier {tier_num}:", self.body)

    def test_sla_timeline_values_present(self) -> None:
        self.assertIn("within **24 Hours**", self.body)
        self.assertIn("within **7 Days**", self.body)
        self.assertIn("within **30 Days**", self.body)
        self.assertIn("within **90 Days**", self.body)

    def test_sign_off_block_references_test_files(self) -> None:
        self.assertIn("tests/test_prepare_docs.py", self.body)
        self.assertIn("tests/test_sitemaps.py", self.body)

    def test_audit_id_prefixes_present(self) -> None:
        for prefix in ("NET-", "SG-", "HST-", "APP-", "DAT-", "MON-"):
            with self.subTest(prefix=prefix):
                self.assertIn(prefix, self.body)


if __name__ == "__main__":
    unittest.main()