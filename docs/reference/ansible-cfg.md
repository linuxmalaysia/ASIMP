---
title: "Ansible Config Parameters Reference"
description: "Detailed specification of ansible.cfg configurations and environmental switches."
type: "reference"
id: "docs/reference/ansible-cfg.md"
dsom_governance:
  domain: "Infrastructure"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "ansible"
  - "config"
related_links:
  - "docs/reference/index.md"
nav_order: 110
layout: "default"
---

# Ansible Config Parameters Reference

The `ansible.cfg` file configures play and task behaviors across local and remote target setups.

---

## ⚙️ Config Parameters & Tuning

### Core Settings
- `stdout_callback = yaml`: Formats playbook outputs using human-readable YAML blocks.
- `bin_ansible_callbacks = True`: Enforces execution metrics callbacks across multiple modules.
- `roles_path = roles:common_roles`: Directs where roles and external Galaxy requirements are loaded.

---

## 🔒 Security Restrictions

- **Host Key Checking**: Configured to be secure in production, but manageable during testing runs.
- **Pipelining**: Enabled by default to accelerate SSH task transfers.
