---
name: openscap-operational-auditor
description: Manages multi-distribution OpenSCAP operational auditing (OVAL & XCCDF), finding-driven air-gapped package harvesting, and safeguarded baseline remediation across RHEL, AlmaLinux, Rocky Linux, Oracle Linux, Ubuntu, Debian, and openSUSE.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Multi-Distribution OpenSCAP Operational Auditor & Remediation Skill
resource: .agents/skills/openscap-operational-auditor
tags: [openscap, oval, xccdf, air-gapped, remediation, tailoring, cis, multi-distro]
timestamp: "2026-10-07T17:38:00+08:00"
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.2"
trust_level: "verified"
sidebarTitle: "OpenSCAP Operational Auditor"
topics: [openscap, oval, xccdf, air-gapped, remediation, tailoring, cis, multi-distro]
---

# Multi-Distribution OpenSCAP Operational Auditor & Remediation Skill

This skill defines the operational procedures for performing dual-track OpenSCAP security assessments (OVAL vulnerability scanning and XCCDF baseline compliance) across enterprise Linux distributions.

## When to Use This Skill

Activate this skill when:
- Conducting authenticated on-host OVAL vulnerability audits across mixed-OS Linux fleets.
- Resolving target OS-specific OVAL feeds (`rhel-8.oval.xml`, `com.ubuntu.noble.usn.oval.xml`, `oval-definitions-bookworm.xml`).
- Executing finding-driven air-gapped package errata harvesting (resolving affected package names from OVAL XML result files).
- Generating custom OpenSCAP Tailoring XML files (`tailoring.xml`) to de-select destructive rules (SCTP protocol disable, `/tmp` noexec, container IP forwarding disable).
- Performing preflight profile structure and datastream validations prior to automated remediation.

## Core Procedures

### 1. Dynamic OVAL Definition Stream Resolution
- Determine `host_oval_filename` per distribution family:
  - RHEL 8 / Alma 8 / Rocky 8 / OL 8 -> `rhel-8.oval.xml`
  - RHEL 9 / Alma 9 / Rocky 9 / OL 9 -> `rhel-9.oval.xml`
  - RHEL 10 / Alma 10 / Rocky 10 / OL 10 -> `rhel-10.oval.xml`
  - Ubuntu -> `com.ubuntu.<release>.usn.oval.xml`
  - Debian 11 -> `oval-definitions-bullseye.xml`
  - Debian 12 -> `oval-definitions-bookworm.xml`
  - Else -> Fail with explicit message indicating unsupported OVAL feed.

### 2. Finding-Driven Air-Gapped Errata Harvesting
- Parse OVAL XML results (`/var/tmp/openscap_oval/oval-results-<hostname>.xml`) using Python `xml.etree.ElementTree` to extract affected package names from definitions evaluated as `true` or `vulnerable`.
- Validate that the target package list file is non-empty (`if [ -s ... ]`) before initiating candidate DEB/RPM downloads.
- Verify downloaded bundle package integrity using `dpkg-deb -I` or `rpm -Va` prior to archiving and offline transport.

### 3. Safeguarded Baseline Remediation
- Deploy tailored XML profiles (`tailoring.xml`) extending standard benchmark profiles (`xccdf_org.ssgproject.content_profile_cis` or `content_profile_standard` for Debian).
- Validate tailoring file structure (`oscap info <tailoring.xml>`) and datastream content (`oscap info <datastream.xml>`) prior to applying fixes with `--remediate`.
- Enforce pre-remediation subsystem health assertions (verifying message broker daemons and container managers are active) to prevent self-inflicted production outages.

## 🧠 Deep State of Mind (DSOM) AI Protocol

```json
{
  "protocol": "DSOM",
  "version": "1.0.0",
  "status": "synchronized",
  "alignment": "ASIMP",
  "agent": "Google Jules",
  "integration": "Google Antigravity",
  "signature": "dsom_protocol_jules_antigravity_openscap_auditor_sync"
}
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0 | [Legal Notice & Disclaimer](https://linuxmalaysia.github.io/ASIMP/legal-notice.html)
