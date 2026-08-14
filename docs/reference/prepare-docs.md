---
title: "Jekyll Pre-processor Reference"
description: "Detailed specification of scripts/prepare_docs.py for automatic Jekyll front matter generation."
type: "reference"
id: "docs/reference/prepare-docs.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "prepare-docs"
  - "jekyll"
related_links:
  - "docs/reference/index.md"
nav_order: 80
layout: "default"
---

# Jekyll Pre-processor Reference

`scripts/prepare_docs.py` parses all Markdown files in the `docs/` folder and auto-generates minimal Jekyll front matter blocks if they are missing.

---

## 🛠️ CLI Execution

```bash
python3 scripts/prepare_docs.py
```

- **Scan Directory**: Scans `/docs` folder.
- **Title Inference**: Automatically parses the first H1/H2 header to populate the front matter title.

---

## 🔒 Exit Codes

- `0`: Success.
- `1`: Directory not found or write-protection error.
