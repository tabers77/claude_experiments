# Strategic Roadmap: claude-library

**Generated**: 2026-02-28
**Domain**: Claude Code plugin providing reusable development workflow skills, agents, hooks, and rules
**Project vision**:
- Bridge theory-to-practice gap for Claude Code usage
- Stay current with Claude Code features (MCP, headless/CI, agent teams)
- Reusable across any project via plugin format

**Sources researched**:
- [x] Domain libraries and frameworks (8 evaluated)
- [x] Recent papers and techniques (6 evaluated)
- [x] Similar/adjacent projects (4 compared)
- [x] Community feedback and requests (5 sources)

---

## Project Understanding

**Domain**: Claude Code plugin providing reusable development workflow skills, agents, hooks, and rules for any software project.

**Core problem**: Setting up Claude Code effectively requires skills, hooks, and rules that enforce consistent workflows — this library provides them as a loadable plugin instead of copy-paste snippets.

**Architecture**: Plugin library — auto-discovered skills (`skills/<name>/SKILL.md`), agents (`agents/<name>.md`), hooks inline in `plugin.json`, loaded via `--plugin-dir`.

**Key abstractions**: Skills (22), Agents (2), Hooks (4), Development phases (Setup → Plan → Build → Review → Wrap up → Learn)

**Current integrations**: GitHub Actions (weekly quality check via Azure OpenAI), ruff linting, git hooks

**Stated vision**: Bridge theory→practice, stay current, cover advanced features, reusable via plugin format

**Design constraints**: Self-contained skills, docs in `documentation/`, sync after every change, no code in advisory skills

**Known gaps**: MCP coverage, headless/CI mode, project template scaffolding, security review, performance analysis, test strategy, hook additionalContext, Setup hook

**Domain keywords**: Claude Code plugin, Claude skills, agent skills, MCP servers, headless mode, CI/CD automation, code review automation, skill auto-activation, plugin marketplace, agent teams

---

## Competitive Landscape

Before recommendations, here's where this project sits relative to the ecosystem:

