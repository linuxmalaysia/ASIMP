---
okf_version: "0.1"
layout: default
type: documentation
title: "Local Knowledge-First & Metadata Discovery"
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, SOP, metadata, discovery, OKF]
---


# Local Knowledge-First & Metadata Discovery

To prevent unnecessary exploratory terminal commands, token window exhaustion, and context loss during agentic development sessions, AI agents must adhere to the **Local Knowledge-First Protocol**. All project facts, architectural specifications, inventory mappings, and operational rules are indexed via **OKF v0.1 YAML Frontmatter** in `.agents/skills/` and `docs/`.

---

## 🧭 The 5-Step Discovery Flow

AI agents must navigate the following protocol sequentially to answer questions, debug issues, or execute changes:

### Step 1: Local Frontmatter & Metadata Search
Search local OKF headers using keywords on `topics:` or `description:` across `docs/` and `.agents/skills/` **before** running system terminal commands.

### Step 2: Targeted File Viewing
Read specific file segments or targeted markdown documents locally instead of executing full-file dumps or remote probes.

### Step 3: Temporal Verification Gate
Inspect the OKF `timestamp` metadata. If the local document appears contextually outdated, research external standards and present a comparison to the human operator.

### Step 4: Human Verification & Knowledge Update
With human consensus, update the local OKF-compliant document to preserve spatial memory before executing infrastructure modifications.

### Step 5: Terminal Execution Gate
Only execute remote terminal queries or run Ansible commands against the target inventory if applying planned updates or querying undocumented real-time state.

---

## 🔒 Mandatory Metadata Rules

1. **Frontmatter Definition**: Every Markdown file must begin with a YAML block starting on line 1 with `---` and closing with `---`.
2. **Mandatory OKF Keys**: Frontmatter must define `okf_version`, `type`, `title`, `timestamp`, and `topics`.
3. **No Drift Policy**: The set of directories under `.agents/skills/` must exactly match the skills documented in `AGENTS.md`.
4. **Standard Footer Compliance**: All markdown documents must end with the standard ASIMP/DSOM footer to ensure consistent branding and legal coverage.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
