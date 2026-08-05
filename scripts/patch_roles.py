#!/usr/bin/env python3
"""
ASIMP Sovereign OS Role Compatibility Patcher
Dynamically and robustly patches Ansible roles for Google Jules sandbox compatibility.
"""

import os
import re

def patch_ssh_templates():
    paths = [
        "roles/dev-sec.ssh-hardening/templates/opensshd.conf.j2",
        "roles/dev-sec.ssh-hardening/templates/openssh.conf.j2"
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
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

def patch_moduli_task():
    path = "roles/dev-sec.ssh-hardening/tasks/hardening.yml"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
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

def split_into_tasks(lines):
    blocks = []
    current_block = []
    current_indent = None

    for line in lines:
        match = re.match(r'^(\s*)-\s', line)
        if match:
            indent = len(match.group(1))
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

def patch_yaml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = split_into_tasks(lines)
    modified = False
    new_lines = []

    for indent_level, block_lines in blocks:
        block_text = "".join(block_lines)

        # Check if block is a service or systemd task or a handler restarting service or augenrules
        is_service = (
            re.search(r'\b(?:ansible\.builtin\.)?(?:service|systemd(?:_service)?):', block_text) or
            'service auditd restart' in block_text or
            'augenrules --load' in block_text
        )
        has_ignore = 'ignore_errors:' in block_text

        if is_service and not has_ignore and indent_level is not None:
            # Find the last non-empty/non-comment line to insert after
            insert_idx = len(block_lines)
            for idx in range(len(block_lines) - 1, -1, -1):
                line_stripped = block_lines[idx].strip()
                if line_stripped and not line_stripped.startswith('#'):
                    insert_idx = idx + 1
                    break

            injection_indent = indent_level + 2
            injection = " " * injection_indent + 'ignore_errors: "{{ is_sandbox_jules | default(false) }}"\n'
            block_lines.insert(insert_idx, injection)
            modified = True

        new_lines.extend(block_lines)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Patched YAML file: {file_path}")

def patch_all_roles():
    for root, dirs, files in os.walk("roles"):
        for file in files:
            if file.endswith(('.yml', '.yaml')):
                file_path = os.path.join(root, file)
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
