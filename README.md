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

Skills are organized by **development phase** — find the phase you're in, pick the skill you need.

> **Essential** = don't skip this. **If needed** = reach for it when the situation fits.

### 1. Project Setup & Onboarding

*Joining a project, assessing health, understanding what exists.*

|  | Skill | When to use |
|--|-------|-------------|
| **Essential** | `/meta-project-setup` | First thing on any new project — audit setup, get recommendations, **discover which new skills to build** |
| **Essential** | `/architecture-arch` | Map the codebase structure before touching anything |
| *If needed* | `/quality-review` | Want a health score with evidence and priority matrix |
| *If needed* | `/quality-strategic-advisor` | Research your domain, get ideas for new features and capabilities |
| *If needed* | `/quality-upgrade-advisor` | Dependencies look outdated, need an upgrade plan |
| *If needed* | `/learning-codebase-mastery` | Deeply *learn* and retain codebase knowledge (4 modes below) |

> **`/learning-codebase-mastery` has 4 modes** — pick by situation:
> | Mode | Trigger words | When to use |
> |------|--------------|-------------|
> | **Deep Dive** (default) | `deep dive`, `analyze` | Understand a module's architecture before touching it |
> | **Tutor** | `tutor`, `quiz`, `interactive` | Test yourself on code you've been reading |
> | **Recent Changes** | `what changed`, `catch up`, `recent changes` | Catch up on git commits — quiz on what changed and why |
> | **Pre-Commit** | `pre-commit`, `before commit`, `review my changes` | Verify you understand your uncommitted changes before committing |

### 2. Planning & Design

*Turning ideas into a concrete plan before writing code.*

|  | Skill | When to use |
|--|-------|-------------|
| **Essential** | `/planning-impl-plan` | Design the implementation approach before coding |
| *If needed* | `/planning-spec-from-text` | Requirements are vague — turn them into testable specs first |

### 3. Building & Implementing

*Writing new code — features, endpoints, methods.*

|  | Skill | When to use |
|--|-------|-------------|
| *If needed* | `/learning-pair-programming` | Want to implement it yourself with Claude guiding you step by step |
| *If needed* | `/api-development-api-impl` | Adding API endpoints with consistent patterns |

### 4. Reviewing & Refactoring

*Improving existing code, catching issues, safe changes.*

|  | Skill | When to use |
|--|-------|-------------|
| **Essential** | `code-reviewer` agent | After writing or modifying code — review your changes |
| *If needed* | `/code-diagnosis` | Something smells off in a specific module or file |
| *If needed* | `/safe-changes-impact-check` | About to make a risky change — check the blast radius |
| *If needed* | `/safe-changes-refactor-safe` | Multi-file refactor — need explicit invariants and checkpoints |
| *If needed* | `/quality-sync-docs` | After refactoring — fix stale paths, counts, and references in all docs |

### 5. Wrapping Up

*End of session — don't lose context.*

|  | Skill | When to use |
|--|-------|-------------|
| **Essential** | `/session-wrapup` | Record progress, sync docs, set next steps before switching context |

### 6. Skill Building — standalone practice

*Not tied to a specific project. Practice sessions you can do anytime.*

> All learning skills use the `learning-coach` agent with persistent memory. Your progress, weak areas, and mastery levels carry across sessions automatically.

| Skill | What it does |
|-------|-------------|
| `/learning-algo-practice` | Algorithm & interview prep (DSA, SQL, pandas, ML) |
| `/learning-concept-recall` | Spaced repetition — quiz yourself on what you've studied |
| `/learning-debug-training` | Systematic debugging training — find bugs methodically |
| `/learning-code-review-eye` | Train your code review instincts on diffs |
| `/learning-pair-programming` | Pair program on real tasks with Claude as senior colleague |

### 7. Library Maintenance — this plugin only

| Skill | What it does |
|-------|-------------|
| `/meta-discover-claude-features` | Scout official docs + community for new Claude Code features to adopt |
| `/meta-experiment-feature` | Set up experiments for a specific feature you already know about |
| `/meta-skill-audit` | Audit library for overlaps and gaps |

