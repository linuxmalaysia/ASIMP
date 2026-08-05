# ASIMP Agent & Google Jules Guidelines & Instructions

Welcome, **Google Jules** and other AI/LLM agents! This document outlines coding conventions, architecture constraints, and testing protocols specifically for automated development tools working on **ASIMP (Ansible System Integrity Management Platform)**.

Use this as your single source of truth for repository structure, styling standards, and operational guidelines.

---

## 🧭 Project Purpose & Core Architecture

ASIMP is an automated security baseline and hardening framework. Its primary mission is to:
1. Conduct initial host compliance checks (OpenSCAP/Lynis) to establish a baseline.
2. Apply systems-level hardening configurations (SSH, kernels, updates).
3. Re-run compliance audits to verify and print the exact security delta.

It follows a strict **"Measure, Harden, Re-Measure"** workflow.

---

## 📁 Repository Structure

- **`play.yml`**: Main playbook designed for multi-host remote configurations.
- **`play-localhost.yml`**: Main playbook tailored for executing ASIMP on the localhost environment.
- **`requirements.yml`**: External Ansible Galaxy dependencies (SSH, chrony, etc.).
- **`requirements.txt`**: Python dependencies (Ansible, ansible-lint, cryptography).
- **`ansible.cfg`**: Configures Ansible behaviors, SSH pipelining, and custom roles paths.
- **`roles/`**:
  - `reporting-ASIMP`: Manages the dual-engine baseline generation, post-hardening analysis, and reporting.
  - `update-ubuntu-ASIMP`: Handles Ubuntu/Debian system upgrades, repository updates, and `debsums` verification.
  - `lynis-ansible`: Manages localized Lynis audit automation and compliance profiling.

---

## 🌌 Google Antigravity & Google Jules Agent Skills

This repository implements a comprehensive suite of **Google Antigravity-compatible Agent Skills** inside `.agents/skills/`. This seamlessly bridges **Google Jules** and **Google Antigravity**, representing all operational and domain-specific knowledge about the ASIMP project.

### Location & Structure
Skills are located under the `.agents/skills/<skill-folder>/` directory. Each skill is self-contained and consists of:
- **`SKILL.md`**: Main instructions, use cases, and guidelines with combined OKF and Antigravity YAML frontmatter, concluding with the standard **Deep State of Mind (DSOM) AI Protocol** footer.
- **Combined Frontmatter**: Unifies the Agent Skills specification (`name`, `description`, `license`, `compatibility`, `metadata`) and the Google Open Knowledge Format (OKF) specification (`type`, `title`, `resource`, `tags`, `timestamp`).

### Available Agent Skills

| Skill Directory | Skill Name | Purpose / Knowledge Covered |
| :--- | :--- | :--- |
| `asimp-core-workflow` | `asimp-core-workflow` | Manages the ASIMP 'Measure, Harden, Re-Measure' workflow with OpenSCAP and Lynis. |
| `ubuntu-scap-auditing` | `ubuntu-scap-auditing` | Controls dynamic SCAP Security Guide (SSG) zip retrieval from ComplianceAsCode and evaluations. |
| `ansible-boolean-conditionals` | `ansible-boolean-conditionals` | Enforces strict boolean evaluations in `when:` conditionals to prevent crashes. |
| `jinja2-template-overrides` | `jinja2-template-overrides` | Standardizes Jinja2 template parameter override headers using capitalized Python booleans (True/False). |
| `jules-sandbox-mode` | `jules-sandbox-mode` | Detects Google Jules environment (using `/home/jules`) and bypasses or ignores container-restricted tasks. |
| `ai-agent-instructions` | `ai-agent-instructions` | Coordinates multi-agent cross-referencing between AGENTS.md, CLAUDE.md, and other rule files. |
| `ansible-galaxy-roles` | `ansible-galaxy-roles` | Documents custom `roles_path` in `ansible.cfg` and Galaxy dependency installs with `--ignore-errors`. |
| `jekyll-docs-deployment` | `jekyll-docs-deployment` | Guides Jekyll documentation preprocessing via `prepare_docs.py` and GitHub Pages deployment. |
| `ansible-testing-linting` | `ansible-testing-linting` | Details syntax check and lint command routines for local verification. |
| `ansible-fqcn-idempotency` | `ansible-fqcn-idempotency` | Enforces Fully Qualified Collection Names (FQCN) and task idempotency (`changed_when` / `failed_when`). |

### Deep State of Mind (DSOM) Protocol
All skills conclude with a standard **Deep State of Mind (DSOM)** AI Protocol footer, guaranteeing that the context boundaries, alignment constraints, and execution statuses are synchronized between Google Jules and Google Antigravity on every activation.

---

## 🛠️ Code Conventions & File Hierarchy

### Ansible Best Practices for Agents
- **Fully Qualified Collection Names (FQCN)**: Always use FQCN for all built-in and community modules (e.g., `ansible.builtin.apt` instead of `apt`, `ansible.builtin.shell` instead of `shell`, `ansible.builtin.command` instead of `command`).
- **Idempotency**: All tasks must be strictly idempotent. Ensure `changed_when` is specified for `ansible.builtin.shell` and `ansible.builtin.command` blocks to prevent incorrect "changed" states during reporting or validation.
- **Error Tolerance & Graceful Fallbacks**: Auditing runs (`oscap`, `lynis`, `debsums`) operate in variable environments where specific utilities might be absent. Use `failed_when: false` or `ignore_errors: yes` strategically, coupled with proper verification steps so that reporting can complete or gracefully degrade instead of breaking the entire playbook.

---

## ⚙️ Development Environment Constraints

1. **Python Dependencies**: Defined in `requirements.txt`.
2. **Ansible Dependencies**: Defined in `requirements.yml`.
3. **No Local Artifact Modification**: When modifying playbook configurations or roles:
   - Edit the specific YAML files in `roles/reporting-ASIMP/`, `roles/update-ubuntu-ASIMP/`, etc.
   - Do not edit `/var/log` artifacts, parsed reports, or local testing directories directly.

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

### Multi-Agent Context Mapping
To provide consistent guidelines across different editors and execution tools, the repository includes targeted instruction files. They all cross-reference this `AGENTS.md` file:
- **Claude Code**: Refer to `CLAUDE.md` in the root for tool-specific commands and style guides.
- **Windsurf**: Refer to `.windsurfrules` in the root.
- **Cursor**: Refer to `.cursorrules` in the root.
- **Cline / Roo-Cline**: Refer to `.clinerules` in the root.
- **GitHub Copilot**: Refer to `.github/copilot-instructions.md` in the repository.

### Common Pitfalls to Avoid:
1. **Implicit Localhost Warnings**: When testing locally, Ansible might output warnings about an empty hosts list. This is normal for `play-localhost.yml`.
2. **Missing SCAP DataStreams**: Different distributions have different default datastream files. `reporting-ASIMP` dynamically determines which XML datastream to use. Ensure your modifications preserve this dynamic OS-detection logic.
3. **Overwriting Logs**: Always use different output file paths for "before" and "after" scans (e.g., `/var/log/openscap-before-results.xml` vs `/var/log/openscap-after-results.xml`).
