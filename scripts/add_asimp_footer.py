#!/usr/bin/env python3
"""
ASIMP Standard Footer Patcher
Scans workspace markdown (.md) documents and enforces compliance with the
project footer standard, auto-appending the standard ASIMP/DSOM footer
if it is not already present, while removing older legacy attributions.
"""

import os
import tempfile
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
    """Check a markdown file and append the standard ASIMP footer if absent,

    while removing any older legacy or standard footers.

    Args:
        filepath: The path of the markdown file to process.
    """
    # 1. File path safety validation guards
    if os.path.islink(filepath):
        print(f"Skipping symlink file: {filepath}")
        return

    resolved_path = os.path.realpath(filepath)
    if not os.path.isfile(resolved_path):
        print(f"Skipping non-regular file: {filepath}")
        return

    repo_root = os.path.realpath(os.getcwd())
    if not resolved_path.startswith(repo_root):
        print(f"Skipping file outside repository root: {filepath}")
        return

    with open(resolved_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Split front matter and body to prevent touch of front matter delimiters
    front_matter = ""
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            front_matter = "---" + parts[1] + "---"
            body = parts[2]

    # 3. Clean legacy / existing standard footers from the body
    # Loop recursively to clean multiple duplicate footer/attribution blocks from the end
    while True:
        lines = body.splitlines()
        footer_start_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line == "---":
                subsequent_text = "\n".join(lines[i+1:])
                # Use stable markers to identify legacy or existing standardized footers
                if "Deep State of Mind (DSOM)" in subsequent_text or "ASIMP (Ansible System" in subsequent_text:
                    footer_start_idx = i
                    break
        if footer_start_idx != -1:
            body = "\n".join(lines[:footer_start_idx])
        else:
            break

    # Strip any trailing whitespace from the body
    cleaned_body = body.rstrip()
    new_body = cleaned_body + "\n\n---\n\n" + FOOTER_TEXT + "\n"
    new_content = front_matter + new_body

    # 4. Atomic file-writing flow using NamedTemporaryFile and os.replace
    target_dir = os.path.dirname(resolved_path)
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        dir=target_dir,
        delete=False,
        encoding="utf-8",
        suffix=".tmp"
    )
    temp_filepath = temp_file.name
    try:
        temp_file.write(new_content)
        temp_file.close()
        os.replace(temp_filepath, resolved_path)
        print(f"Successfully patched footer in: {filepath}")
    except Exception as e:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise e


def main() -> None:
    """Walk through the repository directories and processes all markdown (.md) documents."""
    exclude_dirs: Set[str] = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "lynis-ansible",
        "asimp_mock",  # Prune asimp_mock folder entirely from walking
    }

    # Walk repository from the root directory
    for root, dirs, files in os.walk("."):
        # Modifying dirs in-place to prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)

                # Prune and filter path components to exclude generated report paths or submodules
                norm_path = os.path.normpath(filepath)
                if "roles/lynis-ansible" in norm_path:
                    continue
                if "data/asimp_mock" in norm_path:
                    continue

                patch_markdown_file(filepath)


if __name__ == "__main__":
    main()
