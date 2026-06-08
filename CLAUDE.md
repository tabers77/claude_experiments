# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin (`claude-library`) that provides reusable skills, agents, hooks, and rules for any software project. Not an application — a library of automation workflows loaded via `claude --plugin-dir /path/to/claude_experiments`.

## Running Tests and Validation

```bash
# Validate all skills (frontmatter, naming, count)
python tests/test_skills.py

# Run test project tests
cd test_project && pip install -r requirements.txt && pytest

# Validate plugin manifest
python -c "import json; json.load(open('.claude-plugin/plugin.json'))"
```

CI runs three jobs on push/PR: `validate-skills`, `test-project`, `validate-plugin`.

## Architecture

### Plugin Loading
- **Manifest:** `.claude-plugin/plugin.json` — defines hooks inline (SessionStart/UserPromptSubmit/PreToolUse/PostToolUse)
- **Skills:** Auto-discovered from `skills/<name>/SKILL.md` (25 skills)
- **Agents:** Auto-discovered from `agents/<name>.md` (2 agents)
- **Local dev:** `bash setup-local.sh` creates symlink junctions so skills work without `--plugin-dir`

### Skill Structure
Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) and a markdown body defining purpose, process, and output format. Optional frontmatter: `agent`, `context: fork`, `model`, `tools`.

### Agent Memory Pattern
The 5 learning skills use `context: fork` + `agent: learning-coach` to get persistent memory. The `learning-coach` agent has `memory: user` which stores state in `~/.claude/agent-memory/learning-coach/`. The `code-reviewer` agent has no persistent memory and uses model `sonnet`.

### Self-Learning Skills Pattern
A skill-authoring pattern for skills that improve their own `SKILL.md` based on real runs. Each skill keeps a local `run_history.json` ledger of categorical failure modes; when a counter trips its threshold, the skill auto-edits its body per a stored `remediation_hint`. Reference implementation: `shared-bug-gap-fix` (in the `intelligence-platform` repo). Templates and design doc live at:
- `library/templates/self-learning-skill/` — `SKILL.md.tpl`, `run-plan-phase.md`, `audit-phase.md`, `ledger-phase.md`, `run_history_schema_v1.md`, `freshness-phase.md`, `suggestion-capture.md`, `observer-phase.md`, `observations_schema_v1.md`
- `documentation/SELF_LEARNING_SKILLS.md` — design doc, invariants, authoring checklist

**Per-run adaptive execution (Phase 0.5).** Greenfield- and describe-generated skills get a non-skippable `Phase 0.5` run-plan phase (always-on DNA, no toggle): it reads the user's request, starts from the generation-time baseline phases, and decides per step **reuse / adapt / skip / create**. The audit reconciles the plan (skip-justification rows; a baseline step in neither executed nor skipped rows is a `plan-silent-skip` FAIL; a load-bearing skip without justification is `plan-skipped-load-bearing-step-without-justification`), and the ledger persists `run_plan`. **Convert-mode-retrofitted skills stay fixed-sequence** (no Phase 0.5) to preserve their existing phase order byte-identical.

**Generator dispatch modes.** `meta-self-learning-skill-gen` supports three: greenfield interview (default), **`describe <prose>`** (qualify a natural-language problem → adaptive gap-fill → same build engine), and `convert <path>` (retrofit an existing skill, fixed-sequence).

**Research checkpoint.** `meta-research-checkpoint` is a suggestion-only, cadence-based sweep at two levels — **L1** (the generator + pattern + templates) and **L2** (each generated self-learning skill, gated by the `validation_freshness` AND-gate or forced with `--all`). It orchestrates existing research skills (`/meta-discover-claude-features`, `/quality-upgrade-advisor`, `/quality-strategic-advisor`, `/meta-skill-audit`), aggregates findings into `documentation/RESEARCH_CHECKPOINT.md`, and resets the freshness counter on researched L2 skills. **Level 3 (normal skills) is out of scope.** It never auto-edits a skill.

### Test-cache (shared, branch-level)
A commit-SHA-keyed pytest result cache that's a property of the **target repo + branch**, not of any specific skill. Once a target repo opts in (one-time `conftest.py` snippet — see `documentation/TEST_CACHE_SETUP.md`), every pytest invocation in that repo participates: previously-passed tests for the current HEAD SHA are auto-deselected on a clean tree, and fresh results are auto-recorded to `documentation/test-results/<sha>.json` in the target repo. Any skill running pytest — `shared-bug-gap-fix`, `pr-merge-readiness`, `commit-ready`, raw human pytest, CI — contributes and benefits without skill-specific plumbing.

Two scripts:
- `scripts/pytest_test_cache.py` — the **pytest plugin**. Hooks `pytest_collection_modifyitems` (deselect already-passed) and `pytest_sessionfinish` (record). Adds the `--no-test-cache` flag for per-run opt-out.
- `scripts/test_cache.py` — **CLI helper** for inspection: `status`, `lookup`, plus the underlying functions (`load_entry`, `save_entry`, `is_tree_clean`, junit parsing) the plugin reuses.

