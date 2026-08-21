---
okf_version: "0.1"
type: "reference"
title: "Component & Tool Index"
description: "Reference index and catalog of all scripts, tools, APIs, playbooks, and roles inside ASIMP."
timestamp: "2026-08-15T00:00:00Z"
topics: ["reference", "index", "tools", "scripts", "roles"]
id: "docs/reference/index.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/how-to/run-tool.md"
  - "docs/tutorials/01-getting-started.md"
nav_order: 10
layout: "default"
---

# Component & Tool Index

This section provides exhaustive, information-oriented reference specifications for every script, utility, configuration template, and role present in the ASIMP repository.

---

## 🐍 Python & Shell Utility Scripts

* **[OpenWiki Engine Specification](openwiki-emulator.md)**: Specifications for LangChain's OpenWiki emulator and compact concepts index.
* **[ASIMP Standard Footer Patcher](add-asimp-footer.md)**: Reference for `scripts/add_asimp_footer.py`.
* **[Google OKF Frontmatter Patcher](add-okf-frontmatter.md)**: Reference for `scripts/add_okf_frontmatter.py`.
* **[Sovereign Feedback Collector](jules-gh-feedback.md)**: Reference for `scripts/jules_gh_feedback.sh`.
* **[LLM XML Context Compiler](llms-txt2ctx.md)**: Reference for `scripts/llms_txt2ctx.py`.
* **[Sovereign OS Role Patcher](patch-roles.md)**: Reference for `scripts/patch_roles.py`.
* **[Jekyll Pre-processor](prepare-docs.md)**: Reference for `scripts/prepare_docs.py`.
* **[Sitemap & Link Integrity Validator](verify-sitemap-links.md)**: Reference for `scripts/verify_sitemap_links.py`.
* **[Mock Scanning Utility](mock-asimp.md)**: Reference for `tools/mock-asimp.sh`.

---

## ⚙️ Ansible Configuration & Playbooks

* **[Ansible Config Parameters](ansible-cfg.md)**: Reference for standard `ansible.cfg` parameters.
* **[System Core Playbooks](playbooks.md)**: Reference for `play.yml` and `play-localhost.yml`.
* **[Role: reporting-ASIMP](reporting-asimp-role.md)**: Multi-OS compliance metrics parser and reporting system.
* **[Role: update-ubuntu-ASIMP](update-ubuntu-asimp-role.md)**: OS upgrade pipeline and package integrity checking with `debsums`.
* **[Role: lynis-ansible](lynis-ansible-role.md)**: Security assessment and hardening indices.
* **[Role: sysctl-suse-ASIMP](sysctl-suse-asimp-role.md)**: SUSE/SLED 15 SP7 network sysctl hardening and resource auto-scaling.
