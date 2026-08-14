---
title: "Role lynis-ansible Reference"
description: "Detailed specification of the lynis-ansible role system auditing configurations."
type: "reference"
id: "docs/reference/lynis-ansible-role.md"
dsom_governance:
  domain: "Security"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "role"
  - "lynis"
  - "auditing"
related_links:
  - "docs/reference/index.md"
nav_order: 150
layout: "default"
---

# Role `lynis-ansible` Reference

The `lynis-ansible` role automates Unix-based local systems security auditing using the Lynis engine.

---

## ⚙️ Key Variables & Defaults

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `lynis_profile` | `default` | Scan profile name. |
| `lynis_tests_to_skip` | `[]` | List of tests to skip. |
| `lynis_extra_parameters` | `""` | Extra arguments for the `lynis audit system` command. |

---

## 💾 Extracted Metrics

- **Hardening Index**: An overall numerical representation of how secure the system configurations are (0 to 100).
- **Warnings and Suggestions**: Logged under `/var/log/lynis-report.dat` for post-hardening review.
