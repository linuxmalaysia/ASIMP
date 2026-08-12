#!/usr/bin/env python3
"""
Regression tests for tests/test_asimp_mock_data.yml itself.

This PR changed the first 'that' condition of the "Assert the frontmatter
declares the expected OKF metadata" assertion from:

    report_frontmatter.okf_version == 0.1

to:

    report_frontmatter.okf_version == "0.1"

The report frontmatter (data/asimp_mock/opt/report/openscap/
SECURITY_AUDIT_REPORT.md) declares `okf_version: "0.1"` as a quoted YAML
string. Once parsed with `from_yaml`, `report_frontmatter.okf_version` is
therefore the Python string "0.1", not the float 0.1.

These tests parse tests/test_asimp_mock_data.yml with a real YAML loader
(the same family ansible-playbook itself uses) and verify:
  1. The file loads as valid YAML (a basic sanity check for the whole file).
  2. The specific assertion's 'that' list contains the string comparison
     condition string, not the previous, always-false float comparison.
  3. The compiled Jinja2 expression evaluates True for the real, quoted
     string frontmatter value "0.1" actually used in the mock fixture.
  4. The compiled expression still correctly evaluates False for a
     mismatched okf_version value (negative/boundary case).
  5. Reverting to the previous unconverted form would regress: it would
     evaluate False even for the correct "0.1" string value, demonstrating
     exactly the bug this PR's fix guards against.

Run with:
    python3 -m unittest tests/test_test_asimp_mock_data_yaml_validity.py -v
"""
import os
import unittest

import yaml
from jinja2 import Environment

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_ASIMP_MOCK_DATA_YML = os.path.join(REPO_ROOT, "tests", "test_asimp_mock_data.yml")

TARGET_TASK_NAME = "Assert the frontmatter declares the expected OKF metadata"
EXPECTED_OKF_VERSION_CONDITION = 'report_frontmatter.okf_version == "0.1"'
PREVIOUS_UNCONVERTED_CONDITION = 'report_frontmatter.okf_version == 0.1'


class TestTestAsimpMockDataValidity(unittest.TestCase):
    """Verify tests/test_asimp_mock_data.yml is syntactically valid and semantically correct."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(TEST_ASIMP_MOCK_DATA_YML, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()

    def test_file_is_valid_yaml(self) -> None:
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(f"tests/test_asimp_mock_data.yml must be valid YAML, but failed to parse: {exc}")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_playbook_has_expected_play_and_task(self) -> None:
        data = yaml.safe_load(self.raw_content)
        play = data[0]
        self.assertIn("tasks", play)
        task_names = [t.get("name") for t in play["tasks"]]
        self.assertIn(TARGET_TASK_NAME, task_names)

    def _get_target_task(self):
        data = yaml.safe_load(self.raw_content)
        tasks = data[0]["tasks"]
        matching = [t for t in tasks if t.get("name") == TARGET_TASK_NAME]
        self.assertEqual(
            len(matching), 1, f"Expected exactly one task named {TARGET_TASK_NAME!r}"
        )
        return matching[0]

    def test_that_list_contains_the_float_coerced_condition(self) -> None:
        task = self._get_target_task()
        that_list = task["ansible.builtin.assert"]["that"]
        self.assertIsInstance(that_list, list)
        self.assertIn(EXPECTED_OKF_VERSION_CONDITION, that_list)

    def test_that_list_no_longer_contains_the_previous_unconverted_condition(self) -> None:
        task = self._get_target_task()
        that_list = task["ansible.builtin.assert"]["that"]
        self.assertNotIn(PREVIOUS_UNCONVERTED_CONDITION, that_list)

    def test_float_coerced_condition_evaluates_true_for_the_real_quoted_string_value(self) -> None:
        # Mirrors the actual mock fixture, where okf_version is declared as
        # the quoted YAML string "0.1" and parsed into a Python str by
        # from_yaml, exactly as report_frontmatter.okf_version would be.
        env = Environment()
        compiled = env.compile_expression(EXPECTED_OKF_VERSION_CONDITION)
        report_frontmatter = {"okf_version": "0.1"}
        self.assertTrue(compiled(report_frontmatter=report_frontmatter))

    def test_float_coerced_condition_evaluates_false_for_a_mismatched_version(self) -> None:
        env = Environment()
        compiled = env.compile_expression(EXPECTED_OKF_VERSION_CONDITION)
        report_frontmatter = {"okf_version": "0.2"}
        self.assertFalse(compiled(report_frontmatter=report_frontmatter))

    def test_previous_unconverted_condition_would_regress_into_always_false(self) -> None:
        # Demonstrates *why* comparing string to float literal directly is incorrect
        env = Environment()
        compiled = env.compile_expression(PREVIOUS_UNCONVERTED_CONDITION)
        report_frontmatter = {"okf_version": "0.1"}
        self.assertFalse(
            compiled(report_frontmatter=report_frontmatter),
            "The previous unconverted condition unexpectedly evaluated True; "
            "test fixture assumptions about Jinja2 str/float comparison may have changed",
        )


if __name__ == "__main__":
    unittest.main()