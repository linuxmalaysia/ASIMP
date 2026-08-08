#!/usr/bin/env python3
"""
Unit tests for the embedded OpenSCAP score parser script
(`parse_openscap_score.py`) that roles/reporting-ASIMP/tasks/main.yml writes
out via the "Create OpenSCAP score parser helper script" task
(`ansible.builtin.copy`).

This PR simplifies the xccdf 1.2 -> xccdf 1.1 `<result>` fallback logic in
`get_score()` from two statements:

    results_12 = [elem.text for elem in root.findall('.//xccdf12:result', ns)]
    results_11 = [elem.text for elem in root.findall('.//xccdf11:result', ns)]
    results = results_12 if results_12 else results_11

into a single expression that only evaluates the xccdf 1.1 `findall()` when
no xccdf 1.2 results were found:

    results_12 = [elem.text for elem in root.findall('.//xccdf12:result', ns)]
    results = results_12 if results_12 else [elem.text for elem in root.findall('.//xccdf11:result', ns)]

These tests extract the *actual* embedded script source straight out of
roles/reporting-ASIMP/tasks/main.yml (without requiring PyYAML) and exec it
in an isolated namespace, so they exercise the real code shipped by the role
rather than a hand-copied duplicate. They verify that the pass/fail-`<result>`
-based scoring fallback still:
  - Uses xccdf 1.2 `<result>` elements when present.
  - Falls back to xccdf 1.1 `<result>` elements only when no xccdf 1.2
    results exist.
  - Prefers xccdf 1.2 over xccdf 1.1 when both are present (regression guard
    for the short-circuit behavior preserved by the refactor).
  - Computes percentages correctly for all-pass, all-fail, and mixed
    pass/fail/other-status result sets.
  - Returns None (rather than raising) when there are no usable results, the
    XML is malformed, or the file is missing.

Run with:
    python3 -m unittest tests/test_reporting_asimp_parse_openscap_score.py -v
or, if pytest is available:
    python3 -m pytest tests/test_reporting_asimp_parse_openscap_score.py -v
"""
import os
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(REPO_ROOT, "roles", "reporting-ASIMP", "tasks", "main.yml")
SCRIPT_TASK_NAME = "Create OpenSCAP score parser helper script"

XCCDF12_NS = "http://checklists.nist.gov/xccdf/1.2"
XCCDF11_NS = "http://checklists.nist.gov/xccdf/1.1"


