# Analysis: everything-claude-code (ECC) vs claude-library

**Date:** 2026-03-27
**Source:** https://github.com/affaan-m/everything-claude-code
**Purpose:** Identify patterns, techniques, and features from ECC that could improve our plugin.

---

## Overview Comparison

| Aspect | **ECC** | **claude-library (ours)** |
|--------|---------|--------------------------|
| Scale | 125+ skills, 28 agents, 60 commands | 26 skills, 2 agents, 0 commands |
| Focus | Breadth — covers every Claude Code feature + multi-IDE | Depth — curated workflows for a data science developer |
| Languages | TS, Python, Go, Swift, PHP, Kotlin, Rust, Perl, C++ | Python-centric |
| IDE support | Claude Code, Cursor, OpenCode, Codex, Kiro, Antigravity | Claude Code only |
| Hook engine | Node.js scripts with profile system (minimal/standard/strict) | Python scripts, flat (all-or-nothing) |
| Learning system | "Continuous Learning v2" — auto-extracts patterns from sessions into evolved skills | 5 learning skills via `learning-coach` agent with persistent memory |
| Plugin manifest | v1.9.0, hooks only (no inline skills/agents) | v1.0.0, hooks only (skills/agents auto-discovered) |

---

## ECC Architecture Highlights

### Directory Structure

ECC mirrors its config across multiple IDE formats:

```
everything-claude-code/
├── agents/              # 28 Claude Code subagents
├── skills/              # 125+ curated skills (shipped)
├── commands/            # 60 slash commands
├── hooks/hooks.json     # Central hook config
├── rules/               # Multi-language rule sets (per language)
├── mcp-configs/         # MCP server configurations
├── scripts/             # Node.js hook scripts + utilities
├── tests/               # Node.js test suite
├── docs/                # Policies, guides
├── .claude/             # Claude Code specific (commands, identity, skills, rules, team, enterprise)
├── .cursor/             # Cursor IDE mirror (hooks, rules, skills)
├── .codex/              # Codex CLI mirror (agents, config)
├── .kiro/               # Kiro IDE mirror (agents, hooks, skills, steering)
├── .opencode/           # OpenCode mirror (commands)
├── .agents/             # OpenAI Agents mirror (skills with openai.yaml)
├── .claude-plugin/      # Plugin manifest + marketplace.json
```

### Hook Profile System

ECC's most impactful pattern. Every hook runs through a `run-with-flags.js` wrapper:

```json
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/run-with-flags.js\" \"post:edit:format\" \"scripts/hooks/post-edit-format.js\" \"strict\""
}
```

The third argument (`"strict"`) declares which profiles activate this hook. Users control enforcement via:

```bash
export ECC_HOOK_PROFILE=standard  # Options: minimal, standard, strict
```

**Profile breakdown:**
- `minimal` — Only session persistence, cost tracking, session evaluation
- `standard` — Adds doc warnings, console.log checks, governance, tmux reminders, compaction suggestions, continuous learning, MCP health
- `strict` — Adds auto-format, TypeScript type-checking, quality gates

### Continuous Learning v2

A two-phase system:

1. **Observation** — Pre/Post hooks on `*` (all tools) run `observe.sh` asynchronously to capture tool usage patterns
2. **Evaluation** — `Stop` hook runs `evaluate-session.js` to extract learnable patterns
3. **Storage** — Learned skills go to `~/.claude/skills/learned/<name>/SKILL.md` with `.provenance.json` metadata
4. **Evolution** — Over time, clustered patterns become "instincts" (YAML files) and "evolved skills"

Skill provenance types:
| Type | Location | Shipped? | Provenance Required? |
|------|----------|----------|---------------------|
| Curated | `skills/` (repo) | Yes | No |
| Learned | `~/.claude/skills/learned/` | No | Yes |
| Imported | `~/.claude/skills/imported/` | No | Yes |
| Evolved | `~/.claude/homunculus/evolved/skills/` | No | Inherits from instincts |

### Session Persistence

- `Stop` hook saves session state (what was being worked on, decisions made)
- `SessionStart` hook restores previous context
- Uses SQLite state store for structured session data

### Hook Inventory

