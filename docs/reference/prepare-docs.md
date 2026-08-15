---
okf_version: "0.1"
type: "reference"
title: "Jekyll Pre-processor Reference"
description: "Detailed specification of scripts/prepare_docs.py for automatic Jekyll front matter generation."
timestamp: "2026-08-15T00:00:00Z"
topics: ["prepare-docs", "jekyll", "frontmatter", "reference"]
id: "docs/reference/prepare-docs.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 80
layout: "default"
---

# Jekyll Pre-processor Reference

`scripts/prepare_docs.py` parses all Markdown files in the repository's `docs/` folder and auto-generates minimal Jekyll front matter blocks if they are missing.

---

## 🛠️ CLI Execution

```bash
python3 scripts/prepare_docs.py
```

- **Scan Directory**: Scans the repository's relative `docs/` directory.
- **Title Inference**: Automatically parses the first `#` or `##` heading line to populate the front matter title, falling back to a formatted version of the file's base name.

---

## 🔒 Exit Codes

- `0`: Success.
- `1`: Directory not found or write-protection error.
