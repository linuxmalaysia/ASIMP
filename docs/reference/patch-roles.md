---
title: "Sovereign OS Role Patcher Reference"
description: "Detailed specification of scripts/patch_roles.py for on-the-fly sandbox compatibility patching."
type: "reference"
id: "docs/reference/patch-roles.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "roles"
  - "patcher"
related_links:
  - "docs/reference/index.md"
nav_order: 70
layout: "default"
---

# Sovereign OS Role Patcher Reference

`scripts/patch_roles.py` scans downloaded Ansible Galaxy roles and automatically applies unprivileged sandbox compatibility corrections.

---

## 🛠️ Execution Context

```bash
python3 scripts/patch_roles.py
```
*Processes files in `roles/` directory.*

---

## ⚙️ Modifications Applied

1. **Jinja2 Parameter Parsing**: Ensures `#jinja2: trim_blocks: True` syntax uses uppercase capitalized booleans instead of lowercase string quotes.
2. **Strict Boolean Evaluation**: Patches registered string variables (e.g., `stdout` or list values) used in Ansible `when:` conditionals to explicitly validate string lengths.
3. **Graceful Error Bypass**: Appends `ignore_errors: "{{ is_sandbox_jules | default(false) }}"` on container-restricted systemd and service modules.

---

## 🔒 Exit Codes

- `0`: Success.
- `1`: Failure.
