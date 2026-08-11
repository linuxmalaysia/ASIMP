#!/usr/bin/env python3
"""
Regression tests for the Jekyll {% raw %} / {% endraw %} Liquid guards added
around Ansible/Jinja-templated YAML code fences in docs/lynis.md and
docs/openscap.md.

Jekyll's Liquid templating engine parses `{{ ... }}` found anywhere in a
markdown page (including inside fenced code blocks) as its own Liquid output
tags. Several fenced ```yaml code blocks in these two docs contain literal
Ansible Jinja2 expressions such as `{{ openscap_report_dir }}`, which Liquid
attempted to evaluate as undefined Liquid variables, breaking the GitHub
Pages Jekyll build with a syntax error. This PR fixes that by wrapping every
such fenced code block in Jekyll's `{% raw %}` / `{% endraw %}` tags, which
tell Liquid to treat the enclosed text as plain text instead of a template to
evaluate.

These tests verify, for each affected documentation page:
  1. The overall count of `{% raw %}` / `{% endraw %}` tags matches the
     number of Jinja-templated code fences that needed protecting, and the
     tags are balanced.
  2. Every Jinja-templated code fence changed by this PR is now wrapped
     immediately by `{% raw %}` right before the ```yaml fence and
     `{% endraw %}` right after the closing ```.
  3. Pre-existing code fences that do NOT contain Ansible Jinja `{{ }}`
     expressions were left untouched (not wrapped), guarding against
     over-eager wrapping.
  4. A generalized regression scan: any fenced code block anywhere in the
     document containing a literal `{{` is guarded by adjacent
     {% raw %}/{% endraw %} tags, which is exactly the defect that broke
     the Jekyll build in the first place.

Run with:
    python3 -m unittest tests/test_docs_liquid_raw_blocks.py -v
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LYNIS_DOC_PATH = os.path.join(REPO_ROOT, "docs", "lynis.md")
OPENSCAP_DOC_PATH = os.path.join(REPO_ROOT, "docs", "openscap.md")


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _assert_every_templated_fence_is_raw_guarded(
    testcase: unittest.TestCase, content: str, fence_languages: str
) -> int:
    """Scan every fenced code block matching fence_languages (e.g. "yaml"
    or "yaml|python") and assert that any block containing a literal `{{`
    is immediately wrapped by {% raw %} / {% endraw %}. Returns the number
    of templated fences found, so callers can assert it is non-zero.
    """
    fence_pattern = re.compile(
        r"(\{% raw %\}\n)?```(?:" + fence_languages + r")\n(.*?)```\n(\{% endraw %\}\n?)?",
        re.DOTALL,
    )
    templated_fence_count = 0
    for match in fence_pattern.finditer(content):
        raw_open, body, raw_close = match.group(1), match.group(2), match.group(3)
        if "{{" in body:
            templated_fence_count += 1
            testcase.assertIsNotNone(
                raw_open,
                "Jinja-templated code fence is missing a preceding "
                "{% raw %} guard:\n" + body,
            )
            testcase.assertIsNotNone(
                raw_close,
                "Jinja-templated code fence is missing a following "
                "{% endraw %} guard:\n" + body,
            )
    return templated_fence_count


class TestLynisDocRawBlocks(unittest.TestCase):
    """Verify {% raw %} guards around Jinja-templated code fences in docs/lynis.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _read(LYNIS_DOC_PATH)

    def test_raw_and_endraw_tag_counts_are_balanced_and_expected(self) -> None:
        self.assertEqual(self.content.count("{% raw %}"), 3)
        self.assertEqual(self.content.count("{% endraw %}"), 3)

    def test_audit_command_block_is_wrapped_in_raw_tags(self) -> None:
        expected = (
            "{% raw %}\n"
            "```yaml\n"
            "- name: Run Lynis BEFORE hardening audit\n"
            "  ansible.builtin.shell: lynis audit system --quick --report-file "
            "{{ openscap_report_dir }}/lynis-report-before.dat\n"
            "  register: lynis_before_run\n"
            "  failed_when: false\n"
            "  changed_when: true\n"
            "```\n"
            "{% endraw %}"
        )
        self.assertIn(expected, self.content)

    def test_parse_hardening_index_block_is_wrapped_in_raw_tags(self) -> None:
        expected = (
            "{% raw %}\n"
            "```yaml\n"
            "- name: Parse Lynis BEFORE hardening index\n"
            "  ansible.builtin.shell: grep -E \"^hardening_index=\" "
            "{{ openscap_report_dir }}/lynis-report-before.dat | cut -d'=' -f2\n"
            "  register: parsed_lynis_before\n"
            "  changed_when: false\n"
            "  failed_when: false\n"
            "```\n"
            "{% endraw %}"
        )
        self.assertIn(expected, self.content)

    def test_apply_hardening_configuration_block_is_wrapped_in_raw_tags(self) -> None:
        expected = (
            "{% raw %}\n"
            "```yaml\n"
            "- name: Apply Lynis Hardening Configuration\n"
            "  block:\n"
            "    - name: Apply Lynis Hardening Configuration\n"
            "      ansible.builtin.include_role:\n"
            "        name: lynis-ansible\n"
            "      vars:\n"
            "        lynis_use_packages: true\n"
            "        lynis_audit_system_linux: true\n"
            "  ignore_errors: \"{{ is_sandbox_jules }}\"\n"
            "  when: asimp_privilege_level == 'full'\n"
            "  become: true\n"
            "```\n"
            "{% endraw %}"
        )
        self.assertIn(expected, self.content)

    def test_non_templated_install_task_block_is_not_wrapped_in_raw_tags(self) -> None:
        # The Lynis installation task has no literal `{{ }}` Jinja
        # expressions, so it never needed (and should not have received) a
        # raw guard.
        unwrapped_marker = "```yaml\n- name: Ensure lynis is installed"
        self.assertIn(unwrapped_marker, self.content)
        self.assertNotIn("{% raw %}\n" + unwrapped_marker, self.content)

    def test_every_jinja_templated_yaml_fence_is_raw_guarded(self) -> None:
        templated_fence_count = _assert_every_templated_fence_is_raw_guarded(
            self, self.content, "yaml"
        )
        self.assertEqual(
            templated_fence_count,
            3,
            "Expected exactly 3 Jinja-templated yaml fences in docs/lynis.md",
        )


