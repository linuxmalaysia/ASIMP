---
okf_version: "0.1"
type: "reference"
title: "System Core Playbooks Reference"
description: "Detailed specification of play.yml and play-localhost.yml orchestration entrypoints."
timestamp: "2026-08-15T00:00:00Z"
topics: ["playbooks", "ansible", "orchestration", "reference"]
id: "docs/reference/playbooks.md"
dsom_governance:
  domain: "Infrastructure"
  context_tier: "L3-TechnicalReference"
related_links:
  - "docs/reference/index.md"
nav_order: 120
layout: "default"
---

# System Core Playbooks Reference

ASIMP's execution workflow is controlled by two core playbooks depending on the target host scope.

---

## 🧭 Playbook Breakdown

### 1. `play.yml`
- **Scope**: Designed for multi-node remote configurations.
- **Connection**: Typically standard `ssh` with custom privilege escalation (`become: true`).

### 2. `play-localhost.yml`
- **Scope**: Specialized for executing self-hardening on the local host controller node.
- **Connection**: `connection: local`.

### 3. Distribution-Specific Standalone Playbooks
- **`playbooks/rhel_family_cis.yml`**: Enterprise Linux CIS Level 2 audit and hardening for RHEL, AlmaLinux, Rocky Linux, and Oracle Linux 8, 9, 10.
- **`playbooks/ubuntu_lts_hardening.yml`**: Dedicated audit and hardening workflow for Ubuntu 24.04 LTS and Ubuntu 26.04 LTS.
- **`playbooks/debian_hardening.yml`**: Dedicated audit, package integrity verification (`debsums`), and hardening for Debian 11, 12, and 13.
- **`playbooks/opensuse_hardening.yml`**: Dedicated audit, dynamic sysctl resource calculation (`sysctl-suse-ASIMP`), and hardening for openSUSE (Leap, Tumbleweed) and SUSE (SLES, SLED).

---

## 🔁 Hardening Phase Mapping

Both playbooks follow the **Measure, Harden, Re-Measure** workflow:

```text
Playbook Start -> reporting-ASIMP (Pre-Scan) -> OS Hardening -> reporting-ASIMP (Post-Scan) -> End
```
