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

### One-time use

From any project, pass the plugin path directly:

```bash
claude --plugin-dir /path/to/claude_experiments
```

Skills are namespaced:
```
/claude-library:architecture-arch    # Build mental model of codebase
/claude-library:meta-project-setup   # Analyze project & get recommendations
```

### Permanent setup (no `--plugin-dir` needed)

Instead of typing the full `--plugin-dir` path every time, create a shell alias that does it for you. Follow the guide for your OS below.

> **Why not `settings.json`?** Claude Code's `extraKnownMarketplaces` config is for **marketplace directories** (folders containing multiple plugins in subdirectories). A single plugin repo like this one doesn't fit that format. The `--plugin-dir` flag is the intended way to load a single plugin, and a shell alias is the cleanest way to avoid retyping it.

---

#### Windows (PowerShell) — step by step

This is what most VS Code users on Windows will use.

**Step 1: Check if you already have a PowerShell profile**

Open a terminal in VS Code (or any PowerShell window) and run:

```powershell
Test-Path $PROFILE
```

- If it returns `True` → you already have a profile, skip to Step 3.
- If it returns `False` → continue to Step 2.

**Step 2: Create the profile file**

```powershell
New-Item -Path $PROFILE -Type File -Force
```

**Step 3: Open the profile in Notepad**

```powershell
notepad $PROFILE
```

**Step 4: Add the alias function**

In Notepad, add this line (update the path to match where you cloned this repo):

```powershell
function claude-lib { claude --plugin-dir "C:\Users\YOUR_USERNAME\path\to\claude_experiments" $args }
```

Save the file and close Notepad.

**Step 5: Reload the profile**

Back in your terminal, run:

```powershell
. $PROFILE
```

If you get a script execution error, run this first, then retry:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Step 6: Verify it works**

Navigate to any project and run:

```powershell
claude-lib
```

You should see Claude Code start with all plugin skills available. Done!

---

#### macOS / Linux (Bash or Zsh) — step by step

**Step 1: Open your shell config**

```bash
# For Zsh (default on macOS)
nano ~/.zshrc

# For Bash (default on most Linux)
nano ~/.bashrc
```

**Step 2: Add the alias**

Add this line at the end of the file (update the path to match where you cloned this repo):

```bash
alias claude-lib='claude --plugin-dir /path/to/claude_experiments'
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

**Step 3: Reload**

```bash
source ~/.zshrc   # or source ~/.bashrc
```

**Step 4: Verify it works**

Navigate to any project and run:

```bash
claude-lib
```

---

#### What `claude-lib` does

`claude-lib` is identical to `claude` — same features, same flags, same behavior. The only difference is it automatically adds `--plugin-dir` for you.

| You type | What actually runs |
|---|---|
| `claude-lib` | `claude --plugin-dir "/path/to/claude_experiments"` |
| `claude-lib --model sonnet` | `claude --plugin-dir "/path/to/claude_experiments" --model sonnet` |
| `claude-lib --resume` | `claude --plugin-dir "/path/to/claude_experiments" --resume` |

### Local development (this repo)

```bash
# Set up local symlinks so skills work without --plugin-dir
bash setup-local.sh

