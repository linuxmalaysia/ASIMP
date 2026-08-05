#!/usr/bin/env python3
import os
import re

def guess_type_and_topics(filepath, content):
    filename = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, start=os.getcwd())

    if filename == 'CHANGELOG.md' or filename == 'HISTORY.md':
        return 'meta', ['asimp', 'changelog', 'history', 'releases']
    elif filename == 'CLAUDE.md' or filename == 'AGENTS.md' or filename == '.github/copilot-instructions.md':
        return 'instructions', ['ai', 'agents', 'guidelines', 'rules', 'conventions']
    elif '.agents/skills/' in rel_path:
        return 'skill', ['ai', 'agents', 'skills', 'antigravity', 'jules']
    elif 'docs/' in rel_path:
        return 'documentation', ['asimp', 'docs', 'manual', 'security']
    elif filename == 'SECURITY_AUDIT_REPORT.md':
        return 'report', ['security', 'compliance', 'audit', 'report', 'sandbox']
    elif 'roles/' in rel_path:
        return 'role-documentation', ['ansible', 'role', 'asimp', 'hardening']
    elif filename == 'README.md':
        return 'documentation', ['asimp', 'readme', 'security', 'baseline', 'hardening']
    else:
        return 'documentation', ['asimp', 'general']

def extract_list(key, fm_str):
    # Try finding key: [val1, val2]
    match = re.search(r'^' + re.escape(key) + r'\s*:\s*\[(.*?)\]', fm_str, re.MULTILINE)
    if match:
        items = [item.strip().strip("'\"") for item in match.group(1).split(',')]
        return [i for i in items if i]

    # Try finding key: followed by indented lines with -
    match_block = re.search(r'^' + re.escape(key) + r'\s*:\s*\n((?:\s*-\s*.*?\n)+)', fm_str, re.MULTILINE)
    if match_block:
        items = []
        for line in match_block.group(1).split('\n'):
            line_strip = line.strip()
            if line_strip.startswith('-'):
                items.append(line_strip[1:].strip().strip("'\""))
        return [i for i in items if i]

    return []

def extract_title_from_content(content, filepath):
    # Look for first # or ## heading
    heading_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
    if heading_match:
        title = heading_match.group(1).strip().strip('*_`#')
        return title

    filename = os.path.basename(filepath)
    name_without_ext, _ = os.path.splitext(filename)
    return name_without_ext.replace('_', ' ').replace('-', ' ').title()

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find frontmatter
    has_front_matter = False
    stripped = content.lstrip()

    if stripped.startswith('---'):
        parts = stripped.split('---', 2)
        if len(parts) >= 3:
            has_front_matter = True

    guessed_type, guessed_topics = guess_type_and_topics(filepath, content)
    default_timestamp = "2026-08-05T12:00:00Z"

    if not has_front_matter:
        title = extract_title_from_content(content, filepath)
        topics_str = "[" + ", ".join(guessed_topics) + "]"

        fm = (
            "---\n"
            'okf_version: "0.1"\n'
            f"type: {guessed_type}\n"
            f'title: "{title}"\n'
            f'timestamp: "{default_timestamp}"\n'
            f"topics: {topics_str}\n"
            "---\n"
        )

        new_content = fm + content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added complete OKF v0.1 frontmatter to {filepath}")
    else:
        parts = stripped.split('---', 2)
        fm_content = parts[1]
        body = parts[2]

        lines = fm_content.split('\n')
        keys = {}
        for line in lines:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith('#'):
                continue
            m = re.match(r'^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$', line_strip)
            if m:
                keys[m.group(1)] = m.group(2).strip()

        updates = []
        if 'okf_version' not in keys:
            updates.append('okf_version: "0.1"')
        if 'type' not in keys:
            updates.append(f"type: {guessed_type}")
        if 'title' not in keys:
            title = extract_title_from_content(body, filepath)
            # escape double quotes in title
            title_escaped = title.replace('"', '\\"')
            updates.append(f'title: "{title_escaped}"')
        if 'timestamp' not in keys:
            updates.append(f'timestamp: "{default_timestamp}"')
        if 'topics' not in keys:
            tags_list = extract_list('tags', fm_content)
            if tags_list:
                topics_str = "[" + ", ".join(tags_list) + "]"
            else:
                topics_str = "[" + ", ".join(guessed_topics) + "]"
            updates.append(f"topics: {topics_str}")

        if updates:
            fm_content_clean = fm_content.rstrip('\n')
            new_fm_content = fm_content_clean + "\n" + "\n".join(updates) + "\n"
            new_content = f"---\n{new_fm_content}---\n" + body
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated OKF v0.1 frontmatter in {filepath} with: {updates}")
        else:
            print(f"No OKF v0.1 updates needed for {filepath}")

def main():
    exclude_dirs = {'.git', 'node_modules', 'venv', '.venv'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                process_file(filepath)

if __name__ == '__main__':
    main()
