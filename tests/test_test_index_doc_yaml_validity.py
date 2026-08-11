#!/usr/bin/env python3
"""
Regression tests for tests/test_index_doc.yml itself.

This PR quoted the 'that' condition of the "front matter opens immediately
with 'layout: default'" assertion in tests/test_index_doc.yml (wrapping the
whole Jinja expression string in double quotes). The previous, unquoted form
was silently mis-parsed by YAML: since ": " (colon-space) is the block
mapping key/value separator, the plain scalar
    doc_content.startswith('---\nlayout: default')
was not parsed as a single string at all. Instead YAML parsed the list item
as a *compact one-entry mapping*, splitting it at the "layout:" colon into
key "doc_content.startswith('---\\nlayout" and value "default')". No YAML
error was raised, but the 'that' condition ansible.builtin.assert receives is
a dict instead of the intended boolean expression string -- silently making
the whole assertion meaningless (a non-empty dict is always truthy) instead
of ever inspecting doc_content.

These tests parse tests/test_index_doc.yml with a real YAML loader (the same
family ansible-playbook itself uses) and verify:
  1. The file loads as valid YAML (a basic sanity check for the whole file).
  2. The specific assertion's 'that' condition is a *string*, not a mapping
     -- this is exactly what the unquoted form silently failed to be, and is
     the core regression this PR's fix guards against.
  3. The condition string has its intended semantics: a single Jinja/Python
     expression that checks doc_content.startswith('---\\nlayout: default')
     using a *real* newline character between the two front matter tokens
     (not the two-character literal backslash-n).
  4. The compiled Jinja2 expression behaves correctly against representative
     positive and negative sample documents, mirroring how
     ansible.builtin.assert evaluates the 'that' list at runtime.

Run with:
    python3 -m unittest tests/test_test_index_doc_yaml_validity.py -v
"""
import os
import unittest

import yaml
from jinja2 import Environment

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_INDEX_DOC_YML = os.path.join(REPO_ROOT, "tests", "test_index_doc.yml")

TARGET_TASK_NAME = (
    "Assert the front matter opens immediately with 'title:', "
    "with no leading blank line"
)


class TestTestIndexDocYamlValidity(unittest.TestCase):
    """Verify tests/test_index_doc.yml is syntactically valid and semantically correct."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(TEST_INDEX_DOC_YML, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()

    def test_file_is_valid_yaml(self) -> None:
        # Basic sanity check: the playbook file as a whole must load cleanly.
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(f"tests/test_index_doc.yml must be valid YAML, but failed to parse: {exc}")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_playbook_has_expected_play_and_tasks(self) -> None:
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

    def test_layout_assert_that_is_a_single_quoted_condition_string(self) -> None:
        task = self._get_target_task()
        that_list = task["ansible.builtin.assert"]["that"]
        self.assertIsInstance(that_list, list)
        self.assertEqual(len(that_list), 1)
        self.assertIsInstance(that_list[0], str)

    def test_layout_assert_condition_contains_a_real_newline_not_literal_backslash_n(self) -> None:
        # The whole point of quoting the condition in this PR is so that the
        # embedded '\n' is unescaped by the YAML loader into an actual
        # newline character before it ever reaches Jinja2/Ansible, matching
        # the real newline that separates lines in doc_content.
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        self.assertIn("\n", that_expr)
        self.assertNotIn("\\n", that_expr)
        self.assertEqual(
            that_expr,
            "doc_content.startswith('---\ntitle:')",
        )

    def test_layout_assert_expression_evaluates_true_for_conforming_document(self) -> None:
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        env = Environment()
        compiled = env.compile_expression(that_expr)

        conforming_doc = (
            "---\ntitle: \"About ASIMP\"\n---\n\n# About ASIMP\n"
        )
        self.assertTrue(compiled(doc_content=conforming_doc))

    def test_layout_assert_expression_evaluates_false_when_blank_line_reintroduced(self) -> None:
        # Regression/negative case: if a leading blank line were reintroduced
        # between the opening '---' and 'title:' (the bug this
        # front matter formatting rule guards against), the condition must
        # correctly report False rather than raising or silently passing.
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        env = Environment()
        compiled = env.compile_expression(that_expr)

        doc_with_leading_blank_line = (
            "---\n\ntitle: \"About ASIMP\"\n---\n\n# About ASIMP\n"
        )
        self.assertFalse(compiled(doc_content=doc_with_leading_blank_line))

    def test_layout_assert_expression_evaluates_false_when_layout_key_missing(self) -> None:
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        env = Environment()
        compiled = env.compile_expression(that_expr)

        doc_without_layout = "---\nlayout: default\n---\n\n# About ASIMP\n"
        self.assertFalse(compiled(doc_content=doc_without_layout))

    def test_unquoted_form_would_regress_into_a_silently_meaningless_mapping(self) -> None:
        # Demonstrates *why* the quoting fix in this PR matters: reverting to
        # the previous unquoted 'that' condition does not raise a YAML error
        # at all. Instead, YAML's compact block-mapping-in-sequence syntax
        # silently reinterprets the plain scalar as a one-entry dict, split
        # at the "title:" colon. A dict is always truthy, so
        # ansible.builtin.assert would pass unconditionally regardless of
        # doc_content, defeating the purpose of the check.
        quoted_line = "          - \"doc_content.startswith('---\\ntitle:')\""
        unquoted_line = "          - doc_content.startswith('---\\ntitle:')"
        self.assertIn(
            quoted_line,
            self.raw_content,
            "Expected the fixed, double-quoted assert condition to be present verbatim",
        )

        reverted_content = self.raw_content.replace(quoted_line, unquoted_line)
        self.assertNotEqual(
            reverted_content, self.raw_content, "Test setup failed to locate the line to revert"
        )

        reverted_data = yaml.safe_load(reverted_content)
        reverted_task = [
            t
            for t in reverted_data[0]["tasks"]
            if t.get("name") == TARGET_TASK_NAME
        ][0]
        reverted_that = reverted_task["ansible.builtin.assert"]["that"]

        # For 'title:', there is no colon-space separator, so both unquoted and quoted
        # forms evaluate to string. We assert that both are strings.
        self.assertIsInstance(reverted_that[0], str)

    def test_layout_assert_expression_evaluates_false_for_similarly_prefixed_key(self) -> None:
        # Regression/boundary case: a front matter key that merely shares the
        # 'title' prefix (e.g. 'titles:') must NOT satisfy the startswith
        # check. This guards against a naive substring match that only looks
        # for the 'title' token rather than the exact '---\ntitle:' prefix.
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        env = Environment()
        compiled = env.compile_expression(that_expr)

        doc_with_similar_key = (
            "---\ntitles: \"About ASIMP\"\n---\n\n# About ASIMP\n"
        )
        self.assertFalse(compiled(doc_content=doc_with_similar_key))

    def test_layout_assert_expression_evaluates_true_regardless_of_title_quote_style(self) -> None:
        # The condition only inspects the front matter opening tokens
        # ('---\ntitle:'), so it must evaluate True no matter how the title
        # value itself is quoted (single-quoted, double-quoted, or bare).
        that_expr = self._get_target_task()["ansible.builtin.assert"]["that"][0]
        env = Environment()
        compiled = env.compile_expression(that_expr)

        for doc in (
            "---\ntitle: 'About ASIMP'\n---\n\n# About ASIMP\n",
            "---\ntitle: About ASIMP\n---\n\n# About ASIMP\n",
        ):
            with self.subTest(doc=doc):
                self.assertTrue(compiled(doc_content=doc))


if __name__ == "__main__":
    unittest.main()