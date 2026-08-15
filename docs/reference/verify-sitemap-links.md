---
okf_version: "0.1"
type: "reference"
title: "Sitemap & Link Integrity Validator Reference"
description: "Detailed specification of scripts/verify_sitemap_links.py sitemap validator."
timestamp: "2026-08-15T00:00:00Z"
topics: ["sitemap", "validator", "links", "reference"]
id: "docs/reference/verify-sitemap-links.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 90
layout: "default"
---

# Sitemap & Link Integrity Validator Reference

`scripts/verify_sitemap_links.py` performs rigorous pre-merge validation of all sitemap links across GitBook and GitHub Pages targets.

---

## 🧭 Major Validation Phases

1. **Synchronization check**: Compares root `sitemap.txt` and `sitemap.xml` with `docs/sitemap.txt` and `docs/sitemap.xml`.
2. **Structural check**: Confirms XML and text sitemaps match perfectly.
3. **SSRF Host Check**: Limits HTTP requests strictly to allowed hostnames (`linuxmalaysia.github.io` and `malaysia-open-source-community.gitbook.io`).
4. **GitBook Sampling**: Validates a deterministic sample of five GitBook URLs loaded from a separate validation inventory.
5. **Pre-merge fallback**: If a GitHub Pages URL reports 404, verifies if its corresponding source `.md` file is present locally under `docs/`.

---

## 🔒 Exit Codes

- `0`: Success. All links verified and sitemaps aligned.
- `1`: Failure. Broken links or misaligned sitemaps detected.