> **Discovery workflow**: `/meta-discover-claude-features` finds what's new → you pick what's relevant → `/meta-experiment-feature` sets up the experiment → `/meta-skill-audit` checks the result fits cleanly.

---

## Quick Reference: Which Skill When?

```
I'm in this phase...                  Use this
────────────────────────────────────────────────────────────────
PROJECT SETUP & ONBOARDING
  Set up Claude + find skill gaps      /meta-project-setup        [essential]
  Map the codebase                    /architecture-arch          [essential]
  Assess project health               /quality-review
  Get strategic feature suggestions    /quality-strategic-advisor
  Audit stale dependencies            /quality-upgrade-advisor
  Deeply learn a codebase             /learning-codebase-mastery
  Catch up on recent git changes      /learning-codebase-mastery what changed
  Quiz before committing              /learning-codebase-mastery pre-commit

PLANNING & DESIGN
  Design before coding                /planning-impl-plan         [essential]
  Clarify vague requirements          /planning-spec-from-text

BUILDING & IMPLEMENTING
  Implement with guidance             /learning-pair-programming
  Add an API endpoint                 /api-development-api-impl

REVIEWING & REFACTORING
  Review code I just wrote            code-reviewer agent         [essential]
  Scan specific code for issues       /code-diagnosis
  Check blast radius                  /safe-changes-impact-check
  Refactor safely                     /safe-changes-refactor-safe
  Sync docs after changes             /quality-sync-docs

WRAPPING UP
  End of session                      /session-wrapup             [essential]

SKILL BUILDING (anytime)
  Practice algorithms & interviews    /learning-algo-practice
  Retain concepts (spaced repetition) /learning-concept-recall
  Train debugging skills              /learning-debug-training
  Sharpen code review instincts       /learning-code-review-eye
  Pair program on real tasks          /learning-pair-programming

LIBRARY MAINTENANCE
  What's new in Claude Code?          /meta-discover-claude-features
  Try a specific new feature          /meta-experiment-feature
  Check for skill overlaps            /meta-skill-audit
```

---

## Repository Structure

```
claude_experiments/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (hooks inline)
├── .github/
│   └── workflows/
│       └── weekly-quality-check.yml  # Reusable weekly quality action
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
│   ├── quality-strategic-advisor/
│   ├── quality-upgrade-advisor/
│   ├── learning-codebase-mastery/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   ├── learning-code-review-eye/
│   ├── learning-pair-programming/
│   ├── meta-discover-claude-features/
│   ├── meta-experiment-feature/
│   ├── meta-project-setup/
│   ├── meta-skill-audit/
│   └── quality-sync-docs/
├── agents/                       # Agent definitions
│   ├── code-reviewer.md
│   └── learning-coach.md
├── hooks/                        # Hook reference copy
│   └── hooks.json
├── scripts/                      # Automation scripts
│   └── quality-action/           # Weekly quality check (GitHub Action)
│       ├── run_analysis.py       # Scan repo → call GPT-5.2 → report
│       ├── apply_changes.py      # Apply safe auto-mergeable changes
│       ├── requirements.txt      # Action dependencies
│       ├── example-caller-workflow.yml
│       └── prompts/              # LLM prompt templates
├── appendix/                     # Reference configs (settings.py, etc.)
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

Each skill recommends next steps in its output, so you rarely need to plan chains yourself. **Start with one skill; go deeper only if needed.**

| Scenario | Start here | Go deeper (optional) |
|----------|-----------|---------------------|
| **Onboarding to a new project** | `/meta-project-setup` | `arch` + `quality-review` (also tells you what new skills to build) |
| **Planning a new feature** | `/planning-impl-plan` | `spec-from-text` if requirements are vague |
| **Catching up on changes** | `/learning-codebase-mastery what changed` | `code-diagnosis` if something looks off |
| **Building with guidance** | `/learning-pair-programming` | `code-reviewer` when done |
| **Adding an API endpoint** | `/api-development-api-impl` | `impl-plan` + `code-reviewer` |
| **Investigating suspicious code** | `/code-diagnosis` | `impact-check` + `refactor-safe` |
| **Making a risky change** | `/safe-changes-impact-check` | `impl-plan` + `refactor-safe` |
| **Refactoring existing code** | `/safe-changes-impact-check` | `refactor-safe` + `quality-sync-docs` + `code-reviewer` |
| **Tackling tech debt** | `/quality-review` | `diagnosis` + `refactor-safe` |
| **Planning next capabilities** | `/quality-strategic-advisor` | `impl-plan` for chosen suggestions |
| **Upgrading dependencies** | `/quality-upgrade-advisor` | `impact-check` + `refactor-safe` |
| **Wrapping up a session** | `/session-wrapup` | `code-review-eye` to quiz yourself |
| **Skill building** | `/learning-concept-recall` daily | Add other learning skills as needed |
| **What's new in Claude Code?** | `/meta-discover-claude-features` | `meta-experiment-feature` to try what's relevant |
| **Weekly maintenance** | `/quality-sync-docs` + `pytest` | `meta-skill-audit` if skills changed |

---

## Skill Highlights

### `/meta-project-setup` — Setup Audit + Skill Gap Discovery

Analyzes any project across 7 dimensions, recommends which existing plugin skills fit, and — critically — **detects what skills are missing from the library for your project**. If your project uses a technology that no existing skill covers (DB migrations, async workers, GraphQL, ML pipelines, complex auth, etc.), this skill flags it and suggests exactly what to build: artifact type, name, description, and priority.

```
# Full analysis — audit setup, recommend skills, discover gaps
/meta-project-setup

