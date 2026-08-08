#!/usr/bin/env python3
"""
ASIMP Sovereign OS Role Compatibility Patcher
Dynamically and robustly patches Ansible roles for Google Jules sandbox compatibility.
"""

import os
import re
from typing import List, Tuple, Optional


def patch_ssh_templates() -> None:
    """Replace double-quoted or single-quoted trim_blocks/lstrip_blocks in SSH templates with Python booleans."""
    paths: List[str] = [
        "roles/dev-sec.ssh-hardening/templates/opensshd.conf.j2",
        "roles/dev-sec.ssh-hardening/templates/openssh.conf.j2"
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content: str = f.read()
            # Replace double-quoted or single-quoted trim_blocks/lstrip_blocks with Python booleans
            new_content, count = re.subn(
                r'#\s*jinja2:\s*trim_blocks:\s*[\'"]?(?:true|True)[\'"]?,\s*lstrip_blocks:\s*[\'"]?(?:true|True)[\'"]?',
                '#jinja2: trim_blocks: True, lstrip_blocks: True',
                content,
                flags=re.IGNORECASE
            )
            if count > 0:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Patched SSH template: {path} ({count} replacements)")


def patch_moduli_task() -> None:
    """Patch moduli conditional statement to ensure strict boolean evaluation."""
    path: str = "roles/dev-sec.ssh-hardening/tasks/hardening.yml"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content: str = f.read()
        new_content, count = re.subn(
            r'^(\s*)-\s+sshd_register_moduli\.stdout\s*$',
            r'\1- sshd_register_moduli.stdout | length > 0',
            content,
            flags=re.MULTILINE
        )
        if count > 0:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Patched moduli conditional in: {path} ({count} replacements)")


def split_into_tasks(lines: List[str]) -> List[Tuple[Optional[int], List[str]]]:
    """Split lines of a YAML file into blocks of top-level or nested tasks.

    Args:
        lines: A list of lines read from the YAML file.

    Returns:
        A list of tuples, where each tuple contains an optional indentation level
        and the corresponding list of line strings belonging to that task block.
    """
    blocks: List[Tuple[Optional[int], List[str]]] = []
    current_block: List[str] = []
    current_indent: Optional[int] = None

    for line in lines:
        match = re.match(r'^(\s*)-\s', line)
        if match:
            indent: int = len(match.group(1))
            if current_indent is None or indent <= current_indent:
                if current_block:
                    blocks.append((current_indent, current_block))
                current_block = [line]
                current_indent = indent
            else:
                current_block.append(line)
        else:
            current_block.append(line)

    if current_block:
        blocks.append((current_indent, current_block))
    return blocks


def patch_yaml_file(file_path: str) -> None:
    """Analyze and patch service or systemd tasks inside a YAML file for sandbox compatibility.

    Args:
        file_path: The path of the YAML file to patch.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines: List[str] = f.readlines()

    blocks: List[Tuple[Optional[int], List[str]]] = split_into_tasks(lines)
    modified: bool = False
    new_lines: List[str] = []

    for indent_level, block_lines in blocks:
        block_text: str = "".join(block_lines)

        # Check if block is a service or systemd task or a handler restarting service or augenrules
        is_service: bool = bool(
            re.search(r'\b(?:ansible\.builtin\.)?(?:service|systemd(?:_service)?):', block_text) or
            'service auditd restart' in block_text or
            'augenrules --load' in block_text
        )
        has_ignore: bool = 'ignore_errors:' in block_text

        if is_service and not has_ignore and indent_level is not None:
            # Find the last non-empty/non-comment line to insert after
            insert_idx: int = len(block_lines)
            for idx in range(len(block_lines) - 1, -1, -1):
                line_stripped: str = block_lines[idx].strip()
                if line_stripped and not line_stripped.startswith('#'):
                    insert_idx = idx + 1
                    break

            injection_indent: int = indent_level + 2
            injection: str = " " * injection_indent + 'ignore_errors: "{{ is_sandbox_jules | default(false) }}"\n'
            block_lines.insert(insert_idx, injection)
            modified = True

        new_lines.extend(block_lines)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Patched YAML file: {file_path}")


def patch_all_roles() -> None:
    """Walk through the roles directory and patch all tasks/handlers YAML files."""
    for root, dirs, files in os.walk("roles"):
        for file in files:
            if file.endswith(('.yml', '.yaml')):
                file_path: str = os.path.join(root, file)
                # Only patch tasks and handlers
                if '/tasks/' in file_path or '/handlers/' in file_path:
                    # Skip files in the .git directory or similar metadata
                    if '.git' in file_path:
                        continue
                    patch_yaml_file(file_path)


if __name__ == '__main__':
    print("Starting ASIMP Sovereign OS Role Compatibility Patcher...")
    patch_ssh_templates()
    patch_moduli_task()
    patch_all_roles()
    print("ASIMP Patcher finished successfully.")
