# ASIMP Agent Guidelines & Instructions

Welcome! This document outlines coding conventions, architecture constraints, and testing protocols specifically for AI Agents and automated development tools working on **ASIMP (Ansible System Integrity Management Platform)**.

---

## 🧭 Project Purpose

ASIMP is an automated security baseline and hardening framework. Its primary mission is to:
1. Conduct initial host compliance checks (OpenSCAP/Lynis).
2. Apply systems-level hardening configurations (SSH, kernels, updates).
3. Re-run compliance audits to verify the exact security delta.

---

## 🛠️ Code Conventions & File Hierarchy

- **Ansible Best Practices**: Use fully qualified collection names (FQCN) for all built-in and community modules (e.g., `ansible.builtin.apt` instead of `apt`, `ansible.builtin.shell` instead of `shell`).
- **Idempotency**: All custom tasks must be strictly idempotent. Ensure `changed_when` is specified for `ansible.builtin.shell` and `ansible.builtin.command` blocks to prevent incorrect "changed" states during reporting or validation.
- **Error Tolerance**: Auditing runs (`oscap`, `lynis`, `debsums`) operate in variable environments where specific utilities might be absent. Use `failed_when: false` or `ignore_errors: yes` strategically, coupled with proper verification steps so that reporting can complete or gracefully degrade instead of breaking the entire playbook.

---

## ⚙️ Development Environment Constraints

1. **Python Dependencies**: Defined in `requirements.txt`.
2. **Ansible Dependencies**: Defined in `requirements.yml`.
3. **No Local Artifact Modification**: When modifying playbook configurations or roles:
   - Edit the specific YAML files in `roles/reporting-ASIMP/`, `roles/update-ubuntu-ASIMP/`, etc.
   - Do not edit `/var/log` artifacts, parsed reports, or local testing directories.

---

## 🧪 Testing and Syntax Validation

Before submitting any configuration changes, you **must** perform syntax checking and linting to avoid breaking user systems:

### 1. Verification of Playbooks Syntax
Run the syntax check on both localhost and primary playbooks:
```bash
# In the virtual environment
/tmp/venv/bin/ansible-playbook --syntax-check play.yml
/tmp/venv/bin/ansible-playbook --syntax-check play-localhost.yml
```

### 2. Linting
Verify role and playbook styling compliance:
```bash
/tmp/venv/bin/ansible-lint play.yml
/tmp/venv/bin/ansible-lint play-localhost.yml
```

---

## 🧬 Before/After Verification Logic

If you modify the reporting logic in `roles/reporting-ASIMP/tasks/main.yml`, ensure you do not break the baseline/after sequence:
- The `before` phase must execute **prior** to any upgrades or hardening.
- The `before` scores must be recorded to `/var/log/asimp-baseline-scores.json`.
- The `after` phase must run **last** and slurp the baseline JSON file using `ansible.builtin.slurp` to print the comparative scorecard.