class TestOpenscapDocRawBlocks(unittest.TestCase):
    """Verify {% raw %} guards around Jinja-templated code fences in docs/openscap.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _read(OPENSCAP_DOC_PATH)

    def test_raw_and_endraw_tag_counts_are_balanced_and_expected(self) -> None:
        self.assertEqual(self.content.count("{% raw %}"), 6)
        self.assertEqual(self.content.count("{% endraw %}"), 6)

    def test_fetch_scap_security_guide_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n"
            "- name: OpenSCAP | Fetch latest SCAP Security Guide release "
            "from GitHub (Ubuntu)",
            self.content,
        )
        self.assertIn(
            "register: found_downloaded_ds\n```\n{% endraw %}",
            self.content,
        )

    def test_set_datastream_fact_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n- name: OpenSCAP | Set datastream fact",
            self.content,
        )
        self.assertIn(
            "{%- endif -%}\n```\n{% endraw %}",
            self.content,
        )

    def test_run_scan_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n- name: Run OpenSCAP BEFORE hardening scan",
            self.content,
        )
        self.assertIn(
            "  register: oscap_before_run\n  failed_when: false\n"
            "  changed_when: true\n```\n{% endraw %}",
            self.content,
        )

    def test_parse_score_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n- name: Parse OpenSCAP BEFORE compliance score",
            self.content,
        )
        self.assertIn(
            "  changed_when: false\n  failed_when: false\n```\n{% endraw %}"
            "\n\n---\n\n### 5. Dynamic Bash Remediation Script Generation",
            self.content,
        )

    def test_generate_remediation_script_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n"
            "- name: OpenSCAP | Generate BEFORE Remediation Script (Ubuntu)",
            self.content,
        )
        self.assertIn(
            "  changed_when: true\n  failed_when: false\n```\n{% endraw %}"
            "\n\nThis shell script can then be inspected",
            self.content,
        )

    def test_oval_download_and_evaluation_block_is_wrapped_in_raw_tags(self) -> None:
        self.assertIn(
            "{% raw %}\n```yaml\n- name: OpenSCAP | Download OVAL definitions",
            self.content,
        )
        self.assertIn(
            "{{ openscap_report_dir }}/com.ubuntu.{{ ansible_distribution_release }}"
            ".usn.oval.xml\n```\n{% endraw %}",
            self.content,
        )

    def test_non_templated_blocks_are_not_wrapped_in_raw_tags(self) -> None:
        # These fences never contained literal `{{ }}` expressions and
        # therefore must remain unguarded.
        unwrapped_markers = (
            "```yaml\nopenscap_profile:",
            "```yaml\n- name: OpenSCAP | Install Packages (Ubuntu)",
            "```python\n#!/usr/bin/env python3",
        )
        for unwrapped_marker in unwrapped_markers:
            self.assertIn(unwrapped_marker, self.content)
            self.assertNotIn("{% raw %}\n" + unwrapped_marker, self.content)

    def test_every_jinja_templated_fence_is_raw_guarded(self) -> None:
        templated_fence_count = _assert_every_templated_fence_is_raw_guarded(
            self, self.content, "yaml|python"
        )
        self.assertEqual(
            templated_fence_count,
            6,
            "Expected exactly 6 Jinja-templated fences in docs/openscap.md",
        )


if __name__ == "__main__":
    unittest.main()