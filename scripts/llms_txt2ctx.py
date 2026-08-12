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
        """Initialize the mapping and convert nested dictionaries to attribute-accessible mappings."""
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = AttrDict(v)
            elif isinstance(v, list):
                self[k] = [AttrDict(i) if isinstance(i, dict) else i for i in v]

    def __getattr__(self, name: str) -> Any:
        """
        Retrieve a dictionary value through attribute-style access.
        
        Parameters:
        	name (str): The dictionary key to retrieve.
        
        Returns:
        	Any: The value associated with the key.
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute by storing its value under the corresponding dictionary key.
        
        Parameters:
            name (str): The attribute and dictionary key to assign.
            value (Any): The value to store.
        """
        self[name] = value


def slugify(title: str) -> str:
    """
    Convert a title into a lowercase, hyphen-separated XML tag name.
    
    Parameters:
        title (str): The title to normalize.
    
    Returns:
        str: The normalized tag name, using ``page`` for empty results and
            prefixing names that begin with a digit with ``p``.
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
    """
    Escape a string for use in an XML attribute value.
    
    Args:
        val: Raw attribute text.
    
    Returns:
        The escaped attribute string, or an empty string for falsy input.
    """
    if not val:
        return ""
    val = val.replace('&', '&amp;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    val = val.replace('"', '&quot;')
    val = val.replace("'", '&#39;')
    return val


def parse_link(line: str) -> Optional[Dict[str, Optional[str]]]:
    """Parse a markdown list item containing a hyperlink and optional description.
    
    Args:
        line: The raw markdown list item.
    
    Returns:
        A dictionary with `title`, `url`, and `desc` keys if the line matches, otherwise `None`.
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
    """
    Parse an llms.txt document into structured project metadata.
    
    Parameters:
    	txt: The raw llms.txt content.
    
    Returns:
    	An AttrDict with title, summary, info, and sections.
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
    """
    Read a local document relative to the repository root or provide a placeholder for unavailable content.
    
    Args:
        url_or_path: A local document path or an HTTP(S) URL.
    
    Returns:
        The document content, or a placeholder comment when remote content is skipped, the file is missing, or reading fails.
    """
    if url_or_path.startswith(('http://', 'https://')):
        return f"<!-- Remote content skipped: {url_or_path} -->"

    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(repo_root, url_or_path)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"<!-- Error reading file {url_or_path}: {str(e)} -->"

    return f"<!-- File not found: {url_or_path} -->"


def create_ctx(txt: str, optional: bool = False) -> str:
    """
    Compile llms.txt content into an XML context document.
    
    Args:
        txt: Raw llms.txt text to parse.
        optional: Whether to include the section named Optional.
    
    Returns:
        The assembled XML document.
    """
    parsed = parse_llms_file(txt)

    xml_parts: List[str] = []

    # root tag opening
    title_esc = escape_attr(parsed.title)
    summary_esc = escape_attr(parsed.summary)
    xml_parts.append(f'<project title="{title_esc}" summary="{summary_esc}">')

    # info section
    if parsed.info:
        xml_parts.append(parsed.info)

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
            # Indent content slightly for cleaner formatting
            indented_content = "\n".join("    " + line for line in content.split('\n'))
            xml_parts.append(indented_content)
            xml_parts.append(f'  </{link_tag}>')

        xml_parts.append(f'</{sec_tag}>')

    xml_parts.append('</project>')

    return "\n".join(xml_parts)


def main() -> None:
    """
    Run the command-line converter and print the generated XML.
    
    Reads the input `llms.txt` file specified on the command line. The optional
    section can be included with `--optional` or `--optional=true|1|yes`.
    """
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: llms_txt2ctx <input_llms.txt> [--optional <True|False>]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    include_optional = False

    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg.startswith('--optional='):
                val = arg.split('=', 1)[1].lower()
                include_optional = val in ('true', '1', 'yes')
            elif arg == '--optional':
                include_optional = True

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    xml_output = create_ctx(content, optional=include_optional)
    print(xml_output)


if __name__ == '__main__':
    main()
