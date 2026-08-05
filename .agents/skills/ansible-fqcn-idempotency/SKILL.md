---
name: ansible-fqcn-idempotency
description: Enforces the use of Fully Qualified Collection Names (FQCN) and strict task idempotency using changed_when / failed_when flags. Use when writing or updating any Ansible playbooks or roles.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Ansible FQCN and Task Idempotency Standards
resource: .agents/skills/ansible-fqcn-idempotency
tags: [ansible, fqcn, idempotency, changed_when, failed_when, best-practices]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
---

# Ansible FQCN and Task Idempotency Standards

This skill details ASIMP’s core development constraints regarding module references and state-change reporting. Every Ansible configuration must adhere to these policies to prevent execution drift and style warnings.

## When to Use This Skill

Activate this skill when:
- Creating, refactoring, or updating any task file inside ASIMP roles (`roles/`).
- Introducing new Ansible modules.
- Writing command or shell-based tasks that interact with host-level files or configurations.

## Development Constraints

### 1. Fully Qualified Collection Names (FQCN)
Always call Ansible modules using their fully qualified names. Standard short names are strictly prohibited.
- **Example (Apt)**: Use `ansible.builtin.apt` instead of `apt`.
- **Example (Copy)**: Use `ansible.builtin.copy` instead of `copy`.
- **Example (Shell)**: Use `ansible.builtin.shell` instead of `shell`.

This practice guarantees collection compatibility across environments and prevents name collisions.

### 2. Task Idempotency & Correct Change Logging
Every task must run safely multiple times without introducing changes on secondary executions unless modifications were genuinely performed.
- Shell or command tasks (`ansible.builtin.shell`, `ansible.builtin.command`) always report "changed" by default. You **must** override this with `changed_when` or `failed_when` logic.

```yaml
# INCORRECT (Will always report "changed" state)
- name: Check file existence
  ansible.builtin.command: ls /var/log/asimp-baseline-scores.json

# CORRECT (Idempotent check that maps change state)
- name: Check file existence
  ansible.builtin.command: ls /var/log/asimp-baseline-scores.json
  register: file_check
  changed_when: false
  failed_when: false
```

- When performing actual modifications, specify `changed_when` to reflect the factual state change (e.g., checking text insertion or package updates).

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
