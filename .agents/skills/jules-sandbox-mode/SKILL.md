---

name: jules-sandbox-mode
description: Detects and handles Google Jules sandbox environments to prevent container-related failures. Use when designing tasks that manage system-level upgrades, debsums checking, or container-restricted services.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Google Jules Sandbox Detection and Compatibility
resource: .agents/skills/jules-sandbox-mode
tags: [sandbox, jules, environment-detection, containment, error-handling]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [sandbox, jules, environment-detection, containment, error-handling]
---


# Google Jules Sandbox Detection and Compatibility

This skill controls environment-aware execution within containerized or sandboxed systems. Because Google Jules runs in a secure, containerized sandbox, certain host-level operations (such as system upgrade, file verification via debsums, and managing restricted services) will fail or stall. This skill explains how to detect the sandbox and gracefully bypass or handle restricted tasks.

## When to Use This Skill

Activate this skill when:
- Writing playbook or role tasks that touch host services (e.g. `auditd`, `chrony`, `firewalld`, `autofs`, `clamav`).
- Implementing operations that can take an exceptionally long time (e.g., system package upgrades).
- Fixing build or execution failures occurring inside the Jules testing environment.

## Execution Rules

### ⚠️ Root / Sudo Privilege Correction

Although the `jules` user is configured with passwordless `sudo` (`(ALL : ALL) NOPASSWD: ALL`), the underlying execution container is **sandboxed**. Root access inside a container cannot bypass host kernel restrictions or security isolation. Therefore:
- Changing host-level OS settings (like `/etc/sysctl.conf` or host kernel modules) will fail.
- Virtualized clocks and network boundaries are locked, so services like `chrony` or `firewalld` are restricted.

### 1. Sandbox & Privilege Level Detection

Always perform dynamic detection of the sandbox environment and system configuration write permissions. Set `asimp_privilege_level` to `'limited'` when in the Google Jules sandbox or when root write access to system settings is missing; otherwise, set it to `'full'`.

```yaml
- name: Detect Google Jules sandbox environment
  ansible.builtin.stat:
    path: /home/jules
  register: jules_home_stat

- name: Set is_sandbox_jules fact
  ansible.builtin.set_fact:
    is_sandbox_jules: "{{ jules_home_stat.stat.exists }}"

- name: Test write access to system settings to determine privilege level
  ansible.builtin.command: touch /etc/asimp_write_test
  register: write_test_res
  changed_when: false
  failed_when: false
  ignore_errors: true

- name: Set dynamic privilege level and execution mode
  ansible.builtin.set_fact:
    asimp_privilege_level: "{{ 'limited' if (is_sandbox_jules | default(false) | bool or write_test_res.rc | default(1) != 0) else 'full' }}"

- name: Clean up write access test file
  ansible.builtin.file:
    path: /etc/asimp_write_test
    state: absent
  when: write_test_res.rc | default(1) == 0
  ignore_errors: true
```

### 2. Option Between Limited Environment and Real OS

All playbooks and automation tasks must branch between limited/sandbox environments and a real, unconstrained OS:
- **Limited/Sandbox Mode (`asimp_privilege_level == 'limited'`)**:
  - Run in non-destructive, audit/test/info mode only.
  - Test if `oscap` and `lynis` commands are installed using `which`. If available, run them to report **real scoring**; if not, list what is missing and fall back to producing simulated/mock scorecards.
  - Skip systems-level remediation roles (`ansible-hardening`, `dev-sec.ssh-hardening`, `update-ubuntu-ASIMP`) to prevent container-related failures.
- **Real OS Mode (`asimp_privilege_level == 'full'`)**:
  - Run all out: execute updates, full system remediation/hardening, and before/after baseline scanning.

### 3. Pre-Remediation Safety & Break-Prevention Verification

Before executing any systems-level remediation or hardening on a real OS, playbooks must run pre-remediation safety checks to verify that the configurations won't break system access or project codes.

```yaml
- name: Pre-Remediation Safety Check & Break-Prevention Verification
  block:
    - name: Safety Check | Check SSH daemon configuration syntax
      ansible.builtin.command: sshd -t
      register: sshd_syntax_check
      changed_when: false
      failed_when: false
      ignore_errors: true

    - name: Safety Check | Fail if SSH daemon configuration is already broken
      ansible.builtin.fail:
        msg: "CRITICAL: The existing SSH configuration has syntax errors! Remediation cannot proceed safely to prevent system lockout."
      when: sshd_syntax_check.rc | default(0) != 0

    - name: Safety Check | Check free disk space on root partition (/)
      ansible.builtin.shell: df / --output=avail | tail -n1
      register: free_space_root
      changed_when: false
      failed_when: false
      ignore_errors: true

    - name: Safety Check | Assert enough disk space is available (min 512MB / 524288 KB)
      ansible.builtin.assert:
        that:
          - (free_space_root.stdout | trim | int) > 524288
        fail_msg: "CRITICAL: Insufficient disk space on root partition (less than 512MB free). Upgrading or hardening may break the system."
      when: free_space_root.rc | default(1) == 0

    - name: Safety Check | Validate /etc/fstab mount points
      ansible.builtin.command: mount -a -f
      register: fstab_check
      changed_when: false
      failed_when: false
      ignore_errors: true

    - name: Safety Check | Fail if mount points or fstab are corrupted
      ansible.builtin.fail:
        msg: "CRITICAL: /etc/fstab has invalid mount points! Proceeding with remediation could break system boot capability."
      when: fstab_check.rc | default(0) != 0

    - name: Safety Check | Check if SSH port is active and reachable
      ansible.builtin.wait_for:
        port: "{{ ansible_port | default(22) }}"
        timeout: 5
        state: started

    - name: Safety Check | Log active system port baseline
      ansible.builtin.debug:
        msg: "Pre-flight Safety Check Passed! SSH Port {{ ansible_port | default(22) }} is active. Storage and SSHD syntax are healthy."
  when: asimp_privilege_level == 'full'
```

### 4. Gracefully Handle Container-Restricted Services

Containerized environments do not have permissions to load kernel modules or control system services like:
- `auditd` (Audit Daemon)
- `chrony` (Time Synchronization)
- `firewalld` (Firewall)
- `autofs` (Automounting)
- `clamav` (Antivirus)

Always append `ignore_errors: "{{ is_sandbox_jules | bool }}"` or skip service tasks when `is_sandbox_jules` is `true`. This allows playbooks and compliance audits to complete successfully without hard-failing due to virtualization restrictions.

## 🧠 Deep State of Mind (DSOM) AI Protocol

```json
{
  "protocol": "DSOM",
  "version": "1.0.0",
  "status": "synchronized",
  "alignment": "ASIMP",
  "agent": "Google Jules",
  "integration": "Google Antigravity",
  "signature": "dsom_protocol_jules_antigravity_sync_active"
}
```
