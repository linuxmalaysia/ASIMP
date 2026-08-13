---
layout: default
okf_version: "0.1"
type: documentation
title: "OpenSCAP Integration & Playbook Analysis"
timestamp: "2026-08-05T12:00:00Z"
topics: [openscap, security, compliance, audit, playbooks, ansible]
---

# OpenSCAP Integration & Playbook Analysis

The **Security Content Automation Protocol (SCAP)** is a line-of-defense standard for vulnerability management, measurement, and policy compliance evaluation. In ASIMP, **OpenSCAP** serves as one of the two core security engines to evaluate and enforce system baseline compliance.

ASIMP leverages OpenSCAP to scan target hosts against the **CIS (Center for Internet Security) Level 2 Server** profile, generating baseline audits in Phase 1 and verification audits in Phase 3.

---

## 🧭 Role and Profile Configuration

The primary scanning profile used by ASIMP is defined dynamically in the `reporting-ASIMP` role. To perform valid scans, the framework requires selecting a profile ID that exists in each datastream. Because different profiles exist for different operating system families, the appropriate RHEL-family profile must be used instead of the Ubuntu ID when evaluating RHEL, CentOS, or Rocky Linux hosts:

```yaml
openscap_profile: "xccdf_org.ssgproject.content_profile_cis_level2_server"
```

### Profile Discovery & Validation
Before executing scans, the framework performs discovery and validation of both the profile and the underlying datastream XML content. This ensures compatibility and prevents execution crashes. If a datastream is missing or unsupported on a given target OS, ASIMP ensures the scan is skipped and the host's `openscap_scan_supported` flag is set to `false`. This prevents unsupported scans from being silently treated as successful audits, ensuring complete reporting transparency.

---

## ⚙️ Ansible Playbook Analysis: Step-by-Step

The implementation of OpenSCAP in ASIMP is structured in the `roles/reporting-ASIMP/tasks/main.yml` file. Let's analyze how this plays out during the execution flow:

### 1. Package Installation

To perform SCAP scans, the platform dynamically installs the scanner and operating system specific SCAP Security Guides (SSG).

```yaml
- name: OpenSCAP | Install Packages (Ubuntu)
  ansible.builtin.apt:
    name:
      - openscap-scanner
      - ssg-debian
      - ssg-debderived
      - unzip
      - wget
      - curl
      - bzip2
    state: present
    update_cache: yes
  when:
    - is_ubuntu
    - not (is_sandbox_jules | default(false) | bool)
  ignore_errors: yes
```

- For Debian/Ubuntu-based systems, `openscap-scanner` and standard `ssg-` packages are installed.
- For RedHat/CentOS/Rocky systems, the playbook installs `openscap-scanner` and `scap-security-guide` via `dnf`.
- The task automatically detects and skips installation if running in an unprivileged Google Jules sandbox (`is_sandbox_jules: true`) or limited environment to prevent permission and repository timeouts.

---

### 2. Dynamic XML DataStream Selection & Fetching

To ensure the scanning rules perfectly match the OS, ASIMP dynamically resolves the platform and version.

For **Ubuntu**, ASIMP reaches out to the official `ComplianceAsCode/content` repository on GitHub to fetch the latest SCAP Security Guide zip, extract it, and locate the version-specific DataStream XML:

{% raw %}

```yaml
- name: OpenSCAP | Fetch latest SCAP Security Guide release from GitHub (Ubuntu)
  block:
    - name: OpenSCAP | Get latest release download URL
      ansible.builtin.shell: >
        curl -s https://api.github.com/repos/ComplianceAsCode/content/releases/latest |
        grep "browser_download_url" | grep "scap-security-guide-" | grep ".zip" | head -n 1 | cut -d '"' -f 4
      register: scap_latest_url_raw
      ...
    - name: OpenSCAP | Download latest SCAP Security Guide zip
      ansible.builtin.get_url:
        url: "{{ scap_latest_url }}"
        dest: "{{ openscap_report_dir }}/{{ scap_latest_url | basename }}"
        checksum: "sha512:{{ scap_latest_url }}.sha512"
      ...
    - name: OpenSCAP | Find extracted Ubuntu datastream XML file
      ansible.builtin.find:
        paths: "{{ openscap_report_dir }}"
        patterns: "ssg-ubuntu{{ ansible_distribution_version | replace('.', '') }}-ds.xml"
        recurse: yes
      register: found_downloaded_ds
```