# Then use skills directly
/architecture-arch map the codebase
```

---

## Available Skills

Skills are organized by **tier** — how often you'll reach for them.

### Core — reach for these constantly

| Skill | What it does | Typical trigger |
|-------|-------------|-----------------|
| `/quality-review` | Repo-wide health audit with scoring and priority matrix | "How healthy is this project?" |
| `/architecture-arch` | Structural map of components, flows, risks | "I need a reference doc before I touch anything" |
| `/code-diagnosis` | Targeted scan for bugs, smells, refactoring opportunities | "Something's off in this module" |
| `/safe-changes-impact-check` | Assess blast radius before risky changes | "What breaks if I change this?" |
| `/safe-changes-refactor-safe` | Refactor with explicit invariants and checkpoints | "Refactor this without breaking anything" |
| `/planning-impl-plan` | Design implementation approach before coding | "How should I build this?" |
| `/session-wrapup` | Close out a session — record progress, sync docs, set next steps | "I'm switching projects — wrap up" |
| `code-reviewer` agent | Review recent code changes (git diff) | "Review what I just wrote" |

### Specialized — use when the situation fits

| Skill | What it does | Typical trigger |
|-------|-------------|-----------------|
| `/quality-upgrade-advisor` | Ecosystem currency check + prioritized upgrade roadmap | "Which dependencies are stale?" |
| `/api-development-api-impl` | Implement endpoints with consistent patterns | "Add a new API endpoint" |
| `/planning-spec-from-text` | Convert vague requirements into testable specs | "Requirements are vague — help me clarify" |
| `/learning-codebase-mastery` | Deep understanding through quizzes and exercises | "I need to truly learn this codebase" |
| `/meta-project-setup` | Audit setup, recommend artifacts, detect gaps | "Set up Claude in this new project" |
| `/meta-skill-audit` | Audit library for overlaps and gaps | "Do any skills overlap or have gaps?" |
| `/meta-sync-references` | Fix stale cross-references across files | "Sync all references after structural changes" |

### Learning — standalone practice sessions

| Skill | What it does | Typical trigger |
|-------|-------------|-----------------|
| `/learning-algo-practice` | Algorithm & interview prep for data scientists | "Practice problem-solving patterns" |
| `/learning-concept-recall` | Spaced repetition for DS concepts | "Quiz me on what I've studied" |
| `/learning-debug-training` | Systematic debugging training | "Train my debugging instincts" |
| `/learning-code-review-eye` | Train your code review skills | "Sharpen my review eye" |
| `/learning-pair-programming` | Pair program on real tasks with Claude as guide | "Help me implement this — but I want to write the code" |

### Maintenance — keep the library itself healthy

| Skill | What it does | Typical trigger |
|-------|-------------|-----------------|
| `/meta-experiment-feature` | Set up experiments for new Claude Code features | "Try a new Claude feature (agents, MCP, hooks)" |

---

## Quick Reference: Which Skill When?

```
I need to...                          Use this
────────────────────────────────────────────────────────────────
CORE (use constantly)
  Assess overall project health       /quality-review
  Map a codebase (reference doc)      /architecture-arch
  Scan specific code for issues       /code-diagnosis
  Check blast radius                  /safe-changes-impact-check
  Refactor safely                     /safe-changes-refactor-safe
  Design before coding                /planning-impl-plan
  Wrap up before switching projects   /session-wrapup
  Review code I just wrote            code-reviewer agent

SPECIALIZED (use when the situation fits)
  Audit stale dependencies            /quality-upgrade-advisor
  Add an API endpoint                 /api-development-api-impl
  Clarify vague requirements          /planning-spec-from-text
  Learn a codebase (retain it)        /learning-codebase-mastery
  Set up Claude in a new project      /meta-project-setup
  Check for skill overlaps            /meta-skill-audit
  Fix stale references                /meta-sync-references

LEARNING (standalone practice)
  Practice algorithms & interviews    /learning-algo-practice
  Retain concepts (spaced repetition) /learning-concept-recall
  Train debugging skills              /learning-debug-training
  Sharpen code review instincts       /learning-code-review-eye
  Implement real tasks with guidance   /learning-pair-programming

MAINTENANCE (library upkeep)
  Try a new Claude feature            /meta-experiment-feature
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
│   ├── session-wrapup/
│   ├── api-development-api-impl/
│   ├── quality-review/
│   ├── quality-upgrade-advisor/
│   ├── learning-codebase-mastery/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   ├── learning-code-review-eye/
│   ├── learning-pair-programming/
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

Each entry-point skill already recommends next steps in its output, so you rarely need to plan multi-step chains yourself. **Start with one skill; go deeper only if needed.**

