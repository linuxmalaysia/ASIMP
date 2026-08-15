---
okf_version: "0.1"
type: "reference"
title: "Ansible Config Parameters Reference"
description: "Detailed specification of ansible.cfg configurations and environmental switches."
timestamp: "2026-08-15T00:00:00Z"
topics: ["ansible", "config", "reference", "ansible-cfg"]
id: "docs/reference/ansible-cfg.md"
dsom_governance:
  domain: "Infrastructure"
  context_tier: "L3-TechnicalReference"
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
- `callback_result_format = yaml`: Formats playbook outputs using human-readable YAML blocks (active under ansible-core 2.13+).
- `bin_ansible_callbacks = True`: Enforces execution metrics callbacks across multiple modules.
- `roles_path = roles:common_roles`: Directs where roles and external Galaxy requirements are loaded.

---

## 🔒 Security Restrictions

- **Host Key Checking**: Configured to be secure in production, but manageable during testing runs.
- **Pipelining**: Enabled by default to accelerate SSH task transfers.
