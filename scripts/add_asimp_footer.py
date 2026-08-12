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
    "GNU General Public License v3.0 | "
    "[Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)"
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

    # Check repository containment using commonpath, catching only ValueError
    repo_root = os.path.realpath(os.getcwd())
    try:
        common = os.path.commonpath([repo_root, resolved_path])
        if os.path.realpath(common) != repo_root:
            print(f"Skipping file outside repository root: {filepath}")
            return
    except ValueError:
        print(f"Skipping file outside repository root due to drive mismatch: {filepath}")
        return

    with open(resolved_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.rstrip().endswith("\n\n---\n\n" + FOOTER_TEXT):
        print(f"No update needed (already has footer): {filepath}")
        return

    # 2. Split front matter and body to prevent touch of front matter delimiters
    front_matter = ""
    body = content

    # Find the front-matter block by looking for complete lines containing only the '---' delimiter
    if content.startswith("---\n") or content.startswith("---\r\n"):
        lines = content.splitlines(keepends=True)
        closing_idx = -1
        for idx in range(1, len(lines)):
            if lines[idx].rstrip("\r\n") == "---":
                closing_idx = idx
                break

        if closing_idx != -1:
            front_matter = "".join(lines[:closing_idx + 1])
            body = "".join(lines[closing_idx + 1:])

    # 3. Clean legacy / existing standard footers from the body
    # Loop recursively to clean multiple duplicate footer/attribution blocks from the end.
    # It removes content only when a recognized legacy or standardized footer block
    # is anchored at the end of the document (validated to be exactly a single footer line).
    while True:
        lines = body.splitlines()
        footer_start_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line == "---":
                subsequent_lines = lines[i+1:]
                non_empty_subsequent = [l.strip() for l in subsequent_lines if l.strip()]
                # Validate that it is a trailing block consisting of exactly one line
                if len(non_empty_subsequent) == 1:
                    sub_line = non_empty_subsequent[0]
                    # Use stable markers to identify legacy or existing standardized footers
                    if "Deep State of Mind (DSOM)" in sub_line or "ASIMP (Ansible System" in sub_line:
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
        print(f"Successfully appended standard footer to: {filepath}")
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
        "docs",        # Exclude docs directory so Jekyll site pages do not get inline footers
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
                parts = norm_path.split(os.sep)
                if "roles" in parts and "lynis-ansible" in parts:
                    continue
                if "data" in parts and "asimp_mock" in parts:
                    continue
                if "docs" in parts:
                    continue

                patch_markdown_file(filepath)


if __name__ == "__main__":
    main()
