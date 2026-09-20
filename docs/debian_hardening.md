---
layout: default
okf_version: "0.2"
trust_level: "verified"
type: documentation
title: "Debian GNU/Linux Hardening & Audit Guide"
sidebarTitle: "Debian Hardening Guide"
timestamp: "2026-08-05T12:00:00Z"
topics: [debian, openscap, lynis, audit, remediation, ansible, debsums]
---

# Debian GNU/Linux Hardening & Audit Guide

**Debian GNU/Linux** is renowned for its stability, security, and adherence to free software principles. Securing Debian systems across enterprise server deployments requires package integrity monitoring (`debsums`), system file permission isolation, kernel network hardening, and dual-engine security auditing using Lynis and OpenSCAP.

This guide details the **Ansible System Integrity Management Platform (ASIMP)** workflow for evaluating, auditing, and hardening Debian GNU/Linux distributions.

---

## 🧭 Scope & Distribution Matrix

ASIMP provides target-aware validation for stable Debian releases, integrating package integrity checking (`debsums`), SCAP evaluation, and Lynis security auditing:

| Distribution | Version | Integrity Engine | Audit Engines Supported | Playbook Target |
| :--- | :--- | :--- | :--- | :--- |
| **Debian 11 (Bullseye)** | `11` | `debsums` (MD5 Checksums) | OpenSCAP, Lynis | `playbooks/debian_hardening.yml` |
| **Debian 12 (Bookworm)** | `12` | `debsums` (MD5 Checksums) | OpenSCAP, Lynis | `playbooks/debian_hardening.yml` |
| **Debian 13 (Trixie)** | `13` | `debsums` (MD5 Checksums) | OpenSCAP, Lynis | `playbooks/debian_hardening.yml` |

---

## 📊 Architectural Paradigm: Mode Separation

ASIMP strictly separates operations into two distinct execution modes, controlled via the `execution_mode` variable:

1. **Mode A: Reporting Only (`execution_mode: "report"`)**:
   - Performs non-destructive compliance scanning and evaluation.
   - Outputs visual HTML reports and XML results.
   - Does not apply hardening, but may create report directories and files.

2. **Mode B: Doing (`execution_mode: "remediate"`)**:
   - Performs a pre-remediation baseline assessment ("Phase 1: Measure").
   - Applies `debsums` package integrity checks, file permission controls, SSH hardening, and kernel sysctl tuning ("Phase 2: Harden").
   - Executes a post-remediation evaluation scan ("Phase 3: Re-Measure").
   - Outputs a comparative scorecard.

---

## 🚀 Ansible Playbook Execution Guide

The dedicated playbook `playbooks/debian_hardening.yml` automates both modes across all supported Debian releases.

### 1. Execute Reporting Only Mode

To run a non-destructive security assessment and view compliance reports:

```bash
ansible-playbook -i inventory/hosts playbooks/debian_hardening.yml -e "execution_mode=report"
```

### 2. Execute Doing (Remediation & Hardening) Mode

To run baseline audits, apply Debian security hardening and package integrity verification, and generate verification reports:

```bash
ansible-playbook -i inventory/hosts playbooks/debian_hardening.yml -e "execution_mode=remediate"
```

---

## 🐳 Unprivileged Sandbox & Fallback Strategy

Inside unprivileged container environments or Google Jules sandboxes (detected via `/home/jules`):

1. **Privilege Safety Guards**: Tasks modifying restricted kernel settings or system services run with `ignore_errors: true` or evaluate `is_sandbox_jules`.
2. **Mock Auditing**: Diagnostic scorecards gracefully report simulated baseline and hardened metrics without halting workflow execution.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
