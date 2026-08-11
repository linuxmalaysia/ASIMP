---

layout: default
title: "Troubleshooting & Fallback Behaviors"
okf_version: "0.1"
type: documentation
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, docs, manual, security]
---


# Troubleshooting & Fallback Behaviors

This guide covers common issues, warning states, and standard troubleshooting strategies when using the ASIMP security framework.

---

## 🛠️ OpenSCAP File and Profile Resolution

### Problem: Dynamic DataStream Not Found
* **Symptom**: On specialized, custom, or newer Linux distributions, OpenSCAP might fail to find the exact version-matched XML DataStream (e.g. `ssg-ubuntu2404-ds.xml` on a beta release).
* **ASIMP Mitigation**: The `reporting-ASIMP` role dynamically resolves OS-version-specific datastreams:
  1. It performs an `ansible.builtin.find` search in the standard directory `/usr/share/xml/scap/ssg/content/`.
  2. It constructs the appropriate datastream path based on detected OS distribution and version.
  3. If no OS-version-compatible datastream is found, the scan is considered unsupported for that platform (the role should not proceed with an arbitrary or incompatible datastream file).

### Verification Steps:
Check if the SCAP files exist on your machine:
```bash
ls -la /usr/share/xml/scap/ssg/content/
```
If empty, verify internet access or manual package repositories so that `scap-security-guide` or `ssg-debian` can install correctly.

---

## ⏳ Slow Playbook Runs (Timeouts)

### Problem: Repository Upgrades or Debsums Takes Too Long
* **Symptom**: When upgrading thousands of outdated packages or hashing files via `debsums`, standard Ansible connections can timeout or stall.
* **ASIMP Mitigation**: ASIMP executes heavy tasks asynchronously (`async: 361` with standard polling loops). This allows the task to run independently and provides status polling up to 360 retries.
* **Troubleshooting**: If a timeout is reached, check the local logs directly on the target host:
  - Repository cache / upgrade log: `/var/log/dpkg.log` or `/var/log/apt/history.log`
  - Debsums check logs: `/var/log/debsums.output` and `/var/log/debsums.err`

---

## 🖥️ Sudo / Elevation Failures

### Problem: Become password required
* **Symptom**: `Missing sudo password` or `Permission denied` when executing playbooks.
* **Reason**: ASIMP modifies system-level configurations, installs packages, and runs audits, which requires root/administrator privileges.
* **Solution**: Always execute with `become` parameters (`-b -K` or `--become --ask-become-pass`):
```bash
ansible-playbook -b -K play.yml
```
For localhost operations:
```bash
ansible-playbook --connection=local -b -K play-localhost.yml
```
(The playbook requires privilege escalation. Make sure your current user has sudo capabilities.)

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
