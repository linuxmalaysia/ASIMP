---

description: 'Coding standards and architectural rules for Copilot when working with ASIMP playbooks, roles, and python helper scripts'
applyTo: '**/*.yml, **/*.yaml, **/*.py, **/*.sh'
okf_version: "0.1"
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

## 🧪 Verification Protocol

Always verify all playbooks and role changes using syntax validation and lint checks:
```bash
ansible-playbook --syntax-check play-localhost.yml
ansible-lint play-localhost.yml
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
