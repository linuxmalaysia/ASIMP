---
okf_version: "0.1"
layout: default
type: documentation
title: "Ansible Best Practices & FQCN Standards"
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, ansible, fqcn, idempotency, best-practices]
---


# Ansible Best Practices & FQCN Standards

Modern Ansible requires highly scalable, predictable, and idempotent playbooks. To prevent collisions, version drift, and deprecation warnings, ASIMP enforces strict development standards, mandating **Fully Qualified Collection Names (FQCN)** and **Explicit Task Idempotency**.

---

## 🧭 Fully Qualified Collection Names (FQCN)

All playbooks, roles, and tasks in ASIMP must utilize fully qualified collection paths when invoking Ansible modules. Short, unqualified names (e.g., `apt`, `copy`, `shell`) are strictly prohibited.

| Legacy Module Name | Mandatory FQCN Replacement |
| :--- | :--- |
| `apt` | `ansible.builtin.apt` |
| `copy` | `ansible.builtin.copy` |
| `shell` | `ansible.builtin.shell` |
| `command` | `ansible.builtin.command` |
| `replace` | `ansible.builtin.replace` |

Using FQCN ensures playbooks remain robust across varying Ansible versions and executing environments.

---

## 🛡️ Symmetric Privilege Strategy

ASIMP implements a hybrid, symmetric privilege model that separates global system tuning from unprivileged deployment or auditing steps:

1. **Rootful OS Hardening**: Applied only when `asimp_privilege_level == 'full'`. This installs system utilities, modifies kernel sysctls, and enforces security configurations.
2. **Rootless Auditing**: Executed dynamically under `become_user` or within simulated fallback loops inside Google Jules sandboxes (`is_sandbox_jules: true`).

---

## 📄 FQCN Ansible Task Blueprint

Below is an example of production-grade task construction demonstrating proper FQCN syntax and explicit environment variables for rootless systemd execution:

```yaml
- name: Create Quadlet configuration directory
  ansible.builtin.file:
    path: "/home/songket/.config/containers/systemd"
    state: directory
    owner: songket
    group: songket
    mode: '0755'
  become: yes
  become_user: songket

- name: Deploy Quadlet templates
  ansible.builtin.template:
    src: "templates/{{ item }}.j2"
    dest: "/home/songket/.config/containers/systemd/{{ item }}"
    owner: songket
    group: songket
    mode: '0644'
  loop:
    - skm_network.network
    - skm_pod.pod
  become: yes
  become_user: songket
  register: quadlets_deployed

- name: Reload user-level systemd daemon and restart services
  ansible.builtin.systemd_service:
    daemon_reload: yes
    scope: user
    name: skm_pod-pod.service
    state: restarted
    enabled: yes
  become: yes
  become_user: songket
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ songket_uid | default(2001) }}"
    DBUS_SESSION_BUS_ADDRESS: "unix:path=/run/user/{{ songket_uid | default(2001) }}/bus"
  when: quadlets_deployed.changed
```

---

## 🔍 Task Idempotency and Change Verification

By default, executing shell or command modules always registers a "changed" state. Every shell or command task inside ASIMP must explicitly define `changed_when` or `failed_when` conditions to maintain high-fidelity change tracking.

```yaml
# INCORRECT (Will always report changed)
- name: Check file existence
  ansible.builtin.command: ls /var/log/asimp-baseline-scores.json

# CORRECT (Strictly idempotent check)
- name: Check file existence
  ansible.builtin.command: ls /var/log/asimp-baseline-scores.json
  register: file_check
  changed_when: false
  failed_when: false
```
