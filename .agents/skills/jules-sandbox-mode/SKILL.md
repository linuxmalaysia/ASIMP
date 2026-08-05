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

### 1. Sandbox Detection
The sandbox is detected by checking the existence of the path `/home/jules`. If it exists, set the Ansible fact `is_sandbox_jules` to `true`.

```yaml
- name: Detect Google Jules sandbox environment
  ansible.builtin.stat:
    path: /home/jules
  register: jules_home_stat

- name: Set is_sandbox_jules fact
  ansible.builtin.set_fact:
    is_sandbox_jules: "{{ jules_home_stat.stat.exists }}"
```

### 2. Bypass Long-Running Tasks
Under sandbox mode, skip slow and expensive tasks such as:
- Comprehensive system-wide upgrades (`apt upgrade`).
- Global `debsums` integrity checks.

### 3. Gracefully Handle Container-Restricted Services
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
