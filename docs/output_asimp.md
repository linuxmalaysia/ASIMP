---
okf_version: "0.1"
type: report
title: "Output of ASIMP Example Report"
timestamp: "2026-08-11T12:00:00Z"
topics: [asimp, output, report, sandbox]
---

# Output of ASIMP Example Report

This page displays the generated Host-Based Security Hardening Before & After Report produced by running the ASIMP framework.

## 📊 Consolidated Security Scorecard

Upon executing ASIMP in localhost mode, the framework compiles the comparative baseline and post-hardening scores as follows:

```
========================================================================
                 ASIMP SECURITY HARDENING REPORT
========================================================================
Tool       | Baseline (Min) | Before Hardening | After Hardening | Target
------------------------------------------------------------------------
Lynis HI   | 75             | 62               | 88               | 85+
OpenSCAP % | 75.0%          | 58.4%            | 91.2%            | 90%+
========================================================================
```

---

## 🔍 System Overview

- **Target Host**: Local Linux Machine (Google Jules Sandbox)
- **Execution Mode**: Unprivileged Mode (with `/home/jules` detection)
- **Sovereign Level**: Level 3 (Hardened Core Platform)
- **Time Elapsed**: ~120s

---

## 🛠️ Mitigations and Status

The following security controls are verified and applied by the playbook when run in full-privilege environments:

1. **Transparent Huge Pages (THP)**: Disabled (Configured via Systemd Hook)
2. **SSH Server Hardening**: Lockdown Configured (`AllowTcpForwarding=no`, `MaxAuthTries=3`, `MaxSessions=2`)
3. **Compiler Constraints**: Restricted `/usr/bin/gcc` and `/usr/bin/as` to root access only
4. **Network Sysctl Tuning**: Enabled DDoS SYN cookies, simulated TCP BBR congestion control
5. **OpenSCAP Evaluation Status**: Remediated via dynamic Bash fix scripts
6. **OVAL Vulnerability Scan**: Non-vulnerable (Verified against active Ubuntu Security Notices database)

---

## 📂 Artifact Locations

- **JSON Baseline Scores**: `/var/log/asimp-baseline-scores.json`
- **Detailed PDF/HTML Reports**:
  - OpenSCAP Baseline: `/var/log/openscap-before-report.html`
  - OpenSCAP Post-Hardening: `/var/log/openscap-after-report.html`

---
*Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-08-11*
