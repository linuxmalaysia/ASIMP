# ASIMP Agent & Google Jules Guidelines & Instructions

Welcome, **Google Jules** and other AI/LLM agents! This document outlines coding conventions, architecture constraints, and testing protocols specifically for automated development tools working on **ASIMP (Ansible System Integrity Management Platform)**.

Use this as your source of truth for repository structure, styling standards, and operational guidelines.

---

## 🧭 Project Purpose & Core Architecture

ASIMP is an automated security baseline and hardening framework. Its primary mission is to:
1. Conduct initial host compliance checks (OpenSCAP/Lynis) to establish a baseline.
2. Apply systems-level hardening configurations (SSH, kernels, updates).
3. Re-run compliance audits to verify and print the exact security delta.

It follows a strict **"Measure, Harden, Re-Measure"** workflow.

---

## 🛠️ Code Conventions & File Hierarchy

### Ansible Best Practices for Agents
- **Fully Qualified Collection Names (FQCN)**: Use FQCN for all built-in and community modules (e.g., `ansible.builtin.apt` instead of `apt`, `ansible.builtin.shell` instead of `shell`).
- **Idempotency**: All tasks must be strictly idempotent. Ensure `changed_when` is specified for `ansible.builtin.shell` and `ansible.builtin.command` blocks to prevent incorrect "changed" states during reporting or validation.
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
ansible-playbook --syntax-check play.yml
ansible-playbook --syntax-check play-localhost.yml
```

### 2. Linting
Verify role and playbook styling compliance:
```bash
ansible-lint play.yml
ansible-lint play-localhost.yml
```

---

## 🧬 Before/After Verification Logic

If you modify the reporting logic in `roles/reporting-ASIMP/tasks/main.yml`, ensure you do not break the baseline/after sequence:
- The `before` phase must execute **prior** to any upgrades or hardening.
- The `before` scores must be recorded to `/var/log/asimp-baseline-scores.json`.
- The `after` phase must run **last** and slurp the baseline JSON file using `ansible.builtin.slurp` to print the comparative scorecard.

---

## 🤖 Guide for Google Jules & Other AI Agents

### Common Pitfalls to Avoid:
1. **Implicit Localhost Warnings**: When testing locally, Ansible might output warnings about an empty hosts list. This is normal for `play-localhost.yml`.
2. **Missing SCAP DataStreams**: Different distributions have different default datastream files. `reporting-ASIMP` dynamically determines which XML datastream to use. Ensure your modifications preserve this dynamic OS-detection logic.
3. **Overwriting Logs**: Always use different output file paths for "before" and "after" scans (e.g., `/var/log/openscap-before-results.xml` vs `/var/log/openscap-after-results.xml`).