| Event | Hooks | Notable |
|-------|-------|---------|
| **PreToolUse** | 11 hooks | Block `--no-verify`, tmux reminder, doc file warning, suggest compaction, continuous learning observation, security monitor, governance capture, config protection, MCP health check |
| **PostToolUse** | 8 hooks | PR logging, build analysis (async), quality gate (async), auto-format, TypeScript check, console.log warning, governance capture, learning observation |
| **Stop** | 5 hooks | Console.log check, session persistence, pattern evaluation, cost tracking, desktop notifications |
| **SessionStart** | 1 hook | Restore session state + detect package manager |
| **SessionEnd** | 1 hook | Session end marker |
| **PreCompact** | 1 hook | Save state before compaction |
| **PostToolUseFailure** | 1 hook | MCP health tracking + reconnect |

### Other Notable Patterns

- **identity.json** — Stores user preferences (verbosity, technical level, domains) at `.claude/identity.json`
- **Team config** — `.claude/team/` for shared team settings
- **Enterprise controls** — `.claude/enterprise/controls.md` for governance
- **Instincts** — YAML files with curated conventions extracted from usage patterns
- **Research playbook** — `.claude/research/` for research-first development workflows
- **ecc-tools.json** — Dependency graph for modular package installation (runtime-core, workflow-pack, agentshield-pack, research-pack, team-config-sync, enterprise-controls)

---

## What to Adopt

### Priority 1 — Quick Wins (< 1 hour each)

#### 1.1 Config Protection Hook
**What:** Block modifications to linter/formatter config files (`.ruff.toml`, `pyproject.toml [tool.ruff]`, `.flake8`, `.pylintrc`, `.prettierrc`, `biome.json`, `.eslintrc`).
**Why:** Common failure mode — agent weakens configs instead of fixing code. ECC's `config-protection.js` prevents this.
**How:** Add a new matcher in our `PreToolUse` hooks targeting `Edit|Write` on config file patterns.

#### 1.2 Debug Statement Warning
**What:** Post-edit hook that warns when `print()`, `console.log`, `debugger`, or `breakpoint()` statements are added.
**Why:** Catches leftover debug code before commit. ECC has both post-edit and Stop-level checks for this.
**How:** Add a `PostToolUse` hook for `Edit` that greps the edited file for debug patterns.

#### 1.3 Block `--no-verify` Flag
**What:** Prevent git commits/pushes that skip hooks via `--no-verify`.
**Why:** Pre-commit hooks exist for a reason. ECC uses `block-no-verify` npm package for this.
**How:** Add pattern check in our existing Bash `PreToolUse` hook.

### Priority 2 — Medium Effort, High Payoff (2-4 hours each)

#### 2.1 Hook Profile System
**What:** Wrap all hooks in a profile check so users can choose enforcement level.
**Why:** Our hooks are all-or-nothing. New users may find full enforcement overwhelming. Profiles let them adopt gradually.
**How:**
- Create a Python wrapper script (`scripts/hook-profile-gate.py`) that checks `CLAUDE_LIBRARY_PROFILE` env var
- Three levels: `minimal` (safety only), `standard` (safety + suggestions), `strict` (safety + suggestions + auto-lint)
- Each hook declaration includes its profile level
- Wrapper script runs the actual hook only if the profile matches

**Profile mapping for our hooks:**
| Hook | minimal | standard | strict |
|------|---------|----------|--------|
| Block protected paths | x | x | x |
| Block destructive git | x | x | x |
| Block `--no-verify` | x | x | x |
| Config protection | x | x | x |
| Sensitive file guidance | | x | x |
| Skill auto-suggestion | | x | x |
| Debug statement warning | | x | x |
| Auto-lint with ruff | | | x |
| Session persistence | x | x | x |

#### 2.2 Session State Persistence
**What:** Save working context on `Stop`, restore on `SessionStart`.
**Why:** Continuity between sessions without relying only on auto-memory. Know what was being worked on, which files were touched, what decisions were made.
**How:**
- `Stop` hook: Save to `.claude/session-state.json` — current branch, recently edited files, active task summary
- `SessionStart` hook: Read and inject as context if state exists and is < 24h old
- Keep it lightweight — just key context, not full conversation replay

