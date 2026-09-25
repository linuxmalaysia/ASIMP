---
name: dsom-infrastructure-playbook-documenter
description: Authoritative SOP and review guidelines for Ansible playbook authoring, validation ladder, idempotency gates, and Red Hat CoP/Zen of Ansible compliance (Rules 32.43 & 32.44).
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: DSOM Infrastructure Playbook Documenter & Validation Standard
resource: .agents/skills/dsom-infrastructure-playbook-documenter
tags: [ansible, idempotency, validation-ladder, redhat-cop, zen-of-ansible, linting, dsom]
timestamp: 2026-08-05T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.2"
trust_level: "verified"
topics: [ansible, idempotency, validation-ladder, redhat-cop, zen-of-ansible, linting, dsom]
---

# DSOM Infrastructure Playbook Documenter & Validation Standard

This skill establishes the standard operational procedures (SOPs) for authoring, validating, generating, and reviewing Ansible playbooks, roles, and tasks across carrier, enterprise, and air-gapped environments within DSOM (Rules 32.43 and 32.44).

## When to Use This Skill

Activate this skill when:
- Creating, refactoring, or updating any Ansible playbook, role, or task file.
- Performing pre-execution or pre-commit code reviews of Ansible playbooks.
- Auditing existing playbooks against Red Hat CoP Automation Good Practices or the 5-tier validation ladder.

## 1. Automated Playbook Validation Ladder & Idempotence Assertion (Rule 32.43)

### Pre-Execution Static Gates (Fast-Fail)
Before running any generated or modified Ansible code, enforce these deterministic gates:
- **FQCN Mandatory:** All module calls must use Fully Qualified Collection Names (e.g. `ansible.builtin.package`, `ansible.builtin.copy`).
- **Idempotency Markers:** Prohibit bare `ansible.builtin.shell`, `ansible.builtin.command`, or `ansible.builtin.raw` tasks unless accompanied by `changed_when`, `creates`, or `removes`.
- **Secret Protection:** Banned plaintext passwords, private keys, or API tokens. Tasks handling secrets must specify `no_log: true`.
- **Imperative Naming:** Every play, task, and block must have a clear, capitalized, imperative name.

### The 5-Tier Ascending Cost Validation Ladder
1. **Tier 1 (YAML Static Lint):** Fast syntax/structure validation.
2. **Tier 2 (Ansible Syntax Check):** Run `ansible-playbook <playbook.yml> --syntax-check`.
3. **Tier 3 (Ansible-Lint Production Profile):** Run `ansible-lint --profile production` or project-defined lint rules.
4. **Tier 4 (Check Mode / Dry Run):** Run `ansible-playbook --check --diff` against a testbed inventory to surface undefined variables and structural drift.
5. **Tier 5 (Two-Pass Execution & Idempotence Assertion):**
   - **Run 1 (Converge):** First execution applies state changes and converges host.
   - **Run 2 (Assert Idempotency):** Second pass must finish with `changed=0, failed=0`. Any positive change count indicates procedural flaw or non-declarative mutation.

---

## 2. Red Hat CoP Automation Good Practices & Zen of Ansible (Rule 32.44)

### The Zen of Ansible (Philosophical Review Gate)
- *Ansible is not Python:* Avoid inline complex Jinja2 loops or Python logic in templates and task arguments.
- *Playbooks are not programs:* Prohibit deep control-flow nesting, long `when:` conditional chains, and over-abstracted role variables.
- *Declarative over Imperative:* Always prefer purpose-built modules (`ansible.builtin.user`, `ansible.builtin.lineinfile`, `ansible.builtin.cron`) over bare shell scripts (`useradd`, `sed`, `crontab -e`).
- *Convention over Configuration:* Use sensible defaults instead of sprawling configurable knobs.

### 14-Point Authoring & Style Invariants
1. 2-space YAML indentation, `.yml` file extension (not `.yaml`).
2. Structured YAML dictionary arguments for modules (never inline `key=value` strings).
3. Lowercase `true`/`false` booleans.
4. Fully Qualified Collection Names (`ansible.builtin.*`).
5. Imperative capitalized names for tasks, plays, and blocks.
6. Explicit `state:` parameter where supported (`present`, `absent`, `started`, `restarted`).
7. Modern `loop:` construct over legacy `with_*`.
8. Explicit `failed_when:` conditions rather than blanket `ignore_errors: true`.
9. Prefixed variables: `<role_name>_` for public variables, `__<role_name>_` for internal constants.
10. Mandatory `{{ ansible_managed | comment }}` header at the top of all Jinja2 templates.
11. `snake_case` for filenames, variables, and role names.
12. Modern bracket fact notation: `ansible_facts['distribution']` instead of bare `ansible_distribution`.
13. Handlers triggered cleanly for configuration reloads.
14. Conventional Git commit formatting with FQCN scope (e.g. `feat(ansible.builtin.dnf): update security packages`).

### 14-Category Review Rubric
Code reviews must evaluate and score (1–10) playbooks across:
1. YAML Style & Layout
2. Task & Play Naming
3. Module Selection & Trust
4. Task Structure & Flow
5. Handler Hygiene
6. Jinja2 Template Discipline
7. Variable Naming & Scoping
8. Playbook Structure & Modularity
9. Inventory & Group Handling
10. Error Handling & Recovery
11. Machine-Checkable Idempotency
12. Argument Specifications & Validation
13. Tag Strategy
14. Multi-OS Platform Support

---

## 🧠 Deep State of Mind (DSOM) AI Protocol

```json
{
  "protocol": "DSOM",
  "version": "1.0.0",
  "status": "synchronized",
  "alignment": "ASIMP",
  "agent": "Google Jules",
  "integration": "Google Antigravity",
  "signature": "dsom_protocol_jules_antigravity_sync_active"
}
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
