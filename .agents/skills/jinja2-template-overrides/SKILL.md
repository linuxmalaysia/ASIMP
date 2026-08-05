---

name: jinja2-template-overrides
description: Formats modern Jinja2 template parameter override headers correctly using capitalized Python booleans (True/False). Use when writing or modifying Jinja2 templates inside Ansible roles.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Jinja2 Template Parameter Override Headers
resource: .agents/skills/jinja2-template-overrides
tags: [jinja2, templates, ansible, headers]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [jinja2, templates, ansible, headers]
---


# Jinja2 Template Parameter Override Headers

This skill governs the exact syntax required for Jinja2 template parameter override headers. Modern Jinja2 parsing engines are strict about header format types.

## When to Use This Skill

Activate this skill when:
- Creating or editing Jinja2 templates (`*.j2` files) in Ansible roles.
- Adjusting template formatting, block trimming, or whitespace behavior.
- Troubleshooting Jinja2 parsing and template generation syntax errors.

## Standard Header Convention

### 1. Capitalized Python Booleans
When overriding Jinja2 parameters, you must use capitalized Python booleans (`True` or `False`). Lowercase quoted strings or lowercase unquoted booleans will result in a template syntax error or parsing crash.

```jinja2
# INCORRECT (will cause parsing syntax error)
#jinja2: trim_blocks: "true"

# INCORRECT
#jinja2: trim_blocks: true

# CORRECT
#jinja2: trim_blocks: True, lstrip_blocks: True
```

### 2. Strict Header Placement
The override header must always occupy the absolute first line of the Jinja2 template file. No whitespace, empty lines, or comments should precede it.

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
