#!/usr/bin/env python3
"""
Regression tests for .github/workflows/sync-docs.yml.

This PR introduces the "Mintlify One-Way Docs Sync & Safety Guards Pipeline"
GitHub Actions workflow, which compiles Markdown into Mintlify MDX via
`tools/build_mintlify_mdx.py` and then synchronizes `docs-source/` to a
downstream Mintlify docs repository via `scripts/sync_docs.py`, guarded by
5 strict safety guards (see AGENTS.md).

These tests parse the workflow file with a real YAML loader (the same
family GitHub Actions itself uses) and verify:
  1. The file loads as valid YAML.
  2. The `push` trigger targets the `main` branch and watches the expected
     set of paths (docs/, docs-source/, agent skills, and the two pipeline
     scripts themselves).
  3. The `workflow_dispatch` manual trigger exposes the four expected
     inputs (`dry_run`, `allow_large_deletions`, `min_mdx_files`,
     `max_deletions`) with their documented types and defaults.
  4. The single job builds MDX and then runs the hardened sync script,
     wiring each `workflow_dispatch` input to the correct environment
     variable with a safe fallback default via the `||` operator.
  5. PyYAML's well-known YAML 1.1 boolean quirk (the bare `on:` key is
     resolved to the boolean `True`, not the string `"on"`) is accounted
     for when navigating the parsed structure.

Run with:
    python3 -m unittest tests/test_sync_docs_workflow.py -v
"""
import os
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "sync-docs.yml")


