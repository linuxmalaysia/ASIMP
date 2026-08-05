---
name: ai-agent-instructions
description: Coordinates cross-client AI developer guidelines and rules across various LLM assistants. Use when modifying agent rules, aligning conventions, or adding client-specific instructions.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Multi-Agent AI Instruction Mapping
resource: .agents/skills/ai-agent-instructions
tags: [ai, agents, rules, guidelines, clients]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
---

# Multi-Agent AI Instruction Mapping

This skill outlines the structured system used to manage instructions across different AI clients. To keep development guidelines consistent across editors and execution tools, specific targeted rule files are placed throughout the codebase.

## When to Use This Skill

Activate this skill when:
- Creating or editing LLM-specific operational rules or guidelines.
- Aligning rules for different code editors (Cursor, Windsurf, Cline/Roo-Cline, Claude Code, GitHub Copilot).
- Ensuring all AI engines respect ASIMP’s core architectural constraints.

## Cross-Referencing File Hierarchy

Ensure any modifications are synchronized and align with the following cross-referenced rule files:

| Agent / Editor | Target Instruction File | Primary Focus |
| :--- | :--- | :--- |
| **All Agents / Hub** | `AGENTS.md` | General architecture, coding standards, testing workflow |
| **Claude Code** | `CLAUDE.md` | Tool-specific quick commands and styling preferences |
| **Cursor** | `.cursorrules` | Autocomplete parameters and chat assistance style |
| **Cline / Roo-Cline** | `.clinerules` | Permission-based automation constraints and idempotency |
| **Windsurf** | `.windsurfrules` | Interactive editor/terminal integration boundaries |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Inline suggestion quality and security baseline standards |

All instruction files are strictly aligned to the core architectural constraints of the "Measure, Harden, Re-Measure" workflow of ASIMP.

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
