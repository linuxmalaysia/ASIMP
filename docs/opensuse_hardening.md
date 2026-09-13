---
layout: default
okf_version: "0.1"
type: documentation
title: "openSUSE / SUSE Linux Enterprise Hardening & Audit Guide"
sidebarTitle: "openSUSE Hardening Guide"
timestamp: "2026-08-05T12:00:00Z"
topics: [opensuse, suse, sysctl, lynis, openscap, audit, remediation, ansible]
---

# openSUSE / SUSE Linux Enterprise Hardening & Audit Guide

**openSUSE** (Leap and Tumbleweed) and **SUSE Linux Enterprise Server/Desktop (SLES/SLED)** provide enterprise-class stability and modern package management via Zypper. Securing SUSE environments requires dynamic network socket backlog limits, SSH daemon hardening, system file permission controls, and dual-engine security auditing using Lynis and OpenSCAP.

This guide details the **Ansible System Integrity Management Platform (ASIMP)** workflow for evaluating, auditing, and hardening openSUSE and SUSE systems, highlighting the `sysctl-suse-ASIMP` role for automated sysctl resource calculation.

---

## 🧭 Scope & Distribution Matrix

ASIMP provides target-aware validation for openSUSE and SUSE distributions:

| Target Distribution | Version | Sysctl Auto-Calculation Engine | Audit Engines Supported | Playbook Target |
| :--- | :--- | :--- | :--- | :--- |
| **openSUSE Leap** | `15.x` | `sysctl-suse-ASIMP` | OpenSCAP, Lynis | `playbooks/opensuse_hardening.yml` |
| **openSUSE Tumbleweed** | Rolling | `sysctl-suse-ASIMP` | OpenSCAP, Lynis | `playbooks/opensuse_hardening.yml` |
| **SUSE Linux Enterprise Server (SLES)** | `15.x` | `sysctl-suse-ASIMP` | OpenSCAP, Lynis | `playbooks/opensuse_hardening.yml` |
| **SUSE Linux Enterprise Desktop (SLED)** | `15.x` | `sysctl-suse-ASIMP` | OpenSCAP, Lynis | `playbooks/opensuse_hardening.yml` |

---

## ⚙️ Dynamic Sysctl Calculation (`sysctl-suse-ASIMP`)

The `sysctl-suse-ASIMP` role dynamically computes system resource limits based on node hardware facts (`memtotal_mb`, `processor_vcpus`, and root partition mount size):

- **`net.ipv4.tcp_max_syn_backlog`**: Calculated as `max(4096, memtotal_mb * 4, vcpus * 2048)`.
- **`net.core.somaxconn`**: Calculated as `max(1024, vcpus * 512, memtotal_mb)`.

---

## 📊 Architectural Paradigm: Mode Separation

ASIMP strictly separates operations into two distinct execution modes, controlled via the `execution_mode` variable:

1. **Mode A: Reporting Only (`execution_mode: "report"`)**:
   - Performs non-destructive compliance scanning and evaluation.
   - Outputs visual HTML reports and XML results.
   - Does not apply hardening, but may create report directories and files.

2. **Mode B: Doing (`execution_mode: "remediate"`)**:
   - Performs a pre-remediation baseline assessment ("Phase 1: Measure").
   - Applies dynamic network sysctl tuning via `sysctl-suse-ASIMP`, file permission controls, SSH hardening, and Lynis security auditing ("Phase 2: Harden").
   - Executes a post-remediation evaluation scan ("Phase 3: Re-Measure").
   - Outputs a comparative scorecard.

---

## 🚀 Ansible Playbook Execution Guide

The dedicated playbook `playbooks/opensuse_hardening.yml` automates both modes across all supported openSUSE and SUSE releases.

### 1. Execute Reporting Only Mode

To run a non-destructive security assessment and view compliance reports:

```bash
ansible-playbook -i inventory/hosts playbooks/opensuse_hardening.yml -e "execution_mode=report"
```

### 2. Execute Doing (Remediation & Hardening) Mode

To run baseline audits, apply openSUSE network hardening and security policies, and generate verification reports:

```bash
ansible-playbook -i inventory/hosts playbooks/opensuse_hardening.yml -e "execution_mode=remediate"
```

---

## 🐳 Unprivileged Sandbox & Fallback Strategy

Inside unprivileged container environments or Google Jules sandboxes (detected via `/home/jules`):

1. **Privilege Safety Guards**: Tasks modifying restricted kernel settings or system services run with `ignore_errors: true` or evaluate `is_sandbox_jules`.
2. **Mock Auditing**: Diagnostic scorecards gracefully report simulated baseline and hardened metrics without halting workflow execution.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
