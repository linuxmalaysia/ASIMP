---

name: ansible-testing-linting
description: Guides syntax validation and linting checks on ASIMP Ansible playbooks and roles. Use before committing changes to ensure formatting, structure, and execution conform to standard rules.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Ansible Playbook Syntax Checking and Linting
resource: .agents/skills/ansible-testing-linting
tags: [ansible, testing, linting, syntax-check, validation]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [ansible, testing, linting, syntax-check, validation]
---


# Ansible Playbook Syntax Checking and Linting

This skill enforces strict syntactic correctness and linting standards for Ansible playbooks and roles within ASIMP, avoiding runtime failures and broken states.

## When to Use This Skill

Activate this skill when:
- Reviewing or modifying playbooks (`play.yml`, `play-localhost.yml`).
- Creating new roles or adding tasks under `roles/`.
- Preparing files for commit and pull requests (specifically during the pre-commit steps).

## Validation Commands

You must run the following checks on playbooks whenever any YAML configs or tasks are changed.

### 1. Playbook Syntax Verification
Ensure there are no syntax errors in your Ansible YAML playbooks:
```bash
ansible-playbook --syntax-check play.yml
ansible-playbook --syntax-check play-localhost.yml
```

### 2. Playbook Style & Lint Checking
Validate code against standard community best practices using `ansible-lint`:
```bash
ansible-lint play-localhost.yml
```
All errors must be resolved before finalizing any change.

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
