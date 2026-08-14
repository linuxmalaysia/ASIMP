---
title: "Sovereign Feedback Collector Reference"
description: "Detailed specification of scripts/jules_gh_feedback.sh telemetry aggregator."
type: "reference"
id: "docs/reference/jules-gh-feedback.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L3-TechnicalReference"
tags:
  - "reference"
  - "telemetry"
  - "feedback"
related_links:
  - "docs/reference/index.md"
nav_order: 50
layout: "default"
---

# Sovereign Feedback Collector Reference

`scripts/jules_gh_feedback.sh` is a shell utility designed to aggregate multi-OS run metrics and stream test reports back to the active user session or Pull Request comments.

---

## 🛠️ CLI Execution & Environment

The script is invoked automatically by reporting tasks or during automated pre-merge pipelines.

### Environment Variables Used
- `GITHUB_TOKEN`: Auth token for publishing PR comment feedback.
- `GITHUB_PR_NUMBER`: Targeted Pull Request ID.
- `JULES_TELEMETRY_PATH`: Temporary workspace for metric logs (defaults to `/tmp/jules_telemetry.json`).

---

## 🔒 Exit Codes

- `0`: Success. Telemetry compiled and feedback published.
- `1`: Network or Auth failure when streaming telemetry.
