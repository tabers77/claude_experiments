# Implementation Plan

> Last updated: 2026-02-13
> Source: `/meta-discover-features` audit + `/meta-skill-audit` gap analysis

## Context

The plugin has **21 skills**, **2 agents**, **4 hooks**, **4 rules**. Skills are organized by development phase (Setup → Plan → Build → Review → Wrap up → Learn). The README was restructured with **Essential** vs *If needed* flags per phase.

**Known gaps** (from `documentation/SKILL_AUDIT.md`): testing strategy, security review, performance analysis, DB/migrations, deployment/release.

**Discovery sources**: [Claude Code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), [official plugin docs](https://code.claude.com/docs/en/plugins), [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) (community: 24 agents + 6 workflows for solo devs).

---

## Session 2026-02-13: Completed

- [x] Created `learning-pair-programming` skill (collaborative coding, Claude as senior colleague)
- [x] Created `meta-discover-features` skill (scout official docs + community for new features)
- [x] Restructured README.md — skills organized by development phase with Essential/If needed flags
- [x] Updated CLAUDE.md to match new structure
- [x] Ran `/meta-skill-audit` — no overlaps need merging, 5 gaps identified
- [x] Ran `/meta-discover-features` — 3 adopt-now items, 5 plan-next items found
- [x] **1.1 Agent Memory**: Created `learning-coach` agent with `memory: user`, updated all 5 learning skills with `context: fork` + `agent: learning-coach`
- [x] **Recent Changes mode**: Added Mode C to `learning-codebase-mastery` — quiz on recent git changes (merged into existing skill instead of creating new one)

---

## Priority 1: Quick Wins (enhance existing components)

### 1.1 Add Agent Memory to Learning Skills — DONE

**Implemented**: Created `agents/learning-coach.md` agent with `memory: user` (cross-project persistent memory). Updated all 5 learning skills with `context: fork` + `agent: learning-coach` so they run as subagents with persistent memory. Each skill now loads previous progress on start and saves results on end.

**Note**: `memory` is an agent-only frontmatter field, not available on skills. The solution uses `context: fork` + `agent: learning-coach` to run skills as subagents of the learning-coach agent, which has `memory: user`.

**Files changed**:
- `agents/learning-coach.md` — NEW (persistent learning coach with memory management instructions)
- `skills/learning-concept-recall/SKILL.md` — added `context: fork`, `agent: learning-coach`, memory load/save
- `skills/learning-algo-practice/SKILL.md` — added `context: fork`, `agent: learning-coach`, memory load/save
- `skills/learning-debug-training/SKILL.md` — added `context: fork`, `agent: learning-coach`, memory load/save
- `skills/learning-code-review-eye/SKILL.md` — added `context: fork`, `agent: learning-coach`, memory load/save
- `skills/learning-pair-programming/SKILL.md` — added `context: fork`, `agent: learning-coach`, memory load/save
- `CLAUDE.md` — added Agents section, updated directory tree
- `README.md` — added learning-coach to directory tree, added persistent memory note to Skill Building section

---

### 1.2 PreToolUse additionalContext for Smarter Hooks

**What**: `PreToolUse` hooks (v2.1.9) can return `additionalContext` that gets injected into the model's context — not just block/alert.

**Why**: Current sensitive file hook just says "ALERT: Sensitive file modified." With `additionalContext`, it can inject guidance like "This file handles authentication — verify security implications, check for exposed secrets" — making Claude behave like a cautious colleague.

**How**:
- In `.claude-plugin/plugin.json`, move the sensitive file detection from `PostToolUse` to `PreToolUse`
- Instead of `echo "ALERT: ..."`, return JSON with `additionalContext` field containing guidance
- Example patterns:
  - Files matching `auth|permission` → "This file controls access — verify no auth bypass introduced"
  - Files matching `config|secret` → "This may contain secrets — verify nothing sensitive is exposed"
  - Files matching `migration` → "Database migration — verify rollback safety"
- Keep the existing `PostToolUse` ruff linting hook as-is (it's about formatting, not guidance)

**Effort**: Small (< 1 hour)

**Reference**: Check [Claude Code hooks docs](https://code.claude.com/docs/en/hooks) for `additionalContext` return format.

---

### 1.3 Setup Hook for Plugin Initialization

**What**: `Setup` hook event (v2.1.10) triggers via `--init`, `--init-only`, or `--maintenance` CLI flags.

**Why**: When someone loads this plugin for the first time or runs maintenance, we can auto-validate the plugin and show a quick summary — the "welcome mat."

**How**:
- Add `Setup` event to `.claude-plugin/plugin.json` hooks section
- Hook command: run `python tests/test_skills.py` (already validates skill count, frontmatter, naming)
- Optionally: print a summary of available skills by phase to stdout
- Consider: on `--maintenance`, also run sync-references validation logic

**Effort**: Small (< 1 hour)

---

## Priority 2: New Skills (fill audit gaps)

### 2.1 Security Review Skill

**Gap filled**: Security review (Medium priority from audit)

**Skill name**: `safe-changes-security-review`
**Phase**: Reviewing & Refactoring (alongside `code-diagnosis`, `impact-check`, `refactor-safe`)
**Flag**: *If needed* — use when reviewing auth flows, handling user input, or before security-sensitive deploys

**Inspiration**: Community `security-auditor` agent from [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) does OWASP-based scanning.

**What it should do**:
- Targeted security analysis (not a full repo audit — that's `quality-review`'s job)
- Focus areas: auth flow review, input validation, OWASP top 10 patterns, secrets detection, SQL injection, XSS
- Adapt to our philosophy: teach the user what's risky and why, not just list findings
- Output format: similar to `code-diagnosis` — findings with severity, file paths, and remediation guidance

**Differentiation**:
- vs `code-diagnosis`: that skill finds bugs/smells/refactoring opportunities. This one focuses specifically on security vulnerabilities.
- vs `code-reviewer` agent: that does a general review of recent diffs. This does a deep security-focused scan of specific areas.
- vs `library/rules/security.md`: rules are passive conventions. This skill actively analyzes code.

**Effort**: Medium (1-3 hours)

---

### 2.2 Performance Analysis Skill

**Gap filled**: Performance analysis (Medium priority from audit)

**Skill name**: `code-performance`
**Phase**: Reviewing & Refactoring
**Flag**: *If needed* — use when investigating slow code or optimizing hot paths

**Inspiration**: Community `perf-auditor` agent identifies bottlenecks, bundle size, N+1 queries.

**What it should do**:
- Targeted performance analysis of specific modules/functions
- Focus areas: algorithmic complexity, query performance (N+1, missing indexes), memory usage, data structure choice
- DS-specific patterns: vectorization opportunities in pandas, batch processing, caching strategies, avoiding `.apply()` loops
- Output: findings with impact estimate (high/medium/low), current vs suggested approach, expected improvement

**Differentiation**:
- vs `code-diagnosis`: that finds correctness issues. This finds performance issues.
- Could cross-reference: `code-diagnosis` might flag "this looks slow" and suggest running `/code-performance`

**Effort**: Medium (1-3 hours)

---

### 2.3 Test Strategy Skill

**Gap filled**: Testing strategy (Medium priority from audit)

**Skill name**: `planning-test-strategy`
**Phase**: Planning & Design (alongside `planning-impl-plan`, `planning-spec-from-text`)
**Flag**: *If needed* — use when designing test coverage for a new feature or major change

**Inspiration**: Community `test-writer` agent auto-generates tests. We adapt this to our philosophy: design the test plan, don't write the tests for the user.

**What it should do**:
- Design what to test, at what level (unit/integration/e2e), what to mock, what edge cases matter
- Works alongside `planning-impl-plan` — plan the implementation, then plan the tests
- For `learning-pair-programming`: reference this when reaching the "add tests" step
- Output: test plan with specific test descriptions, test levels, mock strategy — NOT generated test code

**Differentiation**:
- vs `library/rules/testing.md`: rules enforce conventions (naming, structure). This skill designs what to test for a specific feature.
- vs `code-reviewer` agent: that reviews existing tests. This designs new test coverage.

**Effort**: Medium (1-3 hours)

---

### 2.4 LSP Server Configuration

**Gap filled**: No gap — new capability that improves all existing skills

**File**: `.lsp.json` at plugin root

**What it should do**:
- Configure Language Server Protocol servers for common languages (Python via pyright/pylsp, TypeScript via tsserver)
- Gives Claude real-time code intelligence (diagnostics, go-to-definition, completions)
- Improves accuracy of `code-diagnosis`, `architecture-arch`, `code-reviewer`, and any skill that reads code

**How**:
- Create `.lsp.json` at plugin root with Python and TypeScript configs
- Document in README that users need language server binaries installed
- Test across different project types

**Note**: Users need `pyright` or `pylsp` installed for Python, `typescript-language-server` for TypeScript. If not installed, LSP silently does nothing — no breakage.

**Effort**: Small (< 1 hour) for config, but needs cross-project testing

---

### 2.5 Deployment Checklist Skill

**Gap filled**: Deployment/release (Low-Medium priority from audit)

**Skill name**: `session-deploy`
**Phase**: Would create a new sub-phase after Wrapping Up, or integrate into Wrapping Up
**Flag**: *If needed* — use before deploying to production

**Inspiration**: Community `deploy-checker` + `env-validator` agents.

**What it should do**:
- Pre-deploy checklist: tests pass, no secrets in code, env vars set, migrations applied, changelog updated
- Generic (not tied to AWS/GCP/Heroku) — adapts to whatever the project uses
- Verify step: confirm deployment succeeded, basic health check passes

**Lower priority than 2.1-2.3** — deployment workflows vary heavily across projects.

**Effort**: Medium (1-3 hours)

---

## Priority 3: Watch List (not ready yet)

These features are interesting but not mature enough or not urgent. Check back when triggers are met.

| Feature | Source | Trigger to re-evaluate |
|---------|--------|----------------------|
| **Agent Teams** (multi-agent collaboration) | Official v2.1.32 | When it exits `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` research preview |
| **Hooks in frontmatter** (inline hooks in skill/agent YAML) | Official v2.1.0 | When we do a major plugin restructure |
| **Plugin Marketplaces** (one-click install distribution) | Official docs | When plugin is stable enough for public distribution |
| **MCP Apps** (interactive UI from MCP tools) | MCP Jan 2026 | When more clients support MCP Apps rendering |
| **Sub-agent Restriction** (`Task(agent_type)` in tools frontmatter) | Official v2.1.33 | When we add more agents that need isolation |

---

## After Each Implementation

Per `library/rules/library.md` rule 7, after adding/modifying any skill:
1. Update `CLAUDE.md` — skills table, directory tree
2. Update `README.md` — skills table, directory tree, quick reference, workflow guide
3. Update `tests/test_skills.py` — expected skill count
4. Run `python tests/test_skills.py` — all checks must pass
