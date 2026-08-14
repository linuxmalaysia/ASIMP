---
title: "Diátaxis Documentation Framework"
description: "Overview of how the four documentation quadrants organize technical content for human developers and autonomous agents."
type: "concept"
id: "docs/explanation/diataxis.md"
dsom_governance:
  domain: "Automation"
  context_tier: "L1-Overview"
tags:
  - "diataxis-quadrant"
  - "documentation"
  - "dsom-protocol"
related_links:
  - "docs/explanation/dsom-governance.md"
  - "docs/explanation/system-architecture.md"
nav_order: 20
layout: "default"
---

# Diátaxis Documentation Framework

ASIMP documents are organized using the **Diátaxis Structuring Framework**, which separates knowledge into four distinct quadrants based on the reader's intent and context. This structural predictability benefits both human administrators and autonomous AI agents.

---

## 🧭 The Four Quadrants of Diátaxis

```
                          PRACTICAL
                              ^
                              |
             TUTORIALS        |       HOW-TO GUIDES
         (Learning-Oriented)  |    (Problem-Oriented)
                              |
                              +---------------------> USER WORK
                              |
             EXPLANATION      |       REFERENCE
         (Understanding-      |    (Information-
            Oriented)         |       Oriented)
                              v
                         THEORETICAL
```

### 1. Tutorials (Learning-Oriented)
- **Goal**: Helping the newcomer start successfully.
- **Form**: Guided, step-by-step onboarding walkthroughs.
- **Tone**: Friendly, hands-on, educational.

### 2. How-To Guides (Task-Oriented)
- **Goal**: Helping experienced users solve specific, practical problems.
- **Form**: Copy-pasteable recipes, operational scripts, execution blocks.
- **Tone**: Concise, direct, recipe-style.

### 3. Reference Material (Information-Oriented)
- **Goal**: Providing precise, objective descriptions of the system.
- **Form**: API tables, configuration variable lists, file paths, CLI flags, exit states.
- **Tone**: Absolute technical precision. Zero hand-holding.

### 4. Explanation (Understanding-Oriented)
- **Goal**: Explaining architectural choices, governance models, and design trade-offs.
- **Form**: Conceptual descriptions, Mermaid graphs, and system topologies.
- **Tone**: Strategic, explanatory, analytical.

---

## 🧠 Strategic Merging with DSOM Protocol

By matching DSOM's Progressive Disclosure to Diátaxis quadrants:
- **L1-Overview** corresponds to **Explanation**.
- **L2-Operational** corresponds to **Tutorials** and **How-To Guides**.
- **L3-TechnicalReference** corresponds to **Reference Material**.

This allows autonomous crawlers to index and consume only the necessary quadrant depending on their immediate execution phase, saving critical context bandwidth.
