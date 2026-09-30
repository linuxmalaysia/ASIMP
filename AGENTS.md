---
okf_version: "0.2"
trust_level: "verified"
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

## 🛡️ Mintlify One-Way Docs Sync & Safety Guards Mandate

All documentation in `docs/` serves as the single source of truth for Mintlify deployment.
- **Source of Truth**: `docs/` (standard Markdown `.md`).
- **Compiler**: `tools/build_mintlify_mdx.py` automatically compiles `docs/` and `.agents/skills/` into Mintlify MDX files inside `docs-source/` and dynamically generates `docs-source/docs.json`.
- **Sync Script**: `scripts/sync_docs.py` handles one-way synchronization from `docs-source/` to the downstream Mintlify docs repository (`linuxmalaysia/documentation-asimp-ansible-framework`).
- **5 Strict Safety Guards**:
  - **Guard A (Source & JSON Integrity)**: Validates that `docs-source/` exists and `docs-source/docs.json` contains valid JSON.
  - **Guard B (Minimum File Count Floor)**: Requires at least `MIN_MDX_FILES` (default 5) `.mdx` files to exist in `docs-source/`.
  - **Guard C (Navigation Integrity)**: Verifies that every page path declared in `docs.json` navigation has a corresponding `.mdx` file.
  - **Guard D (Diff Preview & Deletion Cap)**: Computes file diffs against downstream and blocks synchronization if deleted files exceed `MAX_DELETIONS` (default 10) unless `ALLOW_LARGE_DELETIONS=true`.
  - **Guard E (Dry-Run Mode)**: Supports `--dry-run` / `DRY_RUN=true` to preview synchronization actions without committing or pushing.
- **Strict One-Way Directive**: Never configure or perform two-way synchronization. Never force-push (`git push --force`) to downstream repositories. All downstream changes must originate from the app repository.

---

## 🌌 Google Antigravity & Google Jules Agent Skills

### Location & Structure

Project operational and domain-specific knowledge is represented using Google Antigravity-compatible Agent Skills. These are placed inside the `.agents/skills/` directory.

Each skill is self-contained in its own directory (e.g., `.agents/skills/<skill-folder>/`) and contains a `SKILL.md` file. Each `SKILL.md` includes OKF v0.2 YAML frontmatter and a standard Deep State of Mind (DSOM) AI Protocol footer, bridging Google Jules and Antigravity capabilities.

### Available Agent Skills

The following table lists the available agent skills present in this repository:

| Skill Directory | Skill Name | Description |
| :--- | :--- | :--- |
| `ai-agent-instructions` | `ai-agent-instructions` | Direct instruction file matching for copilot/cursor/cline/windsurf configurations. |
| `ansible-boolean-conditionals` | `ansible-boolean-conditionals` | Guides on writing boolean conditionals in Ansible. |
| `ansible-fqcn-idempotency` | `ansible-fqcn-idempotency` | Standards for Fully Qualified Collection Names (FQCN) and task idempotency. |
| `ansible-galaxy-roles` | `ansible-galaxy-roles` | Instructions for managing and installing Ansible Galaxy external role dependencies. |
| `ansible-testing-linting` | `ansible-testing-linting` | Guidelines on running ansible-playbook syntax checks and ansible-lint. |
| `asimp-core-workflow` | `asimp-core-workflow` | Highlights Phase 1, Phase 2, and Phase 3 of the core ASIMP workflow. |
| `dsom-infrastructure-playbook-documenter` | `dsom-infrastructure-playbook-documenter` | Standards for playbook authoring, validation ladder, idempotency gates, and Red Hat CoP / Zen of Ansible compliance. |
| `el-cis-level2-hardening` | `el-cis-level2-hardening` | Guides on Enterprise Linux CIS Level 2 auditing and hardening profiles. |
| `jekyll-docs-deployment` | `jekyll-docs-deployment` | Procedures for pre-processing docs and managing GitHub Pages deployments. |
| `jinja2-template-overrides` | `jinja2-template-overrides` | Rules for setting Jinja2 block trim headers with capitalized booleans. |
| `jules-sandbox-mode` | `jules-sandbox-mode` | Handling of sandboxed, unprivileged execution environments. |
| `ubuntu-scap-auditing` | `ubuntu-scap-auditing` | Guides on running SCAP scanner, fetching latest datastreams, and checking USN OVAL. |

### Deep State of Mind (DSOM) Protocol

The DSOM AI Protocol aligns agent-specific operational rules, linking local skill folders with central platform standards. Every `.agents/skills/<skill-folder>/SKILL.md` ends with a DSOM JSON block stating its synchronization status and signature, ensuring complete spatial alignment between Jules and human operators.

---

## 🔒 Google Jules Sandbox Limitations & Compatibility Standards

### ⚠️ Google Jules Sandbox Constraints & Sudo Correction

Although the `jules` user is configured with passwordless `sudo` privileges via `(ALL : ALL) NOPASSWD: ALL` inside the sandbox, virtualization limits prevent modifying host kernel settings or controlling restricted system services.
- **Kernel & Configuration Restrictions**: Modifying `/etc/sysctl.conf` or loading custom kernel modules is blocked.
- **Service Controls**: Managing container-restricted services such as `auditd`, `chrony`, `firewalld`, `autofs`, or `clamav` will fail or hang.
- **Upgrade Operations**: Deep system package upgrades like `apt upgrade` or `dnf upgrade` can stall or consume excessive resources.
- **Integrity Verifiers**: Running file verifications like `debsums` is restricted on sandbox file structures.

