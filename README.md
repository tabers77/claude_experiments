# Claude Code Library (Plugin)

A reusable Claude Code **plugin** of skills, agents, hooks, and rules that connects to any project. No file copying needed.

## Why This Exists

Setting up Claude Code effectively requires more than just installing it. You need:
- **Skills** that enforce consistent workflows (safe refactoring, architecture mapping, code review)
- **Hooks** that automate quality gates and protect sensitive files
- **Rules** that teach Claude your project's conventions

This library provides all of these, extracted from real-world usage patterns documented in the [playbook](playbook/How%20I%20Use%20Claude%20Code.md).

---

## Quick Start

### As a plugin (recommended)

```bash
# Connect to any project — all skills available instantly
claude --plugin-dir /path/to/claude_experiments

# Skills are namespaced
/claude-library:architecture-arch    # Build mental model of codebase
/claude-library:meta-project-setup   # Analyze project & get recommendations
```

### Local development (this repo)

```bash
# Set up local symlinks so skills work without --plugin-dir
bash setup-local.sh

# Then use skills directly
/architecture-arch map the codebase
```

---

## Available Skills

Skills are organized by **workflow phase** — what you're trying to do right now.

### Understand — "What does this code do?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/architecture-arch` | Structural map of components, flows, risks | You need a **reference document** to look at while working |
| `/learning-codebase-mastery` | Deep understanding through quizzes and exercises | You need to **learn and retain** how something works |

### Diagnose — "What's wrong with it?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/code-diagnosis` | Targeted scan for bugs, smells, refactoring opportunities | You want to scan a **specific module or file** for concrete issues |
| `/quality-review` | Repo-wide health audit with scoring and priority matrix | You want a **broad project health score** with prioritized actions |
| `code-reviewer` agent | Review recent code changes (git diff) | You just **wrote or modified code** and want feedback |

### Plan — "What should I build?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/planning-spec-from-text` | Convert vague requirements into testable specs | Requirements are **unclear or ambiguous** |
| `/planning-impl-plan` | Design implementation approach before coding | Requirements are clear, you need to **plan the how** |

### Build — "How do I change it safely?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/api-development-api-impl` | Implement endpoints with consistent patterns | Adding a **new API endpoint** |
| `/safe-changes-refactor-safe` | Refactor with explicit invariants and checkpoints | **Multi-file refactors** or core logic changes |
| `/safe-changes-impact-check` | Assess blast radius before risky changes | Changes to **DB schema, auth, orchestration**, or unclear scope |

### Learn — "How do I get better?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/learning-algo-practice` | Algorithm & interview prep for data scientists | Practicing **problem-solving patterns** |
| `/learning-concept-recall` | Spaced repetition for DS concepts | **Retaining** what you've studied |
| `/learning-debug-training` | Systematic debugging training | Building **debugging instincts** |
| `/learning-code-review-eye` | Train your code review skills | Sharpening your **review eye** |

### Maintain — "How do I keep the library healthy?"

| Skill | Purpose | Use when... |
|-------|---------|-------------|
| `/meta-experiment-feature` | Set up experiments for new Claude Code features | Trying a **new feature** (agents, MCP, hooks) |
| `/meta-project-setup` | Audit setup, recommend artifacts, detect gaps | **Connecting the plugin** to a new project |
| `/meta-skill-audit` | Audit library for overlaps and gaps | After **adding or changing skills** |
| `/meta-sync-references` | Fix stale cross-references across files | After **structural changes** (rename, move, delete) |

### Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Expert code review after writing/modifying code (listed under Diagnose above) |

---

## Quick Reference: Which Skill When?

```
I need to...                          Use this
────────────────────────────────────────────────────────────────
UNDERSTAND
  Map a codebase (reference doc)      /architecture-arch
  Learn a codebase (retain it)        /learning-codebase-mastery

DIAGNOSE
  Scan specific code for issues       /code-diagnosis
  Assess overall project health       /quality-review
  Review code I just wrote            code-reviewer agent

PLAN
  Clarify vague requirements          /planning-spec-from-text
  Design before coding                /planning-impl-plan

BUILD
  Add an API endpoint                 /api-development-api-impl
  Refactor safely                     /safe-changes-refactor-safe
  Check blast radius                  /safe-changes-impact-check

LEARN
  Practice algorithms & interviews    /learning-algo-practice
  Retain concepts (spaced repetition) /learning-concept-recall
  Train debugging skills              /learning-debug-training
  Sharpen code review instincts       /learning-code-review-eye

MAINTAIN
  Try a new Claude feature            /meta-experiment-feature
  Set up Claude in a new project      /meta-project-setup
  Check for skill overlaps            /meta-skill-audit
  Fix stale references                /meta-sync-references
```