{% endraw %}

For **RHEL/CentOS/Rocky Linux**, ASIMP searches for pre-installed datastreams located under `/usr/share/xml/scap/ssg/content/` and selects the appropriate version:

{% raw %}

```yaml
- name: OpenSCAP | Set datastream fact
  ansible.builtin.set_fact:
    openscap_datastream: >-
      {%- if ansible_distribution | lower == 'rocky' -%}
      /usr/share/xml/scap/ssg/content/ssg-rocky{{ ansible_distribution_major_version }}-ds.xml
      {%- elif ansible_distribution | lower == 'centos' -%}
      /usr/share/xml/scap/ssg/content/ssg-centos{{ ansible_distribution_major_version }}-ds.xml
      {%- else -%}
      /usr/share/xml/scap/ssg/content/ssg-rhel{{ ansible_distribution_major_version }}-ds.xml
      {%- endif -%}
```

{% endraw %}

If no compatible datastream XML file exists, the task registers `openscap_scan_supported: false` and gracefully skips the scan.

---

### 3. Execution of Scan (Before / After Hardening)

The OpenSCAP evaluation command is executed using the `ansible.builtin.shell` module. To measure compliance improvement, separate scans are run during Phase 1 (`before`) and Phase 3 (`after`):

{% raw %}

```yaml
- name: Run OpenSCAP BEFORE hardening scan
  ansible.builtin.shell: >
    oscap xccdf eval
    --profile {{ openscap_profile }}
    --fetch-remote-resources
    --results {{ openscap_report_dir }}/ssg-results-ubuntu{{ ansible_distribution_version | replace('.', '') }}.xml
    --report {{ openscap_report_dir }}/ssg-results-ubuntu{{ ansible_distribution_version | replace('.', '') }}.html
    {{ openscap_datastream }}
  register: oscap_before_run
  failed_when: false
  changed_when: true
```

{% endraw %}

The output XML results and HTML reports are written to `ssg-results-ubuntu<version>.xml` / `ssg-results-ubuntu<version>.html`, and then copied to `/var/log/openscap-before-results.xml` (or `/var/log/openscap-after-results.xml`) for unified storage.

---

### 4. OpenSCAP Score Parsing Helper Script

After generating the raw XML result file, ASIMP parses the overall compliance score. It writes a lightweight Python script `parse_openscap_score.py` directly to the report directory at runtime:

```python
#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET

def get_score(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {
            'xccdf12': 'http://checklists.nist.gov/xccdf/1.2',
            'xccdf11': 'http://checklists.nist.gov/xccdf/1.1'
        }
        score_elem = root.find('.//xccdf12:score', ns)
        if score_elem is not None:
            return float(score_elem.text)
        ...
```

The playbook executes this helper script to read the parsed score directly into an Ansible variable:

{% raw %}

```yaml
- name: Parse OpenSCAP BEFORE compliance score
  ansible.builtin.command:
    argv:
      - python3
      - "{{ openscap_report_dir }}/parse_openscap_score.py"
      - /var/log/openscap-before-results.xml
  register: parsed_openscap_before
  changed_when: false
  failed_when: false
```

{% endraw %}

---

### 5. Dynamic Bash Remediation Script Generation

A major feature of ASIMP's OpenSCAP integration is generating a tailor-made remediation script for the target operating system. On Ubuntu systems with full privileges, ASIMP commands OpenSCAP to output a shell script containing the exact remediation configurations needed to align with the CIS Level 2 profile:

{% raw %}

```yaml
- name: OpenSCAP | Generate BEFORE Remediation Script (Ubuntu)
  ansible.builtin.shell: >
    oscap xccdf generate fix
    --profile {{ openscap_profile }}
    --fix-type bash
    --output {{ openscap_report_dir }}/remediate-{{ ansible_distribution_release }}-latest.sh
    {{ openscap_datastream }}
  changed_when: true
  failed_when: false
```

