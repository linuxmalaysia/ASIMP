---
okf_version: "0.1"
type: "architecture"
title: "System Architecture & Security Posture"
description: "Detailed system architecture, security pillars, zero-trust model, and dual-engine auditing pipelines of ASIMP."
timestamp: "2026-08-15T00:00:00Z"
topics: ["architecture", "security", "openscap", "lynis", "sandbox"]
id: "docs/explanation/system-architecture.md"
dsom_governance:
  domain: "Infrastructure"
  context_tier: "L1-Overview"
related_links:
  - "docs/explanation/dsom-governance.md"
  - "docs/explanation/diataxis.md"
nav_order: 30
layout: "default"
---

# System Architecture & Security Posture

ASIMP (Ansible System Integrity Management Platform) is designed around a zero-trust, self-observing host-security framework. It implements a rigorous **"Measure, Harden, Re-Measure"** pipeline powered by Ansible, OpenSCAP, and Lynis.

---

## 🏛️ ASIMP Security Pillars

1. **Dual-Engine Audit Pipeline**: Co-orchestrates OpenSCAP (CIS Level 2 compliance scanning) and Lynis (localized Unix system hardening profiling).
2. **Standardized OS Hardening**: Standardizes kernel configuration settings, SSH security parameters, and limits unprivileged user access vectors.
3. **Integrity Validation with `debsums`**: Continuously verifies local package structures against pristine MD5 checksum databases.

---

## 🗺️ Architectural Workflow Flow

The system orchestrates operations across three distinct execution phases, represented in the Mermaid flow below:

```mermaid
graph TD
    A[Start Hardening Run] --> B[Phase 1: Measure Baseline]
    B --> B1[OpenSCAP Pre-Scan]
    B --> B2[Lynis Pre-Audit]
    B1 & B2 --> C[Phase 2: System Hardening]
    C --> C1[update-ubuntu-ASIMP: OS upgrades & debsums]
    C --> C2[lynis-ansible: System Parameters]
    C --> C3[SSH & Kernel baselines applied]
    C1 & C2 & C3 --> D[Phase 3: Re-Measure Post-Hardening]
    D --> D1[OpenSCAP Post-Scan]
    D --> D2[Lynis Post-Audit]
    D1 & D2 --> E[Scorecard Comparative Analysis]
    E --> F[HTML & Markdown security report output]
    F --> G[Telemetry/Feedback streaming]
```

---

## 🔒 Unprivileged Sandbox Compatibility (Google Jules Mode)

When system-level privileges are constrained (such as running inside containerized, unprivileged Google Jules sandboxes):

- **Environment Detection**: The system detects sandbox mode by evaluating `$USER` / `$LOGNAME` equal to `jules` (or checking `/home/jules` existence) and testing whether `/etc/sysctl.conf` is unwritable/restricted, setting the `is_sandbox_jules: true` fact.
- **Role Integration vs. Standalone Script**:
  - **Ansible `reporting-ASIMP` Role**: During playbook runs, the role automatically bypasses live package installs and writes mock comparative scorecards directly into `data/asimp_mock/opt/report/openscap/`.
  - **Standalone `tools/mock-asimp.sh` Utility**: Can be invoked directly as a standalone shell script in unprivileged CLI environments. It checks environment variables (`IS_JULES_MOCK` or `$USER == "jules"`) and Populates identical mock scorecards and report files under `data/asimp_mock/`.
- **Safety Scaling**: Sets `asimp_privilege_level: 'limited'`, skipping heavy package upgrades and kernel-level sysctl manipulations that would fail under unprivileged container namespaces.
