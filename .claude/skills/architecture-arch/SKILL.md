---
name: architecture-arch
description: Build a mental model before touching code. Use when joining large repos, legacy systems, or before refactoring.
---

# Skill: arch

**Purpose**: Build a mental model before touching code

**Use when**:
- Joining large repos, legacy systems, or agent frameworks
- Before any refactoring work
- Need repeatable, comparable architecture summaries

> **vs `/learning-codebase-mastery`**: Use `/architecture-arch` when you need a **reference document** — a map of components, execution paths, and risks. Use `/learning-codebase-mastery` when you want to **learn and retain** how specific code works through quizzes and exercises.

---

## Process

When user asks to understand architecture:

1) **Ask what the target is**:
   - "whole repo", "service", "pipeline", or "specific module"

2) **Inspect codebase** using search/grep and summarize:
   - Entrypoints (CLI, FastAPI/Flask app, workers)
   - Boundaries (packages, domains)
   - Data flow (inputs -> transforms -> outputs)
   - Runtime flow (requests, async jobs, schedulers)

3) **Produce outputs** in this exact format:

```
A) High-level overview (10 lines max)

B) Component map (bullets)
   - [Component]: [responsibility]

C) Key execution paths (3-5 numbered flows)
   1. [Trigger] → [Step] → [Step] → [Output]

D) Critical files list (with paths)
   - path/to/file.py: [why it matters]

E) Risks / tech debt / unknowns
   - [Risk]: [explanation]
```

4) **If refactor is requested**:
   - Propose 2 options (minimal vs ideal)
   - Include verification plan (tests, perf checks)

---

## Example Usage

```
/architecture_arch Focus on:
- how agent teams are instantiated
- how tools are bound
- where orchestration decisions are made
- where a Composer could plug in safely
```

Or:

```
/architecture_arch map the inference API service and show the main execution paths
```
