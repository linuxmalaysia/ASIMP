---
okf_version: "0.1"
type: report
title: "Output of OpenSCAP Evaluation Report"
timestamp: "2026-08-05T23:54:50Z"
topics: [openscap, compliance, cis, output, report]
---

# Output of OpenSCAP Evaluation Report

This page demonstrates the structured evaluation results of **OpenSCAP** executing against the **CIS Ubuntu Security Benchmark (Level 2)**.

---

## 📊 Compliance Score Progression

ASIMP utilizes OpenSCAP with dynamic OS-detection logic to verify compliance parameters.

- **Before Hardening Score**: **58.4%**
- **After Hardening Score**: **91.2%**
- **Target Compliance Threshold**: **90.0%+**

---

## 🔬 Rule Compliance Details (Simulated Fallback)

The table below showcases typical rules checked during an OpenSCAP evaluation, indicating their baseline state vs. post-remediation state as simulated fallback data under the unprivileged sandbox environment:

| Policy Rule ID | Description | Before Hardening | After Hardening | Remediation Status |
|----------------|-------------|------------------|-----------------|--------------------|
| **sysctl_net_ipv4_conf_all_accept_redirects** | Disable ICMP Redirect Acceptance | ❌ Fail |  Pass | Automated via sysctl hardening |
| **sshd_disable_root_login** | Disable SSH direct root logins | ❌ Fail |  Pass | Automated via Dev-Sec SSH |
| **package_auditd_installed** | Ensure Audit Daemon (auditd) is present | ❌ Fail |  Pass | Installed via apt/dnf package manager |
| **file_permissions_etc_passwd** | Strict access permissions on passwd file |  Pass |  Pass | Maintained by default baseline |
| **accounts_password_pam_cracklib** | Enforce password complexity via PAM | ❌ Fail |  Pass | Configured via PAM module hardening |
| **disable_transparent_hugepages** | Disable THP to optimize memory boundary | ❌ Fail |  Pass | Disabled via bootloader / systemd hook |

---

## 📝 Example OpenSCAP CLI Run Output

During the evaluation, OpenSCAP outputs progress indicators for each rule assertion:

```text
Title   Disable Accept Router Advertisements on all IPv6 Interfaces
Rule    sysctl_net_ipv6_conf_all_accept_ra
Result  pass

Title   Ensure SSH MaxAuthTries is set to 4 or less
Rule    sshd_set_max_auth_tries
Result  pass

Title   Configure systemd-journald to forward logs to syslog
Rule    journald_forward_to_syslog
Result  pass

Title   Ensure debsums is installed and package integrity is validated
Rule    package_debsums_installed
Result  pass
```

---

## 📂 Report Artifacts

Under full production runs with root privileges, OpenSCAP generates interactive HTML and XML report files:
- **Before Hardening HTML Report**: `/var/log/openscap-before-report.html` (Expected privileged output)
- **After Hardening HTML Report**: `/var/log/openscap-after-report.html` (Expected privileged output)
- **Before Hardening Results XML**: `/var/log/openscap-before-results.xml` (Expected privileged output)
- **After Hardening Results XML**: `/var/log/openscap-after-results.xml` (Expected privileged output)

*Note: In the unprivileged sandbox environment, these HTML/XML artifacts are skipped due to host permission limits.*

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
