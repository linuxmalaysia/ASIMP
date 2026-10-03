---
okf_version: "0.2"
trust_level: "verified"
type: documentation
title: "ASIMP Comprehensive Installation & Setup Guide"
timestamp: "2026-08-15T00:00:00Z"
topics: [asimp, installation, uv, ansible, setup, modules]
---

# ASIMP Comprehensive Installation & Module Setup Guide

Welcome to the **ASIMP (Ansible System Integrity Management Platform)** Installation Guide. This document provides step-by-step instructions for installing, configuring, and provisioning all ASIMP modules and environments using a combination of **Python `uv`**, **Ansible Playbooks**, and **Bash scripting**.

---

## 📋 System Prerequisites

Before proceeding with installation, ensure your host environment satisfies the following minimum prerequisites:

* **Operating System**: Linux (Ubuntu 22.04+, Debian 12+, Enterprise Linux 8/9/10, openSUSE Leap 15+) or macOS / WSL2.
* **Python**: Python 3.10+ (Python 3.12+ recommended).
* **Python `uv`**: Fast Python package installer and environment manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
* **Container Engine (Optional for EE/Matrix)**: Podman 5+ (or Docker) for running containerized Execution Environments and local OS test matrix containers.
* **Privilege Level**: Sudo / root access on target nodes for security auditing and hardening operations.

---

## 🚀 Quick Start: Automated Installation Script

To install all core Python dependencies and Ansible Galaxy roles in one command, run the automated installation bash script:

```bash
# Clone the repository
git clone https://github.com/linuxmalaysia/ASIMP.git
cd ASIMP

# Run the automated installer
./scripts/install_all.sh
```

---

## 🧩 Module-by-Module Installation Matrix

ASIMP is composed of several operational modules. Each module can be installed and bootstrapped using **Python `uv`**, **Ansible Playbooks**, or **Bash scripting**.

---

### Module 1: Core Python Environment & Dependencies (`uv` + `requirements.txt`)

This module sets up a high-performance Python virtual environment and installs Ansible Core (`>=9.0.0`), `ansible-lint`, `cryptography`, and `jmespath`.

#### Installation via Bash & Python `uv`:
```bash
# 1. Create Python virtual environment using uv
uv venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install Python dependencies using uv pip
uv pip install -r requirements.txt
```

#### Verification:
```bash
ansible --version
ansible-lint --version
```

---

### Module 2: Ansible Galaxy Roles & Collections (`ansible-galaxy` + `requirements.yml`)

ASIMP relies on external security and hardening roles (such as Dev-Sec SSH Hardening, Chrony time sync, and OpenStack Hardening).

#### Installation via Bash / Galaxy:
```bash
# Install external roles defined in requirements.yml
ansible-galaxy install -r requirements.yml
```

#### Installation via Ansible Playbook:
You can also run a dedicated task or playbook to ensure roles are present on control nodes:
```bash
ansible-playbook -i localhost, -c local playbooks/matrix_test.yml --tags galaxy
```

---

### Module 3: Ansible Execution Environment (EE) Engine (`ansible-builder` + `uv` + Podman)

ASIMP supports containerized Execution Environments (EE) built using `ansible-builder` version 3 schema accelerated by Python `uv`.

#### Installation via Bash Scripting:
```bash
# Run the automated EE build script
./scripts/build_ee.sh
```

#### Manual Build Steps (`uv` + `ansible-builder` + Podman):
```bash
# 1. Install ansible-builder into your uv virtual environment
uv pip install ansible-builder

# 2. Build container image using Podman/Docker
ansible-builder build \
  --file execution-environment/execution-environment.yml \
  --context execution-environment/context \
  --tag asimp-ee:latest
```

---

### Module 4: Sovereign Gitea GitOps Core & Container Registry (`playbooks/gitea_podman_ee.yml`)

This module deploys a self-hosted Gitea GitOps server and OCI container registry running on unprivileged Rootless Podman 5+ & Quadlet systemd units.

#### Installation via Ansible Playbook:
```bash
# Deploy Gitea Quadlet stack on target bastion host
ansible-playbook -i inventory/hosts playbooks/gitea_podman_ee.yml -b
```

---

### Module 5: Security Auditing & Hardening Modules (OpenSCAP, Lynis & Distro Hardening)

ASIMP provides distro-specific security auditing and hardening playbooks for enterprise Linux distributions.

#### Available Hardening Playbooks:

1. **Ubuntu 24.04 / 26.04 LTS Hardening**:
   ```bash
   # Reporting / Audit mode
   ansible-playbook -i inventory/hosts playbooks/ubuntu_lts_hardening.yml -e "execution_mode=report" -b
   # Remediation mode
   ansible-playbook -i inventory/hosts playbooks/ubuntu_lts_hardening.yml -e "execution_mode=remediate" -b
   ```

2. **Debian GNU/Linux Hardening**:
   ```bash
   ansible-playbook -i inventory/hosts playbooks/debian_hardening.yml -e "execution_mode=remediate" -b
   ```

3. **Enterprise Linux (RHEL, AlmaLinux, Rocky) CIS Level 2**:
   ```bash
   ansible-playbook -i inventory/hosts playbooks/rhel_family_cis.yml -e "execution_mode=remediate" -b
   ```

4. **openSUSE Hardening & Sysctl**:
   ```bash
   ansible-playbook -i inventory/hosts playbooks/opensuse_hardening.yml -e "execution_mode=remediate" -b
   ansible-playbook -i inventory/hosts playbooks/suse_sysctl.yml -b
   ```

#### Sandboxed / Unprivileged Fallback (Google Jules Sandbox Mock Engine):
When running inside unprivileged containers or sandboxed environments where SCAP scanners cannot access host kernel interfaces:
```bash
# Run direct mock execution script
./tools/mock-asimp.sh
```

---

### Module 6: Local Multi-OS Podman Testing Matrix (`playbooks/matrix_test.yml`)

The multi-OS testing matrix orchestrates parallel Podman 5+ target OS containers (Ubuntu, Debian, AlmaLinux) using raw execution bootstrapping to verify ASIMP tasks across distributions without SSH overhead.

#### Provisioning via Ansible Playbook:
```bash
# Execute local container testing matrix
ansible-playbook playbooks/matrix_test.yml
```

---

### Module 7: Documentation Compiler & Mintlify Sync Tools (`build_mintlify_mdx.py` & `sync_docs.py`)

ASIMP includes tools to compile standard Markdown into Mintlify MDX format and validate documentation integrity.

#### Execution via Python `uv`:
```bash
# 1. Build Mintlify MDX documentation and docs.json navigation
uv run python tools/build_mintlify_mdx.py

# 2. Run dry-run sync validation
uv run python scripts/sync_docs.py --dry-run

# 3. Verify sitemap links and documentation integrity
uv run python scripts/verify_sitemap_links.py
```

---

## 🛠️ Verification & Diagnostic Checks

After completing installation, verify your environment with the following checklist:

```bash
# 1. Verify Python & Ansible versions
uv run ansible --version

# 2. Perform Playbook Syntax Check
uv run ansible-playbook --syntax-check play-localhost.yml

# 3. Run Unit Test Suite
uv run python -m unittest discover -s tests -p "test_*.py"
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
