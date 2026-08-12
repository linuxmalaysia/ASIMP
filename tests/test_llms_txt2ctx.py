#!/usr/bin/env python3
"""
Unit tests for scripts/llms_txt2ctx.py.
Verifies AttrDict, slugify, escape_attr, parse_link, parse_llms_file, and create_ctx functions.
"""

import unittest
from scripts.llms_txt2ctx import AttrDict, slugify, escape_attr, parse_link, parse_llms_file, create_ctx
Verifies AttrDict, slugify, escape_attr, parse_link, parse_llms_file, create_ctx,
get_doc_content, and the main() CLI entry point.
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.llms_txt2ctx import (
    AttrDict,
    slugify,
    escape_attr,
    parse_link,
    parse_llms_file,
    create_ctx,
    get_doc_content,
    main,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

    def test_attr_dict_setattr_stores_as_dict_item(self) -> None:
        """Test that attribute assignment on AttrDict is reflected as a dict item."""
        d = AttrDict({'title': 'Initial'})
        d.title = 'Updated'
        d.new_key = 'new_value'
        self.assertEqual(d['title'], 'Updated')
        self.assertEqual(d['new_key'], 'new_value')
        self.assertEqual(d.new_key, 'new_value')

    def test_attr_dict_missing_attribute_raises_attribute_error(self) -> None:
        """Test that accessing an absent key via attribute access raises AttributeError, not KeyError."""
        d = AttrDict({'title': 'Test Project'})
        with self.assertRaises(AttributeError):
            _ = d.does_not_exist

    def test_attr_dict_wraps_list_of_plain_scalars_unchanged(self) -> None:
        """Test that list items which are not dicts are left untouched by AttrDict."""
        d = AttrDict({'tags': ['a', 'b', 'c']})
        self.assertEqual(d.tags, ['a', 'b', 'c'])
        self.assertNotIsInstance(d.tags[0], AttrDict)

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

    def test_escape_attr_falsy_none_returns_empty_string(self) -> None:
        """Test that a None value (falsy) is handled without raising and returns an empty string."""
        self.assertEqual(escape_attr(None), '')

    def test_escape_attr_leaves_plain_text_untouched(self) -> None:
        """Test that text without any special characters is returned unchanged."""
        self.assertEqual(escape_attr('plain text 123'), 'plain text 123')

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

    def test_parse_link_strips_surrounding_whitespace(self) -> None:
        """Test that leading/trailing whitespace around title/url/desc is stripped."""
        self.assertEqual(
            parse_link('  - [  Padded Title  ]( https://host/doc.md )  :   padded desc  '),
            {'title': 'Padded Title', 'url': 'https://host/doc.md', 'desc': 'padded desc'}
        )

    def test_parse_link_rejects_line_without_brackets(self) -> None:
        """Test that a bullet line without a markdown link does not match."""
        self.assertIsNone(parse_link('- Just a plain bullet, no link'))

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

    def test_parse_llms_file_with_no_sections(self) -> None:
        """Test parsing a minimal llms.txt with only a title and blockquote and no '##' sections."""
        samp = "# Solo\n\n> Just a summary line.\n"
        parsed = parse_llms_file(samp)
        self.assertEqual(parsed.title, 'Solo')
        self.assertEqual(parsed.summary, 'Just a summary line.')
        self.assertEqual(parsed.info, '')
        self.assertEqual(parsed.sections, {})

    def test_parse_llms_file_with_no_title(self) -> None:
        """Test parsing text lacking an H1 title results in an empty title and no info/summary."""
        samp = "Just some text with no headers at all.\n"
        parsed = parse_llms_file(samp)
        self.assertEqual(parsed.title, '')
        self.assertEqual(parsed.summary, '')
        self.assertEqual(parsed.info, '')

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

    def test_create_ctx_link_without_description_omits_desc_attribute(self) -> None:
        """Test that a link with no ': description' suffix produces no desc attribute in the output tag."""
        samp = (
            "# NoDesc\n"
            "> Summary here\n\n"
            "## Docs\n"
            "- [Quickstart](https://host/quickstart.md)\n"
        )
        xml_output = create_ctx(samp)
        self.assertIn('<quickstart url="https://host/quickstart.md">', xml_output)
        self.assertNotIn('desc=', xml_output)

    def test_create_ctx_embeds_remote_content_skip_placeholder(self) -> None:
        """Test that remote (http/https) links embed the 'Remote content skipped' placeholder comment."""
        samp = (
            "# Remote\n"
            "> Summary\n\n"
            "## Docs\n"
            "- [External](https://example.com/docs.md)\n"
        )
        xml_output = create_ctx(samp)
        self.assertIn('<!-- Remote content skipped: https://example.com/docs.md -->', xml_output)

    def test_create_ctx_embeds_file_not_found_placeholder_for_missing_local_file(self) -> None:
        """Test that a local link pointing at a non-existent file embeds the 'File not found' placeholder."""
        samp = (
            "# Missing\n"
            "> Summary\n\n"
            "## Docs\n"
            "- [Ghost](this/path/does/not/exist.md)\n"
        )
        xml_output = create_ctx(samp)
        self.assertIn('<!-- File not found: this/path/does/not/exist.md -->', xml_output)

    def test_create_ctx_with_multiple_sections_preserves_all_section_tags(self) -> None:
        """Test that multiple non-Optional sections each get their own slugified XML tag."""
        samp = (
            "# Multi\n"
            "> Summary\n\n"
            "## Getting Started\n"
            "- [Setup](https://host/setup.md)\n\n"
            "## API Reference\n"
            "- [Endpoints](https://host/endpoints.md)\n"
        )
        xml_output = create_ctx(samp)
        self.assertIn('<getting-started>', xml_output)
        self.assertIn('</getting-started>', xml_output)
        self.assertIn('<api-reference>', xml_output)
        self.assertIn('</api-reference>', xml_output)


class TestGetDocContent(unittest.TestCase):
    """Test case for the get_doc_content() helper function."""

    def test_remote_http_url_returns_skip_placeholder_without_network_access(self) -> None:
        """Test that http:// URLs are never fetched and instead return a skip placeholder."""
        result = get_doc_content('http://example.com/readme.md')
        self.assertEqual(result, '<!-- Remote content skipped: http://example.com/readme.md -->')

    def test_remote_https_url_returns_skip_placeholder_without_network_access(self) -> None:
        """Test that https:// URLs are never fetched and instead return a skip placeholder."""
        result = get_doc_content('https://example.com/readme.md')
        self.assertEqual(result, '<!-- Remote content skipped: https://example.com/readme.md -->')

    def test_missing_local_file_returns_not_found_placeholder(self) -> None:
        """Test that a local path with no corresponding file returns a 'File not found' placeholder."""
        result = get_doc_content('definitely/does/not/exist.md')
        self.assertEqual(result, '<!-- File not found: definitely/does/not/exist.md -->')

    def test_existing_local_file_returns_its_full_contents(self) -> None:
        """Test that an existing repo-relative file (the newly added .gitbook.yaml) is read verbatim."""
        expected_path = os.path.join(REPO_ROOT, '.gitbook.yaml')
        with open(expected_path, 'r', encoding='utf-8') as f:
            expected_content = f.read()
        result = get_doc_content('.gitbook.yaml')
        self.assertEqual(result, expected_content)

    def test_read_error_returns_error_placeholder(self) -> None:
        """Test that an exception raised while reading an existing file is caught and reported as a placeholder."""
        with patch('scripts.llms_txt2ctx.open', side_effect=OSError('boom'), create=True):
            result = get_doc_content('.gitbook.yaml')
        self.assertEqual(result, '<!-- Error reading file .gitbook.yaml: boom -->')


class TestMainCli(unittest.TestCase):
    """Test case for the main() command-line entry point."""

    def _run_main_with_argv(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(sys, 'argv', argv), \
                contextlib.redirect_stdout(stdout), \
                contextlib.redirect_stderr(stderr):
            try:
                main()
                exit_code = 0
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_no_arguments_prints_usage_and_exits_nonzero(self) -> None:
        """Test that running with no input file argument prints usage to stderr and exits with status 1."""
        exit_code, stdout, stderr = self._run_main_with_argv(['llms_txt2ctx.py'])
        self.assertEqual(exit_code, 1)
        self.assertIn('Usage:', stderr)
        self.assertEqual(stdout, '')

    def test_help_flag_prints_usage_and_exits_nonzero(self) -> None:
        """Test that -h/--help prints usage to stderr and exits with status 1 instead of processing a file."""
        exit_code, _, stderr = self._run_main_with_argv(['llms_txt2ctx.py', '--help'])
        self.assertEqual(exit_code, 1)
        self.assertIn('Usage:', stderr)

    def test_nonexistent_input_file_prints_error_and_exits_nonzero(self) -> None:
        """Test that a missing input file path prints an error to stderr and exits with status 1."""
        exit_code, stdout, stderr = self._run_main_with_argv(
            ['llms_txt2ctx.py', 'this/file/does/not/exist.txt']
        )
        self.assertEqual(exit_code, 1)
        self.assertIn('Error: File not found', stderr)
        self.assertEqual(stdout, '')

    def test_valid_input_file_prints_xml_to_stdout(self) -> None:
        """Test that a valid llms.txt input file produces XML output on stdout without raising."""

        content = "# Tool\n> A short summary\n\n## Docs\n- [Guide](https://host/guide.md)\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            exit_code, stdout, stderr = self._run_main_with_argv(['llms_txt2ctx.py', tmp_path])
        finally:
            os.remove(tmp_path)
        self.assertEqual(exit_code, 0)
        self.assertIn('<project title="Tool" summary="A short summary">', stdout)
        self.assertEqual(stderr, '')

    def test_optional_flag_true_variants_include_optional_section(self) -> None:
        """Test that --optional and --optional=true both cause the Optional section to be emitted."""

        content = (
            "# Tool\n> Summary\n\n"
            "## Docs\n- [Guide](https://host/guide.md)\n\n"
            "## Optional\n- [Extra](https://host/extra.md)\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            for flag in ('--optional', '--optional=true', '--optional=1', '--optional=yes'):
                exit_code, stdout, _ = self._run_main_with_argv(['llms_txt2ctx.py', tmp_path, flag])
                self.assertEqual(exit_code, 0)
                self.assertIn('<optional>', stdout, f"flag {flag!r} should include the Optional section")
        finally:
            os.remove(tmp_path)

    def test_optional_flag_false_or_absent_excludes_optional_section(self) -> None:
        """Test that omitting --optional (or passing an explicit falsy value) excludes the Optional section."""

        content = (
            "# Tool\n> Summary\n\n"
            "## Docs\n- [Guide](https://host/guide.md)\n\n"
            "## Optional\n- [Extra](https://host/extra.md)\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            exit_code, stdout, _ = self._run_main_with_argv(['llms_txt2ctx.py', tmp_path])
            self.assertEqual(exit_code, 0)
            self.assertNotIn('<optional>', stdout)

            exit_code, stdout, _ = self._run_main_with_argv(
                ['llms_txt2ctx.py', tmp_path, '--optional=false']
            )
            self.assertEqual(exit_code, 0)
            self.assertNotIn('<optional>', stdout)
        finally:
            os.remove(tmp_path)


if __name__ == '__main__':
    unittest.main()
