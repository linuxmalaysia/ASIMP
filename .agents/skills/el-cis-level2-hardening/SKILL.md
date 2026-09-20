---

name: el-cis-level2-hardening
description: Manages OpenSCAP CIS Level 2 auditing, SSG DataStream resolution, and automated Ansible hardening across RHEL 8/9/10, AlmaLinux 8/9/10, Rocky Linux 8/9/10, and Oracle Linux 8/9/10. Use when configuring or evaluating CIS Level 2 profiles or executing reporting vs remediation modes on Enterprise Linux.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Enterprise Linux CIS Level 2 Auditing & Hardening Engine
resource: .agents/skills/el-cis-level2-hardening
tags: [scap, openscap, rhel, almalinux, rockylinux, oraclelinux, cis, level2, hardening]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.2"
trust_level: "verified"
sidebarTitle: "EL CIS L2 Hardening"
topics: [scap, openscap, rhel, almalinux, rockylinux, oraclelinux, cis, level2, hardening]
---


# Enterprise Linux CIS Level 2 Auditing & Hardening Engine

This skill outlines the mechanisms used by ASIMP to perform robust CIS Security Linux Level 2 auditing, DataStream resolution, and automated Ansible hardening across RHEL 8, 9, 10, AlmaLinux 8, 9, 10, Rocky Linux 8, 9, 10, and Oracle Linux 8, 9, 10.

## When to Use This Skill

Activate this skill when:
- Evaluating host compliance against the CIS Level 2 profile (`xccdf_org.ssgproject.content_profile_cis`).
- Resolving host-native SCAP Security Guide DataStreams (`ssg-rhel8-ds.xml`, `ssg-almalinux8-ds.xml`, `ssg-rocky8-ds.xml`, `ssg-ol8-ds.xml`, EL9, EL10).
- Running non-destructive Reporting Only mode (`execution_mode: "report"`) vs active Remediation mode (`execution_mode: "remediate"`).
- Writing reports, Bash fix scripts, and Ansible fix playbooks into `/opt/report/openscap`.

## Core Procedures

### 1. DataStream Resolution with Fallback
To ensure valid compliance scoring across all Enterprise Linux major releases:
- Dynamically resolve the distribution-preferred DataStream path (`ssg-almalinux8-ds.xml`, `ssg-rocky8-ds.xml`, `ssg-ol8-ds.xml`, `ssg-rhel8-ds.xml`).
- Check file existence with `ansible.builtin.stat`. If preferred path is absent, fall back to the RHEL DataStream (`ssg-rhel8-ds.xml`).

### 2. Operational Mode Delineation
- **Mode 1: Reporting Only (`execution_mode: "report"`)**: Performs non-destructive `oscap xccdf eval` scans with `changed_when: false`, outputs HTML/XML reports, generates fix scripts (`oscap xccdf generate fix`), and makes ZERO system configuration changes.
- **Mode 2: Doing (`execution_mode: "remediate"`)**: Performs baseline assessment scan (Phase 1), applies automated Ansible hardening for storage mount options, PAM password complexity, crypto-policies, SSH daemon, sysctl network parameters, and auditd (Phase 2), conducts post-remediation verification scan (Phase 3), and presents comparative scorecards.

### 3. Report Output & Unavailable Score Handling
- Write all generated XML, HTML, YAML, shell, and Python parser scripts exclusively to `/opt/report/openscap`.
- Handle scan or parsing failures gracefully by marking scores as `UNAVAILABLE` rather than reporting invalid false-positive percentages.

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

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
