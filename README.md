# ASIMP (Ansible System Integrity Management Platform)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Ansible](https://img.shields.io/badge/Ansible-%3E%3D9.0.0-red.svg)](https://www.ansible.com/)
[![OpenSCAP](https://img.shields.io/badge/Security-OpenSCAP-green.svg)](https://www.open-scap.org/)
[![Lynis](https://img.shields.io/badge/Audit-Lynis-orange.svg)](https://cisofy.com/lynis/)

**ASIMP** is a host-based, automated security hardening, compliance, and auditing framework. Powered by Ansible, ASIMP is designed to secure modern Linux systems and evaluate their compliance against standard security baselines.

It implements a **"Measure, Harden, Re-Measure"** paradigm, providing immediate visibility into system compliance posture before and after security policies are applied.

---

## 🚀 Key Features

* **Dual-Engine Security Auditing**: Combines **OpenSCAP** (scanning against CIS Security Linux Level 2 profile) and **Lynis** (comprehensive system configuration auditing) to assess system integrity.
* **Pre & Post Auditing (Reporting)**: Runs security scans *before* applying modifications to establish a baseline, runs them *afterwards*, and outputs a comparative, clear progress report.
* **Automated Package Updates**: Standardizes Ubuntu/Debian updates and checks package-level integrity using `debsums`.
* **Standardized OS Hardening**: Integrates standard hardening benchmarks via OpenStack's `ansible-hardening` and secure SSH setups via Dev-Sec's `ssh-hardening`.
* **Extensible & Multi-Platform**: Fully compatible with modern enterprise-grade Linux distributions including **Ubuntu**, **Debian**, **RedHat (RHEL)**, **CentOS**, and **Rocky Linux**.

---

## 🛠️ Architecture & Workflow

The platform executes hardening and compliance in a three-phase pipeline:

```
+-----------------------------------+
|  PHASE 1: Baseline Auditing       |
|  - Run OpenSCAP & Lynis Baseline  |  ==> Establishes "/var/log/asimp-baseline-scores.json"
|  - Store pre-hardening scores     |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
|  PHASE 2: Hardening & Mitigation  |
|  - Update OS & Verify Integrity   |  ==> Installs updates, runs "debsums"
|  - Apply System Hardening policies|  ==> OpenStack Hardening & SSH Hardening
|  - Apply Lynis-specific fixes     |  ==> Fine-grained configuration policies
+-----------------------------------+
                  |
                  v
+-----------------------------------+
|  PHASE 3: Verification & Reporting|
|  - Re-run OpenSCAP & Lynis Audits |  ==> Generates "after" results
|  - Compute Comparative Report     |  ==> Displays side-by-side compliance improvement
+-----------------------------------+
```

---

## 📁 Repository Structure

* **`play.yml`**: Main playbook designed for multi-host remote configurations.
* **`play-localhost.yml`**: Main playbook tailored for executing ASIMP on the localhost environment.
* **`requirements.yml`**: External Ansible Galaxy dependencies (SSH, chrony, etc.).
* **`requirements.txt`**: Python dependencies (Ansible, ansible-lint, cryptography).
* **`ansible.cfg`**: Configures Ansible behaviors, SSH pipelining, and custom roles paths.
* **`roles/`**:
  * `reporting-ASIMP`: Manages the dual-engine baseline generation, post-hardening analysis, and reporting.
  * `update-ubuntu-ASIMP`: Handles Ubuntu/Debian system upgrades, repository updates, and `debsums` verification.
  * `lynis-ansible`: Manages localized Lynis audit automation and compliance profiling.

---

## 📋 Prerequisites & Installation

### 1. Python & Local Tools Setup
Ensure you have Python 3 installed. It is recommended to create a virtual environment to avoid package conflicts:

```bash
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Ansible Galaxy Roles
Download the required external roles defined in `requirements.yml` (e.g., Dev-Sec SSH, OpenStack hardening, Chrony):

```bash
ansible-galaxy install -r requirements.yml
```

---

## 💻 How to Run ASIMP

### Option A: Localhost Hardening
To audit and harden the machine you are currently logged into:

```bash
# Activate your virtual environment first
source /tmp/venv/bin/activate

# Execute the local playbook (requires sudo/become)
ansible-playbook --connection=local play-localhost.yml
```

### Option B: Remote Inventory Hardening
To secure and audit remote systems:

```bash
# Run against all hosts in your inventory (specify -i your_inventory_file)
ansible-playbook -b -K play.yml
```

---

## 📊 Security Metrics & Reports

Upon execution, ASIMP will display a consolidated security scorecard similar to this:

```
========================================================================
                 ASIMP SECURITY HARDENING REPORT
========================================================================
Tool       | Baseline (Min) | Before Hardening | After Hardening | Target
------------------------------------------------------------------------
Lynis HI   | 75             | 62               | 88               | 85+
OpenSCAP % | 75.0%          | 58.4%            | 91.2%            | 90%+
========================================================================
Reports generated successfully:
  - OpenSCAP Before Report: /var/log/openscap-before-report.html
  - OpenSCAP After Report:  /var/log/openscap-after-report.html
========================================================================
```

Comprehensive HTML reports are generated at `/var/log/openscap-before-report.html` and `/var/log/openscap-after-report.html` for deep inspection.

---

## 🐳 Testing & Integration

### Testing in Centos/RHEL Container
A pre-configured CentOS-based hardening Docker image is available on DockerHub for testing:
* **Docker Hub**: [linuxmalaysia/docker-centos-latest-harden](https://hub.docker.com/repository/docker/linuxmalaysia/docker-centos-latest-harden/general)

To test a RHEL/CentOS 8 hardening pipeline manually:
```bash
cd roles
git clone https://github.com/RedHatOfficial/ansible-role-rhel8-ospp.git
```

### ARA Integration
For visual inspection and historical tracking of playbook execution, check out **ARA (Ansible Records Ansible)**:
* **GitHub**: [ARA Community](https://github.com/ansible-community/ara)

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
