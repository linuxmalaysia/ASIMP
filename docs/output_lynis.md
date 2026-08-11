---
okf_version: "0.1"
type: report
title: "Output of Lynis Auditing Report"
timestamp: "2026-08-11T12:00:00Z"
topics: [lynis, auditing, output, report]
---

# Output of Lynis Auditing Report

This page provides an example output of the **Lynis** security auditing tool integrated into the ASIMP workflow.

---

## 📈 Lynis Hardening Index Delta

ASIMP automates Lynis audits during both the baseline evaluation (before hardening) and validation checks (after hardening).

- **Before Hardening Score**: **62 / 100**
- **After Hardening Score**: **88 / 100**
- **Target Threshold**: **85+** (Enterprise Standard)

---

## 📋 Example Lynis Console Scan Output

When ASIMP invokes Lynis, the console log captures category-by-category checks:

```text
[+] Boot and services
    - Service Manager                                           [ Systemd ]
    - Checking enabled services                                 [ OK ]
    - Checking startup files (permissions)                      [ OK ]

[+] Kernel
    - Check active kernel modules                               [ OK ]
    - sysctl: net.ipv4.conf.all.rp_filter                       [ OK ]
    - sysctl: net.ipv4.tcp_syncookies                          [ OK ]
    - sysctl: net.ipv4.conf.all.accept_redirects                [ Hardened ]

[+] Users, Groups and Authentication
    - Administrator accounts                                    [ OK ]
    - Unique UIDs                                               [ OK ]
    - Password hashing algorithm                                [ SHA512 ]
    - Password strength / rules                                 [ Hardened ]

[+] Shells
    - Checking shell session timeout                            [ Hardened ]

[+] SSH Support
    - SSH Daemon found                                          [ Yes ]
    - SSH Configuration file                                    [ /etc/ssh/sshd_config ]
    - SSH Port                                                  [ 22 ]
    - SSH PermitRootLogin                                       [ No ]
    - SSH Protocol version                                      [ 2 ]
```

---

## ⚠️ Suggestions & Warnings Resolved by ASIMP

During Phase 2 (Hardening), ASIMP parses Lynis suggestions from `/var/log/lynis-report.dat` and applies targeted remediations.

### 1. SSH Server Security
* **Lynis Suggestion**: `Disable SSH root login and restrict password logins.`
* **ASIMP Mitigation**: Configured via `ssh-hardening` role, disabling direct root authentication.

### 2. File Integrity Checking
* **Lynis Suggestion**: `Install a file integrity checker to detect modifications to system binaries.`
* **ASIMP Mitigation**: Executed system-wide package verification with `debsums`.

### 3. Compiler Restriction
* **Lynis Suggestion**: `Restrict compilers like gcc to root-only to prevent on-box privilege escalation exploits.`
* **ASIMP Mitigation**: Modified file permissions on `gcc`, `as`, and `make`.

---

## 📂 Report Files

The detailed report and findings database are saved to:
- **Scan Report File**: `/var/log/lynis.log`
- **Findings Database**: `/var/log/lynis-report.dat`

---
*Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-08-11*