# Focus only on gap detection
/meta-project-setup only detect gaps for this project
```

**Output**: Project fingerprint, recommended artifacts, **library gaps table** (what's missing, suggested skill name, priority), tailored workflows, staged rollout plan, `documentation/CLAUDE_SETUP.md`.

**vs `/meta-skill-audit`**: That skill audits the *plugin itself* for overlaps and redundancies. This skill audits a *target project* to find what the plugin is missing for that project's needs.

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

### `/quality-strategic-advisor` — Strategic Feature Discovery

Research your project's domain and get actionable suggestions for new capabilities:

```
/quality-strategic-advisor
This is an LLM evaluation framework. We want to know:
- What libraries and techniques exist for multi-agent scoring?
- What's the state of the art in process reward models?
- What similar tools do that we don't?
```

**Output**: Project understanding card, prioritized recommendations (Implement Next / Plan Later / Watch / Skip), implementation sketches, strategic sequence, `documentation/STRATEGIC_ROADMAP.md`.

**vs `/quality-upgrade-advisor`**: That skill checks if your existing dependencies are up to date. This skill finds new libraries, techniques, and features you're not using yet.

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

## Automated Weekly Quality Checks (GitHub Action)

This plugin includes a **reusable GitHub Action** that runs `/quality-upgrade-advisor` and `/quality-strategic-advisor` automatically on a weekly schedule. It uses **Azure OpenAI (GPT-5.2)** to analyze your repos and create PRs with improvements.

### How it works

```
Every Monday 9am UTC (configurable)
  │
  ├─ Job 1: Analyze ─── Scans repo → calls GPT-5.2 → JSON report
  ├─ Job 2: Issue    ─── Opens/updates a GitHub Issue with all findings
  ├─ Job 3: PR       ─── Applies safe changes → runs tests → opens PR
  └─ Job 4: Merge    ─── Auto-merges ONLY if Tier 3 + all tests pass
