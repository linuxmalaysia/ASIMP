---
okf_version: "0.1"
type: "tutorial"
title: "Quickstart Onboarding Guide"
description: "Step-by-step tutorial for setting up ASIMP, installing dependencies, and running your first compliance scan on localhost."
timestamp: "2026-08-15T00:00:00Z"
topics: ["tutorial", "quickstart", "onboarding", "asimp"]
id: "docs/tutorials/01-getting-started.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L2-Operational"
related_links:
  - "docs/how-to/run-tool.md"
  - "docs/reference/index.md"
nav_order: 10
layout: "default"
---

# Quickstart Onboarding Guide

Welcome to ASIMP! This step-by-step tutorial will guide you through setting up a clean development environment, installing core Ansible requirements, and executing a safe local security audit using localhost sandbox fallback mechanisms.

---

## 📋 Prerequisites

Before you begin, ensure your target Linux machine has:
- Python 3.10+
- `sudo` privileges (not required under Jules Sandbox Mode)
- Access to the Internet (to download Galaxy roles)

---

## 🛠️ Step 1: Clone and Set Up Python Virtual Environment

Create an isolated environment to prevent Python dependency conflicts with your system packages:

```bash
# Clone the repository
git clone https://github.com/linuxmalaysia/ASIMP.git
cd ASIMP

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 📦 Step 2: Install Ansible Galaxy Dependencies

Deploy the external SSH hardening and system audit roles locally into the standard roles pathway:

```bash
ansible-galaxy install -r requirements.yml
```

---

## 🚀 Step 3: Run the Local Host Security Playbook

Execute the localhost audit playbook. Under unprivileged user contexts (like the Google Jules environment), the platform will automatically detect and fall back to safe sandbox operations:

```bash
ansible-playbook -i tests/inventory play-localhost.yml
```

### Expected Console Output

You should see a clean Ansible playbook execution run:

```text
PLAY [Hardening and Auditing localhost] ****************************************

TASK [reporting-ASIMP : Detect if running under Google Jules Sandbox] ***********
ok: [localhost]

TASK [reporting-ASIMP : Set Jules Sandbox Facts] ********************************
ok: [localhost]

...

PLAY RECAP *********************************************************************
localhost                  : ok=114  changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

---

## 📄 Step 4: Inspect Generated Reports

After execution, examine the generated security posture reports:

### Unprivileged / Sandbox Execution (Google Jules Mode)

In sandboxed or unprivileged environments (`is_sandbox_jules: true`), reports are saved locally under the mock report workspace:

```bash
cat data/asimp_mock/opt/report/openscap/SECURITY_AUDIT_REPORT.md
```

### Full Privileged Real OS Execution

On fully privileged Linux systems (`asimp_privilege_level: 'full'`), live OpenSCAP XCCDF evaluation reports are written directly to system log paths:

```bash
# HTML Compliance Reports
ls -la /var/log/openscap-*.html

# Lynis Audit Log
cat /var/log/lynis-report.dat
```

Congratulations! You have completed your first successful ASIMP compliance and auditing cycle.