| Project | What it is | Size | Model |
|---------|-----------|------|-------|
| **claude-library** (this project) | Curated, opinionated workflow plugin | 22 skills, 2 agents | Single plugin, phase-organized, self-contained |
| [awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) | Directory/index of community skills | 88 skills listed, 169 repos linked | Curated list — no code, just links |
| [claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | Massive plugin collection + package manager | 270+ plugins, 739 skills, CCPI | Breadth-first — many small plugins |
| [anthropics/skills](https://github.com/anthropics/skills) | Official Anthropic reference skills | 4 document skills + spec | Production-grade reference implementations |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Official Anthropic plugin marketplace | Growing catalog | Centralized discovery, version tracking |

**Your differentiation**: You're not a directory (awesome-claude-skills) or a bulk collection (plugins-plus-skills). You're an **opinionated workflow system** — skills organized by development phase, with agents providing persistent memory, hooks enforcing quality gates, and skills that chain into workflows. That's your moat. The recommendations below reinforce it.

---

## Implement Next

### 1. Skill Auto-Activation via Hooks (skill-rules.json pattern)

**Category**: Architecture pattern
**Fills gap**: No — new capability (progressive skill loading)
**Priority**: High
**Maturity**: Production-ready (community-proven pattern)

**What it is**:
A `UserPromptSubmit` hook that reads a `skill-rules.json` file, matches the user's prompt (or file context) against trigger patterns, and injects skill-loading instructions into Claude's context — making skills activate automatically without `/slash-commands`. This is the single most impactful pattern the community has adopted that you're missing.

**Why it matters for this project**:
Your 22 skills are powerful but require users to know which `/slash-command` to invoke. Research shows skill auto-activation sits at only ~20-50% without hooks. With this pattern, users working in a specific context (e.g., editing migration files, writing tests, reviewing diffs) would automatically get relevant skill guidance loaded. This transforms your plugin from "toolkit you invoke" to "intelligent assistant that adapts."

**How it would integrate**:
- Where: New file `skill-rules.json` at plugin root + `UserPromptSubmit` hook in `plugin.json`
- New abstractions: `skill-rules.json` mapping triggers → skills
- Existing code affected: `plugin.json` (add `UserPromptSubmit` hook section)
- Dependencies added: None — pure hook + JSON config

**Implementation sketch**:
1. Create `skill-rules.json` mapping context patterns to skills (e.g., "refactor" → `safe-changes-refactor-safe`, "deploy" → `session-deploy`, mentions of "test" + "plan" → `planning-test-strategy`)
2. Write a small shell/Python script that reads `skill-rules.json`, matches against `$CLAUDE_USER_PROMPT`, and outputs `additionalContext` suggesting the matched skill
3. Add `UserPromptSubmit` hook to `plugin.json` pointing to the script
4. Document the pattern so users can extend `skill-rules.json` with their own triggers

**Effort**: Small (< 1 day)
**Risk**: Low — additive, doesn't change existing behavior. Worst case: suggestions are ignored.

**Sources**:
- [Skills Auto-Activation via Hooks](https://paddo.dev/blog/claude-skills-hooks-solution/) — analysis of the pattern
- [How to Make Claude Code Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably) — practical guide
- [How to Activate Claude Skills Automatically: 2 Fixes for 95% Activation](https://dev.to/oluwawunmiadesewa/claude-code-skills-not-triggering-2-fixes-for-100-activation-3b57) — community fix
- [diet103/claude-code-infrastructure-showcase skill-rules.json](https://github.com/diet103/claude-code-infrastructure-showcase/blob/main/.claude/skills/skill-rules.json) — reference implementation

---

### 2. Publish to Official Plugin Marketplace

**Category**: Distribution / Architecture pattern
**Fills gap**: Yes — "Plugin Marketplaces" is on Watch list in IMPLEMENTATION.md
**Priority**: High
**Maturity**: Production-ready (official Anthropic feature, 9,000+ plugins)

**What it is**:
Making this plugin installable via `/plugin install claude-library` through Anthropic's official plugin directory or a community marketplace. Currently, users must clone the repo and use `--plugin-dir`. The marketplace supports git-based installation with version tracking and automatic updates.

**Why it matters for this project**:
The plugin marketplace has 9,000+ plugins as of Feb 2026. Not being listed means your carefully crafted 22-skill workflow system is invisible to the majority of Claude Code users. awesome-claude-skills (6.7k stars) exists precisely because discovery is hard — being in the official marketplace solves this without relying on a third-party directory.

**How it would integrate**:
- Where: `plugin.json` metadata + submission to marketplace
- New abstractions: None
- Existing code affected: `plugin.json` (may need version/category metadata)
- Dependencies added: None

**Implementation sketch**:
1. Review [official marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces) for submission requirements
2. Ensure `plugin.json` has all required metadata (version, description, category, homepage)
3. Submit to [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) via PR
4. Optionally: Submit to community marketplaces (awesome-claude-skills, composio) for additional visibility
5. Update README with install instructions: `/plugin install claude-library`

**Effort**: Small (< 1 day)
**Risk**: Low — the plugin already works; this is distribution.

**Sources**:
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) — official docs
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — official directory
- [Claude Code Plugins: Installation & Build Guide](https://www.morphllm.com/claude-code-plugins) — community guide

---

### 3. Headless/CI Mode Skill

**Category**: New skill
**Fills gap**: Yes — "Headless/CI mode" listed as uncovered in IMPLEMENTATION.md
**Priority**: High
**Maturity**: Production-ready (60%+ of teams use headless mode)

**What it is**:
A learning/reference skill that teaches users how to use Claude Code's headless mode (`-p` flag) for CI/CD pipelines. Covers common use cases: automated code review in PRs, test generation, changelog creation, documentation updates, linting, and migration assistance.

**Why it matters for this project**:
Headless mode is one of Claude Code's most impactful features — over 60% of teams use it, and it reduces code review time by ~40%. Your plugin already has a weekly quality check GitHub Action, but no skill teaches users how to build their own headless workflows. This is a gap that both awesome-claude-skills and plugins-plus-skills also largely miss — most entries there are interactive skills, not CI-oriented.

**How it would integrate**:
- Where: `skills/learning-ci-headless/SKILL.md`
- Phase: Learning (standalone practice) or Setup & Onboarding
- Existing code affected: CLAUDE.md, README.md, tests/test_skills.py (count bump)
- Dependencies: None

**Implementation sketch**:
1. Create `skills/learning-ci-headless/SKILL.md` covering: headless mode basics, `-p` flag usage, output formats (text/JSON/streaming), GitHub Actions integration, permission modes for CI
2. Include practical examples: PR reviewer workflow, test generator, changelog bot, doc updater
3. Reference the project's existing `scripts/quality-action/` as a real-world example
4. Include cost estimation guidance ($0.50/day for 10 daily calls at Sonnet rates)
5. Update docs (CLAUDE.md, README.md, test count)

**Effort**: Medium (1-2 days)
**Risk**: Low — additive skill, no existing code changes

**Sources**:
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless) — official docs
- [Headless Mode and CI/CD Cheatsheet](https://institute.sfeir.com/en/claude-code/claude-code-headless-mode-and-ci-cd/cheatsheet/) — SFEIR Institute
- [Headless Mode: Unleash AI in Your CI/CD Pipeline](https://dev.to/rajeshroyal/headless-mode-unleash-ai-in-your-cicd-pipeline-1imm) — practical guide

---

### 4. Agent Teams Orchestration Skill

**Category**: New skill
**Fills gap**: Yes — "Agent Teams" on Watch list, now available (experimental but widely discussed)
**Priority**: Medium-High
**Maturity**: Beta (experimental flag required, but actively used by community)

**What it is**:
A skill that teaches users how to orchestrate Agent Teams — multiple Claude Code instances coordinating on tasks. Covers: when to use teams vs subagents, team lead patterns, scope decomposition, cost management, and practical workflows (parallel debugging, cross-layer changes, research + implementation splits).

**Why it matters for this project**:
Agent Teams is the most talked-about Claude Code feature of Feb 2026. The community is actively sharing patterns (Addy Osmani's "Claude Code Swarms" post, multiple Medium articles). Your plugin's philosophy is "plan before code" and "small checkpoints" — Agent Teams is a natural extension where the team lead plans and teammates execute distinct scopes. Having a skill for this before it exits experimental positions you ahead of the curve.

**How it would integrate**:
- Where: `skills/meta-agent-teams/SKILL.md`
- Phase: Library Maintenance (meta skill) or Building & Implementing
- Existing code affected: CLAUDE.md, README.md, test count
- Dependencies: None (skill teaches the pattern; Agent Teams is built into Claude Code)

**Implementation sketch**:
1. Create `skills/meta-agent-teams/SKILL.md` covering: when to use teams, team composition, scope decomposition, communication patterns, cost awareness
2. Include concrete scenarios: frontend+backend+tests split, research+implement split, debugging with competing hypotheses
3. Warn about overhead — teams use significantly more tokens than single sessions
4. Document the enable flag: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

**Effort**: Medium (1-2 days)
**Risk**: Medium — feature is still experimental. Skill should be labeled as experimental and updated when API stabilizes.

**Sources**:
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams) — official docs
- [Claude Code Swarms](https://addyosmani.com/blog/claude-code-agent-teams/) — Addy Osmani's analysis
- [Agent Teams: Multi-Agent Coordination](https://bertomill.medium.com/tldr-agent-teams-multi-agent-coordination-in-claude-code-a73590d8453f) — community patterns
- [How to Set Up and Use Agent Teams](https://darasoba.medium.com/how-to-set-up-and-use-claude-code-agent-teams-and-actually-get-great-results-9a34f8648f6d) — practical guide

---

## Plan for Later

### 5. MCP Learning Module

**Category**: New skill
**Fills gap**: Yes — "MCP coverage" listed as uncovered in IMPLEMENTATION.md
**Priority**: Medium
**Maturity**: Production-ready ecosystem (10,000+ MCP servers, MCP Apps launched Jan 2026)

**What it is**:
A learning skill that teaches users how to connect Claude Code to external tools via MCP servers. Covers: what MCP is, how to configure servers, transport options (Streamable HTTP, stdio), common servers (GitHub, filesystem, databases), building custom MCP servers, and the new MCP Apps pattern for interactive UI.

**Why it matters for this project**:
MCP is the primary extension mechanism for Claude Code. The ecosystem has exploded to 10,000+ servers. Your plugin teaches development workflows (plan, build, review) but doesn't teach how to connect Claude to the tools users actually work with (databases, APIs, cloud services). This is the biggest content gap relative to what awesome-claude-skills catalogs — many of their 88 skills are essentially MCP integrations.

**How it would integrate**:
- Where: `skills/learning-mcp-servers/SKILL.md`
- Phase: Learning or Setup & Onboarding
- Could use `context: fork` + `learning-coach` agent for persistent progress tracking

**Implementation sketch**:
1. Cover MCP fundamentals: protocol, transports, tool discovery
2. Walk through connecting 3-4 common servers (GitHub, postgres, filesystem)
3. Show how to build a minimal custom MCP server
4. Discuss MCP Apps and when they're useful
5. Include troubleshooting patterns (tool search auto mode, context limits)

**Effort**: Medium (2-3 days)
**Risk**: Low — additive, large ecosystem to reference

**Sources**:
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) — official docs
- [Claude Skills vs. MCP: Technical Comparison](https://intuitionlabs.ai/articles/claude-skills-vs-mcp) — positioning guide
- [Extending Claude's capabilities with skills and MCP](https://claude.com/blog/extending-claude-capabilities-with-skills-mcp-servers) — Anthropic blog

---

### 6. Self-Improving Skill Pattern (Claudeception)

**Category**: Architecture pattern
**Fills gap**: No — new capability (meta-learning)
**Priority**: Medium
**Maturity**: Beta (community project, novel pattern)

**What it is**:
A pattern where a skill observes Claude Code's interactions and extracts reusable knowledge — essentially skills that improve themselves over time. The [Claudeception](https://github.com/blader/Claudeception) project demonstrates autonomous skill extraction and continuous learning. The [task-observer](https://github.com/BehiSecc/awesome-claude-skills) meta-skill on awesome-claude-skills builds and improves skills including itself.

**Why it matters for this project**:
Your `learning-coach` agent already has persistent memory. Extending this pattern to observe which skills get used, which workflows succeed, and what patterns emerge would make the plugin progressively smarter. This aligns with your "tutor mode for active learning" goal — the plugin learns alongside the user.

**How it would integrate**:
- Where: Enhancement to `learning-coach` agent or new `meta-self-improve` skill
- Leverages existing `PostToolUse` edit logging (`edit_log.txt`) as a data source
- Could track: skill usage frequency, workflow chains, common failures

**Implementation sketch**:
1. Add a `SessionEnd` or `PostToolUse` hook that logs which skills were invoked per session
2. Create a periodic analysis that reviews skill usage and suggests workflow improvements
3. Store observations in `learning-coach` agent memory for cross-session patterns

**Effort**: Large (3+ days)
**Risk**: Medium — novel pattern, may produce low-signal noise. Start minimal.

**Sources**:
- [Claudeception](https://github.com/blader/Claudeception) — autonomous skill extraction
- [task-observer on awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) — meta-skill pattern

---

### 7. Skill Description Optimization for Auto-Activation

**Category**: Enhancement to all existing skills
**Fills gap**: No — quality improvement
**Priority**: Medium
**Maturity**: Production-ready (community best practices established)

**What it is**:
Systematically rewriting the `description` field in all 22 skills' frontmatter to improve auto-activation rates. Research shows optimized descriptions can improve activation from 20% to 90%. The pattern is: capability statement + "Use when..." triggers + explicit keywords users might say.

**Why it matters for this project**:
Your skills are invoked via `/slash-commands`. But Claude Code's auto-activation uses the `description` field to decide when to suggest skills — and the community has found this is unreliable without explicit trigger phrases. Optimizing descriptions across all 22 skills would make the plugin feel more intelligent, especially when combined with recommendation #1 (skill-rules.json).

**How it would integrate**:
- Where: All 22 `SKILL.md` files — frontmatter `description` field only
- Existing code affected: Only frontmatter, not skill body
- Dependencies: None

**Implementation sketch**:
1. Audit all 22 skill descriptions for trigger phrase coverage
2. Add "Use when..." patterns with common user phrases
3. Add explicit keywords that should trigger each skill
4. Test activation rates before/after with common prompts

**Effort**: Small-Medium (half day, but touches all skills)
**Risk**: Low — only changes frontmatter metadata

**Sources**:
- [Claude Code Skills Structure and Usage Guide](https://gist.github.com/mellanon/50816550ecb5f3b239aa77eef7b8ed8d) — description optimization
- [How to Make Claude Code Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably) — community findings

---

## Watch

| # | What | Source | Why watching | Adopt when |
|---|------|--------|-------------|------------|
| 1 | **MCP Apps** (interactive UI from tools) | [MCP Jan 2026 release](https://claude.com/blog/extending-claude-capabilities-with-skills-mcp-servers) | Could enable dashboard-style skill outputs (quality scores, architecture maps). No skill use case clear yet. | When a specific skill would benefit from interactive output (e.g., quality-review score dashboard) |
| 2 | **CCPI Package Manager pattern** | [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | A CLI for installing individual skills from a collection. Interesting but adds complexity that conflicts with this project's "single coherent plugin" philosophy. | Only if the plugin grows beyond 40+ skills and users request à la carte installation |
| 3 | **AI agent delegation** | awesome-claude-skills (Jules, Deep Research, Manus skills) | Skills that delegate work to other AI services (Google Jules for coding, Gemini Deep Research for research). Novel but adds external dependencies. | When a specific workflow clearly benefits from multi-AI orchestration (e.g., research skill delegating to Perplexity) |
| 4 | **Document generation skills** | [anthropics/skills](https://github.com/anthropics/skills) (docx, pdf, xlsx, pptx) | Anthropic's official reference implementations. High quality but tangential to this project's focus on *development workflows*. | Only if users request documentation generation as part of session-wrapup or reporting workflows |
| 5 | **Conditional skill loading by file type** | [skill-rules.json pattern](https://github.com/diet103/claude-code-infrastructure-showcase) | Load skills based on file extensions being edited (e.g., `.py` → Python rules, `.ts` → TypeScript rules). Powerful but requires per-language skill variants. | After implementing recommendation #1 (skill-rules.json) — this is a natural extension |

---

## Skip

| # | What | Source | Why skipped |
|---|------|--------|------------|
| 1 | **Bulk skill collections** (claude-starter's 40 auto-activating skills, jeffallan's 65 skills) | awesome-claude-skills | Breadth-first approach conflicts with this project's opinionated, phase-organized design. Adding 40 generic skills would dilute the curated workflow value. |
| 2 | **Database-specific skills** (read-only postgres/mysql/mssql) | awesome-claude-skills | These are MCP server territory, not skill territory. The correct approach for database access is `mcp.json` configuration, not a skill. |
| 3 | **Domain-specific bundles** (marketing, health, scientific) | awesome-claude-skills (clawfu/mcp-skills, claude-ally-health, claude-scientific-skills) | Completely outside this project's scope. This plugin is domain-agnostic development workflows. |
| 4 | **Media generation skills** (video, audio, image) | awesome-claude-skills | Outside scope. This is a development workflow plugin, not a content creation tool. |
| 5 | **Token optimization formats** (TOON format from claude-starter) | awesome-claude-skills | Premature optimization. Current skill sizes are reasonable. If context pressure becomes an issue, revisit. |

---

## Strategic Sequence

**Theme 1: Discoverability & Distribution** — Make the plugin findable and skills load automatically

1. **Skill auto-activation via hooks** (#1) — Small effort, high impact. Users get relevant skills without memorizing slash commands.
2. **Publish to official marketplace** (#2) — Small effort, unlocks distribution. Once listed, the plugin is discoverable by 9,000+ marketplace users.
3. **Skill description optimization** (#7) — Amplifies #1. Better descriptions = better auto-activation even without hooks.

**Theme 2: Fill Coverage Gaps** — Address the three uncovered areas from IMPLEMENTATION.md

1. **Headless/CI mode skill** (#3) — High demand (60% of teams), fills stated gap, builds on existing quality-action work.
2. **Agent Teams skill** (#4) — Timely (hottest Claude Code topic of Feb 2026), positions ahead of curve.
3. **MCP learning module** (#5) — Largest content gap vs. ecosystem (10k servers, no coverage in this plugin).

**Theme 3: Intelligence Layer** — Make the plugin progressively smarter

1. **PreToolUse additionalContext** (already in IMPLEMENTATION.md as 1.2) — Foundation for context-aware hooks.
2. **Self-improving skill pattern** (#6) — Longer term, builds on learning-coach agent memory + edit logging.

---

## Synergies

- **#1 (skill-rules.json) + #7 (description optimization)**: Both improve discoverability — hooks for reliable activation, descriptions for LLM-based activation. Together they provide two redundant activation paths.
- **#1 (skill-rules.json) + #3 (headless/CI skill)**: The CI skill can teach users to invoke skills programmatically via `-p` flag, which pairs with auto-activation for non-interactive use.
- **#2 (marketplace) + #7 (descriptions)**: Better descriptions improve the plugin's listing quality in the marketplace — descriptions appear in search results.
- **#4 (agent teams) + #5 (MCP)**: Agent Teams can leverage MCP connections — teammates accessing different services in parallel. Teaching both creates a compound workflow.
- **#3 (headless) + existing weekly quality check**: The headless skill can reference `scripts/quality-action/` as a real-world example, making it concrete instead of abstract.

---

## What awesome-claude-skills Has That You Should NOT Copy

This is important context given your request. The awesome-claude-skills ecosystem (88 skills) is a **breadth play** — it catalogs everything from YouTube transcripts to genealogy research. Your plugin is a **depth play** — opinionated development workflows that chain together.

What to learn from them:
- **Listing presence matters** — Submit your plugin to awesome-claude-skills, awesome-claude-plugins, and the official marketplace
- **Security skills are highlighted** — Their VibeSec-Skill gets top billing. Your planned `safe-changes-security-review` (IMPLEMENTATION.md 2.1) aligns with market demand
- **Self-improving meta-skills** — The task-observer pattern is unique to their ecosystem and worth watching

What NOT to copy:
- Domain-specific skills (marketing, health, science) — stay development-focused
- Delegation to other AIs (Jules, Manus) — adds fragile external dependencies
- Bulk collections — your curation and phase organization IS the value

---

## Next Steps

1. [ ] **Implement skill-rules.json + UserPromptSubmit hook** (#1) — highest ROI, < 1 day
2. [ ] **Review marketplace submission requirements** (#2) and submit PR to [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
3. [ ] **Create `learning-ci-headless` skill** (#3) — fills biggest stated gap
4. [ ] Use `/planning-impl-plan` to design Agent Teams skill (#4)
5. [ ] **Optimize all 22 skill descriptions** (#7) after implementing #1
6. [ ] Submit to [awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) and [awesome-claude-plugins](https://github.com/Chat2AnyLLM/awesome-claude-plugins) for community visibility
7. [ ] **Implement PreToolUse additionalContext** (IMPLEMENTATION.md 1.2) — already planned, aligns with Theme 1
8. [ ] Use `/quality-upgrade-advisor` to check dependency versions before building new skills
