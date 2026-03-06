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
- **Skills:** Auto-discovered from `skills/<name>/SKILL.md` (22 skills)
- **Agents:** Auto-discovered from `agents/<name>.md` (2 agents)
- **Local dev:** `bash setup-local.sh` creates symlink junctions so skills work without `--plugin-dir`

### Skill Structure
Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) and a markdown body defining purpose, process, and output format. Optional frontmatter: `agent`, `context: fork`, `model`, `tools`.

### Agent Memory Pattern
The 5 learning skills use `context: fork` + `agent: learning-coach` to get persistent memory. The `learning-coach` agent has `memory: user` which stores state in `~/.claude/agent-memory/learning-coach/`. The `code-reviewer` agent has no persistent memory and uses model `sonnet`.

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
- `skill-rules.json` — Trigger patterns mapping user prompts to skills

## Rules for Contributing

1. **Skills must be self-contained** — each skill folder works independently when loaded as plugin
2. **Test in `test_project/`** — verify skills before considering them complete
3. **Skill directories use hyphens**, not underscores; name in frontmatter must match directory name
4. **Documentation `.md` files go in `documentation/`** — only `CLAUDE.md` and `README.md` at repo root
5. **Keep docs in sync after every change** — when adding/removing/modifying skills, update:
   - This file (`CLAUDE.md`) — skills table, directory tree
   - `README.md` — skills table, directory tree, workflow guide
   - `tests/test_skills.py` — expected skill count (currently >= 22)

### Implementation Roadmap Sync

`documentation/IMPLEMENTATION.md` is the **single source of truth** for the project roadmap, priority items, and progress tracking. `README.md` contains a summarized status section that must mirror it.

When updating roadmap status, priorities, or completed items:
1. **Always update `documentation/IMPLEMENTATION.md` first** — project goals, priority sections, and completed work
2. **Then update `README.md`** to reflect the same status
3. Never update one without the other — if you mark an item as done in one file, mark it in both

If a new priority item is added or an existing one is split/merged/completed, update both files in the same edit session.

## Available Skills (22)

| Phase | Skills |
|-------|--------|
| Setup & Onboarding | `meta-project-setup`, `architecture-arch`, `quality-review`, `quality-strategic-advisor`, `quality-upgrade-advisor`, `learning-codebase-mastery` |
| Planning | `planning-impl-plan`, `planning-spec-from-text` |
| Building | `learning-pair-programming`, `api-development-api-impl` |
| Reviewing & Refactoring | `code-diagnosis`, `safe-changes-impact-check`, `safe-changes-refactor-safe`, `quality-sync-docs` |
| Wrapping Up | `commit-ready` |
| Learning | `learning-algo-practice`, `learning-concept-recall`, `learning-debug-training`, `learning-code-review-eye` |
| Library Maintenance | `meta-discover-claude-features`, `meta-experiment-feature`, `meta-skill-audit` |