#### 2.3 Skill Provenance Policy
**What:** Define where user-generated vs curated skills live.
**Why:** As users create custom skills or import from other plugins, we need clear separation.
**How:**
- Curated: `skills/` (shipped, validated by CI)
- User-created: `~/.claude/skills/custom/` (local, not shipped)
- Imported: `~/.claude/skills/imported/` (from external sources, needs provenance)
- Document in a `docs/SKILL-PLACEMENT-POLICY.md`

### Priority 3 — Larger Investment (4-8 hours each)

#### 3.1 Passive Learning Hook
**What:** Lightweight `Stop` hook that logs session patterns for the learning-coach agent.
**Why:** Currently learning is opt-in (user must invoke `/learning-*` skills). A passive hook would accumulate patterns automatically, making learning skills more effective when invoked.
**How:**
- `Stop` hook: Extract key patterns (files edited, tools used, errors encountered, skills invoked)
- Append to `~/.claude/agent-memory/learning-coach/session-log.jsonl`
- Learning skills can read this log for richer context
- Keep async with short timeout to avoid blocking

#### 3.2 Cost/Token Tracking
**What:** Track token usage and cost per session.
**Why:** Helps users understand which workflows are expensive and optimize accordingly.
**How:**
- `Stop` hook: Parse session metadata for token counts
- Append to `~/.claude/claude-library/cost-log.jsonl`
- Optional: Add a `/cost-report` skill that summarizes usage

#### 3.3 PreCompact State Save
**What:** Save important state before context compaction happens.
**Why:** When Claude compacts context, information can be lost. Saving state beforehand preserves key decisions.
**How:**
- `PreCompact` hook: Dump current task state, key decisions, file edit history to `.claude/pre-compact-state.json`
- SessionStart or post-compact can re-inject this context

---

## Gaps Identified: Skill Discoverability & Learning

The ECC analysis surfaced good infrastructure patterns, but two areas need targeted additions beyond what ECC offers — because they address our project's core value propositions.

### Gap 1: "Not clear which skill to use when"

