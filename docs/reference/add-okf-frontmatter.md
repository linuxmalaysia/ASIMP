---
title: "Google OKF Frontmatter Patcher Reference"
description: "Detailed specification of scripts/add_okf_frontmatter.py for Google OKF v0.1 YAML compliance."
type: "reference"
id: "docs/reference/add-okf-frontmatter.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "okf"
  - "patcher"
related_links:
  - "docs/reference/index.md"
nav_order: 40
layout: "default"
---

# Google OKF Frontmatter Patcher Reference

`scripts/add_okf_frontmatter.py` enforces compliance with the Google Open Knowledge Format (OKF) v0.1 specification by ensuring five mandatory frontmatter fields are present in every Markdown file.

---

## 🗂️ Mandatory Fields Validated

1. `okf_version`: Declaring `"0.1"`.
2. `type`: The semantic category of the file (`instructions`, `documentation`, `skill`, `concept`, etc.).
3. `title`: The display header, parsed from the first Markdown title (`#`).
4. `timestamp`: ISO-8601 formatted modification date.
5. `topics`: List of relevant topics/tags.

---

## 🛠️ CLI Execution

```bash
python3 scripts/add_okf_frontmatter.py
```
*Processes all `.md` files in place recursively.*

---

## 🔒 Exit Codes

- `0`: Success.
- `1`: Failure due to parsing exception or bad file access.
