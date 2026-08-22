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
        title, desc = extract_title_and_description(fm, body, "Fallback")
        self.assertEqual(title, "FM Title")
        self.assertEqual(desc, "First paragraph here.")

    def test_convert_md_to_mdx(self):
        fm = {"title": "MDX Test", "description": "MDX Desc"}
        body = "Hello Mintlify!"
        mdx = convert_md_to_mdx(fm, body, "Fallback")
        self.assertTrue('title: "MDX Test"' in mdx)
        self.assertTrue('description: "MDX Desc"' in mdx)
        self.assertTrue("Hello Mintlify!" in mdx)

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
