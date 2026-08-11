#!/usr/bin/env python3
"""
Regression tests for docs/_layouts/default.html.

This PR made two related changes to the Jekyll default layout:
  1. The left-hand "Documentation" navigation loop was extended to also
     exclude the new report/checklist pages (output_asimp.md,
     output_lynis.md, output_openscap.md, security_posture_assessment.md)
     from the generic auto-generated documentation link list, in addition
     to the pre-existing exclusions (index.md, README.md).
  2. A new "Reports & SPA" navigation block was added directly below the
     "Documentation" block, containing four explicit links to the HTML
     output of those excluded pages.

These tests parse the raw Liquid/HTML template as text (the same approach
used elsewhere in this test suite for Jekyll markdown front matter) and
verify the exact substrings/ordering introduced by this PR, without
requiring a full Jekyll build.

Run with:
    python3 -m unittest tests/test_docs_layout_default_html.py -v
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LAYOUT_PATH = os.path.join(REPO_ROOT, "docs", "_layouts", "default.html")

NEW_EXCLUDED_PAGES = [
    "output_asimp.md",
    "output_lynis.md",
    "output_openscap.md",
    "security_posture_assessment.md",
]

EXPECTED_REPORT_LINKS = [
    ("/output_asimp.html", "Output of ASIMP"),
    ("/output_lynis.html", "Output of Lynis"),
    ("/output_openscap.html", "Output of OpenSCAP"),
    ("/security_posture_assessment.html", "SPA Requirement Checklist"),
]


class TestDefaultHtmlLayout(unittest.TestCase):
    """Verify docs/_layouts/default.html reflects the new nav filtering and Reports & SPA block."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(DEFAULT_LAYOUT_PATH, "r", encoding="utf-8") as f:
            cls.raw_content = f.read()

    def test_file_exists_and_is_non_empty(self) -> None:
        self.assertTrue(os.path.isfile(DEFAULT_LAYOUT_PATH))
        self.assertGreater(len(self.raw_content), 0)

    def _get_documentation_loop_if_line(self) -> str:
        match = re.search(
            r"\{%\s*if\s+p\.path\s*!=\s*\"index\.md\".*?%\}",
            self.raw_content,
        )
        self.assertIsNotNone(
            match, "Expected to find the documentation loop's Liquid {% if %} condition"
        )
        return match.group(0)

    def test_documentation_loop_still_excludes_pre_existing_pages(self) -> None:
        if_line = self._get_documentation_loop_if_line()
        self.assertIn('p.path != "index.md"', if_line)
        self.assertIn('p.path != "README.md"', if_line)
        self.assertIn('p.path contains ".md"', if_line)

    def test_documentation_loop_excludes_all_new_report_pages(self) -> None:
        if_line = self._get_documentation_loop_if_line()
        for page in NEW_EXCLUDED_PAGES:
            with self.subTest(page=page):
                self.assertIn(
                    f'p.path != "{page}"',
                    if_line,
                    f"Documentation nav loop must exclude {page} to avoid duplicate/awkward auto-generated links",
                )

    def test_documentation_loop_exclusions_are_joined_with_and(self) -> None:
        if_line = self._get_documentation_loop_if_line()
        # Seven conditions total (index.md exclusion, ".md" contains check,
        # README.md exclusion, and the four new report page exclusions) must
        # be combined with 'and' (6 joins), not 'or', so that a page is only
        # rendered when it satisfies every condition simultaneously.
        self.assertEqual(if_line.count(" and "), 6)
        self.assertNotIn(" or ", if_line)

    def test_reports_and_spa_section_heading_present_exactly_once(self) -> None:
        self.assertEqual(self.raw_content.count("<h3>Reports & SPA</h3>"), 1)

    def test_reports_and_spa_links_have_correct_hrefs_and_labels(self) -> None:
        for href_path, label in EXPECTED_REPORT_LINKS:
            expected_snippet = (
                f"<a href=\"{{{{ '{href_path}' | relative_url }}}}\">{label}</a>"
            )
            with self.subTest(href_path=href_path, label=label):
                self.assertIn(
                    expected_snippet,
                    self.raw_content,
                    f"Expected exact Reports & SPA link markup for {href_path} ({label!r})",
                )

    def test_reports_and_spa_links_appear_in_declared_order(self) -> None:
        positions = [
            self.raw_content.index(f"href=\"{{{{ '{href_path}' | relative_url }}}}\"")
            for href_path, _label in EXPECTED_REPORT_LINKS
        ]
        self.assertEqual(positions, sorted(positions))

    def test_reports_and_spa_section_appears_after_documentation_and_before_about_asimp(self) -> None:
        documentation_heading_pos = self.raw_content.index("<h3>Documentation</h3>")
        reports_heading_pos = self.raw_content.index("<h3>Reports & SPA</h3>")
        about_heading_pos = self.raw_content.index("<h3>About ASIMP</h3>")

        self.assertLess(documentation_heading_pos, reports_heading_pos)
        self.assertLess(reports_heading_pos, about_heading_pos)

    def test_reports_and_spa_section_uses_buttonscontainer_wrapper(self) -> None:
        # The new block should follow the same "buttonscontainer" / "buttons"
        # markup convention as the pre-existing Documentation block so that it
        # picks up identical CSS styling.
        reports_heading_pos = self.raw_content.index("<h3>Reports & SPA</h3>")
        preceding_snippet = self.raw_content[max(0, reports_heading_pos - 200):reports_heading_pos]
        self.assertIn('<div class="buttonscontainer">', preceding_snippet)

        following_snippet = self.raw_content[reports_heading_pos:reports_heading_pos + 400]
        self.assertIn('<div class="buttons">', following_snippet)

    def test_pre_existing_sections_still_intact(self) -> None:
        # Sanity check that unrelated parts of the layout were not disturbed
        # by this PR's changes.
        self.assertIn("<h3>About ASIMP</h3>", self.raw_content)
        self.assertIn("<h3>Framework Engines</h3>", self.raw_content)
        self.assertIn('<a href="{{ \'/\' | relative_url }}">Home</a>', self.raw_content)
        self.assertIn("</html>", self.raw_content)

    def test_documentation_loop_condition_is_syntactically_balanced(self) -> None:
        if_line = self._get_documentation_loop_if_line()
        # Every quoted string literal must be properly closed (even count of ").
        self.assertEqual(if_line.count('"') % 2, 0)
        self.assertTrue(if_line.startswith("{% if "))
        self.assertTrue(if_line.endswith("%}"))
        self.assertEqual(if_line.count("!="), 6)


if __name__ == "__main__":
    unittest.main()