def _extract_copy_content(yaml_text, task_name):
    """Pull the literal block scalar assigned to `content:` for the
    `ansible.builtin.copy` task named `task_name`, straight out of a raw
    tasks/main.yml, without depending on PyYAML being installed.
    """
    lines = yaml_text.splitlines()
    task_marker = f"- name: {task_name}"

    start_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == task_marker), None
    )
    if start_idx is None:
        raise AssertionError(f"Task {task_name!r} not found in {TASKS_FILE}")

    content_idx = None
    for i in range(start_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("- name:") and i != start_idx:
            break
        if stripped.startswith("content:"):
            content_idx = i
            break
    if content_idx is None:
        raise AssertionError(f"'content:' not found for task {task_name!r}")

    content_indent = len(lines[content_idx]) - len(lines[content_idx].lstrip(" "))

    block_lines = []
    body_indent = None
    for line in lines[content_idx + 1:]:
        if line.strip() == "":
            block_lines.append("")
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= content_indent:
            break
        if body_indent is None:
            body_indent = indent
        block_lines.append(line[body_indent:])
    return "\n".join(block_lines) + "\n"


def _load_get_score():
    """Extract parse_openscap_score.py's source from the role's tasks file
    and exec it in an isolated namespace, returning its `get_score`
    function so tests exercise the real, currently-shipped implementation.
    """
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        yaml_text = f.read()
    script_source = _extract_copy_content(yaml_text, SCRIPT_TASK_NAME)
    namespace = {"__name__": "parse_openscap_score_under_test"}
    exec(compile(script_source, "parse_openscap_score.py", "exec"), namespace)
    return namespace["get_score"]


def _build_xccdf_xml(results_12=None, results_11=None):
    """Build a minimal XCCDF-like TestResult XML document containing the
    given xccdf 1.2 and/or xccdf 1.1 <result> elements (no <score>
    elements), to exercise the pass/fail-count-based scoring fallback.
    """
    parts = [
        f'<TestResult xmlns:xccdf12="{XCCDF12_NS}" xmlns:xccdf11="{XCCDF11_NS}">'
    ]
    for text in results_12 or []:
        parts.append(f"<xccdf12:result>{text}</xccdf12:result>")
    for text in results_11 or []:
        parts.append(f"<xccdf11:result>{text}</xccdf11:result>")
    parts.append("</TestResult>")
    return "\n".join(parts)


class ParseOpenscapScoreResultsFallbackTestCase(unittest.TestCase):
    """Tests for the xccdf 1.2 -> xccdf 1.1 <result> fallback logic changed
    by this PR inside get_score().
    """

    @classmethod
    def setUpClass(cls):
        cls.get_score = staticmethod(_load_get_score())

    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp_dir.cleanup()

    def _write_xml(self, xml_text, filename="results.xml"):
        path = os.path.join(self._tmp_dir.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_text)
        return path

    def test_uses_xccdf12_results_when_present(self):
        xml_path = self._write_xml(
            _build_xccdf_xml(results_12=["pass", "pass", "fail"])
        )
        score = self.get_score(xml_path)
        self.assertAlmostEqual(score, (2 / 3) * 100)

    def test_falls_back_to_xccdf11_results_when_no_xccdf12_results(self):
        xml_path = self._write_xml(
            _build_xccdf_xml(results_11=["pass", "fail", "fail"])
        )
        score = self.get_score(xml_path)
        self.assertAlmostEqual(score, (1 / 3) * 100)

    def test_prefers_xccdf12_results_over_xccdf11_when_both_present(self):
        # xccdf 1.2 results are all passes (100%); xccdf 1.1 results are all
        # failures (0%). The refactored one-line expression must still only
        # use the xccdf 1.1 findall() when results_12 is empty, so the
        # xccdf 1.2 results must win here.
        xml_path = self._write_xml(
            _build_xccdf_xml(
                results_12=["pass", "pass"],
                results_11=["fail", "fail", "fail"],
            )
        )
        score = self.get_score(xml_path)
        self.assertAlmostEqual(score, 100.0)

    def test_all_results_pass_yields_100_percent(self):
        xml_path = self._write_xml(_build_xccdf_xml(results_12=["pass", "pass"]))
        self.assertAlmostEqual(self.get_score(xml_path), 100.0)

    def test_all_results_fail_yields_0_percent(self):
        xml_path = self._write_xml(_build_xccdf_xml(results_12=["fail", "fail"]))
        self.assertAlmostEqual(self.get_score(xml_path), 0.0)

    def test_non_pass_fail_statuses_are_excluded_from_the_denominator(self):
        # 'notapplicable'/'notchecked'/etc. must not count towards `total`;
        # only 'pass' and 'fail' do.
        xml_path = self._write_xml(
            _build_xccdf_xml(
                results_12=["pass", "notapplicable", "fail", "notchecked"]
            )
        )
        score = self.get_score(xml_path)
        self.assertAlmostEqual(score, 50.0)

    def test_results_with_only_non_pass_fail_statuses_returns_none(self):
        # results_12 is truthy (non-empty) but the pass+fail count is 0, so
        # get_score must return None rather than raising ZeroDivisionError.
        xml_path = self._write_xml(
            _build_xccdf_xml(results_12=["notapplicable", "notchecked"])
        )
        self.assertIsNone(self.get_score(xml_path))

    def test_no_result_or_score_elements_returns_none(self):
        xml_path = self._write_xml(_build_xccdf_xml())
        self.assertIsNone(self.get_score(xml_path))

    def test_unparseable_xml_returns_none(self):
        xml_path = self._write_xml("not valid xml <<<")
        self.assertIsNone(self.get_score(xml_path))

    def test_missing_file_returns_none(self):
        missing_path = os.path.join(self._tmp_dir.name, "does-not-exist.xml")
        self.assertIsNone(self.get_score(missing_path))


class ExtractedScriptSourceRegressionTestCase(unittest.TestCase):
    """Regression guards that pin the exact refactored source text of the
    changed fallback expression, so an accidental revert or further edit is
    caught even if runtime behavior happened to stay the same.
    """

    def setUp(self):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            self.script_source = _extract_copy_content(f.read(), SCRIPT_TASK_NAME)

    def test_fallback_expression_is_a_single_statement(self):
        self.assertIn(
            "results = results_12 if results_12 else "
            "[elem.text for elem in root.findall('.//xccdf11:result', ns)]",
            self.script_source,
        )

    def test_intermediate_results_11_variable_no_longer_assigned_separately(self):
        self.assertNotIn("results_11 = [elem.text", self.script_source)


if __name__ == "__main__":
    unittest.main()