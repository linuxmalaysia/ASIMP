#!/usr/bin/env python3
"""
Unit tests for scripts/patch_roles.py (ASIMP Sovereign OS Role Compatibility
Patcher).

These tests exercise each patch function in isolation against temporary
fixture directories so the regex/text-transformation logic can be verified
without depending on the real vendored roles (dev-sec.ssh-hardening,
ansible-hardening, etc.), which are pulled in via ansible-galaxy / git
submodules and may not be present in a bare checkout.

Run with:
    python3 -m unittest tests/test_patch_roles.py -v
or, if pytest is available:
    python3 -m pytest tests/test_patch_roles.py -v
"""
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import patch_roles  # noqa: E402


class PatchRolesTestCase(unittest.TestCase):
    """Base test case that runs each test inside an isolated temp cwd.

    patch_roles.py operates exclusively on relative paths (e.g.
    "roles/dev-sec.ssh-hardening/templates/opensshd.conf.j2"), so every test
    chdir's into a fresh temporary directory that mimics the relevant slice
    of the repository layout.
    """

    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

    def tearDown(self):
        os.chdir(self._orig_cwd)
        self._tmp_dir.cleanup()

    @staticmethod
    def _write(path, content):
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _read(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


class TestPatchSshTemplates(PatchRolesTestCase):
    SSHD_PATH = "roles/dev-sec.ssh-hardening/templates/opensshd.conf.j2"
    OPENSSH_PATH = "roles/dev-sec.ssh-hardening/templates/openssh.conf.j2"

    def test_double_quoted_directive_is_rewritten(self):
        self._write(
            self.SSHD_PATH,
            '#jinja2: trim_blocks: "true", lstrip_blocks: "true"\nSome content\n',
        )
        patch_roles.patch_ssh_templates()
        content = self._read(self.SSHD_PATH)
        self.assertIn("#jinja2: trim_blocks: True, lstrip_blocks: True", content)
        self.assertIn("Some content", content)

    def test_single_quoted_directive_is_rewritten(self):
        self._write(
            self.OPENSSH_PATH,
            "#jinja2: trim_blocks: 'true', lstrip_blocks: 'true'\n",
        )
        patch_roles.patch_ssh_templates()
        content = self._read(self.OPENSSH_PATH)
        self.assertIn("#jinja2: trim_blocks: True, lstrip_blocks: True", content)

    def test_unquoted_capitalized_directive_is_unchanged(self):
        original = "#jinja2: trim_blocks: True, lstrip_blocks: True\n"
        self._write(self.SSHD_PATH, original)
        patch_roles.patch_ssh_templates()
        self.assertEqual(self._read(self.SSHD_PATH), original)

    def test_missing_files_do_not_raise(self):
        # Neither template exists in this temp cwd; the function must be a no-op.
        try:
            patch_roles.patch_ssh_templates()
        except Exception as exc:  # pragma: no cover - defensive
            self.fail(f"patch_ssh_templates() raised unexpectedly: {exc}")

    def test_only_existing_file_is_patched(self):
        self._write(
            self.SSHD_PATH,
            '#jinja2: trim_blocks: "true", lstrip_blocks: "true"\n',
        )
        # openssh.conf.j2 intentionally left absent.
        patch_roles.patch_ssh_templates()
        content = self._read(self.SSHD_PATH)
        self.assertIn("trim_blocks: True, lstrip_blocks: True", content)
        self.assertFalse(os.path.exists(self.OPENSSH_PATH))


class TestPatchModuliTask(PatchRolesTestCase):
    PATH = "roles/dev-sec.ssh-hardening/tasks/hardening.yml"

    def test_zero_indent_directive_is_rewritten(self):
        # When the matched directive sits on the final line of the file, the
        # trailing `\s*$` in the regex greedily consumes the final newline
        # too (since `\s` matches `\n` and MULTILINE `$` still matches at
        # end-of-string), so the replaced content ends up without a
        # trailing newline. This differs from the indented, non-final-line
        # case exercised below, where backtracking stops before the newline.
        self._write(self.PATH, "- sshd_register_moduli.stdout\n")
        patch_roles.patch_moduli_task()
        content = self._read(self.PATH)
        self.assertEqual(content, "- sshd_register_moduli.stdout | length > 0")

    def test_indented_directive_preserves_indentation(self):
        self._write(
            self.PATH,
            "when:\n  - sshd_register_moduli.stdout\n  - some_other_cond\n",
        )
        patch_roles.patch_moduli_task()
        content = self._read(self.PATH)
        self.assertIn("  - sshd_register_moduli.stdout | length > 0\n", content)
        self.assertIn("  - some_other_cond\n", content)

    def test_is_idempotent_across_repeated_runs(self):
        self._write(self.PATH, "- sshd_register_moduli.stdout\n")
        patch_roles.patch_moduli_task()
        first_pass = self._read(self.PATH)
        patch_roles.patch_moduli_task()
        second_pass = self._read(self.PATH)
        self.assertEqual(first_pass, second_pass)
        self.assertEqual(first_pass.count("| length > 0"), 1)

    def test_missing_file_does_not_raise(self):
        try:
            patch_roles.patch_moduli_task()
        except Exception as exc:  # pragma: no cover - defensive
            self.fail(f"patch_moduli_task() raised unexpectedly: {exc}")

    def test_unrelated_content_is_untouched(self):
        original = "- some_other_var.stdout\n- sshd_register_moduli.stdout_extra\n"
        self._write(self.PATH, original)
        patch_roles.patch_moduli_task()
        self.assertEqual(self._read(self.PATH), original)


class TestSplitIntoTasks(unittest.TestCase):
    def test_empty_input_returns_no_blocks(self):
        self.assertEqual(patch_roles.split_into_tasks([]), [])

    def test_single_top_level_task_is_one_block(self):
        lines = ["- name: task one\n", "  debug: msg=hi\n"]
        blocks = patch_roles.split_into_tasks(lines)
        self.assertEqual(len(blocks), 1)
        indent, block_lines = blocks[0]
        self.assertEqual(indent, 0)
        self.assertEqual(block_lines, lines)

    def test_nested_items_stay_in_parent_block(self):
        lines = [
            "- name: outer\n",
            "  block:\n",
            "    - name: inner\n",
            "      debug: msg=hi\n",
        ]
        blocks = patch_roles.split_into_tasks(lines)
        self.assertEqual(len(blocks), 1)
        indent, block_lines = blocks[0]
        self.assertEqual(indent, 0)
        self.assertEqual(block_lines, lines)

    def test_sibling_top_level_tasks_are_separate_blocks(self):
        lines = [
            "- name: task one\n",
            "  debug: msg=one\n",
            "- name: task two\n",
            "  debug: msg=two\n",
        ]
        blocks = patch_roles.split_into_tasks(lines)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0], (0, ["- name: task one\n", "  debug: msg=one\n"]))
        self.assertEqual(blocks[1], (0, ["- name: task two\n", "  debug: msg=two\n"]))

    def test_preamble_before_first_dash_becomes_its_own_block(self):
        lines = ["---\n", "# a comment\n", "- name: task one\n", "  debug: msg=one\n"]
        blocks = patch_roles.split_into_tasks(lines)
        self.assertEqual(len(blocks), 2)
        preamble_indent, preamble_lines = blocks[0]
        self.assertIsNone(preamble_indent)
        self.assertEqual(preamble_lines, ["---\n", "# a comment\n"])
        self.assertEqual(blocks[1][0], 0)

    def test_dash_at_shallower_indent_closes_previous_block(self):
        lines = [
            "  - name: first item at indent two\n",
            "    debug: msg=one\n",
            "- name: second item at indent zero\n",
            "  debug: msg=two\n",
        ]
        blocks = patch_roles.split_into_tasks(lines)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0][0], 2)
        self.assertEqual(blocks[1][0], 0)


