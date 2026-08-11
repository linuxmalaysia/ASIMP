#!/usr/bin/env python3
"""
Regression tests for .github/workflows/jekyll-gh-pages.yml.

This PR changed the push trigger of the Jekyll GitHub Pages deploy workflow
from `branches: ["main"]` to `branches: ["master"]`, so that the workflow
actually fires on pushes to this repository's default branch (`master`)
instead of a branch (`main`) that does not exist here and therefore would
have silently never triggered the deploy.

These tests parse the workflow file with a real YAML loader (the same
family GitHub Actions itself uses) and verify:
  1. The file loads as valid YAML (basic sanity check for the whole file).
  2. The `push.branches` trigger list is exactly `["master"]`.
  3. The stale `"main"` branch name is no longer present anywhere in the
     push trigger, guarding against regressing back to the old, non-firing
     configuration.
  4. The unrelated `workflow_dispatch` manual trigger is still present
     alongside the push trigger.
  5. PyYAML's well-known YAML 1.1 boolean quirk (the bare `on:` key is
     resolved to the boolean `True`, not the string `"on"`) is accounted
     for when navigating the parsed structure, so the test itself does not
     silently pass for the wrong reason.

Run with:
    python3 -m unittest tests/test_jekyll_gh_pages_workflow.py -v
"""
import os
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_PATH = os.path.join(
    REPO_ROOT, ".github", "workflows", "jekyll-gh-pages.yml"
)


class TestJekyllGhPagesWorkflow(unittest.TestCase):
    """Verify the Jekyll GitHub Pages deploy workflow's push trigger branch."""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load and parse the Jekyll GitHub Pages workflow for the test class.
        
        Stores the workflow source text and parsed YAML data as class attributes.
        """
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()
        cls.data = yaml.safe_load(cls.raw_content)

    def test_workflow_file_is_valid_yaml(self) -> None:
        # Basic sanity check: the workflow file as a whole must load cleanly.
        try:
            data = yaml.safe_load(self.raw_content)
        except yaml.YAMLError as exc:
            self.fail(
                f".github/workflows/jekyll-gh-pages.yml must be valid YAML, "
                f"but failed to parse: {exc}"
            )
        self.assertIsInstance(data, dict)

    def _get_on_block(self) -> dict:
        # PyYAML resolves the bare scalar key `on` to the boolean True under
        # YAML 1.1 core schema rules (like `y`/`yes`/`no`/`off`), *not* the
        # string "on". GitHub Actions workflow files rely on this key, so
        # tests must look it up the same way a real parse would produce it.
        """
        Retrieve the parsed GitHub Actions trigger configuration.
        
        Returns:
        	dict: The workflow's `on` configuration.
        """
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

    def test_push_trigger_branches_is_master(self) -> None:
        on_block = self._get_on_block()
        self.assertIn("push", on_block)
        self.assertIn("branches", on_block["push"])
        self.assertEqual(on_block["push"]["branches"], ["master"])

    def test_push_trigger_does_not_reference_main_branch(self) -> None:
        # Regression guard: the previous configuration pointed at "main",
        # which does not exist in this repository (whose default branch is
        # "master"), so the workflow would never have run. Ensure "main" is
        # not reintroduced anywhere in the push branch trigger.
        """
        Verify that the push trigger does not include the `main` branch.
        """
        on_block = self._get_on_block()
        self.assertNotIn("main", on_block["push"]["branches"])

    def test_workflow_dispatch_trigger_still_present(self) -> None:
        # The manual dispatch trigger is untouched by this PR and must
        # continue to coexist with the corrected push trigger.
        on_block = self._get_on_block()
        self.assertIn("workflow_dispatch", on_block)

    def test_push_branches_line_is_present_verbatim_in_source(self) -> None:
        # Complements the parsed-structure assertions above with a direct
        # textual check on the exact line changed by this PR.
        self.assertIn('branches: ["master"]', self.raw_content)
        self.assertNotIn('branches: ["main"]', self.raw_content)

    def test_reverting_to_main_would_change_parsed_branches(self) -> None:
        # Demonstrates why this fix matters: reverting the branch name back
        # to "main" changes the parsed trigger away from "master", which
        # would once again silently prevent this workflow from running on
        # pushes to this repository's actual default branch.
        """Verify that reverting the workflow branch configuration to `main` changes the parsed push branches accordingly."""
        reverted_content = self.raw_content.replace(
            'branches: ["master"]', 'branches: ["main"]'
        )
        self.assertNotEqual(
            reverted_content,
            self.raw_content,
            "Test setup failed to locate the branches line to revert",
        )
        reverted_data = yaml.safe_load(reverted_content)
        reverted_branches = reverted_data[True]["push"]["branches"]
        self.assertEqual(reverted_branches, ["main"])
        self.assertNotEqual(reverted_branches, ["master"])


if __name__ == "__main__":
    unittest.main()