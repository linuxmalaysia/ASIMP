---
okf_version: "0.1"
type: "guide"
title: "Execute Tool Workflows"
description: "How to use ASIMP's python and shell utility scripts to automate common compliance, patching, and documentation validation tasks."
timestamp: "2026-08-15T00:00:00Z"
topics: ["guide", "how-to", "scripts", "workflows"]
id: "docs/how-to/run-tool.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L2-Operational"
related_links:
  - "docs/how-to/index.md"
  - "docs/reference/index.md"
nav_order: 20
layout: "default"
---

# Execute Tool Workflows

This guide provides concrete, problem-solving procedures for executing ASIMP's system and workspace utilities.

---

## 🧭 How to Patch File Footers Idempotently

To enforce standard corporate and protocol attributions across all Markdown files (excluding `docs/` files):

### Prerequisites

- Active Python virtual environment.

### Command Block

```bash
python3 scripts/add_asimp_footer.py
```

### Expected Output

```text
Successfully appended standard footer to: ./README.md
No update needed (already has footer): ./AGENTS.md
```

---

## 🗂️ How to Enforce Google OKF v0.1 Frontmatter

To scan and update workspace `.md` documents with the five mandatory YAML fields (okf_version, type, title, timestamp, topics):

### Command Block

```bash
python3 scripts/add_okf_frontmatter.py
```

### Expected Output

```text
Updated OKF v0.1 frontmatter in README.md with: ['okf_version: "0.1"']
No OKF v0.1 updates needed for docs/index.md
```

---

## ⚙️ How to Patch Third-Party Roles for Sandbox Compatibility

If you install fresh external Galaxy roles and need to patch systemd services or Jinja templates on-the-fly for unprivileged Google Jules runs:

### Command Block

```bash
python3 scripts/patch_roles.py
```

### Expected Output

```text
Starting ASIMP Sovereign OS Role Compatibility Patcher...
Patched SSH template: roles/dev-sec.ssh-hardening/templates/opensshd.conf.j2 (1 replacements)
Patched YAML file: roles/dev-sec.ssh-hardening/tasks/hardening.yml
ASIMP Patcher finished successfully.
```

---

## 🌐 How to Compile High-Density XML Context for LLM Agents

To parse the `llms.txt` file and generate a single XML document containing embedded Markdown contents for Anthropic Claude or other models:

### Command Block

```bash
python3 scripts/llms_txt2ctx.py llms.txt --optional=false > compiled_context.xml
```

---

## 🗺️ How to Verify Sitemap Links Before Committing

To ensure that both root sitemaps and deployed sitemaps match perfectly and that all relative URLs point to valid on-disk markdown sources:

### Command Block

```bash
python3 scripts/verify_sitemap_links.py
```

### Expected Output

```text
[*] Starting Sitemap and Link Integrity Verification...
[+] Deployed copy docs/sitemap.txt is perfectly synchronized with root sitemap.txt (txt sitemap).
[+] Structural check passed: sitemap.txt and sitemap.xml URL lists match perfectly.
[+] GitHub Pages URL OK (Source exists on disk, pre-merge): https://linuxmalaysia.github.io/ASIMP/architecture.html -> docs/architecture.md
[+] All verified sitemap links and inventory URLs are fully operational and synchronized!
```
