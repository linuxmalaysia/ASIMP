#!/usr/bin/env python3
"""
ASIMP Standard Footer Patcher
Scans workspace markdown (.md) documents and enforces compliance with the
project footer standard, auto-appending the standard ASIMP/DSOM footer
if it is not already present.
"""

import os
from typing import Set

FOOTER_TEXT = (
    "ASIMP (Ansible System Integrity Management Platform) | "
    "Deep State of Mind (DSOM) For My AI Protocol | "
    "Harisfazillah Jamel (LinuxMalaysia) | "
    "2026-07-12 Standard: UK English | "
    "DBP-standard Bahasa Melayu Malaysia (Piawai) | "
    "GNU General Public License v3.0"
)


def patch_markdown_file(filepath: str) -> None:
    """Check a markdown file and append the standard ASIMP footer if absent.

    Args:
        filepath: The path of the markdown file to process.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if the footer text is already present in any form
    if FOOTER_TEXT in content:
        print(f"No update needed (already has footer): {filepath}")
        return

    # To keep formatting clean, strip trailing whitespace and append the footer
    # separated by a markdown horizontal rule (---) and clean spacing.
    cleaned_content = content.rstrip()
    new_content = cleaned_content + "\n\n---\n\n" + FOOTER_TEXT + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Successfully appended standard footer to: {filepath}")


def main() -> None:
    """
    Process repository Markdown files and add the standard footer where needed.
    
    Directories excluded from traversal include version-control, dependency, virtual-environment, and `lynis-ansible` directories. Files under `roles/lynis-ansible` are also skipped.
    """
    exclude_dirs: Set[str] = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "lynis-ansible",  # Also exclude any folder named lynis-ansible to be safe
    }

    # Walk repository from the root directory
    for root, dirs, files in os.walk("."):
        # Modifying dirs in-place to prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)

                # Skip files inside the third-party submodule 'roles/lynis-ansible'
                norm_path = os.path.normpath(filepath)
                if "roles/lynis-ansible" in norm_path:
                    print(f"Skipping third-party submodule file: {filepath}")
                    continue

                patch_markdown_file(filepath)


if __name__ == "__main__":
    main()
