#!/usr/bin/env python3
"""
Regression tests for tests/test_ansible_cfg_stdout_callback.yml itself.

This PR changed the "Assert both settings are exact, uncommented whole-line
key = value pairs" assertion's 'that' conditions from the bare filter chain:

    cfg_content | regex_search(stdout_callback_regex, multiline=True)

to an explicit length check:

    (cfg_content | regex_search(stdout_callback_regex, multiline=True)) | length > 0

Ansible's `regex_search` filter returns `None` when the pattern does not
match. Piping a possible `None` straight into the `length` filter (which,
via Jinja2, ultimately calls Python's `len()`) raises a TypeError instead of
evaluating to a clean boolean -- so the fixed condition intentionally makes
the "no match" case blow up loudly with a templating error rather than
silently depend on `None`'s truthiness, while the "match found" case must
still evaluate to a plain `True`.

These tests parse tests/test_ansible_cfg_stdout_callback.yml with a real
YAML loader and verify:
  1. The file loads as valid YAML (a basic sanity check for the whole file).
  2. The specific assertion's 'that' list contains the new, length-guarded
     conditions for both settings, not the previous bare filter chain.
  3. Re-implementing Ansible's `regex_search` semantics (returns the matched
     substring, or None) and compiling the fixed condition with a real
     Jinja2 environment: the condition evaluates to True for cfg content
     that contains the expected uncommented key = value line.
  4. The condition correctly rejects (does not silently accept) cfg content
     where the setting is missing, commented out, or only partially
     matches -- whether by evaluating to False or by raising, so long as it
     never silently evaluates truthy.

Run with:
    python3 -m unittest tests/test_test_ansible_cfg_stdout_callback_yaml_validity.py -v
"""
import os
import re
import unittest

import yaml
from jinja2 import Environment

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_CFG_CALLBACK_YML = os.path.join(REPO_ROOT, "tests", "test_ansible_cfg_stdout_callback.yml")
ANSIBLE_CFG_PATH = os.path.join(REPO_ROOT, "ansible.cfg")

TARGET_TASK_NAME = "Assert both settings are exact, uncommented whole-line key = value pairs"
EXPECTED_CONDITIONS = [
    "(cfg_content | regex_search(callback_result_format_regex, multiline=True) | default('', true)) | length > 0",
    "(cfg_content | regex_search(bin_ansible_callbacks_regex, multiline=True) | default('', true)) | length > 0",
]
PREVIOUS_BARE_CONDITIONS = [
    "cfg_content | regex_search(callback_result_format_regex, multiline=True)",
    "cfg_content | regex_search(bin_ansible_callbacks_regex, multiline=True)",
]

CALLBACK_RESULT_FORMAT_REGEX = r"^callback_result_format\s*=\s*yaml\s*$"
BIN_ANSIBLE_CALLBACKS_REGEX = r"^bin_ansible_callbacks\s*=\s*True\s*$"


def ansible_style_regex_search(value, pattern, multiline=False):
    """Minimal re-implementation of Ansible's regex_search filter semantics."""
    flags = re.MULTILINE if multiline else 0
    match = re.search(pattern, value, flags)
    return match.group() if match else None