```

### Three tiers of automation

| Tier | Behavior | Risk |
|------|----------|------|
| **1** | Issue only — report findings, no code changes | Zero |
| **2** (default) | PR with safe changes — human reviews and merges | Low |
| **3** | Auto-merge if tests pass AND changes are low-risk only | Medium |

Auto-merge (Tier 3) only applies to:
- Patch/minor dependency bumps with no breaking changes
- Security patches
- Trivial code fixes (unused imports, missing `__init__.py`)

It will **never** auto-merge major version bumps, framework upgrades, or logic changes.

### Prerequisites

You need **Azure OpenAI** access with GPT-5.2 (or GPT-4o) deployed, and secrets stored in **Azure Key Vault**. No Anthropic API key is needed.

### Setup (5 minutes)

**Step 1: Add 4 secrets to your GitHub repo**

Go to your repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret name | Value | Where to find it |
|-------------|-------|-------------------|
| `AZURE_CLIENT_ID` | Your Azure service principal client ID | Azure Portal → App registrations |
| `AZURE_TENANT_ID` | Your Azure tenant ID | Azure Portal → Microsoft Entra ID |
| `AZURE_CLIENT_SECRET` | Your Azure service principal secret | Azure Portal → App registrations → Certificates & secrets |
| `KEY_VAULT_ENDPOINT` | `https://your-keyvault.vault.azure.net/` | Azure Portal → Key Vault → Overview |

The action authenticates to Key Vault, which provides the Azure OpenAI API key at runtime. No API keys are stored in GitHub.

**Step 2: Copy the caller workflow to your repo**

Create `.github/workflows/weekly-quality.yml` in your target repo:

```yaml
name: Weekly Quality Check

on:
  schedule:
    - cron: "0 9 * * 1"  # Every Monday 9am UTC
  workflow_dispatch:
    inputs:
      auto_merge_tier:
        description: "1=issues only, 2=PRs only, 3=auto-merge"
        type: choice
        options: ["1", "2", "3"]
        default: "2"

jobs:
  quality:
    uses: YOUR_GITHUB_USER/claude_experiments/.github/workflows/weekly-quality-check.yml@master
    with:
      auto_merge_tier: ${{ github.event.inputs.auto_merge_tier || 2 }}
      test_command: "pytest tests/ -x"   # Your test command
      target_branch: "dev"               # Branch to target PRs against
      model: "gpt-5.2"                   # Azure OpenAI model
      analysis_mode: "both"              # upgrade, strategic, or both
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      KEY_VAULT_ENDPOINT: ${{ secrets.KEY_VAULT_ENDPOINT }}
```

Replace `YOUR_GITHUB_USER` with your GitHub username.

**Step 3: Done.** The action will run every Monday, or trigger it manually from Actions → Weekly Quality Check → Run workflow.

### Configuration options

| Input | Default | Description |
|-------|---------|-------------|
| `auto_merge_tier` | `2` | `1`=issues only, `2`=PRs, `3`=auto-merge |
| `test_command` | `pytest tests/ -x` | Command to validate changes |
| `target_branch` | `dev` | Branch PRs target |
| `model` | `gpt-5.2` | Azure OpenAI model (`gpt-5.2` or `gpt-4o`) |
| `analysis_mode` | `both` | `upgrade`, `strategic`, or `both` |
| `python_version` | `3.11` | Python version for the runner |

### What it analyzes

**Upgrade analysis** — scans dependency files (requirements.txt, pyproject.toml, package.json, etc.) and identifies:
- Security vulnerabilities and CVEs
- Deprecated packages or EOL versions
- Available version bumps with risk assessment
- Exact upgrade commands

**Strategic analysis** — scans codebase structure and source files for:
- Anti-patterns and code quality improvements
- Missing best practices
- Architecture improvements
- Performance and security suggestions

### Files

```
scripts/quality-action/
├── run_analysis.py             # Main: scan repo → call GPT-5.2 → JSON report
├── apply_changes.py            # Apply safe auto-mergeable changes only
├── requirements.txt            # Action dependencies (openai, azure-identity)
├── example-caller-workflow.yml # Copy this to your repos
└── prompts/
    ├── upgrade_advisor.md      # Dependency analysis prompt
    └── strategic_advisor.md    # Code/architecture analysis prompt

.github/workflows/
└── weekly-quality-check.yml    # Reusable workflow (called by other repos)
```

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
