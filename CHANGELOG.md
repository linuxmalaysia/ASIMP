# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-30

### Added
- **Dual-Engine Before/After Reporting Pipeline**: Implemented a comprehensive reporting mechanism in `roles/reporting-ASIMP` that evaluates system integrity via OpenSCAP and Lynis before applying hardening, saves baseline scores, and prints a comparative scorecard post-hardening.
- **OpenSCAP Integration**: Added automated scanning against the CIS Security Linux Level 2 profile (`xccdf_org.ssgproject.content_profile_cis_level2_server`) with dynamic datastream discovery for Ubuntu, CentOS, Rocky Linux, and RHEL.
- **Debsums Verification**: Added debsums package integrity checks within the `update-ubuntu-ASIMP` role to detect unauthorized binary changes or corruption.
- **Enterprises OS Support**: Added explicit OS discovery and tasks to support modern CentOS, Rocky Linux, and RHEL alongside Debian/Ubuntu.

### Changed
- **Ansible & Toolchain Modernization**: Upgraded the minimum requirements and refined configurations to match standard, secure, and modern Ansible releases (Ansible >= 9.0.0).
- **Asynchronous Execution**: Enabled asynchronous execution for long-running apt/dnf package updates and debsums scans to prevent playbooks from timing out.
- **Improved SSH & Core Hardening**: Updated dependency configurations for Dev-Sec SSH hardening and OpenStack baseline system-hardening policies.

### Fixed
- Fixed host detection logic to correctly identify RHEL, Rocky Linux, and Debian variants and apply matching configuration files and datastreams dynamically.
- Gracefully handled environments where OpenSCAP packages or datastreams are missing by falling back to any available baseline/profile profiles.

---

## [1.0.0] - 2020-01-27

### Added
- Initial release of the Ansible System Integrity Management Platform (ASIMP).
- Added base Ubuntu upgrade/update management role.
- Added support for Lynis-based host security auditing.
- Added playbooks for local and multi-node execution (`play.yml`, `play-localhost.yml`).
- Added Docker-based test environments for CentOS/RHEL systems.

[1.1.0]: https://github.com/linuxmalaysia/ASIMP/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/linuxmalaysia/ASIMP/releases/tag/v1.0.0
