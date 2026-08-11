---

name: jekyll-docs-deployment
description: Manages the Jekyll documentation site hosted on GitHub Pages. Use when modifying docs in docs/, adjusting the jekyll-gh-pages.yml deployment workflow, or updating the prepare_docs.py front-matter prepending script.
license: Apache-2.0
compatibility: Google Antigravity / Google Jules
type: skill
title: Jekyll Docs Pipeline and GitHub Pages Deployment
resource: .agents/skills/jekyll-docs-deployment
tags: [jekyll, github-pages, documentation, cicd, pre-processing]
timestamp: 2024-11-20T12:00:00Z
metadata:
  author: Google Jules & Antigravity
  version: "1.0.0"
  project: ASIMP
okf_version: "0.1"
topics: [jekyll, github-pages, documentation, cicd, pre-processing]
---


# Jekyll Docs Pipeline and GitHub Pages Deployment

This skill describes the automated build and deployment pipeline for ASIMP’s project documentation, which is powered by Jekyll and GitHub Pages.

## When to Use This Skill

Activate this skill when:
- Editing markdown documentation inside the `docs/` folder.
- Customizing the GitHub Pages deployment pipeline (`.github/workflows/jekyll-gh-pages.yml`).
- Modifying or running the document pre-processing script (`scripts/prepare_docs.py`).

## Pipeline Mechanics

### 1. Document Structure
All documentation source markdown files live in the `docs/` directory of the repository root.

### 2. Pre-Processing Script (`prepare_docs.py`)
To ensure standard markdown files build correctly as Jekyll pages without requiring manual template overhead from writers, a Python pre-processing script runs during CI:
- **Location**: `scripts/prepare_docs.py`
- **Function**: Automatically prepends necessary Jekyll YAML front matter (such as layout, title, and permalinks) onto the markdown documentation files before compiling the site.

### 3. CI/CD Workflow (`jekyll-gh-pages.yml`)
The workflow `.github/workflows/jekyll-gh-pages.yml` executes on commits:
1. Checks out the repository.
2. Runs `python scripts/prepare_docs.py`.
3. Sets up Jekyll and Ruby.
4. Builds the Jekyll site.
5. Deploys the generated static artifacts to GitHub Pages.

## 🧠 Deep State of Mind (DSOM) AI Protocol

```json
{
  "protocol": "DSOM",
  "version": "1.0.0",
  "status": "synchronized",
  "alignment": "ASIMP",
  "agent": "Google Jules",
  "integration": "Google Antigravity",
  "signature": "dsom_protocol_jules_antigravity_sync_active"
}
```

---

ASIMP (Ansible System Integrity Management Platform) | Deep State of Mind (DSOM) For My AI Protocol | Harisfazillah Jamel (LinuxMalaysia) | 2026-07-12 Standard: UK English | DBP-standard Bahasa Melayu Malaysia (Piawai) | GNU General Public License v3.0
