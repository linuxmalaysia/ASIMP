---

name: asimp-core-workflow
description: Automates and guides the execution of the ASIMP 'Measure, Harden, Re-Measure' compliance and system hardening workflow. Use when evaluating systems, applying baselines, or reviewing security compliance deltas.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: ASIMP "Measure, Harden, Re-Measure" Core Workflow
resource: .agents/skills/asimp-core-workflow
tags: [asimp, hardening, compliance, baseline, workflow]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [asimp, hardening, compliance, baseline, workflow]
---


# ASIMP "Measure, Harden, Re-Measure" Core Workflow

This skill contains the foundational workflow principles for the Ansible System Integrity Management Platform (ASIMP). ASIMP integrates OpenSCAP and Lynis to create a repeatable audit-to-remediate-to-audit feedback loop.

## When to Use This Skill

Use this skill whenever you need to:
- Formulate baseline compliance evaluations.
- Direct or inspect the execution sequence of ASIMP playbooks (`play.yml` and `play-localhost.yml`).
- Implement features/fixes in `reporting-ASIMP` or system-hardening roles.
- Understand how pre-hardening ("Measure" before) and post-hardening ("Re-Measure" after) security metrics are extracted and analyzed.

## Workflow Phases

### Phase 1: Measure (Before Baseline)
The workflow initiates with an automated security compliance baseline assessment before any system alterations are made.
- **Engines**: Runs OpenSCAP (SCAP Security Guide content) and Lynis locally.
- **Reporting**: Stores scores in a structured format `/var/log/asimp-baseline-scores.json`.
- **Validation**: Ensures that files are safely written and can be retrieved later.

### Phase 2: Harden (Remediation & Upgrades)
The next step is applying the targeted hardening policies.
- Packages are updated and verified (via `update-ubuntu-ASIMP` using `debsums`).
- System-level hardening parameters are applied (e.g., limits, sysctl, firewalls, and service-specific configurations).

### Phase 3: Re-Measure (After Baseline Verification)
The third phase executes a second round of audits.
- **Engines**: Re-runs OpenSCAP and Lynis.
- **Reporting**: Compares current scores against `/var/log/asimp-baseline-scores.json`.
- **Output**: Generates a comparative scorecard showing the exact security delta/improvement.

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

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
