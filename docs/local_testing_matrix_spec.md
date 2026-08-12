---
okf_version: "0.1"
layout: default
type: documentation
title: "ASIMP Local Testing Matrix & Telemetry Spec"
timestamp: "2026-08-05T12:00:00Z"
topics: [asimp, architecture, testing, telemetry, pipeline]
---


# ASIMP Local Testing Matrix & Telemetry Specification

This document defines the architectural specification and implementation protocol for the local multi-OS testing matrix and bidirectional feedback telemetry pipeline within the Ansible System Integrity Management Platform (ASIMP).

---

## 1. Architecture & Mode Separation Protocol

To ensure a strict boundary between testing telemetry and user execution, ASIMP employs a conditional mode separation protocol controlled by the environment variable `EXECUTION_MODE` and the Ansible inventory variable `execution_mode`.

```text
                        +----------------------------------------+
                        |  Execution Context Init (Ansible/Bash) |
                        +----------------------------------------+
                                            |
                                            v
                                 Is EXECUTION_MODE=dev?
                                 (or execution_mode == 'dev')
                                   /                  \
                                  /                    \
                                 v                      v
                      [ Yes: Developer Mode ]     [ No: User Mode ]
                                 |                      |
                      +----------------------+  +-------------------------+
                      | Enable Telemetry     |  | Zero Telemetry          |
                      | Gather Debug Metrics |  | Lightweight Execution   |
                      | Hook API/Jules CLI   |  | Clean Exit / Zero Hooks |
                      +----------------------+  +-------------------------+
```

### Modes Defined

1. **Developer / Feedback Mode (`EXECUTION_MODE=dev` / `execution_mode=dev`)**:
   - **Telemetry Collection**: Full capture of tasks, outcomes, stdout/stderr, kernel state, exit codes, and diff analysis.
   - **Dynamic Feedback**: Automatic packaging of telemetry into `/tmp/jules_telemetry.json` and streaming back to Google Jules and active GitHub Pull Requests.
   - **Performance Profiling**: Captures resources utilized by Podman containers.

2. **User / Production Mode (`EXECUTION_MODE=user` / `execution_mode=user`)**:
   - **Zero Telemetry**: All external feedback hooks, API dispatches, and temporary telemetry file writing are physically bypassed.
   - **Lightweight Execution**: Minimum resource overhead, executing native ASIMP baselining and hardening strictly within host borders.

---

## 2. Multi-OS Matrix Orchestration Architecture

Execution runs natively inside Windows WSL2 (Ubuntu 26.04 LTS) and manages a multi-distribution Podman 5+ container matrix.

### Container Grid

- **Ubuntu 24.04 LTS (`ubuntu24`)**: Active baseline testing.
- **Ubuntu 26.04 LTS (`ubuntu26`)**: Bleeding-edge environment validation.
- **AlmaLinux 9 (`alma9`)**: RHEL-compatible ecosystem validation.
- **Debian 12 (`debian12`)**: Pure Debian system compliance validation.

### Failure Diagnostics & Capture

Inside `playbooks/matrix_test.yml`, task-level error handlers (`block/rescue/always`) capture failure states:
- **`block`**: Contains the target tests (ASIMP scans, compliance audits, shell commands).
- **`rescue`**: Activates upon task failure. Registers failure messages, step location, system state, and appends them to host-level telemetry arrays.
- **`always`**: Executes regardless of outcome, ensuring the `feedback_collector` role is loaded to preserve and structure the telemetry data.

---

## 3. Bidirectional Jules CLI & GitHub PR Bridge

The bridge script (`scripts/jules_gh_feedback.sh`) acts as an idempotent dispatch courier between the local testing matrix, Google Jules CLI, and the GitHub Pull Request API.

```text
       +----------------------------+
       |   /tmp/jules_telemetry.json|
       +----------------------------+
                      |
                      v
         +-------------------------+
         | scripts/jules_gh_feedback.sh
         +-------------------------+
               /                 \
              v                   v
     +-----------------+   +-------------------------+
     | Google Jules CLI|   | GitHub API / gh CLI     |
     | (jules chat)    |   | (gh pr comment <PR_ID>) |
     +-----------------+   +-------------------------+
```

### Integrations and Fallbacks

- **Google Jules CLI**: Automatically feeds markdown-formatted test summaries and detailed bug reports via `jules chat` or local HTTP feedback endpoints if available.
- **GitHub PR Integration**: Leverages the official `gh` CLI to post rich, sanitized Markdown status boards directly on the active PR (`gh pr comment <PR_ID> --body-file ...`).
- **Graceful Fallbacks**: If API tokens (`GITHUB_TOKEN`/`GH_TOKEN`) or the Jules environment are absent, the script outputs the exact payload to `/tmp/jules_payload.md` and displays it to stdout, completing successfully without failing the pipeline.

---

## 4. Human-in-the-Loop Developer Workflow

```text
 +-----------------------------------------------------------------------------------+
 | 1. Developer asks Jules: "Generate and patch ASIMP OpenSCAP datastream retrieval" |
 +-----------------------------------------------------------------------------------+
                                          |
                                          v
 +-----------------------------------------------------------------------------------+
 | 2. Jules applies fixes, pushes branch, and generates GitHub Pull Request (e.g., #1) |
 +-----------------------------------------------------------------------------------+
                                          |
                                          v
 +-----------------------------------------------------------------------------------+
 | 3. Developer executes the local test suite on WSL2:                               |
 |    ansible-playbook -i inventory/hosts.yml playbooks/matrix_test.yml \            |
 |                     --extra-vars "execution_mode=dev pr_id=1"                     |
 +-----------------------------------------------------------------------------------+
                                          |
                                          v
 +-----------------------------------------------------------------------------------+
 | 4. Playbook orchestrates Podman containers, runs tests, and logs failing states   |
 +-----------------------------------------------------------------------------------+
                                          |
                                          v
 +-----------------------------------------------------------------------------------+
 | 5. Scripts automatically trigger, pushing telemetry to Jules & commenting on PR   |
 +-----------------------------------------------------------------------------------+
                                          |
                                          v
 +-----------------------------------------------------------------------------------+
 | 6. Developer reviews results in Jules and GitHub, giving next refactoring command |
 +-----------------------------------------------------------------------------------+
```

---

## 5. File Tree Structure

The local matrix integration introduces the following files to the codebase:

```text
├── ansible.cfg                          # Custom Ansible configuration with local roles path
├── inventory/
│   └── hosts.yml                        # Matrix hosts and execution variables
├── playbooks/
│   ├── matrix_test.yml                  # Playbook orchestrating Podman 5+ multi-OS containers
│   └── roles/
│       └── feedback_collector/
│           └── tasks/
│               └── main.yml             # Role assembling host metrics into structured JSON
└── scripts/
    └── jules_gh_feedback.sh             # Telemetry courier bridge script (Jules & GitHub PR)
```