---

## Repository Structure

```
claude_experiments/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (hooks inline)
├── skills/                       # Plugin skills (auto-discovered)
│   ├── architecture-arch/
│   ├── code-diagnosis/
│   ├── safe-changes-refactor-safe/
│   ├── safe-changes-impact-check/
│   ├── planning-spec-from-text/
│   ├── planning-impl-plan/
│   ├── api-development-api-impl/
│   ├── quality-review/
│   ├── learning-codebase-mastery/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   ├── learning-code-review-eye/
│   ├── meta-experiment-feature/
│   ├── meta-project-setup/
│   ├── meta-skill-audit/
│   └── meta-sync-references/
├── agents/                       # Agent definitions
│   └── code-reviewer.md
├── hooks/                        # Hook reference copy
│   └── hooks.json
├── documentation/                # All generated .md docs
│   ├── PROBLEM_STATEMENT.md
│   └── BRAINSTORMING.md
├── library/                      # Reference material
│   ├── hooks/                    # Hook examples by category
│   ├── rules/                    # Reusable rule templates
│   └── templates/                # CLAUDE.md templates
├── playbook/                     # Source of truth
├── test_project/                 # Verification project
├── tests/                        # Validation scripts
└── experiments/                  # Feature experiments
```

---

## Practical Workflow Guide

Skills are designed to be **chained**, not used in isolation. This guide shows which combinations to use and when.

### Recurring Routines

#### Weekly Maintenance (keep the library healthy)

```
1. /meta-project-setup              # Re-audit setup, check for new best practices
2. /meta-skill-audit                # Check for overlaps or gaps after recent changes
3. /meta-sync-references            # Fix any stale references across files
4. python tests/test_skills.py      # Verify all skills are valid
```

Run this every week or after a batch of changes. This is your "hygiene" loop — it catches drift before it accumulates.

#### After Adding or Modifying a Skill

```
1. /meta-skill-audit                # Does the new skill overlap with existing ones?
2. /meta-sync-references            # Update CLAUDE.md, README, tests with new skill
3. python tests/test_skills.py      # Confirm structure is valid
```

#### After Any Structural Change (moving files, renaming, deleting)

```
1. /meta-sync-references            # Detect and fix all broken references
```

---

### Scenario Workflows

#### Onboarding to a New Project

You just connected the plugin to a project you've never seen before.

```
1. /meta-project-setup               # Fingerprint the project, get tailored recommendations
2. /architecture-arch                 # Map the structure — components, paths, risks
3. /learning-codebase-mastery         # Deep dive into critical modules (tutor mode)
4. /code-diagnosis                    # Scan key modules for bugs and smells
5. /quality-review                    # Baseline health score + what needs fixing
```

#### Planning a New Feature

You have a feature request — from a clear spec to a vague idea.

```
# If requirements are vague:
1. /planning-spec-from-text           # Turn vague input into a testable spec

# Once requirements are clear:
2. /planning-impl-plan                # Design the implementation before coding
3. [write code]
4. code-reviewer agent                # Review what you just wrote
```

#### Adding an API Endpoint

```
1. /planning-impl-plan                # Design the endpoint (models, errors, auth)
2. /api-development-api-impl          # Implement with consistent patterns
3. code-reviewer agent                # Review for quality and security
```

#### Refactoring Existing Code

```
1. /architecture-arch                 # Understand what you're about to change
2. /code-diagnosis                    # Find all issues in the target area
3. /safe-changes-impact-check         # Assess blast radius — what breaks?
4. /safe-changes-refactor-safe        # Execute with invariants and checkpoints
5. code-reviewer agent                # Verify the result
```

#### Tackling Tech Debt

```
1. /quality-review                    # Score the project, get the priority matrix
   # Phase 1: identifies all issues with evidence
   # Phase 2: categorizes into Do Now / Plan Soon / Monitor / Accept
2. /code-diagnosis                    # Deep dive into "Do Now" items
3. /safe-changes-refactor-safe        # Execute each fix safely
4. /quality-review                    # Re-score to measure improvement
```

#### Investigating Suspicious Code