class TestSyncDocsWorkflow(unittest.TestCase):
    """Verify the Mintlify docs sync GitHub Actions workflow definition."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()
        cls.data = yaml.safe_load(cls.raw_content)

    def test_workflow_file_is_valid_yaml(self) -> None:
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(
                f".github/workflows/sync-docs.yml must be valid YAML, "
                f"but failed to parse: {exc}"
            )
        self.assertIsInstance(data, dict)

    def test_workflow_name(self) -> None:
        self.assertEqual(
            self.data.get("name"), "Mintlify One-Way Docs Sync & Safety Guards Pipeline"
        )

    def _get_on_block(self) -> dict:
        # PyYAML resolves the bare scalar key `on` to the boolean True under
        # YAML 1.1 core schema rules, not the string "on". GitHub Actions
        # workflow files rely on this key, so tests must look it up the same
        # way a real parse would produce it.
        self.assertIn(
            True,
            self.data,
            "Expected the YAML 1.1 boolean-resolved 'on' key (True) in the "
            "parsed workflow; the parser behavior may have changed.",
        )
        self.assertNotIn(
            "on",
            self.data,
            "Did not expect a literal string 'on' key; PyYAML should have "
            "resolved the bare 'on:' scalar to the boolean True.",
        )
        return self.data[True]

    def test_push_trigger_branches_is_main(self) -> None:
        on_block = self._get_on_block()
        self.assertIn("push", on_block)
        self.assertIn("branches", on_block["push"])
        self.assertEqual(on_block["push"]["branches"], ["main"])

    def test_push_trigger_paths_include_expected_entries(self) -> None:
        on_block = self._get_on_block()
        expected_paths = {
            "docs/**",
            "docs-source/**",
            ".agents/skills/**",
            "skills/**",
            "tools/build_mintlify_mdx.py",
            "scripts/sync_docs.py",
        }
        actual_paths = set(on_block["push"].get("paths", []))
        self.assertEqual(actual_paths, expected_paths)

    def test_workflow_dispatch_inputs_present_with_expected_shape(self) -> None:
        on_block = self._get_on_block()
        self.assertIn("workflow_dispatch", on_block)
        inputs = on_block["workflow_dispatch"].get("inputs", {})

        expected_inputs = {
            "dry_run": {"type": "boolean", "default": True},
            "allow_large_deletions": {"type": "boolean", "default": False},
            "min_mdx_files": {"type": "string", "default": "5"},
            "max_deletions": {"type": "string", "default": "10"},
        }
        self.assertEqual(set(inputs.keys()), set(expected_inputs.keys()))
        for name, expected in expected_inputs.items():
            with self.subTest(input=name):
                self.assertEqual(inputs[name]["type"], expected["type"])
                self.assertEqual(inputs[name]["default"], expected["default"])
                self.assertIn("description", inputs[name])
                self.assertTrue(inputs[name]["description"].strip())

    def _get_sync_job(self) -> dict:
        jobs = self.data.get("jobs", {})
        self.assertIn("sync-mintlify-docs", jobs)
        return jobs["sync-mintlify-docs"]

    def test_job_runs_on_ubuntu_latest(self) -> None:
        job = self._get_sync_job()
        self.assertEqual(job.get("runs-on"), "ubuntu-latest")
        self.assertEqual(job.get("name"), "Build MDX & Sync Mintlify Docs")

    def _get_steps(self) -> list:
        return self._get_sync_job().get("steps", [])

    def test_checkout_step_uses_full_history(self) -> None:
        steps = self._get_steps()
        checkout_steps = [s for s in steps if s.get("uses", "").startswith("actions/checkout")]
        self.assertEqual(len(checkout_steps), 1)
        checkout_step = checkout_steps[0]
        self.assertEqual(checkout_step["with"].get("fetch-depth"), 0)

    def test_python_setup_step_pins_python_3_11(self) -> None:
        steps = self._get_steps()
        setup_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/setup-python")
        ]
        self.assertEqual(len(setup_steps), 1)
        self.assertEqual(setup_steps[0]["with"].get("python-version"), "3.11")

    def test_dependencies_step_installs_pyyaml(self) -> None:
        steps = self._get_steps()
        install_steps = [s for s in steps if s.get("name") == "Install Dependencies"]
        self.assertEqual(len(install_steps), 1)
        self.assertIn("pip install pyyaml", install_steps[0]["run"])

    def test_build_mdx_step_invokes_compiler(self) -> None:
        steps = self._get_steps()
        build_steps = [
            s for s in steps if s.get("name") == "Compile Markdown to Mintlify MDX"
        ]
        self.assertEqual(len(build_steps), 1)
        self.assertIn("python tools/build_mintlify_mdx.py", build_steps[0]["run"])

    def test_sync_step_invokes_guarded_sync_script(self) -> None:
        steps = self._get_steps()
        sync_steps = [
            s
            for s in steps
            if s.get("name") == "Execute Hardened One-Way Docs Sync with Safety Guards"
        ]
        self.assertEqual(len(sync_steps), 1)
        self.assertIn("python scripts/sync_docs.py", sync_steps[0]["run"])

    def test_sync_step_env_maps_dispatch_inputs_with_safe_fallbacks(self) -> None:
        # Each env var must reference the corresponding workflow_dispatch
        # input and fall back to a safe default via the `||` operator, so
        # that ordinary `push` events (which have no `github.event.inputs`)
        # still run the sync script with sane guard values.
        steps = self._get_steps()
        sync_steps = [
            s
            for s in steps
            if s.get("name") == "Execute Hardened One-Way Docs Sync with Safety Guards"
        ]
        env = sync_steps[0].get("env", {})

        self.assertEqual(env.get("DOCS_REPO_TOKEN"), "${{ secrets.DOCS_REPO_TOKEN }}")
        self.assertEqual(
            env.get("DRY_RUN"), "${{ github.event.inputs.dry_run || 'false' }}"
        )
        self.assertEqual(
            env.get("ALLOW_LARGE_DELETIONS"),
            "${{ github.event.inputs.allow_large_deletions || 'false' }}",
        )
        self.assertEqual(
            env.get("MIN_MDX_FILES"),
            "${{ github.event.inputs.min_mdx_files || '5' }}",
        )
        self.assertEqual(
            env.get("MAX_DELETIONS"),
            "${{ github.event.inputs.max_deletions || '10' }}",
        )

    def test_steps_execute_in_documented_order(self) -> None:
        # Regression guard: the compiler must run before the sync script,
        # since the sync script consumes the MDX output the compiler
        # produces in docs-source/.
        steps = self._get_steps()
        names = [s.get("name") for s in steps]
        build_index = names.index("Compile Markdown to Mintlify MDX")
        sync_index = names.index(
            "Execute Hardened One-Way Docs Sync with Safety Guards"
        )
        self.assertLess(
            build_index,
            sync_index,
            "The MDX compilation step must run before the docs sync step",
        )

    def test_does_not_force_push(self) -> None:
        # Regression guard aligned with AGENTS.md's "Strict One-Way
        # Directive": this workflow file itself must never invoke a
        # force-push directly.
        self.assertNotIn("--force", self.raw_content)
        self.assertNotIn("push --force", self.raw_content)

    def test_only_one_job_defined(self) -> None:
        jobs = self.data.get("jobs", {})
        self.assertEqual(list(jobs.keys()), ["sync-mintlify-docs"])


if __name__ == "__main__":
    unittest.main()