class TestPatchYamlFile(PatchRolesTestCase):
    PATH = "roles/some-role/tasks/main.yml"

    def test_service_task_without_ignore_errors_gets_patched(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        self.assertIn(
            '  ignore_errors: "{{ is_sandbox_jules | default(false) }}"\n', content
        )
        # Injected line must be the last line of the file/task block.
        lines = content.splitlines(keepends=True)
        self.assertTrue(lines[-1].strip().startswith("ignore_errors:"))

    def test_service_task_with_existing_ignore_errors_is_untouched(self):
        original = (
            "---\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n"
            "  ignore_errors: true\n"
        )
        self._write(self.PATH, original)
        patch_roles.patch_yaml_file(self.PATH)
        self.assertEqual(self._read(self.PATH), original)

    def test_non_service_task_is_left_untouched(self):
        original = (
            "---\n"
            "- name: install a package\n"
            "  ansible.builtin.package:\n"
            "    name: lynis\n"
            "    state: present\n"
        )
        self._write(self.PATH, original)
        patch_roles.patch_yaml_file(self.PATH)
        self.assertEqual(self._read(self.PATH), original)

    def test_handler_restarting_auditd_via_shell_gets_patched(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: restart auditd\n"
            "  ansible.builtin.shell: service auditd restart\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        self.assertIn(
            'ignore_errors: "{{ is_sandbox_jules | default(false) }}"', content
        )

    def test_augenrules_handler_gets_patched(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: generate audit rules\n"
            "  ansible.builtin.command: augenrules --load\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        self.assertIn(
            'ignore_errors: "{{ is_sandbox_jules | default(false) }}"', content
        )

    def test_systemd_service_module_is_also_patched(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: start chrony\n"
            "  ansible.builtin.systemd_service:\n"
            "    name: chrony\n"
            "    state: restarted\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        self.assertIn(
            'ignore_errors: "{{ is_sandbox_jules | default(false) }}"', content
        )

    def test_injection_indent_matches_block_indent_plus_two(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: outer\n"
            "  block:\n"
            "    - name: start chrony\n"
            "      ansible.builtin.service:\n"
            "        name: chrony\n"
            "        state: started\n"
            "        enabled: true\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        # The whole "outer" block (including its nested list item) shares a
        # single indent_level of 0, so the injected line is indented by 2,
        # matching the indentation of the "- name:"/"block:" keys.
        self.assertIn(
            '\n  ignore_errors: "{{ is_sandbox_jules | default(false) }}"\n', content
        )

    def test_trailing_blank_line_does_not_receive_injection_after_it(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: start firewalld\n"
            "  ansible.builtin.service:\n"
            "    name: firewalld\n"
            "    state: started\n"
            "    enabled: true\n"
            "\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        lines = content.splitlines(keepends=True)
        non_blank = [line for line in lines if line.strip()]
        self.assertTrue(non_blank[-1].strip().startswith("ignore_errors:"))
        self.assertEqual(lines[-1], "\n")

    def test_multiple_tasks_only_service_tasks_are_patched(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: install a package\n"
            "  ansible.builtin.package:\n"
            "    name: lynis\n"
            "    state: present\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        content = self._read(self.PATH)
        self.assertEqual(content.count("ignore_errors:"), 1)
        self.assertIn("install a package", content)
        self.assertIn("start auditd", content)

    def test_second_run_is_idempotent(self):
        self._write(
            self.PATH,
            "---\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n",
        )
        patch_roles.patch_yaml_file(self.PATH)
        first_pass = self._read(self.PATH)
        patch_roles.patch_yaml_file(self.PATH)
        second_pass = self._read(self.PATH)
        self.assertEqual(first_pass, second_pass)
        self.assertEqual(first_pass.count("ignore_errors:"), 1)

    def test_content_without_any_task_list_items_is_untouched(self):
        # A file with no top-level "- " list items at all (indent_level is
        # None for the whole "block") must never receive an injection, even
        # if the text happens to mention "service:" in a comment.
        original = (
            "---\n"
            "# just a comment mentioning ansible.builtin.service: nothing else\n"
        )
        self._write(self.PATH, original)
        patch_roles.patch_yaml_file(self.PATH)
        self.assertEqual(self._read(self.PATH), original)


class TestPatchAllRoles(PatchRolesTestCase):
    def test_walks_tasks_and_handlers_only(self):
        tasks_path = "roles/my-role/tasks/main.yml"
        handlers_path = "roles/my-role/handlers/main.yml"
        vars_path = "roles/my-role/vars/main.yml"

        self._write(
            tasks_path,
            "---\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n",
        )
        self._write(
            handlers_path,
            "---\n"
            "- name: restart audit rules\n"
            "  ansible.builtin.command: augenrules --load\n",
        )
        self._write(
            vars_path,
            "---\n"
            "- name: start clamav\n"
            "  ansible.builtin.service:\n"
            "    name: clamav\n"
            "    state: started\n"
            "    enabled: true\n",
        )

        patch_roles.patch_all_roles()

        self.assertIn("ignore_errors:", self._read(tasks_path))
        self.assertIn("ignore_errors:", self._read(handlers_path))
        # vars/ files must never be treated as tasks/handlers, even if they
        # happen to contain service-like content.
        self.assertNotIn("ignore_errors:", self._read(vars_path))

    def test_no_roles_directory_does_not_raise(self):
        # cwd has no "roles" subdirectory at all.
        try:
            patch_roles.patch_all_roles()
        except Exception as exc:  # pragma: no cover - defensive
            self.fail(f"patch_all_roles() raised unexpectedly: {exc}")

    def test_multiple_roles_are_all_patched(self):
        for role in ("role-a", "role-b"):
            self._write(
                f"roles/{role}/tasks/main.yml",
                "---\n"
                "- name: start auditd\n"
                "  ansible.builtin.service:\n"
                "    name: auditd\n"
                "    state: started\n"
                "    enabled: true\n",
            )
        patch_roles.patch_all_roles()
        for role in ("role-a", "role-b"):
            self.assertIn("ignore_errors:", self._read(f"roles/{role}/tasks/main.yml"))

    def test_git_metadata_directory_is_skipped(self):
        # A tasks-shaped file living under a nested ".git" path must never be
        # touched, even though its path contains "/tasks/".
        git_path = "roles/.git/tasks/main.yml"
        original = (
            "---\n"
            "- name: start auditd\n"
            "  ansible.builtin.service:\n"
            "    name: auditd\n"
            "    state: started\n"
            "    enabled: true\n"
        )
        self._write(git_path, original)
        patch_roles.patch_all_roles()
        self.assertEqual(self._read(git_path), original)


if __name__ == "__main__":
    unittest.main()