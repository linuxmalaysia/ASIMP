---

name: ansible-boolean-conditionals
description: Enforces strict boolean evaluations in Ansible 'when:' conditionals to prevent syntax errors and runtime crashes. Use when writing or modifying Ansible tasks with registered variables.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Strict Boolean Validation in Ansible Conditionals
resource: .agents/skills/ansible-boolean-conditionals
tags: [ansible, conditionals, best-practices, boolean]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [ansible, conditionals, best-practices, boolean]
---


# Strict Boolean Validation in Ansible Conditionals

This skill governs the writing of reliable Ansible conditional tasks. In modern Ansible versions, `when:` statements must evaluate strictly to boolean values (`true` or `false`). Passing a raw string result or unvalidated command stdout can cause crashes.

## When to Use This Skill

Activate this skill when:
- Writing or reviewing Ansible playbook tasks that use `when:` conditionals.
- Checking for compatibility issues or fixing evaluation crashes.
- Utilizing stdout/stderr or search results from registered variables as conditions.

## Best Practices and Rules

### 1. Avoid String Conditionals
Never use a string directly in a conditional where a boolean is expected. Ansible does not automatically treat non-empty strings as `true` in all contexts, leading to parsing warnings or runtime evaluation crashes.

### 2. Explicitly Validate String Length
When validating stdout or similar output, always check its length explicitly:
```yaml
# INCORRECT
when: register_var.stdout

# CORRECT
when: register_var.stdout | length > 0
```

### 3. Handle Undefined Variables Safely
Ensure variables are defined before checking them, or provide default values to avoid "undefined variable" errors:
```yaml
when:
  - register_var is defined
  - register_var.stdout is defined
  - register_var.stdout | length > 0
```

### 4. Cast or Compare Booleans
Use standard jinja2 boolean checks:
```yaml
when: is_sandbox_jules | bool
```

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