### 📜 Mandatory Playbook Compliance Standard

To run successfully under any context, all playbooks must dynamically detect the execution environment and adjust behavior:
- **Environment Detection**: Detect the Google Jules sandbox by checking if `/home/jules` exists. Set the `is_sandbox_jules` fact accordingly.
- **Conditional Enforcement & Privilege Scaling**: Set `asimp_privilege_level` to `'limited'` when running in sandboxes or without full root permissions, and to `'full'` on real unconstrained operating systems.
  - **Limited/Sandbox Mode**: Run in non-destructive, audit/test/info mode only. Bypasses package upgrades, heavy downloads, and skips system-level remediation roles.
  - **Real OS Mode**: run full-throttle remediations, package upgrades, and auditing with full privileges.
- **Pre-Remediation Safety & Break-Prevention Verification**: When `asimp_privilege_level == 'full'`, the playbook must execute rigorous pre-remediation safety checks before hardening. These checks assert SSH syntax checks (`sshd -t`), root space availability, and `/etc/fstab` health to ensure that remediation tasks will not break the host system or active project codes.

---

## 🛠️ Code Conventions & File Hierarchy

To maintain the high-fidelity auditability of ASIMP, developers and agents must adhere to the following file conventions:
- Use Fully Qualified Collection Names (FQCN) for all tasks.
- Avoid deprecated features and ensure strict idempotency of every command/shell execution.
- Maintain standardized layouts for documentation and playbook structures.

---

## 🏛️ Governance Rules

### Rule 32.43: Automated Ansible Playbook Validation Ladder & Idempotence Assertion Standard

Whenever the AI generates, refactors, or fixes Ansible playbooks, roles, or tasks, it must strictly adhere to the Declarative Validation Ladder:
1. **Deterministic Static Gates:** The AI must ensure all tasks use Fully Qualified Collection Names (FQCN, e.g. `ansible.builtin.package`), descriptive capitalized task names, and strictly prohibit bare `shell`/`command` tasks unless accompanied by explicit idempotency guards (`changed_when`, `creates`, or `removes`). Plaintext secrets are strictly banned, and tasks handling vaulted secrets must specify `no_log: true`.
2. **Tiered Validation Sequence:** Playbook code must pass:
   - (a) **Tier 1 & 2 Syntax validation:** `ansible-playbook <playbook.yml> --syntax-check`
   - (b) **Tier 3 Static standards validation:** `ansible-lint --profile production` (or project-defined lint rules)
   - (c) **Tier 4 Dry-run verification:** `ansible-playbook --check --diff` against testbed inventory where supported
3. **The Two-Pass Idempotence Assertion:** In testbeds and staging environments, true declarative compliance requires a two-pass execution: Run 1 must converge successfully; Run 2 must complete with `changed=0, failed=0`. Any positive change count on Run 2 denotes procedural regression that must be corrected before production promotion.
4. **Execution Blast Radius Isolation:** The AI is strictly prohibited from applying generated or unvalidated playbooks directly to production carrier inventories without prior syntax validation and operator review.

### Rule 32.44: Ansible Community AI-Forge & Red Hat CoP Automation Good Practices Standard

When authoring, refactoring, or auditing Ansible playbooks, roles, and inventories, the AI must enforce the Red Hat Communities of Practice (CoP) Automation Good Practices and the Zen of Ansible:
1. **The Zen of Ansible Philosophical Gate:** Playbooks are declarative specifications, not procedural programs. The AI must prohibit Jinja2 Python abuse, deep YAML nesting, and excessive `when` conditional chains. Simple, readable, declarative automation takes precedence over complex abstractions.
2. **Authoring Style Invariants:**
   - (a) **Syntax & Layout:** 2-space indentation, `.yml` extension, structured YAML argument mapping (no `key=value` string syntax), and lowercase `true`/`false` booleans;
   - (b) **Naming & Facts:** Imperative capitalized task names, `snake_case` identifiers, `<role_name>_` variable prefixes, `__<role_name>_` internal constant prefixes, and bracket fact notation (`ansible_facts['distribution']`);
   - (c) **Module Trust & Hygiene:** Highest-trust module selection (`ansible.builtin` -> vendor collections -> custom), explicit `state:`, modern `loop:`, and `failed_when:` over `ignore_errors: true`;
   - (d) **Template Discipline:** Mandatory `{{ ansible_managed | comment }}` header at the top of all Jinja2 configuration templates.
3. **CoP 14-Category Review Checklist:** Code reviews of playbooks and roles must evaluate against the 14 standard categories (YAML Style, Naming, Module Usage, Task Structure, Handlers, Templates, Variables, Playbook Structure, Inventory, Error Handling, Idempotency, Argument Specs, Tags, Platform Support) and emit prioritized actionable recommendations.

---

## 📖 Google Open Knowledge Format (OKF) v0.2 Specification

All documentation within this repository conforms to the Google Open Knowledge Format (OKF) v0.2.

### 📐 Required Frontmatter Fields

Every Markdown file must begin with a YAML frontmatter block containing:
1. `okf_version`: Declaring `"0.2"`.
2. `trust_level`: Trust verification level (e.g., `"verified"`).
3. `type`: File category (e.g., `instructions`, `documentation`).
4. `title`: Page header string.
5. `timestamp`: ISO-8601 creation/modification time.
6. `topics`: A list of relevant tags or keywords.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
