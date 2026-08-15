---
okf_version: "0.1"
type: "reference"
title: "ASIMP Standard Footer Patcher Reference"
description: "Detailed specification of scripts/add_asimp_footer.py for automating standard attributions."
timestamp: "2026-08-15T00:00:00Z"
topics: ["footer", "patcher", "python", "reference"]
id: "docs/reference/add-asimp-footer.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 30
layout: "default"
---

# ASIMP Standard Footer Patcher Reference

`scripts/add_asimp_footer.py` scans the repository and appends standard footer attributions to Markdown files.

---

## 🛠️ CLI Arguments & Syntax

```bash
python3 scripts/add_asimp_footer.py
```
*No arguments are required or parsed.*

---

## ⚙️ Configuration & Exclusion Rules

The script excludes several directories by default to prevent altering third-party role sources or built pages:
- `.git`
- `node_modules`
- `venv`, `.venv`
- `lynis-ansible` (submodule)
- `asimp_mock` (mock reporting directory)
- `docs` (pre-processed Jekyll templates)

---

## 🔒 Exit Codes

- `0`: Success. All eligible files scanned and modified if necessary.
- `1`: Unexpected exception (e.g., file permissions or filesystem error).
