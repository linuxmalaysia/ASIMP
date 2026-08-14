---
title: "LLM XML Context Compiler Reference"
description: "Detailed specification of scripts/llms_txt2ctx.py for converting llms.txt to LLM context."
type: "reference"
id: "docs/reference/llms-txt2ctx.md"
dsom_governance:
  domain: "AI"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "llms-txt"
  - "xml-compiler"
related_links:
  - "docs/reference/index.md"
nav_order: 60
layout: "default"
---

# LLM XML Context Compiler Reference

`scripts/llms_txt2ctx.py` parses a standard `llms.txt` file and builds a complete XML-formatted representation of files listed inside, ideal for loading directly into LLM context prompts.

---

## 🛠️ CLI Arguments & Syntax

```bash
python3 scripts/llms_txt2ctx.py <input_llms.txt> [--optional <True|False>]
```

### Parameters
- `<input_llms.txt>`: Path to the target text index.
- `--optional`: Specifies whether sections labeled as "Optional" should be parsed and included in the output XML (defaults to False).

---

## 🔒 Exit Codes

- `0`: Success. Printed valid XML to `stdout`.
- `1`: Failure due to file not found or invalid syntax.