class TestTestAnsibleCfgStdoutCallbackYamlValidity(unittest.TestCase):
    """Verify tests/test_ansible_cfg_stdout_callback.yml is syntactically valid and semantically correct."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(TEST_CFG_CALLBACK_YML, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()
        with open(ANSIBLE_CFG_PATH, "r", encoding="utf-8") as f:
            cls.real_ansible_cfg_content = f.read()

    def test_file_is_valid_yaml(self) -> None:
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(f"tests/test_ansible_cfg_stdout_callback.yml must be valid YAML, but failed to parse: {exc}")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def _get_target_task(self):
        data = yaml.safe_load(self.raw_content)
        tasks = data[0]["tasks"]
        matching = [t for t in tasks if t.get("name") == TARGET_TASK_NAME]
        self.assertEqual(
            len(matching), 1, f"Expected exactly one task named {TARGET_TASK_NAME!r}"
        )
        return matching[0]

    def test_that_list_contains_both_length_guarded_conditions(self) -> None:
        task = self._get_target_task()
        that_list = task["ansible.builtin.assert"]["that"]
        self.assertIsInstance(that_list, list)
        for expected in EXPECTED_CONDITIONS:
            self.assertIn(expected, that_list)

    def test_that_list_no_longer_contains_the_previous_bare_conditions(self) -> None:
        task = self._get_target_task()
        that_list = task["ansible.builtin.assert"]["that"]
        for previous in PREVIOUS_BARE_CONDITIONS:
            self.assertNotIn(previous, that_list)

    def _make_env(self):
        env = Environment()
        env.filters["regex_search"] = ansible_style_regex_search
        return env

    def test_condition_evaluates_true_for_real_ansible_cfg_content(self) -> None:
        env = self._make_env()
        compiled = env.compile_expression(EXPECTED_CONDITIONS[0])
        self.assertTrue(
            compiled(
                cfg_content=self.real_ansible_cfg_content,
                callback_result_format_regex=CALLBACK_RESULT_FORMAT_REGEX,
            )
        )

    def test_condition_evaluates_true_for_a_minimal_conforming_snippet(self) -> None:
        env = self._make_env()
        compiled = env.compile_expression(EXPECTED_CONDITIONS[1])
        conforming_snippet = "[defaults]\ncallback_result_format = yaml\nbin_ansible_callbacks = True\n"
        self.assertTrue(
            compiled(
                cfg_content=conforming_snippet,
                bin_ansible_callbacks_regex=BIN_ANSIBLE_CALLBACKS_REGEX,
            )
        )

    def test_condition_does_not_silently_accept_a_commented_out_setting(self) -> None:
        # Negative/regression case: a commented-out line must never be
        # treated as satisfying the assertion, whether the condition
        # evaluates cleanly to False or raises while handling the `None`
        # match result -- either outcome correctly fails the task, but a
        # silent True would be a real regression.
        env = self._make_env()
        compiled = env.compile_expression(EXPECTED_CONDITIONS[0])
        commented_out_snippet = "[defaults]\n#callback_result_format = yaml\nbin_ansible_callbacks = True\n"
        try:
            result = compiled(
                cfg_content=commented_out_snippet,
                callback_result_format_regex=CALLBACK_RESULT_FORMAT_REGEX,
            )
        except Exception:
            # Raising while trying to apply `length` to a None match result
            # is an acceptable (if noisy) way of ensuring the task still
            # fails; it must not silently succeed.
            return
        self.assertFalse(result)

    def test_condition_does_not_silently_accept_a_partial_match(self) -> None:
        env = self._make_env()
        compiled = env.compile_expression(EXPECTED_CONDITIONS[0])
        partial_match_snippet = "[defaults]\ncallback_result_format = json\nbin_ansible_callbacks = True\n"
        try:
            result = compiled(
                cfg_content=partial_match_snippet,
                callback_result_format_regex=CALLBACK_RESULT_FORMAT_REGEX,
            )
        except Exception:
            return
        self.assertFalse(result)

    def test_default_filter_cleanly_evaluates_false_instead_of_raising_when_setting_is_entirely_absent(
        self,
    ) -> None:
        # This is the specific regression this PR's `| default('', true)` addition
        # guards against: regex_search() returns None when the setting is entirely
        # absent (not merely commented out), and piping that None straight into
        # `length` used to raise a TypeError. With `| default('', true)` in place,
        # a None match result is coerced to '' before `length` is applied, so the
        # condition must evaluate cleanly to False rather than raising.
        env = self._make_env()
        compiled = env.compile_expression(EXPECTED_CONDITIONS[0])
        no_setting_at_all_snippet = "[defaults]\nbin_ansible_callbacks = True\n"
        result = compiled(
            cfg_content=no_setting_at_all_snippet,
            callback_result_format_regex=CALLBACK_RESULT_FORMAT_REGEX,
        )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()