#!/usr/bin/env python3
"""
Unit tests for scripts/llms_txt2ctx.py.
Verifies AttrDict, slugify, escape_attr, parse_link, parse_llms_file, and create_ctx functions.
"""

import unittest
from scripts.llms_txt2ctx import AttrDict, slugify, escape_attr, parse_link, parse_llms_file, create_ctx


class TestLlmsTxt2Ctx(unittest.TestCase):
    """Test case for the llms.txt compiler utility functions."""

    def test_attr_dict(self) -> None:
        """Test AttrDict allows attribute-style access and nested dictionaries/lists are wrapped."""
        d = AttrDict({
            'title': 'Test Project',
            'summary': 'A simple test project',
            'info': 'Some text info',
            'sections': {
                'Docs': [{'title': 'Link 1', 'url': 'doc1.md', 'desc': 'A test link'}]
            }
        })
        self.assertEqual(d.title, 'Test Project')
        self.assertEqual(d.summary, 'A simple test project')
        self.assertEqual(d.sections.Docs[0].title, 'Link 1')
        self.assertEqual(d.sections.Docs[0].desc, 'A test link')

    def test_slugify(self) -> None:
        """Test that slugify generates clean and valid XML element names."""
        self.assertEqual(slugify('FastHTML quick start'), 'fasthtml-quick-start')
        self.assertEqual(slugify('S1'), 's1')
        self.assertEqual(slugify('3d-graphics'), 'p3d-graphics')
        self.assertEqual(slugify('!@#'), 'page')
        self.assertEqual(slugify('  Nested_Space-Header  '), 'nested-space-header')

    def test_escape_attr(self) -> None:
        """Test escaping XML special characters inside attributes."""
        self.assertEqual(escape_attr('Hello & <World>'), 'Hello &amp; &lt;World&gt;')
        self.assertEqual(escape_attr('"Double" & \'Single\''), '&quot;Double&quot; &amp; &#39;Single&#39;')
        self.assertEqual(escape_attr(''), '')

    def test_parse_link(self) -> None:
        """Test extraction of markdown hyperlink structures."""
        self.assertEqual(
            parse_link('- [Surreal](https://host/README.md): Tiny jQuery alternative'),
            {'title': 'Surreal', 'url': 'https://host/README.md', 'desc': 'Tiny jQuery alternative'}
        )
        self.assertEqual(
            parse_link('* [Surreal](https://host/README.md)'),
            {'title': 'Surreal', 'url': 'https://host/README.md', 'desc': None}
        )
        self.assertEqual(parse_link('No link here'), None)

    def test_parse_llms_file_with_blockquote(self) -> None:
        """Test parsing llms.txt structure that includes a blockquote summary."""
        samp = (
            "# FastHTML\n\n"
            "> FastHTML is a python library for hypermedia apps.\n\n"
            "Remember:\n- Use serve()\n\n"
            "## Docs\n"
            "- [Surreal](https://host/README.md): Tiny jQuery alternative\n"
            "- [Quickstart](https://host/quickstart.md)\n\n"
            "## Optional\n"
            "- [Starlette](https://host/starlette.md): Subset of Starlette docs\n"
        )
        parsed = parse_llms_file(samp)
        self.assertEqual(parsed.title, 'FastHTML')
        self.assertEqual(parsed.summary, 'FastHTML is a python library for hypermedia apps.')
        self.assertEqual(parsed.info, 'Remember:\n- Use serve()')
        self.assertEqual(len(parsed.sections['Docs']), 2)
        self.assertEqual(parsed.sections['Docs'][0]['title'], 'Surreal')
        self.assertEqual(parsed.sections['Docs'][1]['desc'], None)
        self.assertEqual(parsed.sections['Optional'][0]['title'], 'Starlette')

    def test_parse_llms_file_fallback_no_blockquote(self) -> None:
        """Test parsing llms.txt structure that lacks a blockquote summary (falls back to first paragraph)."""
        samp = (
            "# ASIMP\n\n"
            "ASIMP is a security baseline framework.\n\n"
            "It implements measure, harden, re-measure.\n\n"
            "## Docs\n"
            "- [Architecture](docs/architecture.md)\n"
        )
        parsed = parse_llms_file(samp)
        self.assertEqual(parsed.title, 'ASIMP')
        self.assertEqual(parsed.summary, 'ASIMP is a security baseline framework.')
        self.assertEqual(parsed.info, 'It implements measure, harden, re-measure.')
        self.assertEqual(len(parsed.sections['Docs']), 1)

    def test_create_ctx(self) -> None:
        """Test building LLM context XML compilation with optional section filtering."""
        samp = (
            "# My Tool\n"
            "> My short description\n\n"
            "Info about tool\n\n"
            "## Docs\n"
            "- [Arch](docs/architecture.md): design\n\n"
            "## Optional\n"
            "- [Extra](docs/troubleshooting.md)\n"
        )

        # 1. Without optional
        xml_without = create_ctx(samp, optional=False)
        self.assertIn('<project title="My Tool" summary="My short description">', xml_without)
        self.assertIn('Info about tool', xml_without)
        self.assertIn('<docs>', xml_without)
        self.assertIn('<arch url="docs/architecture.md" desc="design">', xml_without)
        self.assertNotIn('<optional>', xml_without)
        self.assertNotIn('<extra', xml_without)

        # 2. With optional
        xml_with = create_ctx(samp, optional=True)
        self.assertIn('<optional>', xml_with)
        self.assertIn('<extra url="docs/troubleshooting.md">', xml_with)


if __name__ == '__main__':
    unittest.main()
