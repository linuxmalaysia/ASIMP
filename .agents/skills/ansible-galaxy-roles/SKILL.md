---

name: ansible-galaxy-roles
description: Manages Ansible Galaxy dependencies and role path configurations. Use when introducing external roles, downloading dependencies via requirements.yml, or configuring custom role search paths.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Ansible Galaxy Role Paths and Dependencies
resource: .agents/skills/ansible-galaxy-roles
tags: [ansible, galaxy, roles, dependencies, requirements]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [ansible, galaxy, roles, dependencies, requirements]
---


# Ansible Galaxy Role Paths and Dependencies

This skill defines how external Ansible dependencies are structured, resolved, and installed in the ASIMP repository.

## When to Use This Skill

Activate this skill when:
- Adding external, community-developed Ansible roles.
- Managing dependencies configured in `requirements.yml`.
- Configuring or troubleshooting roles search paths in `ansible.cfg`.

## Path Specifications and Installation

### 1. Role Path Customization (`ansible.cfg`)
To prevent external dependencies from polluting global system directories or conflicting with localized roles, `ansible.cfg` specifies:
```ini
roles_path = roles:common_roles
```
This forces all Galaxy and community roles to load or be installed directly within the workspace’s `roles/` (or `common_roles/`) folder.

### 2. Dependency Installation
To install required external roles defined in `requirements.yml`, execute:
```bash
ansible-galaxy role install -r requirements.yml --ignore-errors
```
- **Strategic Use of `--ignore-errors`**: External network hiccups or version tagging mismatch should not crash development workflows. Using `--ignore-errors` ensures valid roles are installed successfully while permitting downstream custom validation to handle failures gracefully.

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
