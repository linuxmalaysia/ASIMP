#!/usr/bin/env python3
"""
llms.txt to XML Context Parser and Compiler
Provides a Python API and CLI to parse an llms.txt file and build an XML context
representation suitable for LLMs (such as Anthropic Claude) according to the
specification detailed in https://llmstxt.org/intro.html.
"""

import os
import re
import sys
from typing import Dict, Any, List, Tuple, Optional


class AttrDict(dict):
    """A dictionary subclass that allows attribute-style access to its keys."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = AttrDict(v)
            elif isinstance(v, list):
                self[k] = [AttrDict(i) if isinstance(i, dict) else i for i in v]

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def slugify(title: str) -> str:
    """Convert a title string into a valid, clean XML tag name.

    Args:
        title: The input title string.

    Returns:
        A lowercased, hyphenated alphanumeric string safe for XML tag names.
    """
    s: str = title.strip().lower()
    s = re.sub(r'[^a-z0-9\-]', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    if not s:
        return 'page'
    if s[0].isdigit():
        return 'p' + s
    return s


def escape_attr(val: str) -> str:
    """Escape special characters for use in XML attribute values.

    Args:
        val: The raw attribute string.

    Returns:
        A serialized XML-safe attribute string.
    """
    if not val:
        return ""
    val = val.replace('&', '&amp;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    val = val.replace('"', '&quot;')
    val = val.replace("'", '&#39;')
    return val


def escape_text(val: str) -> str:
    """Escape special characters for use in XML tag text bodies.

    Args:
        val: The raw text string.

    Returns:
        An XML-safe text body string.
    """
    if not val:
        return ""
    val = val.replace('&', '&amp;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    return val


def parse_link(line: str) -> Optional[Dict[str, Optional[str]]]:
    """Parse a single markdown list line containing a hyperlink and optional description.

    Args:
        line: The raw markdown list line.

    Returns:
        A dictionary with keys 'title', 'url', 'desc' if matched, otherwise None.
    """
    # Regex matching optional list bullets, then a markdown link [title](url) followed optionally by : description
    match = re.match(r'^\s*[-\*]\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*:\s*(.*))?$', line.strip())
    if match:
        title = match.group(1).strip()
        url = match.group(2).strip()
        desc = match.group(3).strip() if match.group(3) else None
        return {
            'title': title,
            'url': url,
            'desc': desc
        }
    return None


def parse_llms_file(txt: str) -> AttrDict:
    """Parse the raw content of an llms.txt file into a structured AttrDict object.

    Args:
        txt: The raw string content of the llms.txt file.

    Returns:
        An AttrDict containing 'title', 'summary', 'info', and 'sections'.
    """
    # Split text into introduction and sections using H2 headers
    parts: List[str] = re.split(r'^##\s*(.*?)$', txt, flags=re.MULTILINE)
    intro_part: str = parts[0].strip()

    sections: Dict[str, List[Dict[str, Optional[str]]]] = {}
    for i in range(1, len(parts), 2):
        sec_name: str = parts[i].strip()
        sec_content: str = parts[i + 1] if i + 1 < len(parts) else ""

        links: List[Dict[str, Optional[str]]] = []
        for line in sec_content.split('\n'):
            parsed_lnk = parse_link(line)
            if parsed_lnk:
                links.append(parsed_lnk)
        sections[sec_name] = links

    # Extract H1 title and summary/info blocks from intro_part
    title: str = ""
    h1_match = re.search(r'^#\s*(.*?)$', intro_part, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()

    blockquote_lines: List[str] = []
    other_lines: List[str] = []

    title_found: bool = False
    for line in intro_part.split('\n'):
        if line.strip().startswith('#') and not title_found:
            title_found = True
            continue
        if line.strip().startswith('>'):
            content_line = re.sub(r'^>\s*', '', line.strip())
            blockquote_lines.append(content_line)
        else:
            if title_found:
                other_lines.append(line)

    summary: str = " ".join(blockquote_lines).strip()
    summary = re.sub(r'\s+', ' ', summary)
    info: str = "\n".join(other_lines).strip()

    # Fallback to treat the first non-empty paragraph as summary if no blockquote was provided
    if not summary:
        first_para_lines: List[str] = []
        remaining_lines: List[str] = []
        in_first_para: bool = False
        finished_first_para: bool = False

        for line in other_lines:
            stripped = line.strip()
            if not finished_first_para:
                if stripped:
                    in_first_para = True
                    first_para_lines.append(stripped)
                else:
                    if in_first_para:
                        finished_first_para = True
                    else:
                        # Leading empty lines before the first paragraph
                        pass
            else:
                remaining_lines.append(line)

        summary = " ".join(first_para_lines).strip()
        info = "\n".join(remaining_lines).strip()

    return AttrDict({
        'title': title,
        'summary': summary,
        'info': info,
        'sections': sections
    })


def get_doc_content(url_or_path: str) -> str:
    """Retrieve document content. For local relative paths, reads from repository root.

    Args:
        url_or_path: The URL or path to retrieve.

    Returns:
        The content string or a placeholder message on failure or network block.
    """
    if url_or_path.startswith(('http://', 'https://')):
        return f"<!-- Remote content skipped: {url_or_path} -->"

    # Reject absolute paths
    if os.path.isabs(url_or_path) or url_or_path.startswith('/'):
        return f"<!-- Error: Absolute path rejected: {url_or_path} -->"

    try:
        # Determine and normalize the repo root
        repo_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        repo_root_real = os.path.realpath(repo_root)

        # Build candidate filepath and resolve all symlinks/relative paths
        filepath = os.path.join(repo_root_real, url_or_path)
        filepath_real = os.path.realpath(filepath)

        # Check path containment to prevent directory traversal
        # filepath_real must start with repo_root_real (and follow path separator boundaries)
        prefix = repo_root_real if repo_root_real.endswith(os.sep) else repo_root_real + os.sep
        if not (filepath_real == repo_root_real or filepath_real.startswith(prefix)):
            return f"<!-- Error: Path traversal detected and rejected: {url_or_path} -->"

        # Verify it is a regular file (not a directory, symlink directory, or special file)
        if not os.path.isfile(filepath_real):
            return f"<!-- Error: Not a regular file: {url_or_path} -->"

        with open(filepath_real, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<!-- Error reading file {url_or_path}: {str(e)} -->"


def create_ctx(txt: str, optional: bool = False) -> str:
    """Create an LLM context XML compilation from the raw text content of an llms.txt file.

    Args:
        txt: Raw text content of the input llms.txt file.
        optional: If True, includes optional H2 sections. Otherwise, skips them.

    Returns:
        An XML-formatted string compiling the project and documentation sections.
    """
    parsed = parse_llms_file(txt)

    xml_parts: List[str] = []

    # root tag opening
    title_esc = escape_attr(parsed.title)
    summary_esc = escape_attr(parsed.summary)
    xml_parts.append(f'<project title="{title_esc}" summary="{summary_esc}">')

    # info section
    if parsed.info:
        xml_parts.append(escape_text(parsed.info))

    # loop through markdown sections
    for sec_name, links in parsed.sections.items():
        if not optional and sec_name.strip().lower() == 'optional':
            continue

        sec_tag = slugify(sec_name)
        xml_parts.append(f'<{sec_tag}>')

        for link in links:
            title_val = link.get('title', 'page')
            url_val = link.get('url', '')
            desc_val = link.get('desc', '')

            link_tag = slugify(title_val if title_val else 'page')
            url_esc = escape_attr(url_val if url_val else '')

            desc_attr = ""
            if desc_val:
                desc_esc = escape_attr(desc_val)
                desc_attr = f' desc="{desc_esc}"'

            xml_parts.append(f'  <{link_tag} url="{url_esc}"{desc_attr}>')
            content = get_doc_content(url_val if url_val else '')
            # Escape document content to ensure valid XML tag contents
            content_esc = escape_text(content)
            # Indent content slightly for cleaner formatting
            indented_content = "\n".join("    " + line for line in content_esc.split('\n'))
            xml_parts.append(indented_content)
            xml_parts.append(f'  </{link_tag}>')

        xml_parts.append(f'</{sec_tag}>')

    xml_parts.append('</project>')

    return "\n".join(xml_parts)


def main() -> None:
    """CLI execution entrypoint."""
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: llms_txt2ctx <input_llms.txt> [--optional <True|False>]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    include_optional = False

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--optional='):
            val = arg.split('=', 1)[1].lower()
            include_optional = val in ('true', '1', 'yes')
        elif arg == '--optional':
            # Check if there is a next argument that represents a boolean value
            if i + 1 < len(args) and args[i + 1].lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                val = args[i + 1].lower()
                include_optional = val in ('true', '1', 'yes')
                i += 1  # consume next argument
            else:
                include_optional = True
        i += 1

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    xml_output = create_ctx(content, optional=include_optional)
    print(xml_output)


if __name__ == '__main__':
    main()
