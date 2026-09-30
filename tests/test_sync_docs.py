"""Unit tests for scripts/sync_docs.py safety guards A through E."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
import subprocess
from unittest.mock import patch

from scripts.sync_docs import (
    run_cmd,
    guard_a_source_and_json_integrity,
    guard_b_minimum_file_count_floor,
    guard_c_navigation_integrity,
    guard_d_diff_preview_and_deletion_cap,
)


class TestSyncDocsGuards(unittest.TestCase):
    """Validate 5 safety guards under pass and fail scenarios."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.docs_source = Path(self.test_dir) / "docs-source"
        self.docs_source.mkdir()

        self.downstream = Path(self.test_dir) / "downstream"
        self.downstream.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_guard_a_success(self):
        docs_json = self.docs_source / "docs.json"
        docs_json.write_text(json.dumps({"test": "ok"}), encoding="utf-8")
        data = guard_a_source_and_json_integrity(self.docs_source)
        self.assertEqual(data.get("test"), "ok")

    def test_guard_a_missing_dir(self):
        missing_dir = Path(self.test_dir) / "nonexistent"
        with self.assertRaises(SystemExit):
            guard_a_source_and_json_integrity(missing_dir)

    def test_guard_a_preserves_nested_json_and_unicode(self):
        expected = {
            "name": "Documentation – sécurité",
            "navigation": {"tabs": [{"pages": ["index", "skills/example"]}]},
            "enabled": False,
            "count": 0,
            "optional": None,
        }
        (self.docs_source / "docs.json").write_text(
            json.dumps(expected, ensure_ascii=False), encoding="utf-8"
        )
        self.assertEqual(guard_a_source_and_json_integrity(self.docs_source), expected)

    def test_guard_a_missing_json_exits_with_failure(self):
        with self.assertRaises(SystemExit) as raised:
            guard_a_source_and_json_integrity(self.docs_source)
        self.assertEqual(raised.exception.code, 1)

    def test_guard_a_unreadable_json_exits_with_failure(self):
        (self.docs_source / "docs.json").mkdir()
        with self.assertRaises(SystemExit) as raised:
            guard_a_source_and_json_integrity(self.docs_source)
        self.assertEqual(raised.exception.code, 1)

    def test_guard_a_invalid_utf8_exits_with_failure(self):
        (self.docs_source / "docs.json").write_bytes(b'{"name": "\xff"}')
        with self.assertRaises(SystemExit) as raised:
            guard_a_source_and_json_integrity(self.docs_source)
        self.assertEqual(raised.exception.code, 1)

    def test_guard_a_invalid_json(self):
        docs_json = self.docs_source / "docs.json"
        docs_json.write_text("INVALID JSON", encoding="utf-8")
        with self.assertRaises(SystemExit):
            guard_a_source_and_json_integrity(self.docs_source)

    def test_guard_b_success(self):
        for i in range(5):
            (self.docs_source / f"file_{i}.mdx").write_text("content", encoding="utf-8")
        files = guard_b_minimum_file_count_floor(self.docs_source, min_mdx_files=5)
        self.assertEqual(len(files), 5)

    def test_guard_b_fail_below_floor(self):
        for i in range(3):
            (self.docs_source / f"file_{i}.mdx").write_text("content", encoding="utf-8")
        with self.assertRaises(SystemExit):
            guard_b_minimum_file_count_floor(self.docs_source, min_mdx_files=5)

    def test_guard_c_success(self):
        (self.docs_source / "page1.mdx").write_text("p1", encoding="utf-8")
        (self.docs_source / "page2.mdx").write_text("p2", encoding="utf-8")

        docs_data = {
            "navigation": {
                "tabs": [
                    {
                        "tab": "Test",
                        "groups": [
                            {"group": "G1", "pages": ["page1", "page2"]}
                        ]
                    }
                ]
            }
        }
        # Should pass without raising SystemExit
        guard_c_navigation_integrity(self.docs_source, docs_data)

    def test_guard_c_missing_page(self):
        (self.docs_source / "page1.mdx").write_text("p1", encoding="utf-8")

        docs_data = {
            "navigation": {
                "tabs": [
                    {
                        "tab": "Test",
                        "groups": [
                            {"group": "G1", "pages": ["page1", "missing_page"]}
                        ]
                    }
                ]
            }
        }
        with self.assertRaises(SystemExit):
            guard_c_navigation_integrity(self.docs_source, docs_data)

    def test_guard_d_success_and_fail(self):
        # Setup downstream with 12 files
        for i in range(12):
            (self.downstream / f"old_{i}.mdx").write_text("old", encoding="utf-8")

        # Setup docs_source with 1 file (so 12 deletions)
        (self.docs_source / "new.mdx").write_text("new", encoding="utf-8")

        # Should fail with max_deletions=10 and allow_large_deletions=False
        with self.assertRaises(SystemExit):
            guard_d_diff_preview_and_deletion_cap(
                self.docs_source, self.downstream, max_deletions=10, allow_large_deletions=False
            )

        # Should pass when allow_large_deletions=True
        added, modified, deleted = guard_d_diff_preview_and_deletion_cap(
            self.docs_source, self.downstream, max_deletions=10, allow_large_deletions=True
        )
        self.assertEqual(len(deleted), 12)
        self.assertEqual(len(added), 1)


class TestRunCmd(unittest.TestCase):
    """Optional subprocess arguments must retain their runtime semantics."""

    @patch("scripts.sync_docs.subprocess.run")
    def test_omitted_and_explicit_none_options_inherit_process_context(self, mock_run):
        command = ["example", "argument with spaces"]
        mock_run.return_value = subprocess.CompletedProcess(command, 0, "résultat\n", "")
        for options in ({}, {"cwd": None, "env": None}):
            with self.subTest(options=options):
                mock_run.reset_mock()
                self.assertEqual(run_cmd(command, **options), (0, "résultat\n", ""))
                mock_run.assert_called_once_with(
                    command, cwd=None, env=None, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                )

    @patch("scripts.sync_docs.subprocess.run")
    def test_explicit_path_and_environment_are_forwarded_even_when_empty(self, mock_run):
        command = ["example", "literal; argument"]
        cwd = Path("working directory")
        mock_run.return_value = subprocess.CompletedProcess(command, 7, "partial\n", "failure\n")
        for env in ({}, {"LANG": "C.UTF-8"}):
            with self.subTest(env=env):
                self.assertEqual(run_cmd(command, cwd=cwd, env=env), (7, "partial\n", "failure\n"))
                self.assertEqual(mock_run.call_args.args, (command,))
                self.assertEqual(mock_run.call_args.kwargs["cwd"], cwd)
                self.assertIs(mock_run.call_args.kwargs["env"], env)

    @patch("scripts.sync_docs.subprocess.run", side_effect=FileNotFoundError("missing executable"))
    def test_launch_failure_is_propagated(self, mock_run):
        with self.assertRaises(FileNotFoundError):
            run_cmd(["missing-executable"])
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
