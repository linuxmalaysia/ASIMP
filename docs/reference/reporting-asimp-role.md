---
title: "Role reporting-ASIMP Reference"
description: "Detailed specification of the reporting-ASIMP role metrics engine and compliance scorecard parser."
type: "reference"
id: "docs/reference/reporting-asimp-role.md"
dsom_governance:
  domain: "Security"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "role"
  - "reporting"
  - "openscap"
  - "lynis"
related_links:
  - "docs/reference/index.md"
nav_order: 130
layout: "default"
---

# Role `reporting-ASIMP` Reference

The `reporting-ASIMP` role handles OpenSCAP/Lynis baselining, delta calculation, and output report compiling.

---

## ⚙️ Key Variables & Defaults

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `scap_profile` | `xccdf_org.ssgproject.content_profile_cis_level2_server` | Targeted compliance profile. |
| `openscap_scan_supported` | `false` (on sandbox) | Specifies whether live scanning should be bypassed. |
| `is_sandbox_jules` | `false` | Automatically set to True in sandbox environments. |

---

## 🔒 Execution Flow

1. Executes Pre-scan metrics collections.
2. Extracts and parses OpenSCAP scores and Lynis hardening indices.
3. Compiles pre/post-remediation metrics into comparative reports.
