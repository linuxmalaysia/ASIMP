---
okf_version: "0.1"
type: "reference"
title: "OpenWiki Emulator Specification"
description: "Technical reference for the lightweight, LangChain-compatible local conceptual memory indexer."
timestamp: "2026-08-15T00:00:00Z"
topics: ["openwiki", "ai", "emulator", "reference"]
id: "docs/reference/openwiki-emulator.md"
dsom_governance:
  domain: "AI"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 20
layout: "default"
---

# OpenWiki Emulator Specification

The **OpenWiki Emulator** is a high-density, conceptual memory indexer that compiles complex repository structures into a compact, lightweight format optimized for low-token AI traversal.

---

## ⚙️ Functional Specifications

The emulator reads Markdown files from `docs/` and `.agents/` and produces:
1. **`./openwiki/.last-update.json`**: Tracking indexing metadata and schema hashes.
2. **`./openwiki/_skeleton.md`**: Representing the lightweight knowledge graph skeleton.

---

## 📄 Schemas & Signatures

### Last Update JSON Schema
```json
{
  "last_updated": "ISO-8601 Timestamp",
  "files_count": "integer",
  "hash": "SHA-256 sum of skeleton structure"
}
```

### Skeleton Markdown Format
```markdown
# Repository Topology Skeleton

- **Domain: Security** -> [DSOM Governance](docs/explanation/dsom-governance.md)
- **Domain: Automation** -> [Diátaxis Architecture](docs/explanation/diataxis.md)
```

---

## 🚪 Exit States

| Exit Code | Cause |
| :--- | :--- |
| `0` | Success: Graph compiled and output directories written. |
| `1` | Failure: Invalid frontmatter or non-readable source directory. |
| `2` | Failure: Syntax error or disk full. |
