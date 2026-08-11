---
okf_version: "0.1"
type: instructions
title: "ASIMP Agent & Google Jules Guidelines & Instructions"
timestamp: "2026-08-05T12:00:00Z"
topics: [ai, agents, guidelines, rules, conventions]
---
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

## 🔒 Google Jules Sandbox Limitations & Compatibility Standards

Google Jules executes in a secure, containerized sandbox environment. This introduces several system-level operational constraints that must be accounted for by all AI agents.

### ⚠️ Google Jules Sandbox Constraints & Sudo Correction

1. **Root / Sudo Privilege Fallacy**: While the `jules` user inside the sandbox technically has full passwordless `sudo` privileges configured (`(ALL : ALL) NOPASSWD: ALL`), it is run within a restricted containerized context. Therefore, root-level operations cannot override or bypass host OS virtualization constraints. Any operations attempting to alter host OS settings (such as `/etc/sysctl.conf`, loading kernel modules, modifying sysctl settings) will fail.
2. **Container-Restricted Services**: Managing or interacting with hardware-bound or kernel-restricted system services (such as `auditd`, `chrony`, `firewalld`, `autofs`, `clamav`) will fail or stall.
3. **Upgrade/Integrity Operations**: Global package manager upgrades (`apt upgrade` / `dnf upgrade`) and complete system-wide file integrity verifications (`debsums`) can hang, freeze, or fail due to network blocks or virtualization limits.

### 📜 Mandatory Playbook Compliance Standard

Any Ansible playbook or automation code created, edited, or used in this repository **MUST** detect and account for the Jules sandbox environment (or any environment with identical conditions):
- **Detection Pattern**: Use the `is_sandbox_jules` fact check (via detecting `/home/jules`) to determine if the environment is sandboxed.
- **Conditional Enforcement**: Always provide distinct options/paths between limited environments (sandbox/ordinary user) and a real, unconstrained OS. On a real OS, run full-throttle remediations, package upgrades, and auditing with full privileges. On a sandboxed/limited OS, run in non-destructive, audit/test/info mode only, or gracefully skip tasks that modify restricted services.
- **Pre-Remediation Safety & Break-Prevention Verification**: Before applying any remediation or hardening on a real OS, playbooks must implement dry-run and safety checks (such as verifying existing configuration syntax with `sshd -t`, checking root partition space, validating `/etc/fstab` and baselining crucial ports) to ensure that the modifications will not break the host system or active project codes.

---

## 📖 Google Open Knowledge Format (OKF) v0.1 Specification

To ensure a standardized, self-describing, human-readable, and machine-parseable representation of project knowledge, **all** markdown (`.md`) files in this repository strictly adhere to the **Google Open Knowledge Format (OKF) v0.1** specification.

### 📐 Required Frontmatter Fields
Every `.md` document in the repository must begin with a YAML frontmatter block containing exactly these five mandatory fields:

1. **`okf_version`**: Declares the version of the OKF specification. For this repository, it must be `"0.1"`.
2. **`type`**: Identifies the semantic classification of the document. Standard types used in this repository include:
   - `documentation`: For general manuals, readmes, and user guides.
   - `skill`: For Google Antigravity/Jules agent skills.
   - `instructions`: For agent-specific guidelines and rule mappings (e.g., `.clinerules`, `CLAUDE.md`).
   - `report`: For compliance audits and security hardening scorecards.
   - `meta`: For changelogs and historical project logs.
   - `role-documentation`: For Ansible role-specific README files.
3. **`title`**: A clean, descriptive, human-readable display title for the document.
4. **`timestamp`**: An ISO 8601 UTC datetime string indicating when the document was created or last updated (e.g., `"2026-08-05T12:00:00Z"`).
5. **`topics`**: A YAML array/list of short string tags summarizing the key concepts, modules, or domains covered by the document.

### 📝 Example OKF v0.1 Frontmatter
```yaml
---
okf_version: "0.1"
type: documentation
title: "ASIMP Architecture & System Component Flow"
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, architecture, design, audit, workflow]
---
```

### 🤖 Rules for Agents
When creating new `.md` files or editing existing ones:
- **Mandatory Frontmatter**: You must always include the 5 required fields at the very beginning of the document.
- **Topics & Tags Mapping**: If the document contains any legacy `tags` field, ensure those are mapped/mirrored to the `topics` list field as well.
- **Automation**: You can run the automation script `scripts/add_okf_frontmatter.py` to automatically scan, parse, format, and align all workspace markdown files.

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

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
