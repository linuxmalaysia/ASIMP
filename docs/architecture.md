---

layout: default
title: "Architecture & Design"
okf_version: "0.1"
type: documentation
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, docs, manual, security]
---


# Architecture & Design

ASIMP (Ansible System Integrity Management Platform) is designed around a three-phase security pipeline. Unlike standard configuration management playbooks which focus purely on applying states, ASIMP emphasizes continuous observability and self-reporting.

---

## 🏛️ System Component Flow

The core workflow of ASIMP consists of:

```
[Phase 1: Auditing Baseline]
          |
          +---> Run OpenSCAP Baseline scan (CIS Linux L2 profile)
          +---> Run Lynis Baseline audit (--quick mode)
          +---> Save initial compliance metrics to: `/var/log/asimp-baseline-scores.json`
          |
[Phase 2: Hardening & System Remediation]
          |
          +---> update-ubuntu-ASIMP (Applies safety updates & runs debsums check)
          +---> ansible-hardening (OpenStack security recommendations)
          +---> dev-sec.ssh-hardening (Secures SSH Server & Client configurations)
          +---> lynis-ansible (Remediates localized audit exceptions)
          |
[Phase 3: Verification & Reporting]
          |
          +---> Run OpenSCAP Post-Hardening scan
          +---> Run Lynis Post-Hardening audit
          +---> Slurp baseline scores from `/var/log/asimp-baseline-scores.json`
          +---> Parse and match results using `/usr/local/bin/parse_openscap_score.py`
          +---> Output terminal scorecard & generate complete HTML/DAT audit reports
```

---

## 🔍 The Auditing Engines

### 1. OpenSCAP (Security Content Automation Protocol)
OpenSCAP is a NIST-certified tool for verifying compliance against defined benchmarks. ASIMP automatically installs the required packages (`openscap-scanner`, `ssg-debian`, `ssg-debderived`, or `scap-security-guide`) on target systems, detects the operating system version, and locates the correct XML DataStream.

The primary scanning target profile is:
* **Profile**: `xccdf_org.ssgproject.content_profile_cis_level2_server` (Center for Internet Security - Level 2 Server)

If the profile or OS data stream is not present, ASIMP automatically performs a graceful fallback to available baselines.

### 2. Lynis Auditing Engine
Lynis is a host-based, open-source security auditing tool. It scans system configurations, file permissions, kernel parameters, and services. In Phase 1, ASIMP executes `lynis audit system --quick` and extracts the `hardening_index` from `/var/log/lynis-report.dat`. Post-hardening, a second audit is run, and the two indexes are compared side-by-side to measure exact security enhancement.

---

## 🛠️ Integrity Verification with `debsums`

The package integrity check is performed using `debsums`, which verifies MD5 hashes of all installed package files against original registry hashes. This helps detect:
* System binary modifications or tampering.
* Filesystem corruption.
* Unauthorized or manually modified library files.

The check runs asynchronously in the background so as not to stall playbook execution, with its output saved under `/var/log/debsums.output`.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
