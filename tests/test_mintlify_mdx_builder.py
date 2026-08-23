"""Unit tests for tools/build_mintlify_mdx.py."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.build_mintlify_mdx import (
    build_docs_json,
    categorize_page,
    convert_md_to_mdx,
    extract_title_and_description,
    parse_frontmatter,
    synthesize_sidebar_title,
)


class TestMintlifyMDXBuilder(unittest.TestCase):
    """Test MDX compilation, frontmatter parsing, and docs.json assembly."""

    def test_parse_frontmatter_valid(self):
        content = "---\ntitle: 'Test Title'\ndescription: 'Test Desc'\n---\n# Body Title\nBody content."
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm.get("title"), "Test Title")
        self.assertEqual(fm.get("description"), "Test Desc")
        self.assertTrue("Body content." in body)

    def test_parse_frontmatter_missing(self):
        content = "# Just Heading\nSome content without frontmatter."
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm, {})
        self.assertEqual(body, content)

    def test_extract_title_and_description(self):
        fm = {"title": "FM Title"}
        body = "# Header Title\nFirst paragraph here."
        title, sidebar, desc = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(title, "FM Title")
        self.assertEqual(sidebar, "Fm Title")
        self.assertEqual(desc, "First paragraph here.")

    def test_extract_title_and_description_explicit_sidebar_title(self):
        fm = {"title": "Full Page Title", "sidebarTitle": "Custom Sidebar"}
        body = "Body content."
        title, sidebar, desc = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(title, "Full Page Title")
        self.assertEqual(sidebar, "Custom Sidebar")

    def test_convert_md_to_mdx(self):
        fm = {"title": "MDX Test", "description": "MDX Desc"}
        body = "Hello Mintlify!"
        mdx = convert_md_to_mdx(fm, body, "Fallback")
        self.assertTrue('title: "MDX Test"' in mdx)
        self.assertTrue('sidebarTitle: "Mdx Test"' in mdx)
        self.assertTrue('description: "MDX Desc"' in mdx)
        self.assertTrue("Hello Mintlify!" in mdx)

    def test_convert_md_to_mdx_explicit_sidebar_title(self):
        fm = {"title": "MDX Test", "sidebarTitle": "Explicit Label", "description": "MDX Desc"}
        body = "Hello Mintlify!"
        mdx = convert_md_to_mdx(fm, body, "Fallback")
        self.assertTrue('sidebarTitle: "Explicit Label"' in mdx)
    def test_synthesize_sidebar_title_short_title_unchanged(self):
        self.assertEqual(synthesize_sidebar_title("Architecture & Design"), "Architecture & Design")

    def test_synthesize_sidebar_title_strips_product_name(self):
        self.assertEqual(
            synthesize_sidebar_title("ASIMP Local Testing Matrix & Telemetry Spec"),
            "Local Testing Matrix",
        )

    def test_synthesize_sidebar_title_strips_product_name_case_insensitive(self):
        self.assertEqual(
            synthesize_sidebar_title("asimp Local Testing Matrix"),
            "Local Testing Matrix",
        )

    def test_synthesize_sidebar_title_trims_after_colon(self):
        self.assertEqual(
            synthesize_sidebar_title("Review & Adoption of DSOM Ansible Configuration Guide (v3.6.2): Notes"),
            "Review & Adoption",
        )

    def test_synthesize_sidebar_title_trims_after_dash(self):
        self.assertEqual(
            synthesize_sidebar_title("Jekyll Pre-processor Reference"),
            "Jekyll Pre",
        )

    def test_synthesize_sidebar_title_limits_to_three_words(self):
        result = synthesize_sidebar_title("Ansible Best Practices & FQCN Standards")
        self.assertEqual(result, "Ansible Best Practices")
        self.assertLessEqual(len(result.split()), 3)

    def test_synthesize_sidebar_title_falls_back_when_stripped_title_empty(self):
        # Title consisting solely of the product name has nothing left after
        # stripping "ASIMP", so the function must fall back to the original
        # (unstripped) title's words instead of returning an empty string.
        self.assertEqual(synthesize_sidebar_title("ASIMP"), "Asimp")

    def test_synthesize_sidebar_title_preserves_non_alpha_characters(self):
        self.assertEqual(
            synthesize_sidebar_title("SUSE/SLED Sysctl Hardening Role Reference"),
            "Suse/Sled Sysctl Hardening",
        )

    def test_synthesize_sidebar_title_preserves_unicode_characters(self):
        self.assertEqual(
            synthesize_sidebar_title("Di\u00e1taxis Documentation Framework"),
            "Di\u00e1taxis Documentation Framework",
        )

    def test_extract_title_and_description_preserves_existing_sidebar_title(self):
        fm = {"title": "FM Title", "sidebarTitle": "Custom Sidebar"}
        body = "First paragraph here."
        _, sidebar, _ = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(sidebar, "Custom Sidebar")

    def test_extract_title_and_description_synthesizes_when_sidebar_title_empty_string(self):
        fm = {"title": "ASIMP Rootless Podman Orchestration", "sidebarTitle": ""}
        body = "Body content."
        _, sidebar, _ = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(sidebar, "Rootless Podman Orchestration")

    def test_extract_title_and_description_synthesizes_from_derived_title(self):
        # No title provided in frontmatter or fallback needed: title should be
        # derived from the first H1, and the sidebar title synthesized from it.
        fm = {}
        body = "# ASIMP Quickstart Onboarding Guide\nSome intro text."
        title, sidebar, _ = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(title, "ASIMP Quickstart Onboarding Guide")
        self.assertEqual(sidebar, "Quickstart Onboarding Guide")

    def test_convert_md_to_mdx_uses_frontmatter_sidebar_title(self):
        fm = {"title": "MDX Test", "sidebarTitle": "Custom Label", "description": "MDX Desc"}
        body = "Hello Mintlify!"
        mdx = convert_md_to_mdx(fm, body, "Fallback")
        self.assertTrue('sidebarTitle: "Custom Label"' in mdx)

    def test_convert_md_to_mdx_escapes_quotes_in_sidebar_title(self):
        fm = {"title": 'ASIMP "Measure, Harden, Re-Measure" Core Workflow'}
        body = "Body text."
        mdx = convert_md_to_mdx(fm, body, "Fallback")
        # json.dumps must escape the embedded double quotes so the resulting
        # frontmatter remains valid YAML/JSON.
        self.assertIn('sidebarTitle: "\\"Measure, Harden, Re"', mdx)

    def test_categorize_page(self):
        self.assertEqual(categorize_page("tutorials/01-start"), "Tutorials")
        self.assertEqual(categorize_page("how-to/run-tool"), "How-To Guides")
        self.assertEqual(categorize_page("reference/playbooks"), "Reference")
        self.assertEqual(categorize_page("explanation/diataxis"), "Explanation & Architecture")
        self.assertEqual(categorize_page("skills/asimp-workflow"), "Agent Skills")
        self.assertEqual(categorize_page("openscap"), "Security Engines & Auditing")
        self.assertEqual(categorize_page("architecture"), "Core Architecture & Config")
        self.assertEqual(categorize_page("ai_agents"), "Governance & AI Protocol")
        self.assertEqual(categorize_page("README"), "Get Started")

    def test_build_docs_json(self):
        pages = ["README", "tutorials/01-start", "reference/playbooks"]
        config = build_docs_json(pages)
        self.assertEqual(config["$schema"], "https://mintlify.com/docs.json")
        self.assertEqual(config["theme"], "aspen")
        nav_tabs = config["navigation"]["tabs"]
        self.assertEqual(len(nav_tabs), 1)
        groups = nav_tabs[0]["groups"]
        group_names = [g["group"] for g in groups]
        self.assertIn("Get Started", group_names)
        self.assertIn("Tutorials", group_names)
        self.assertIn("Reference", group_names)


if __name__ == "__main__":
    unittest.main()
