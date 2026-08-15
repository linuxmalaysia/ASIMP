---
okf_version: "0.1"
type: "reference"
title: "Role update-ubuntu-ASIMP Reference"
description: "Detailed specification of the update-ubuntu-ASIMP role upgrade pipeline and package integrity checking."
timestamp: "2026-08-15T00:00:00Z"
topics: ["upgrade", "debsums", "role", "ubuntu", "reference"]
id: "docs/reference/update-ubuntu-asimp-role.md"
dsom_governance:
  domain: "Infrastructure"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 140
layout: "default"
---

# Role `update-ubuntu-ASIMP` Reference

The `update-ubuntu-ASIMP` role coordinates OS upgrades and package integrity monitoring via filesystem check utilities.

---

## ⚙️ Key Variables & Defaults

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `upgrade_packages` | `true` | Enforces standard security package updates. |
| `debsums_check` | `true` | Enables background file verification checks against original package checksums. |
| `rpmsums_check` | `true` | Triggers RedHat file verification via `rpm -Va` command. |

---

## 🔒 Constraints & Limits

Under sandbox contexts (`is_sandbox_jules: true`), the execution skips destructive system package upgrades and ignores errors on restricted filesystem checkers.