```
1. /code-diagnosis                    # Scan for bugs, smells, security issues
2. /safe-changes-impact-check         # Before fixing — what's the blast radius?
3. /safe-changes-refactor-safe        # Fix with explicit invariants
```

#### Experimenting with a New Claude Code Feature

```
1. /meta-experiment-feature agents    # (or mcp, hooks, etc.)
   # Creates the right artifact type + experiment notes
2. Test the feature
3. Update experiments/*/NOTES.md with findings
4. /meta-skill-audit                  # Does this new artifact overlap with existing ones?
```

#### Skill Building & Interview Prep

```
# Daily practice routine
1. /learning-concept-recall quiz, weak areas, quick    # Reinforce what you're forgetting
2. /learning-algo-practice mix, medium                 # One problem to stay sharp

# Deep practice session
1. /learning-algo-practice SQL + pandas, hard, timed   # Simulate interview pressure
2. /learning-debug-training mix, medium                # Find bugs systematically
3. /learning-code-review-eye focus on my blind spots   # Review training on weak areas

# After learning something new
1. /learning-concept-recall add concepts               # Register new topics for future recall
```

#### Making a Risky Change (DB schema, auth, core logic)

```
1. /safe-changes-impact-check         # What's the blast radius?
   # Shows: direct/indirect dependencies, data impact, rollback strategy
2. /planning-impl-plan                # Plan the safest approach
3. /safe-changes-refactor-safe        # Execute with explicit invariants
4. code-reviewer agent                # Final review
```

---

## Skill Highlights

### `/architecture-arch` — Architecture Mapping

Before touching unfamiliar code, map it first:

```
/architecture-arch focus on:
- how requests flow from API to database
- where authentication is enforced
- what the main execution paths are
```

**Output**: 10-line overview, component map, execution paths, critical files, risks.

### `/code-diagnosis` — Targeted Code Diagnosis

Point it at code you're suspicious of:

```
/code-diagnosis src/auth/
/code-diagnosis src/pipeline.py focus on performance
/code-diagnosis src/utils/ I'm about to refactor this — what should I know?
```

**Output**: Bugs (fix now), smells (fix soon), opportunities (fix when convenient), refactoring roadmap.

### `/safe-changes-refactor-safe` — Safe Refactoring

Refactor like a senior engineer reviewing a junior:

```
/safe-changes-refactor-safe
Goal: extract validation logic into separate module
Constraints:
- keep all existing tests passing
- no API changes
```

**Output**: Current behavior, invariants, step-by-step plan with checkpoints, verification commands.

### `/quality-review` — Quality Assessment + Prioritization

Get calibrated, evidence-based project assessment with prioritized action plan:

```
/quality-review run tests if possible; focus on test quality
```

**Output**: Score (0-100), category breakdown, evidence with file paths, priority matrix (Do Now / Plan Soon / Monitor / Accept), next 3 PR-sized actions.

### `/learning-codebase-mastery` — Learning Mode

Two modes for deep understanding:

```
# Deep dive analysis
/learning-codebase-mastery src/auth/

# Interactive tutor mode (Claude asks YOU questions)
/learning-codebase-mastery tutor src/api/routes.py
```

---

## Hook Examples

Hooks are inlined in `.claude-plugin/plugin.json`. Reference copies in `hooks/hooks.json`.

### Block edits to protected paths

```json
{
  "matcher": "Edit|Write",
  "hooks": [{
    "type": "command",
    "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -qE '^(protected/|migrations/|.env)'; then echo 'BLOCKED' && exit 2; fi"
  }]
}
```

### Auto-lint Python files

```json
{
  "matcher": "Edit|Write",
  "hooks": [{
    "type": "command",
    "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.py$'; then ruff check \"$CLAUDE_FILE_PATH\"; fi"
  }]
}
```

See `library/hooks/*/README.md` for more examples.

---

## The Philosophy

> **Claude is a junior engineer + reviewer + tutor — never an autopilot.**

Key patterns:
- **Plan before code**: Use `/planning-impl-plan` and `/safe-changes-refactor-safe` to think first
- **Explicit invariants**: Always state what must not change
- **Small checkpoints**: Verify after each step, not at the end
- **Evidence-based**: Scores without file paths and confidence levels are ignored

Read the full philosophy: [playbook/How I Use Claude Code.md](playbook/How%20I%20Use%20Claude%20Code.md)

---

## License

MIT
