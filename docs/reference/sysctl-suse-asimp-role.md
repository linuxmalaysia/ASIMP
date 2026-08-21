---
okf_version: "0.1"
type: reference
title: SUSE/SLED Sysctl Hardening Role Reference
timestamp: "2026-08-05T12:00:00Z"
topics:
  - asimp
  - suse
  - sysctl
  - hardening
  - performance
  - security
---

# SUSE/SLED Sysctl Hardening Role Reference

The `sysctl-suse-ASIMP` Ansible role implements the network security sysctl recommendations from [SUSE Linux Enterprise Desktop (SLED) 15 SP7 Security and Hardening Guide](https://documentation.suse.com/sled/15-SP7/html/SLED-all/cha-sec-sysctl.html).

It applies kernel network parameter hardening and automatically scales resource limits (`net.ipv4.tcp_max_syn_backlog` and `net.core.somaxconn`) dynamically based on node RAM memory and vCPU capacity, while inspecting root disk size for telemetry and storage safety checks.

---

## 📋 Features

- **RAM & vCPU Auto Resource Calculation**: Dynamically measures RAM (`ansible_facts['memtotal_mb']`) and vCPU count (`ansible_facts['processor_vcpus']`) to calculate optimal network socket backlogs, while reporting root disk size (`ansible_facts['mounts']`) for node telemetry.
- **Configurable Auto-Calculation Gating**: Automatic calculation can be toggled using `suse_sysctl_auto_calc_resources` (defaults to `true`), or explicitly overridden with `suse_sysctl_override_tcp_max_syn_backlog` and `suse_sysctl_override_somaxconn`.
- **Deduplicated Network Hardening**: Consolidates SUSE/SLED network sysctl settings into `/etc/sysctl.d/99-suse-network-hardening.conf` without duplicate entries.
- **Standalone or Integrated Playbook Execution**: Can be executed standalone via `playbooks/suse_sysctl.yml` or as part of `play.yml` / `play-localhost.yml` pipeline on SUSE-family hosts after OpenSCAP and Lynis hardening steps.
- **Sandbox Safety Protocols**: Respects `asimp_privilege_level` ('full' vs 'limited') and gracefully skips unprivileged container failures in Google Jules sandboxes.

---

## ⚙️ Configured Kernel Parameters

The role applies the following standardized configuration in `/etc/sysctl.d/99-suse-network-hardening.conf`:

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `net.ipv4.conf.default.rp_filter` | `1` | Strict reverse path filtering |
| `net.ipv4.conf.all.rp_filter` | `1` | Strict reverse path filtering for all interfaces |
| `net.ipv4.conf.default.accept_source_route` | `0` | Reject source routed packets |
| `net.ipv4.conf.all.accept_source_route` | `0` | Reject source routed packets for all interfaces |
| `net.ipv4.tcp_syncookies` | `1` | Enable TCP SYN Cookie protection |
| `net.ipv4.tcp_max_syn_backlog` | *Auto-calculated* | Dynamic queue size (base 4096, scales with RAM & vCPUs) |
| `net.core.somaxconn` | *Auto-calculated* | Dynamic listen socket limit (base 1024, scales with vCPUs) |
| `net.ipv4.icmp_echo_ignore_broadcasts` | `1` | Ignore ICMP broadcast pings |
| `net.ipv4.icmp_ignore_bogus_error_responses` | `1` | Ignore invalid ICMP error responses |
| `net.ipv4.conf.default.accept_redirects` | `0` | Disable ICMP redirect acceptance |
| `net.ipv4.conf.all.accept_redirects` | `0` | Disable ICMP redirect acceptance for all interfaces |
| `net.ipv6.conf.default.accept_redirects` | `0` | Disable IPv6 ICMP redirect acceptance |
| `net.ipv6.conf.all.accept_redirects` | `0` | Disable IPv6 ICMP redirect acceptance for all interfaces |
| `net.ipv4.conf.default.secure_redirects` | `0` | Disable secure ICMP redirects |
| `net.ipv4.conf.all.secure_redirects` | `0` | Disable secure ICMP redirects for all interfaces |
| `net.ipv4.conf.default.send_redirects` | `0` | Disable ICMP redirect sending |
| `net.ipv4.conf.all.send_redirects` | `0` | Disable ICMP redirect sending for all interfaces |
| `net.ipv4.ip_forward` | `0` | Disable IPv4 packet forwarding |
| `net.ipv6.conf.all.forwarding` | `0` | Disable IPv6 packet forwarding |
| `net.ipv6.conf.default.forwarding` | `0` | Disable IPv6 packet forwarding for defaults |
| `net.ipv4.conf.all.log_martians` | `1` | Log martian packets |
| `net.ipv4.conf.default.log_martians` | `1` | Log default martian packets |

---

## 🚀 Standalone Execution

To execute this sysctl hardening playbook independently on target hosts:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/suse_sysctl.yml
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
