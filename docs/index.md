---
title: "About ASIMP & Documentation"
okf_version: "0.1"
type: documentation
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, docs, manual, security]
---

# About ASIMP (Ansible System Integrity Management Platform)

Welcome to the official documentation and info portal for **ASIMP**.

**ASIMP** is an automated, host-based security hardening, compliance auditing, and integrity monitoring framework. Powered entirely by Ansible, ASIMP is designed to secure modern enterprise Linux environments against standard security baselines.

The platform implements a strict **"Measure, Harden, Re-Measure"** paradigm, offering instant visibility into system compliance posture before and after security configurations are applied.

---

## 🚀 Key Security Pillars

1. **Dual-Engine Security Auditing**:
   - **OpenSCAP**: Scans systems against the CIS (Center for Internet Security) Level 2 Security Profile.
   - **Lynis**: Performs a thorough check of system settings, kernel parameters, file permissions, and vulnerable endpoints.

2. **Standardized OS Hardening**:
   - Integrates secure default baselines using OpenStack's `ansible-hardening` recommendations.
   - Applies robust, production-grade SSH security using Dev-Sec's SSH-hardening suite.

3. **Integrity Validation with `debsums`**:
   - Compares installed package files against locally stored MD5 checksums to detect local changes or corruption.

4. **Self-Observing Comparative Scorecard**:
   - Automatically computes exact "before" vs. "after" audit scores and saves details locally, outputting a clear visual comparison directly to the console or log files.

---

## 📁 Technical Documentation Index

Explore the different sections of our system design, setup guides, and troubleshooting:

- **[Architecture & Design](architecture.html)**: Learn about the internal components, dual auditing flow, three-phase security pipeline, and our package integrity monitoring engines.
- **[AI Agents & DSOM Integration](ai_agents.html)**: Learn how ASIMP integrates with autonomous AI agents following the Deep State Of Mind (DSOM) For My AI Protocol, using spatial, procedural, and conceptual memory.
- **[OpenSCAP Integration & Playbooks](openscap.html)**: Detailed overview of how ASIMP manages OpenSCAP packages, selects dynamic datastreams, parses compliance scores, and handles USN OVAL reviews.
- **[Lynis Auditing & Playbooks](lynis.html)**: Detailed analysis of how ASIMP conducts host audits, extracts the Hardening Index, and integrates with the `lynis-ansible` hardening role.
- **[Configuration & Variables](configuration.html)**: Discover customizable variables for our roles (`reporting-ASIMP`, `update-ubuntu-ASIMP`, `lynis-ansible`) and sample inventories.
- **[Troubleshooting & Fallbacks](troubleshooting.html)**: Read detailed instructions on addressing DataStream resolution errors, connection elevation failures, and timeout behaviors.
- **[Review & Adoption of DSOM Guide](dsom_ansible_review.html)**: Structural alignment review of the DSOM Ansible Configuration Guide v3.6.2.
- **[Rootless Podman 5+ & Quadlet Orchestration](podman_rootless.html)**: Overview of rootless orchestration, systemd Quadlets, namespace mappings, and unprivileged container matrix testing.
- **[Ansible Best Practices & FQCN Standards](ansible_fqcn.html)**: Guidelines for Fully Qualified Collection Names (FQCN), task idempotency checks, and privilege strategies.
- **[Ansible Playbook and Document Architecture Map](ansible_playbook_map.html)**: Architectural dictionary linking playbook files with their core roles and operational documents.
- **[Local Knowledge-First & Metadata Discovery](sop_knowledge_first_discovery.html)**: SOP guidelines for unprivileged and agentic spatial discovery and context preservation.

---

## 💻 Fast Setup & Playbook Execution

Get started with ASIMP inside a Python virtual environment:

```bash
# Setup Virtual Environment
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -r requirements.txt

# Install Ansible Galaxy Dependencies
ansible-galaxy install -r requirements.yml

# Execute Local Host Hardening
ansible-playbook --connection=local -b -K play-localhost.yml
```
