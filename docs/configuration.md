---

layout: default
title: "Configuration & Variables"
okf_version: "0.1"
type: documentation
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, docs, manual, security]
---


# Configuration & Variables

ASIMP is highly customizable. Many aspects of the system-level hardening, audits, and operating system packages can be configured through Ansible variables.

---

## ⚙️ Core Variables

The main variables are declared in `play.yml` (or `play-localhost.yml`) and roles defaults.

### 1. Global / Common Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `security_enable_firewalld` | `false` | Controls whether `firewalld` is installed and enabled during hardening. |
| `security_rhel7_initialize_aide` | `true` | Initializes the AIDE (Advanced Intrusion Detection Environment) database on RHEL/CentOS systems. |
| `security_contrib_enabled` | `true` | Allows using community-contributed hardening components. |
| `security_ntp_servers` | `["ntp1.sirim.my", "ntp2.sirim.my"]` | Custom NTP servers to set on hardened nodes. |

---

### 2. `update-ubuntu-ASIMP` Role Variables

These variables are defined in `roles/update-ubuntu-ASIMP/defaults/main.yml`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `upgrade_ubuntu_check` | `no` | If enabled (`yes`), runs `apt upgrade` on all packages to the latest versions. |
| `dist_upgrade_ubuntu_check` | `no` | If enabled (`yes`), runs `apt-get dist-upgrade` to handle changing dependencies. |
| `safe_upgrade_ubuntu_check` | `yes` | Standard safe package upgrade behavior (avoids removing packages). |
| `debsums_ubuntu_check` | `yes` | Installs `debsums` and executes an asynchronous file integrity audit. |

---

### 3. `lynis-ansible` Role Variables

These variables customize the Lynis auditing execution:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `lynis_use_packages` | `true` | Standardizes package installation for Lynis instead of running from source tarballs. |
| `lynis_audit_system_linux` | `true` | Enables automatic audit scanning for Linux systems. |

---

## 📂 Multi-Node Inventory Configuration

To run ASIMP across multiple enterprise servers, construct an inventory file (e.g., `hosts.ini`):

```ini
[webservers]
web1.internal.corp ansible_host=10.0.1.15
web2.internal.corp ansible_host=10.0.1.16

[dbservers]
db1.internal.corp ansible_host=10.0.2.20

[hardened:children]
webservers
dbservers
```

Execute ASIMP against the inventory with elevated privileges:
```bash
ansible-playbook -i hosts.ini -b -K play.yml
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
