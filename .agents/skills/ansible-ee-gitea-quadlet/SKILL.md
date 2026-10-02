---
name: ansible-ee-gitea-quadlet
description: Standardise Ansible Execution Environments built via ansible-builder with Python uv and deploy Sovereign Gitea on Rootless Podman Quadlets for air-gapped carrier and enterprise bastions.
okf_version: "0.2"
trust_level: "verified"
type: skill
title: "Ansible Execution Environments & Sovereign Gitea Quadlet Skill"
timestamp: "2026-08-20T12:00:00Z"
topics: [ansible, execution-environment, gitea, podman, quadlet, uv]
---

# Ansible Execution Environments & Sovereign Gitea Quadlet Skill

## Overview

This Agent Skill provides domain operational knowledge and automated procedure specifications for constructing standardized **Ansible Execution Environments (EE)** using `ansible-builder` version 3 schema with Python `uv` acceleration, and publishing EE container images to a self-hosted **Sovereign Gitea Core & Container Registry** running on unprivileged **Rootless Podman 5+ & Quadlets**.

## When to Apply This Skill

Apply this skill when:
1. Standardizing execution environments for air-gapped carrier or enterprise bastion hosts.
2. Accelerating `ansible-builder` container image creation using Python `uv`.
3. Automating Sovereign Gitea deployment over Rootless Podman Quadlets (`.kube` and Kubernetes YAML specs).
4. Running `ansible-runner` or `ansible-navigator` with process isolation inside air-gapped bastions.

## Operational Standards & Invariants

1. **Ansible Builder Schema v3 & Immutable Digest**:
   - `execution-environment/execution-environment.yml` must use `version: 3`.
   - Base image `quay.io/ansible/ansible-runner` must be pinned by an immutable SHA256 digest (`@sha256:...`).
   - Prepend build steps install `uv` (`RUN pip install --no-cache-dir uv`).

2. **Rootless Podman 5+ & User Namespace Mapping**:
   - Gitea runs unprivileged using systemd Quadlets (`gitea-stack.kube` & `gitea-stack.yaml`).
   - TLS private keys (`gitea.key`) use mode `0600` and are assigned to container namespace `1000:1000` via `podman unshare chown 1000:1000`.

3. **Ansible Playbook Execution Standards**:
   - User identity resolved dynamically via `ansible.builtin.getent`.
   - Database passwords loaded from Vault or environment variables and serialized via `{{ gitea_db_pass | to_json }}`.
   - User systemd service managed via `ansible.builtin.systemd_service` with `scope: user`.

4. **Air-Gapped Bastion Execution & Registry Security**:
   - Requires a trusted registry CA by default for both image pushes and pulls, permitting disabled TLS verification only on isolated air-gapped test networks.
   - Requires the EE container image to be referenced by immutable digest or tag (`10.17.250.28:3000/songketmailsdnbhd-group/asimp-ee@sha256:...`).
   - `ansible-runner` runs with process isolation: `ansible-runner run /etc/ansible/runner --process-isolation --process-isolation-executable podman --container-image ...`.

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