`pr-merge-readiness` Phase 4 assumes the project has opted in: pytest commands are plain (no per-tier plumbing), and the audit row captures the `[test-cache] …` summary line emitted by the plugin.

### Hooks
- **SessionStart:** Validate plugin and show skill count on new sessions via `scripts/session-start-hook.py`
- **UserPromptSubmit:** Auto-suggest relevant skills based on user prompt via `skill-rules.json` + `scripts/skill-activation-hook.py`
- **PreToolUse:** Block edits to `protected/`, `migrations/`, `.env`; block `git push --force`, `reset --hard`, `clean -f`; inject context-aware guidance before editing sensitive files (auth, config, migration, secrets, security) via `scripts/sensitive-file-hook.py`
- **PostToolUse:** Auto-lint `.py` files with `ruff`

### Key Directories
- `library/` — Reference templates (hook examples, rule templates, CLAUDE.md templates)
- `test_project/` — Minimal FastAPI app used to validate skills work
- `playbook/` — Source-of-truth guide ("How I Use Claude Code.md")
- `documentation/` — All generated `.md` output files (audits, plans, reports)
- `scripts/quality-action/` — Weekly quality check (Azure OpenAI analysis → GitHub issue)
- `scripts/skill-activation-hook.py` — UserPromptSubmit hook script for skill auto-suggestion
- `scripts/sensitive-file-hook.py` — PreToolUse hook injecting guidance for sensitive file edits
- `scripts/session-start-hook.py` — SessionStart hook validating plugin on new sessions
- `scripts/test_cache.py` — Commit-SHA-keyed pytest result cache: CLI helper for inspection + shared functions
- `scripts/pytest_test_cache.py` — Pytest plugin that auto-skips already-passed tests and auto-records results (see Test-cache helper below)
- `skill-rules.json` — Trigger patterns mapping user prompts to skills

## Rules for Contributing

1. **Skills must be self-contained** — each skill folder works independently when loaded as plugin
2. **Test in `test_project/`** — verify skills before considering them complete
3. **Skill directories use hyphens**, not underscores; name in frontmatter must match directory name
4. **Documentation `.md` files go in `documentation/`** — only `CLAUDE.md` and `README.md` at repo root
5. **Keep docs in sync after every change** — when adding/removing/modifying skills, update:
   - This file (`CLAUDE.md`) — skills table, directory tree
   - `README.md` — skills table, directory tree, workflow guide
   - `tests/test_skills.py` — expected skill count (currently >= 25)

### Implementation Roadmap Sync

`documentation/IMPLEMENTATION.md` is the **single source of truth** for the project roadmap, priority items, and progress tracking. `README.md` contains a summarized status section that must mirror it.

When updating roadmap status, priorities, or completed items:
1. **Always update `documentation/IMPLEMENTATION.md` first** — project goals, priority sections, and completed work
2. **Then update `README.md`** to reflect the same status
3. Never update one without the other — if you mark an item as done in one file, mark it in both

If a new priority item is added or an existing one is split/merged/completed, update both files in the same edit session.

## Available Skills (29)

| Phase | Skills |
|-------|--------|
| Setup & Onboarding | `meta-project-setup`, `meta-claude-md-gen`, `architecture-arch`, `quality-review`, `quality-strategic-advisor`, `quality-upgrade-advisor`, `learning-codebase-mastery` |
| Planning | `planning-impl-plan`, `planning-spec-from-text` |
| Building | `learning-pair-programming`, `api-development-api-impl` |
| Reviewing & Refactoring | `code-diagnosis`, `quality-bug-sweep`, `safe-changes-impact-check`, `safe-changes-refactor-safe`, `quality-sync-docs` |
| Wrapping Up | `commit-ready`, `pr-merge-readiness`, `smart-test-selection` |
| Learning | `learning-algo-practice`, `learning-concept-recall`, `learning-debug-training`, `learning-code-review-eye` |
| Library Maintenance | `meta-agent-teams`, `meta-discover-claude-features`, `meta-experiment-feature`, `meta-skill-audit`, `meta-self-learning-skill-gen`, `meta-research-checkpoint` |

## Skill Decision Guide

### For documentation work

| Goal | Skill |
|------|-------|
| Fix stale refs, broken paths, merge overlapping docs | `/quality-sync-docs` |
| Update docs affected by code changes + commit | `/commit-ready` |
| Generate CLAUDE.md from scratch | `/meta-claude-md-gen` |

### For test work

| Goal | Skill |
|------|-------|
| Find test gaps for uncommitted changes + write tests | `/commit-ready` |
| Understand what tests would break from a proposed change | `/safe-changes-impact-check` |
| Score overall test quality as part of health check | `/quality-review` |

### For bug finding

| Goal | Skill |
|------|-------|
| Check changed files for bugs before committing | `/commit-ready` (Step 3.5) |
| Scan a specific file/module for bugs | `/code-diagnosis` |
| Scan entire project for bugs with severity | `/quality-bug-sweep` |
| Review recent git changes for issues | `code-reviewer` agent |
| Broad quality score with prioritized improvements | `/quality-review` |

### For all three combined (full health check)

Use `/meta-agent-teams` to plan parallel execution of docs + tests + bugs agents.