| Scenario | Start here | Go deeper (optional) |
|----------|-----------|---------------------|
| **Onboarding to a new project** | `/meta-project-setup` | `arch` + `quality-review` |
| **Tackling tech debt** | `/quality-review` | `diagnosis` + `refactor-safe` |
| **Refactoring existing code** | `/safe-changes-impact-check` | `refactor-safe` + `code-reviewer` |
| **Planning a new feature** | `/planning-impl-plan` | `spec-from-text` if requirements are vague |
| **Wrapping up a session** | `/session-wrapup` | `learning-code-review-eye` to quiz yourself on what you just built |
| **Upgrading dependencies** | `/quality-upgrade-advisor` | `impact-check` + `refactor-safe` |
| **Adding an API endpoint** | `/api-development-api-impl` | `impl-plan` + `code-reviewer` |
| **Making a risky change** | `/safe-changes-impact-check` | `impl-plan` + `refactor-safe` |
| **Investigating suspicious code** | `/code-diagnosis` | `impact-check` + `refactor-safe` |
| **Weekly maintenance** | `/meta-sync-references` + `pytest` | (that's it) |
| **Skill building** | `/learning-concept-recall` daily | Add other learning skills as needed |
| **Implementing with guidance** | `/learning-pair-programming` | `code-reviewer` when done |

---

## Skill Highlights

### `/quality-review` — Quality Assessment + Prioritization

Get calibrated, evidence-based project assessment with prioritized action plan:

```
/quality-review run tests if possible; focus on test quality
```

**Output**: Score (0-100), category breakdown, evidence with file paths, priority matrix (Do Now / Plan Soon / Monitor / Accept), next 3 PR-sized actions.

### `/architecture-arch` — Architecture Mapping

Before touching unfamiliar code, map it first:

```
/architecture-arch focus on:
- how requests flow from API to database
- where authentication is enforced
- what the main execution paths are
```

**Output**: 10-line overview, component map, execution paths, critical files, risks.

### `/quality-upgrade-advisor` — Ecosystem Currency Check

Audit dependencies against official docs and produce an upgrade roadmap:

```
# Full ecosystem audit
/quality-upgrade-advisor

# With vision context
/quality-upgrade-advisor
We want to move toward async-first architecture.
Only recommend upgrades that help with that goal.
```

**Output**: Project Identity Card, tiered recommendations (Critical / Recommended / Consider / Skip), batched upgrade sequence with exact commands, `documentation/UPGRADE_ROADMAP.md`.

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

## Setting Up Rules

Rules are `.md` files in `.claude/rules/` that Claude reads automatically on every conversation. They teach Claude your project's conventions so you don't repeat yourself.

**Rules vs `CLAUDE.md`**: `CLAUDE.md` is the project overview (the "what"). Rules are behavioral constraints Claude must follow (the "how").

### Where rules live

```
your-project/
└── .claude/
    └── rules/
        ├── style.md       # Naming, formatting, imports
        ├── testing.md      # Test conventions and coverage
        ├── security.md     # Secrets, validation, auth
        └── api.md          # Endpoint patterns (if applicable)
```

### Minimum rules for any project

You need at least **two rules** to get meaningful value. These cover the most common sources of "Claude did something I wouldn't do."

**1. `style.md`** (required) — prevents Claude from using wrong naming, skipping type hints, or misorganizing imports:

```markdown
# Style Rules

## Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Type Hints
- Required for function signatures
- Use `Optional[]` for nullable

## Imports
- Standard library first, third-party second, local third
- Sorted alphabetically within groups

## Formatting
- Use project formatter (ruff/black)
- Line length: 88-100 characters
```

**2. `testing.md`** (required) — ensures tests go in the right place with the right patterns:

```markdown
# Testing Rules

## Structure
- Unit tests in `tests/unit/`, integration in `tests/integration/`
- Files named `test_*.py`

## Conventions
- One assertion concept per test
- Names: `test_[what]_[condition]_[expected]`
- Use fixtures for common setup
- Mock external dependencies

## Coverage
- Critical paths: 90%+
- Happy + error paths: covered
```

### Additional rules (add as needed)

| Rule | When to add | What it prevents |
|------|-------------|-----------------|
| `security.md` | Projects with user input, auth, or secrets | Hardcoded secrets, skipped validation, careless auth changes |
| `api.md` | Projects with API endpoints | Inconsistent error formats, wrong status codes, missing docs |
| `project.md` | Projects with unique workflows | Claude ignoring your team's specific conventions |

Ready-to-copy templates are in `library/rules/`. Or run `/meta-project-setup` to get recommendations tailored to your project.

### Rule writing tips

- **Be specific** — "Functions: `snake_case`" is actionable. "Write clean code" is not.
- **One topic per file** — Don't mix style and security in the same file.
- **Include commands** — If the rule relates to running something, include the exact command.
- **List sensitive paths** — Tell Claude which directories need extra caution.

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
