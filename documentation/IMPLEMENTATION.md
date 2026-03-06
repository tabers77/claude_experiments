# Implementation Plan

> Last updated: 2026-03-06
> Source: `/meta-discover-claude-features` audit + `/meta-skill-audit` gap analysis + `/quality-strategic-advisor` roadmap

## Current State

The plugin has **22 skills**, **2 agents** (code-reviewer, learning-coach), **6 hook handlers** across 4 events (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse), **4 rules**. Skills are organized by development phase (Setup → Plan → Build → Review → Wrap up → Learn).

**Discovery sources**: [Claude Code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), [official plugin docs](https://code.claude.com/docs/en/plugins), [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) (community agents + workflows).

---

## Project Goals Status

Consolidated from the original problem statement. Tracks what motivated this project and what's left.

| Goal | Status | Notes |
|------|--------|-------|
| **Bridge theory→practice gap** | Done | `test_project/` for validation, skills are hands-on |
| **Stay current with Claude Code** | Done | `meta-discover-claude-features` + `meta-project-setup` |
| **Cover advanced features** | Partial | Hooks and agents covered. **MCP** and **headless/CI mode** still uncovered — no skills or learning modules for these. |
| **Tutor mode for active learning** | Done | 5 learning skills + `learning-coach` agent with persistent memory |
| **Reusability across projects** | Done | Plugin format, loadable via `--plugin-dir` in any project |
| **Spaced repetition** | Done | `learning-concept-recall` skill |
| **Community patterns** | Done | `meta-discover-claude-features` scouts community repos |
| **Project templates** | Not started | `library/templates/` has generic + python-api CLAUDE.md templates, but no scaffolding skill to apply them |

### Remaining from original scope

- **MCP coverage**: No skill teaches or experiments with MCP servers. Consider a learning module or extend `meta-experiment-feature`.
- **Headless/CI mode**: The weekly quality check now uses `anthropics/claude-code-action@v1` (Claude Code in CI). No dedicated learning skill for headless mode yet.
- **Project templates**: Could create a skill that scaffolds Claude Code config (CLAUDE.md, rules, hooks) for new projects using `library/templates/`.

---

## Overlap Analysis Summary

> From `/meta-skill-audit` (2026-02-13). All 7 detected overlaps are **Low severity** — components share scenarios but serve distinct purposes. Existing "vs" documentation in SKILL.md files clarifies boundaries. **No merges needed.**

---

## Completed Work

### Session 2026-02-13

- [x] Created `learning-pair-programming` skill (collaborative coding, Claude as senior colleague)
- [x] Created `meta-discover-claude-features` skill (scout official docs + community for new features)
- [x] Restructured README.md — skills organized by development phase with Essential/If needed flags
- [x] Updated CLAUDE.md to match new structure
- [x] Ran `/meta-skill-audit` — no overlaps need merging, 5 gaps identified
- [x] Ran `/meta-discover-claude-features` — 3 adopt-now items, 5 plan-next items found
- [x] **1.1 Agent Memory**: Created `learning-coach` agent with `memory: user`, updated all 5 learning skills with `context: fork` + `agent: learning-coach`
- [x] **Recent Changes mode**: Added Mode D to `learning-codebase-mastery` — quiz on recent git changes

**Key insight from 1.1**: `memory` is an agent-only frontmatter field. Skills get persistent memory via `context: fork` + `agent: learning-coach`.

### Session 2026-02-28

- [x] Created CLAUDE.md for the repository
- [x] Consolidated `PROBLEM_STATEMENT.md` and `SKILL_AUDIT.md` into `IMPLEMENTATION.md`
- [x] Added Implementation Roadmap Sync rule to CLAUDE.md
- [x] **Weekly quality check simplification**: Rewrote from 4-job pipeline (analyze → issue → PR → auto-merge) to 1-job pipeline (analyze → issue). Removed `apply_changes.py` and `prompts/` directory. The script now outputs markdown directly instead of JSON (no more fragile JSON parsing). Dropped PR creation and auto-merge tiers — findings go to a GitHub issue for manual review. Still uses Azure OpenAI via Key Vault.

### Session 2026-03-06

- [x] Migrated `STRATEGIC_ROADMAP.md` next steps into `IMPLEMENTATION.md` and deleted the file
- [x] **1.2 PreToolUse additionalContext**: Created `scripts/sensitive-file-hook.py` — injects context-aware guidance before editing sensitive files (auth, config, migration, secrets, security patterns). Replaced old PostToolUse alert.
- [x] **1.3 SessionStart hook**: Created `scripts/session-start-hook.py` — validates plugin and shows skill count on new sessions. Added `SessionStart` hook to `plugin.json`.

---

## Priority 0: Strategic (from `/quality-strategic-advisor` 2026-02-28)

Items addressing discoverability, distribution, and stated coverage gaps. Ordered by theme:

**Theme 1 — Discoverability & Distribution**: 0.1 → 0.6 → 0.2 (+ community submissions)
**Theme 2 — Fill Coverage Gaps**: 0.3 → 0.4 → 0.5

### 0.1 Skill Auto-Activation via Hooks (skill-rules.json)

**What**: A `UserPromptSubmit` hook that reads `skill-rules.json`, matches user prompts against trigger patterns, and injects skill-loading instructions into Claude's context — making skills activate without `/slash-commands`.

**Why**: Research shows skill auto-activation sits at 20-50% without hooks, up to 90% with optimized triggers. Transforms the plugin from "toolkit you invoke" to "assistant that adapts."

**How**:
- Create `skill-rules.json` mapping context patterns → skills
- Write a script that reads rules, matches against `$CLAUDE_USER_PROMPT`, outputs `additionalContext`
- Add `UserPromptSubmit` hook to `plugin.json`

**Effort**: Small | **Status**: Done (2026-02-28)

**Implemented**:
- `skill-rules.json` — 22 rules mapping trigger patterns to skills
- `scripts/skill-activation-hook.py` — matches user prompts, outputs `additionalContext`
- `UserPromptSubmit` hook in `plugin.json` — runs the script on every prompt

---

### 0.2 Publish to Official Plugin Marketplace

**What**: Make installable via `/plugin install claude-library` through Anthropic's official directory.

**Why**: 9,000+ plugins listed as of Feb 2026. Not being listed = invisible to most Claude Code users.

**How**:
- Review [marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces) for submission requirements
- Ensure `plugin.json` has required metadata
- Submit PR to [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- Submit to community directories (awesome-claude-skills, awesome-claude-plugins)

**Effort**: Small | **Status**: Not started

**Community submissions** (do alongside 0.2):
- [ ] Submit to [awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
- [ ] Submit to [awesome-claude-plugins](https://github.com/Chat2AnyLLM/awesome-claude-plugins)

---

### 0.3 Headless/CI Mode Skill

**What**: Learning skill teaching Claude Code headless mode (`-p` flag) for CI/CD pipelines — automated code review, test generation, changelog creation, doc updates.

**Why**: 60%+ of teams use headless mode. Biggest stated coverage gap. Plugin already has `scripts/quality-action/` as a real-world example.

**Skill name**: `learning-ci-headless` | **Phase**: Learning
**Effort**: Medium | **Status**: Not started

---

### 0.4 Agent Teams Orchestration Skill

**What**: Skill teaching Agent Teams — multiple Claude Code instances coordinating on tasks. When to use, team composition, scope decomposition, cost awareness.

**Why**: Hottest Claude Code feature of Feb 2026. Positions ahead of curve before it exits experimental.

**Skill name**: `meta-agent-teams` | **Phase**: Library Maintenance
**Effort**: Medium | **Status**: Not started

---

### 0.5 MCP Learning Module

**What**: Learning skill covering MCP fundamentals — protocol, transports, common servers, building custom servers, MCP Apps.

**Why**: 10,000+ MCP servers, largest content gap vs. ecosystem. Many awesome-claude-skills entries are MCP integrations.

**Skill name**: `learning-mcp-servers` | **Phase**: Learning
**Effort**: Medium | **Status**: Not started

---

### 0.6 Skill Description Optimization

**What**: Rewrite `description` frontmatter in all 22 skills with "Use when..." triggers and explicit keywords for better auto-activation.

**Why**: Amplifies 0.1 (skill-rules.json). Descriptions appear in marketplace search results (amplifies 0.2).

**Effort**: Small-Medium | **Status**: Not started

---

## Priority 1: Quick Wins (enhance existing components)

### 1.2 PreToolUse additionalContext for Smarter Hooks

**What**: `PreToolUse` hooks can return `additionalContext` that gets injected into the model's context — not just block/alert.

**Why**: Previous sensitive file hook just said "ALERT: Sensitive file modified" after the fact. With `additionalContext`, guidance is injected *before* the edit executes — making Claude behave like a cautious colleague.

**Effort**: Small | **Status**: Done (2026-03-06)

**Implemented**:
- `scripts/sensitive-file-hook.py` — reads tool input from stdin JSON, matches file path against 5 pattern categories (auth, config, migration, secrets, security), returns `additionalContext` guidance
- Added as second PreToolUse handler for `Edit|Write` in `plugin.json`
- Removed the old PostToolUse "ALERT: Sensitive file modified" echo (replaced by this richer pre-execution guidance)
- PostToolUse ruff linting hook kept as-is (formatting, not guidance)

---

### 1.3 SessionStart Hook for Plugin Initialization

**What**: `SessionStart` hook fires on session startup. Shows plugin health and skill count as a "welcome mat."

**Why**: When someone loads this plugin, they immediately see it's active and how many skills are available. Lightweight validation catches broken skills early.

**Effort**: Small | **Status**: Done (2026-03-06)

**Implemented**:
- `scripts/session-start-hook.py` — counts skills, runs lightweight validation (frontmatter, naming), returns `additionalContext` with summary
- Added `SessionStart` hook with `startup` matcher in `plugin.json` (only on new sessions, not resume/compact)
- Outputs: skill count + any validation issues found
- 10-second timeout to keep startup fast

---

## Priority 2: New Skills (fill audit gaps)

### 2.1 Security Review Skill

**Gap**: Security review (Medium priority)

**Skill name**: `safe-changes-security-review`
**Phase**: Reviewing & Refactoring

**What it should do**:
- Targeted security analysis (not a full repo audit — that's `quality-review`'s job)
- Focus areas: auth flow review, input validation, OWASP top 10 patterns, secrets detection, SQL injection, XSS
- Teach the user what's risky and why, not just list findings
- Output: findings with severity, file paths, and remediation guidance

**Differentiation**:
- vs `code-diagnosis`: finds bugs/smells. This focuses on security vulnerabilities.
- vs `code-reviewer` agent: reviews recent diffs broadly. This does deep security-focused scans.
- vs `library/rules/security.md`: rules are passive. This actively analyzes code.

**Effort**: Medium

---

### 2.2 Performance Analysis Skill

**Gap**: Performance analysis (Medium priority)

**Skill name**: `code-performance`
**Phase**: Reviewing & Refactoring

**What it should do**:
- Targeted performance analysis of specific modules/functions
- Focus: algorithmic complexity, query performance (N+1, missing indexes), memory usage, data structure choice
- DS-specific: vectorization in pandas, batch processing, caching, avoiding `.apply()` loops
- Output: findings with impact estimate, current vs suggested approach

**Differentiation**: vs `code-diagnosis` — correctness issues vs performance issues.

**Effort**: Medium

---

### 2.3 Test Strategy Skill

**Gap**: Testing strategy (Medium priority)

**Skill name**: `planning-test-strategy`
**Phase**: Planning & Design

**What it should do**:
- Design what to test, at what level (unit/integration/e2e), what to mock, what edge cases matter
- Works alongside `planning-impl-plan` — plan implementation, then plan tests
- Output: test plan with descriptions, levels, mock strategy — NOT generated test code

**Differentiation**: vs `library/rules/testing.md` (conventions) and vs `code-reviewer` (reviews existing tests).

**Effort**: Medium

---

### 2.4 LSP Server Configuration

**What**: Configure `.lsp.json` for Python (pyright/pylsp) and TypeScript (tsserver) to give Claude real-time code intelligence.

**Why**: Improves accuracy of `code-diagnosis`, `architecture-arch`, `code-reviewer`, and any skill that reads code. Silently does nothing if language servers aren't installed.

**Effort**: Small (config), but needs cross-project testing

---

### 2.5 Deployment Checklist Skill

**Gap**: Deployment/release (Low-Medium priority)

**Skill name**: `session-deploy`
**Phase**: Wrapping Up

**What it should do**: Pre-deploy checklist (tests pass, no secrets, env vars set, migrations applied, changelog updated). Generic — adapts to whatever the project uses.

**Lower priority** — deployment workflows vary heavily across projects.

**Effort**: Medium

---

### 2.6 Database/Migration Safety

**Gap**: DB-specific guidance (Low-Medium priority from audit)

**Option A**: Extend `safe-changes-impact-check` with DB-specific checklists when it detects schema changes (migration safety, rollback plans, data backfill strategies).
**Option B**: Create `safe-changes-migration` skill.

**Recommendation**: Start with Option A (extend existing skill). Only create a separate skill if the scope grows too large.

**Effort**: Small-Medium

---

## Priority 3: Watch List

Features that are interesting but not mature enough or not urgent.

| Feature | Source | Trigger to re-evaluate |
|---------|--------|----------------------|
| **Hooks in frontmatter** (inline hooks in skill/agent YAML) | Official v2.1.0 | When we do a major plugin restructure |
| **MCP Apps** (interactive UI from MCP tools) | MCP Jan 2026 | When a specific skill would benefit from interactive output (e.g., quality-review dashboard) |
| **Sub-agent Restriction** (`Task(agent_type)` in tools frontmatter) | Official v2.1.33 | When we add more agents that need isolation |
| **CCPI Package Manager pattern** | [plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | Only if plugin grows beyond 40+ skills and users request à la carte install |
| **AI agent delegation** (Jules, Deep Research, Manus) | awesome-claude-skills | When a workflow clearly benefits from multi-AI orchestration |
| **Self-improving skill pattern** (Claudeception) | [Claudeception](https://github.com/blader/Claudeception), task-observer | When learning-coach agent memory has enough data to mine patterns from |
| **Conditional skill loading by file type** | [skill-rules.json pattern](https://github.com/diet103/claude-code-infrastructure-showcase) | After 0.6 (description optimization) — natural extension of auto-activation |
| **Project template scaffolding** | Project goal | When `library/templates/` has enough templates to justify a skill |

---

## After Each Implementation

Per `.claude/rules/library.md` rule 7, after adding/modifying any skill:
1. Update `CLAUDE.md` — skills table, directory tree
2. Update `README.md` — skills table, directory tree, quick reference, workflow guide
3. Update `tests/test_skills.py` — expected skill count
4. Run `python tests/test_skills.py` — all checks must pass
