---

description: 'Coding standards and architectural rules for Copilot when working with ASIMP playbooks, roles, and python helper scripts'
applyTo: '**/*.yml, **/*.yaml, **/*.py, **/*.sh'
okf_version: "0.2"
trust_level: "verified"
type: documentation
title: "GitHub Copilot Custom Instructions for ASIMP"
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, general]
---


# GitHub Copilot Custom Instructions for ASIMP

Welcome! Follow these instructions when generating or updating code in the **ASIMP (Ansible System Integrity Management Platform)** codebase.

For comprehensive architectural design, pitfalls, and testing guidelines, please refer directly to [AGENTS.md](AGENTS.md).

---

## 🧭 Project Architecture Overview

ASIMP implements a **Measure, Harden, Re-Measure** sequence across three main roles:
1. `reporting-ASIMP`: Runs baseline scans, parses outcomes, and outputs side-by-side scorecard.
2. `update-ubuntu-ASIMP`: Safely applies system updates and runs background integrity verification.
3. `lynis-ansible`: Applies fine-grained operating system hardening profiles.

---

## 🛠️ Naming Conventions & Code Standards

- **FQCN (Fully Qualified Collection Names)**: Always prefix Ansible built-in and community modules with their namespace/collection names.
- **Strict Idempotency**: Provide explicit `changed_when` rules for shell/command executions so that repeated runs do not erroneously report changes.
- **Fail-Safe Robustness**: Because scanning and auditing depend heavily on local binaries (e.g. `oscap`, `lynis`, `debsums`) which may be absent in some environments, use dynamic feature/existence checking or ignore errors appropriately to enable graceful degradation instead of playbook crashes.
- **No Direct Log/Artifact Modification**: Do not modify system log files under `/var/log` or generated report files directly. Always edit the source playbooks or role files.

---

## 📝 Code Examples

### 1. Module Invocation & FQCN

#### ❌ Bad Example (Implicit name)
```yaml
- name: Install audit tools
  apt:
    name: lynis
    state: present
```

####  Good Example (Fully Qualified)
```yaml
- name: Install audit tools
  ansible.builtin.apt:
    name: lynis
    state: present
    update_cache: yes
```

### 2. Idempotency on Shell Commands

#### ❌ Bad Example (Missing execution state check)
```yaml
- name: Run audit score parser
  shell: python3 /usr/local/bin/parse_openscap_score.py /var/log/before.xml
  register: score
```

####  Good Example (Explicit idempotency marker)
```yaml
- name: Run audit score parser
  ansible.builtin.shell: python3 /usr/local/bin/parse_openscap_score.py /var/log/before.xml
  register: score
  changed_when: false
```

---

## 🏛️ Governance Rules

### Rule 32.43: Automated Playbook Validation Ladder & Idempotence Assertion
All playbook modifications must pass:
1. Pre-execution static gates (FQCN, descriptive imperative names, explicit idempotency flags like `changed_when`, `no_log: true` on secrets).
2. 5-Tier Validation Ladder (YAML static lint -> `ansible-playbook --syntax-check` -> `ansible-lint` -> check mode dry run -> two-pass execution where pass 2 asserts `changed=0, failed=0`).
3. Execution blast radius isolation (never run unvalidated playbooks directly on production).

### Rule 32.44: Red Hat CoP Automation Good Practices & Zen of Ansible
1. Zen of Ansible: Declarative over procedural, simple over complex, convention over configuration. Prohibit Jinja2 Python abuse and deep `when:` nesting.
2. Authoring standards: 2-space indentation, `.yml` extensions, structured YAML arguments, lowercase `true`/`false` booleans, bracket fact notation (`ansible_facts['...']`), `<role_name>_` variable prefixes, and `{{ ansible_managed | comment }}` in Jinja2 templates.
3. Review against 14 CoP audit categories.

---

## 🧪 Verification Protocol

Always verify all playbooks and role changes using syntax validation and lint checks:
```bash
ansible-playbook --syntax-check play-localhost.yml
ansible-lint play-localhost.yml
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