{% endraw %}

This shell script can then be inspected or executed manually by administrators seeking a transparent, audited mitigation path.

---

### 6. Ubuntu USN OVAL Vulnerability Assessment

To check for unpatched Ubuntu Security Notices (USNs), the playbook downloads Canonical's official OVAL definition file and performs an OVAL evaluation:

{% raw %}

```yaml
- name: OpenSCAP | Download OVAL definitions
  ansible.builtin.get_url:
    url: "https://security-metadata.canonical.com/oval/com.ubuntu.{{ ansible_distribution_release }}.usn.oval.xml.bz2"
    dest: "{{ openscap_report_dir }}/com.ubuntu.{{ ansible_distribution_release }}.usn.oval.xml.bz2"
  ...
- name: OpenSCAP | Decompress OVAL definitions
  ansible.builtin.command: "bunzip2 -f -k {{ openscap_report_dir }}/com.ubuntu.{{ ansible_distribution_release }}.usn.oval.xml.bz2"
  ...
- name: OpenSCAP | Run OVAL evaluation
  ansible.builtin.shell: >
    oscap oval eval
    --report {{ openscap_report_dir }}/oval-{{ ansible_distribution_release }}.html
    {{ openscap_report_dir }}/com.ubuntu.{{ ansible_distribution_release }}.usn.oval.xml
```

{% endraw %}

---

## 🐳 Unprivileged Sandbox & Mock Execution Mode

In restricted or unprivileged environments (such as the Google Jules containerized sandbox detected via `/home/jules`), low-level system calls, kernel configurations, and downloading heavy zip files are prevented.

To handle these limitations gracefully:
1. **Dynamic Detection**: ASIMP identifies the sandbox via `/home/jules` and sets `openscap_scan_supported: false` to avoid installation and download failures.
2. **Audit Check & Fallback Execution**: The playbook tests if `oscap` is installed in the path. If it is present and an XML datastream can be located, it runs a safe, non-destructive evaluation.
3. **Simulated Scoring (NON-AUTHORITATIVE & TEST-ONLY)**: If the tools or datastreams are missing or fail, the playbook falls back to safe simulated scoring (e.g., a baseline score of `58.4%` and a post-hardening score of `91.2%`).
   - **Important Note**: These simulated/mock fallback scores and any derived "Compliant" or "Non-vulnerable" reports are strictly **non-authoritative and test-only data**. They are preserved strictly for sandbox test verification and CI/CD logical consistency.
4. **Downstream Compliance Gate Behavior**: To prevent any security bypasses, downstream compliance-gate verification explicitly **rejects** simulated/mock results. Simulated executions will fail to satisfy any actual compliance checkpoints (i.e. `openscap_success` and `audits_completed` are set to `false` when simulated fallbacks are used), ensuring only real, verified audits can validate a system's true security baseline.
5. **Mock Scorecard Generation**: It saves the scores to `data/asimp_mock/var/log/asimp-baseline-scores.json` and templates a comprehensive Markdown report at `data/asimp_mock/opt/report/openscap/SECURITY_AUDIT_REPORT.md` conforming to standard OKF v0.1 guidelines. This guarantees that execution pipelines compile and complete successfully under any privilege level.

---

## 🔒 Safety & Boot/Network Lockout Prevention

A critical design choice in ASIMP's OpenSCAP integration is generating a tailor-made remediation bash script (`remediate-*.sh`) for manual inspection **instead of automatically or blindly running raw, destructive SCAP fixes**.

While this approach significantly reduces the risk of system instability, pre-flight checks and manual remediation reviews cannot fully guarantee boot, SSH, PAM, or network availability under all system conditions, and require final validation by an administrator:
- **No Silently Broken Configuration**: High-risk SCAP compliance changes (such as aggressive PAM modifications or bootloader parameters) are never applied blindly by the background playbooks.
- **Pre-execution Audit Path**: System administrators can audit, customize, test, and selectively execute parts of the generated bash fixes manually when they are confident that no boot or network capabilities will be impacted.
