#!/usr/bin/env python3
"""
Jekyll Documentation Pre-processing Script
Scans the documentation files and ensures that each markdown file contains
the necessary Jekyll front matter block, auto-generating layouts and titles if absent.
"""

import os
import re
from typing import Optional


def process_markdown_file(filepath: str) -> None:
    """Read a markdown file, parse its header, and add or update Jekyll front matter.

    Args:
        filepath: The exact path of the markdown file to be processed.
    """
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content: str = f.read()

    # Check if the file already has front matter
    has_front_matter: bool = False
    # Strip leading whitespace or empty lines to check
    stripped_content: str = content.lstrip()
    if stripped_content.startswith('---'):
        has_front_matter = True

    if not has_front_matter:
        # Extract title from the first heading line
        title: Optional[str] = None
        # Look for first # or ## heading
        heading_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
        else:
            # Fallback to filename capitalized
            filename: str = os.path.basename(filepath)
            name_without_ext, _ = os.path.splitext(filename)
            title = name_without_ext.replace('_', ' ').replace('-', ' ').title()

        # Build the front matter block
        front_matter: str = f"---\nlayout: default\ntitle: \"{title}\"\n---\n\n"
        new_content: str = front_matter + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  -> Added front matter with title: '{title}'")
    else:
        # Even if it has front matter, make sure 'layout:' is defined
        # Find the front matter boundaries
        parts = stripped_content.split('---', 2)
        if len(parts) >= 3:
            fm_content: str = parts[1]
            if 'layout:' not in fm_content:
                # Add layout: default inside front matter
                new_fm: str = fm_content.rstrip('\n') + "\nlayout: default\n"
                new_content: str = f"---\n{new_fm}---\n" + parts[2]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("  -> Injected 'layout: default' to existing front matter")
            else:
                print("  -> Already has layout configured")


def main() -> None:
    """Scan all markdown (.md) documents inside the docs folder and processes them."""
    docs_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
    print(f"Scanning markdown files under: {docs_dir}")
    if not os.path.exists(docs_dir):
        print(f"Error: {docs_dir} does not exist.")
        return

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                process_markdown_file(os.path.join(root, file))


if __name__ == '__main__':
    main()
