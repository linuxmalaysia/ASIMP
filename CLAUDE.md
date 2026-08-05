---
okf_version: "0.1"
type: instructions
title: "CLAUDE.md - Claude Code Instructions for ASIMP"
timestamp: "2026-08-05T12:00:00Z"
topics: [ai, agents, guidelines, rules, conventions]
---
# CLAUDE.md - Claude Code Instructions for ASIMP

This file provides system-specific build commands, test commands, and coding rules for Anthropic's **Claude Code** when working in the **ASIMP** repository.

For full architecture details, pitfalls, and guidelines, please refer to the main [AGENTS.md](AGENTS.md) file.

---

## 🛠️ Useful Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Ansible Galaxy dependencies
ansible-galaxy role install -r requirements.yml --ignore-errors
```

### Syntax & Lint Checks
```bash
# Check syntax of localhost playbook
ansible-playbook --syntax-check play-localhost.yml

# Check syntax of multi-host playbook
ansible-playbook --syntax-check play.yml

# Lint the Ansible playbooks and roles
ansible-lint play-localhost.yml
```

---

## 📐 Coding Rules & Style Guidelines

1. **Fully Qualified Collection Names (FQCN)**:
   Always use FQCN for all Ansible modules.
   - *Good*: `ansible.builtin.apt`, `ansible.builtin.shell`, `ansible.builtin.copy`
   - *Bad*: `apt`, `shell`, `copy`

2. **Strict Idempotency**:
   - Provide `changed_when` or `failed_when` for all command or shell tasks so they are strictly idempotent and do not cause false "changed" states.

3. **Graceful Failures & Fallbacks**:
   - Use `failed_when: false` or `ignore_errors: yes` coupled with safety checks (e.g., `ansible.builtin.stat`) when executing platform-specific audits (`oscap`, `lynis`, `debsums`) so the playbooks gracefully degrade rather than crash in environments where utilities may be absent.

4. **No Direct Log/Artifact Modification**:
   - Never directly modify `/var/log/*` files or generated report HTMLs. Always modify the source Ansible task files under `roles/` or the playbook templates.