**Current state:** The README has three layers of guidance (phase tables, quick reference, decision guide) and `skill-activation-hook.py` auto-suggests based on keyword matching. The CLAUDE.md has a lighter Skill Decision Guide. This is solid documentation — but it's **static**. It depends on the user already knowing what phase they're in, and keyword matching is reactive (only fires when the user's prompt happens to contain a trigger word).

**What the ECC plan already addresses:**
- **Hook profile system (2.1)** removes a barrier — new users won't be overwhelmed by all hooks firing at once, so they can discover skills gradually.
- **Session state persistence (2.2)** enables phase-awareness — if Claude knows what you just did (committed, started a branch, reviewed code), suggestions can be contextual, not just keyword-based.

**What's missing — new items to add:**

#### 2.4 Phase-Aware Skill Suggestion
**What:** Enhance `skill-activation-hook.py` to infer the current development phase from recent actions (git state, recent edits, session history) and weight skill suggestions accordingly.
**Why:** Keyword matching only fires when the user's prompt accidentally contains a trigger. Phase-awareness makes suggestions proactive — "you just finished building, consider `/commit-ready`" — without the user needing to ask.
**How:**
- On `UserPromptSubmit`, read lightweight signals: current git status (uncommitted changes? new branch? recent commits?), session state (if 2.2 is implemented), time since last commit
- Map signals to likely phase: new branch + no edits = Setup/Planning, many edits + no commits = Building, staged changes = Wrapping Up
- Boost suggestions from the inferred phase, suppress suggestions from irrelevant phases
- Keep it lightweight — this runs on every prompt, so no git log parsing or file scanning

**Phase mapping logic:**
| Signal | Inferred Phase | Boosted Skills |
|--------|---------------|----------------|
| New branch, no edits | Setup/Planning | `/architecture-arch`, `/planning-impl-plan` |
| Many uncommitted edits | Building | `/code-diagnosis`, `/learning-pair-programming` |
| Staged changes, no commit yet | Wrapping Up | `/commit-ready`, `/learning-codebase-mastery pre-commit` |
| Just committed | Review/Next | `code-reviewer`, `/quality-sync-docs` |
| No repo / clean state | Skill Building | `/learning-algo-practice`, `/learning-concept-recall` |

#### 2.5 `/what-next` Lightweight Orientation Skill
**What:** A fast (< 10 second) skill that reads git state and session context, then outputs a 3-line orientation: what phase you're in, what skills are relevant, and what the logical next step is.
**Why:** Sometimes users don't know what to type to trigger a suggestion. A simple `/what-next` gives them a starting point without requiring them to read the README.
**How:**
- Read git status, recent commits, uncommitted changes, branch name
- Map to phase (same logic as 2.4)
- Output: "You're in [phase]. Relevant: [2-3 skills]. Suggested next: [one action]."
- No heavy analysis — just orientation

### Gap 2: Learning is the most valuable part but entirely opt-in

**Current state:** Five learning skills with persistent memory via `learning-coach` agent. All require explicit invocation. The learning-coach remembers progress across sessions, but has no visibility into what the user actually does between learning sessions. Learning skills are grouped in a separate "Skill Building" phase, disconnected from the development workflow.

**What the ECC plan already addresses:**
- **Passive learning hook (3.1)** logs session patterns so the learning-coach has real data about the user's work, not just practice sessions.
- **Session persistence (2.2)** gives the learning-coach continuity about what was being worked on.

**What's missing — new items to add:**

#### 2.6 Learning Integration into Development Workflow
**What:** The skill suggestion hook should recommend learning skills at natural integration points in the development workflow, not just when the user explicitly asks to practice.
**Why:** `/learning-codebase-mastery` modes like "Pre-Commit" and "Daily Practice" are development-phase skills, not standalone practice. But they're only suggested when the user types "quiz" or "practice." They should surface automatically at the right moment.
**How:**
- When phase-aware suggestion (2.4) detects "about to commit" → suggest `/learning-codebase-mastery pre-commit`
- When session has been long (many edits) and user says "done" or "wrap up" → suggest `/learning-codebase-mastery daily practice`
- When user is reading unfamiliar code (lots of Read tool calls, few edits) → suggest `/learning-codebase-mastery tutor`
- Keep these as gentle suggestions, not forced — the user can ignore them

**Integration points:**
| Development Moment | Learning Suggestion |
|-------------------|-------------------|
| About to commit (staged changes) | `/learning-codebase-mastery pre-commit` — verify you understand what you're committing |
| End of session (wrapping up) | `/learning-codebase-mastery daily practice` — reinforce what you built today |
| Reading unfamiliar code | `/learning-codebase-mastery tutor` — quiz yourself on what you're reading |
| After catching up on git changes | `/learning-codebase-mastery recent changes` — test retention of what changed |
| Clean state, no active work | `/learning-concept-recall` — review concepts from previous sessions |

#### 3.4 Learning Summary in Session Start
**What:** When `SessionStart` restores state (2.2), include a one-liner from the learning-coach's memory: last practice topic, current weak areas, streak status.
**Why:** Creates continuity without requiring the user to explicitly start a learning session. Seeing "Your weak area is pandas indexing (3 sessions)" is a natural nudge to practice.
**How:**
- `SessionStart` hook reads `~/.claude/agent-memory/learning-coach/` for latest state
- Extracts: last practice date, current weak areas, mastery streak
- Injects as one-line `additionalContext`: "Learning coach: last practiced [topic] on [date]. Weak areas: [X, Y]."
- Only fires if learning data exists (no noise for users who haven't used learning skills)

#### 3.5 Passive Learning Enrichment
**What:** Extend the passive learning hook (3.1) to not just log raw actions, but extract *learning-relevant patterns*: repeated errors, tools used inefficiently, code patterns the user keeps looking up.
**Why:** Raw session logs are noisy. The learning-coach needs curated signals: "user hit IndexError 3 times this week in pandas code" is more useful than "user ran 47 tool calls."
**How:**
- `Stop` hook (3.1) filters actions into learning-relevant categories:
  - **Errors encountered** — repeated error types suggest knowledge gaps
  - **Code patterns looked up** — files read but not edited suggest learning/exploration
  - **Skills used** — which skills the user reaches for most
  - **Topics touched** — infer from file paths and content (pandas, SQL, API, etc.)
- Write curated summary to `~/.claude/agent-memory/learning-coach/passive-log.jsonl`
- Learning skills read this log to personalize: concept-recall prioritizes topics the user works with, debug-training uses error patterns the user actually hits

---

## What NOT to Adopt

| ECC Pattern | Why Skip |
|-------------|----------|
| 125+ skills breadth | Quantity over quality. Our curated 26 skills with clear phases is better for our use case. |
| Multi-IDE mirroring (.cursor, .codex, .kiro, .opencode, .agents) | Not needed — we target Claude Code only. Adds massive maintenance burden. |
| Node.js hook scripts | We're Python-centric. Switching to Node would fragment our toolchain. |
| Complex dependency graph (ecc-tools.json) | Over-engineered for our scale. The package/module/tier system is enterprise overhead. |
| Enterprise governance / controls | Not relevant for a personal/small-team plugin. |
| Domain-specific skills (investor materials, market research, article writing, video editing) | Specific to ECC author's needs, not ours. |
| identity.json user preferences | Our auto-memory system already handles this better with richer context. |
| Marketplace packaging (marketplace.json) | Premature for our stage. |

---

## Implementation Order

```
Phase 1 (Quick Wins) ─────────────────────────────────
  1.1 Config protection hook
  1.2 Debug statement warning hook
  1.3 Block --no-verify

Phase 2 (Core Infrastructure + Discoverability) ──────
  2.1 Hook profile system
  2.2 Session state persistence
  2.3 Skill provenance policy doc
  2.4 Phase-aware skill suggestion          ← NEW (discoverability)
  2.5 /what-next orientation skill          ← NEW (discoverability)
  2.6 Learning integration into dev workflow ← NEW (learning)

Phase 3 (Advanced + Learning) ────────────────────────
  3.1 Passive learning hook
  3.2 Cost/token tracking
  3.3 PreCompact state save
  3.4 Learning summary in session start     ← NEW (learning)
  3.5 Passive learning enrichment           ← NEW (learning)
```

**Dependencies:**
- Phase 1 items are independent — any order.
- 2.4 (phase-aware suggestions) benefits from 2.2 (session state) but can work without it using git signals alone.
- 2.5 (`/what-next`) shares logic with 2.4 — implement together.
- 2.6 (learning integration) depends on 2.4 (phase-awareness) to know when to suggest learning skills.
- 3.1 (passive learning) is standalone.
- 3.4 (learning summary) depends on 2.2 (session persistence) and 3.1 (passive learning data).
- 3.5 (learning enrichment) extends 3.1 — implement after 3.1 is validated.

---

## Key Takeaways

1. **ECC is broad, we are deep.** Their strength is coverage; ours is curation. We should stay curated but adopt their best infrastructure patterns.
2. **The hook profile system is their best idea.** It solves a real adoption problem — hooks that are too aggressive drive users away.
3. **Passive learning is their most innovative pattern.** Auto-extracting patterns from sessions is genuinely useful and aligns with our learning-coach architecture.
4. **Session persistence fills a real gap.** Our auto-memory helps, but explicit session state restoration is more reliable for continuity.
5. **We should NOT try to match their scale.** 125+ skills with multi-IDE support is a different product. Our value is being a focused, well-tested plugin for Python-centric data science workflows.
6. **Skill discoverability needs runtime intelligence, not more documentation.** The README and CLAUDE.md already have good guidance — the gap is that suggestions are keyword-reactive instead of phase-aware. Phase-aware suggestion (2.4) and `/what-next` (2.5) solve this at runtime.
7. **Learning should be woven into the development workflow, not siloed.** The five learning skills are powerful but isolated in a "Skill Building" phase. Integrating learning suggestions at natural moments (pre-commit, end-of-session, code exploration) makes them part of how you work, not a separate activity.
8. **Passive learning + enrichment is the highest-leverage improvement for the learning system.** The learning-coach is blind between explicit practice sessions. Passive observation (3.1) + curated enrichment (3.5) gives it real data about what the user struggles with, making every learning session more targeted.
