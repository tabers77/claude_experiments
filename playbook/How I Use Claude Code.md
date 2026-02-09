

**Personal Playbook (Senior DS / Software Engineer)**

---

TODO:
custom agents
CLAUDE tutor mode

> **Note (2026-02-06):** This playbook is the source of truth. Skills are now
> packaged as a Claude Code plugin (`claude-library`). Skill files live in
> `skills/<name>/SKILL.md` (hyphenated names, e.g. `architecture-arch`).
> Use via: `claude --plugin-dir /path/to/claude_experiments`
> Or locally: `bash setup-local.sh` to create .claude/skills/ links.

## Mental model: Understanding Claude Code's architecture

### The system model (updated): Memory + Skills + Prompts (+ Hooks/Subagents)

#### 1) Use **Project memory** for always-true team guidance
Prefer **project memory + modular rules**:
- `./CLAUDE.md` or `./.claude/CLAUDE.md` → the *index* (keep it short)
- `./.claude/rules/*.md` → topic files (testing, security, API), optionally path-scoped

Also available (don’t misuse):
- `CLAUDE.local.md` → private, per-project prefs (auto gitignored)
- `~/.claude/CLAUDE.md` + `~/.claude/rules/` → personal defaults across repos
- managed policy memory → org-wide constraints

Rule of thumb:
> Put *stable team invariants* in project memory; put *private/local* stuff in `CLAUDE.local.md`.

#### 2) Use **skills** for repeatable workflows (your “power tools”)
- Reusable checklists + output formats + procedures.
- Important safety knob: set `disable-model-invocation: true` for any skill that is stateful or dangerous (deploy/migrations).

#### 3) Use **plain prompting** for one-off thinking
Exploration, brainstorming, quick questions — until it earns a skill.

#### 4) Add **hooks** only for “must happen every time”
Hooks are deterministic automation (outside the LLM loop). Treat them like build tooling: minimal, auditable, fail-safe.

#### 5) Use **subagents** for isolation + parallelism
Offload noisy scans or specialized reviews to isolated contexts; restrict tools via allow/deny lists.

## 0. My core principle (read this first)

> **Claude is a junior engineer + reviewer + tutor — never an autopilot.**  
> I use Claude to **understand systems faster**, **reduce risk**, and **learn by implementing myself**.

If I feel Claude is “doing too much,” I switch to **planning, questioning, or tutor mode**.

---

## 1. Initial setup (per repository)

### 1.1 Project memory — index + modular rules (not “single source of truth”)

**Goal:** keep always-true guidance **team-shared and maintainable**.

**Recommended structure**
- `./.claude/CLAUDE.md` (or `./CLAUDE.md`): *short index*
  - repo purpose
  - how to run/test/lint
  - core conventions + invariants
  - pointers to deeper rule files
- `./.claude/rules/`:
  - `testing.md`, `api.md`, `security.md`, `style.md`
  - optional path scoping via frontmatter `paths:` when rules truly vary by area
- `CLAUDE.local.md`: private per-project notes (auto gitignored) for URLs, creds *references*, local test data, etc.

**Hard rule**
> If it changes often or is personal → it does **not** belong in team memory. Put it in `CLAUDE.local.md`.


### 1.2 Practical setup workflow

#### Step A — Create a tight `CLAUDE.md` (project rules only)

In your repo root:

1. Run `/init` (then edit what it generates).
2. Make it look more like this (copy/paste as a starting point):

```markdown
# CLAUDE.md (project guidance)

## Repo purpose
- This repo contains: (1) ML pipelines, (2) inference API service, (3) shared libs.
- Primary languages: Python. Runtime: Docker. Deployment: Azure.

## How to run locally
- Create venv: (your command)
- Install deps: (your command)
- Run service: (your command)
- Run pipelines: (your command)

## Quality gates (must follow)
- Formatting/lint: (ruff/black/etc) + how to run
- Tests: (pytest) + how to run a subset
- Type checks (if any): (mypy/pyright)

## Repo conventions
- Module layout:
  - src/... (or app/..., etc)
- Naming:
  - services live in ...
  - pipeline DAGs live in ...
- Logging & config:
  - use structured logging, config via env vars
- API conventions:
  - request/response models, error handling patterns

## Safety rules for changes
- Prefer small PR-sized diffs.
- Never change public API contracts without calling it out.
- If unsure: propose a plan before editing files.
```

This solves the "doesn't follow repo conventions" pain: you put the conventions in the one place Claude always reads.

#### Step B — Create your core skills

Make a folder: `.claude/skills/`

See section 2 below for the detailed skill templates.

---

## 2. My core skill set (used across most projects)

These are **reusable thinking procedures**, not prompts.

### 2.1 🔥 Architecture & understanding: `/arch_map`

**Purpose:** Build a mental model before touching code

**Why I use it:**
- Join large repos, legacy systems, or agent frameworks
- Never trust myself (or Claude) to refactor without a mental model
- Want **repeatable, comparable architecture summaries**

**What this skill enforces:**
- Entry points
- Control flow
- Boundaries
- Extension points
- Risk zones

**Skill template:** `skills/architecture-arch/SKILL.md`

```markdown
# Skill: arch
When user asks to understand architecture, do:

1) Ask what the target is:
   - "whole repo", "service", "pipeline", or "specific module"
2) Inspect codebase using search/grep and summarize:
   - entrypoints (CLI, FastAPI/Flask app, workers)
   - boundaries (packages, domains)
   - data flow (inputs -> transforms -> outputs)
   - runtime flow (requests, async jobs, schedulers)
3) Produce outputs in this exact format:
   A) 10-line overview
   B) Component map (bullets)
   C) Key execution paths (3-5 numbered flows)
   D) Critical files list (with paths)
   E) Risks / tech debt / unknowns
4) If refactor is requested:
   - propose 2 options (minimal vs ideal)
   - include verification plan (tests, perf checks)
```

**Output format:**
```
A) High-level overview (10 lines max)
B) Runtime flow (numbered)
C) Components & responsibilities
D) Key files (paths)
E) Where it's safe vs dangerous to change things
```

**Example usage:**
```
/arch_map Focus on:
- how agent teams are instantiated
- how tools are bound
- where orchestration decisions are made
- where a Composer could plug in safely
```

Or in terminal:
```
claude
/arch map the inference API service and show the main execution paths
```

---

### 2.2 🔥 Safe change & correctness: `/refactor_safe`

**Purpose:** Refactor like a senior reviewing a junior

**Why I use it:**
- Refactors are where AI causes the most damage
- I care more about _what must not change_ than what will
- Implements the "treat Claude like a junior engineer" approach

**What this skill enforces:**
- Explicit invariants
- Step-by-step plan
- Small diffs
- Verification after each step

**Skill template:** `skills/safe-changes-refactor-safe/SKILL.md`

```markdown
# Skill: refactor_safe

Goal: refactor without breaking behavior.

Process:
1) Restate the current behavior + constraints.
2) Identify invariants (inputs/outputs, performance constraints, API schema).
3) Propose a step-by-step plan with checkpoints:
   - checkpoint = code change + test or validation
4) Implement in small diffs.
5) After each checkpoint:
   - run existing tests or propose exact commands
   - if no tests exist, add minimal tests around the invariant
6) Provide a "review note" section:
   - what changed
   - why safe
   - what to watch in rollout
```

**Typical structure:**
```
1) Restate current behavior
2) List invariants (schemas, APIs, outputs, perf)
3) Propose plan with checkpoints
4) Implement incrementally
5) Verify after each checkpoint
6) Summarize risks
```

**Example usage:**
```
/refactor_safe
Goal: refactor the feature pipeline to reduce duplicate joins
Constraints:
- keep output schema identical
- add tests
```

Or:
```
/refactor_safe
Goal: Introduce a Composer module
Constraints:
- Existing /chat behavior must remain unchanged
- Existing agent teams must still load correctly
- No tool permissions widened implicitly
```

This is exactly the "engineers work properly" pattern: **plan → small change → verify → repeat**.

---

### 2.3 🔥 Safe change & correctness: `/impact_check`

**Purpose:** Understand blast radius before risky changes

**Why I use it:**
- Think in blast radius, not just correctness
- Especially critical in orchestration / agent routing code

**What this skill enforces:**
- Who/what might break
- What needs regression testing
- Rollback thinking

**Skill template:** `skills/safe-changes-impact-check/SKILL.md`

```markdown
# Skill: impact_check

When assessing change impact:
1) Identify directly affected components
2) Map indirect dependencies
3) Assess data/schema impact
4) Consider runtime/perf impact
5) Identify test gaps
6) Provide rollback strategy
```

**Output structure:**
```
- Directly affected components
- Indirect dependencies
- Data/schema impact
- Runtime/perf impact
- Test gaps
```

**Example usage:**
```
/impact_check
Change: Make workflows reusable and persisted
Focus on:
- Orchestrator behavior
- DB schema
- Agent instantiation lifecycle
```

---

### 2.4 🔥 From idea → implementation: `/spec_from_text`

**Purpose:** Turn vague input into a testable spec

**Why I use it:**
- Business language is ambiguous
- Specs are testable, diffable, reusable
- Never let Claude jump from **business text → code**

**What this skill enforces:**
- Structured outputs (YAML/JSON)
- Missing info surfaced early
- Separation of "what" from "how"

**Skill template:** `skills/planning-spec-from-text/SKILL.md`

```markdown
# Skill: spec_from_text

When converting free-form text to spec:
1) Parse requirements and constraints
2) Generate structured spec (YAML/JSON)
3) List assumptions made
4) Surface open questions
5) Identify implied constraints

Output format:
- structured spec
- assumptions
- open questions
- implied constraints
```

**Example usage:**
```
/spec_from_text
Convert this PM template into:
- BusinessCaseSpec
- Required capabilities
- Explicit constraints
```

This is foundational for **"business case → reusable workflow"** goals.

---

### 2.5 🔥 From idea → implementation: `/impl_plan`

**Purpose:** Design first, code second

**Why I use it:**
- Prevents "clever but wrong" implementations
- Allows human judgment before code is touched
- Forces Claude to plan before implementing

**What this skill enforces:**
- Files to change
- Order of changes
- Test strategy
- Stop points

**Skill template:** `skills/planning-impl-plan/SKILL.md`

```markdown
# Skill: impl_plan

When planning implementation:
1) Restate goal
2) Define non-goals
3) Break into steps (small, ordered)
4) Define tests per step
5) Provide rollback plan

Output format:
- Goal
- Non-goals
- Steps (small, ordered)
- Tests per step
- Rollback plan
```

**Example usage:**
```
/impl_plan
Design a Composer module that:
- parses BusinessCaseSpec
- selects agents
- binds MCP tools
- persists workflow
- runs via existing orchestrator
```

---

### 2.6 🔥 API Implementation: `/api_impl`

**Purpose:** Implement inference endpoints consistently

**Why I use it:**
- Enforces API conventions (models, errors, logging, config)
- Ensures consistent patterns across endpoints
- Considers docker/runtime requirements

**What this skill enforces:**
- Request/response models
- Validation + clear errors
- Structured logs + trace IDs
- Timeouts, retries if calling downstream

**Skill template:** `skills/api-development-api-impl/SKILL.md`

```markdown
# Skill: api_impl

When implementing an inference endpoint:
1) Ask for: route, request schema, response schema, latency budget, model location.
2) Ensure:
   - request/response models
   - validation + clear errors
   - structured logs + trace IDs
   - timeouts, retries if calling downstream
3) Provide:
   - handler code
   - unit tests
   - update to OpenAPI/docs
   - docker/runtime notes if needed
4) End with "how to test locally" commands.
```

**Example usage:**
```
/api_impl
Route: /predict/sentiment
Request: {"text": str}
Response: {"sentiment": str, "confidence": float}
Latency: <200ms p95
```

---

**Summary:** These six skills cover **80% of my daily work**.

---

## 3. Learning-first workflow (critical for long-term independence)

### `/codebase_mastery` (with Tutor Mode)

I use this when:

- onboarding to a new codebase
    
- understanding a critical file
    
- preparing to implement features myself
    

**Two modes**

#### A) Deep Dive mode

- structured understanding
    
- call graphs
    
- invariants
    
- extension points
    

#### B) Tutor mode (my default for learning)

- Claude asks **me** questions about the code
    
- I answer
    
- Claude corrects with evidence
    
- I get **micro-exercises** to implement myself
    

> If I’m passively reading output, I switch to Tutor mode.

---

## 4. Project quality & technical debt

### `/quality-review`

Purpose: **calibrated judgment, not fake precision**

It gives me:

- a provisional score (0–100)
- confidence level (high / medium / low)
- evidence (file paths, tests, tools run)
- design quality (patterns, boundaries)
- test quality (not just presence)
- security signals
- top risks
- next 3 PR-sized improvements

**Rule**

> Scores without evidence or confidence are ignored.

### Full skill template: `skills/quality-review/SKILL.md`

```markdown
# Skill: project_review

Goal: Evaluate the repository quality and provide a scored report with evidence.

Rules:
- Be evidence-based: cite file paths and brief observations.
- If you did not run a check (tests/lint/typecheck), explicitly state that.
- Use a provisional 0–100 score with category breakdown and weights.
- Provide prioritized improvements (top 10) and the next 3 PR-sized actions.

Process:
1) Identify project type: library/service/pipeline/monorepo.
2) Gather evidence:
   - list key files: README, pyproject/requirements, Dockerfile, CI config
   - locate tests and test framework
   - search for lint/type tools
   - identify entrypoints, dependency injection, config approach
3) Run (if allowed):
   - unit tests (pytest)
   - lint (ruff/flake8)
   - typecheck (mypy/pyright)
4) Score categories:
   A Build & Run (10)
   B Code Organization (10)
   C Correctness & Testing (25)
   D Maintainability (15)
   E Reliability & Observability (10)
   F Security & Safety (10)
   G Performance (10)
   H Design & Architecture (10)
5) Output format:
   - Summary (10 lines)
   - Score breakdown table
   - Evidence highlights (paths)
   - Top risks (5)
   - Improvements (top 10)
   - Next 3 PRs (scoped, with files & commands)

If any category cannot be assessed, mark as "unknown" and reduce confidence.
```

**How to use it:**

```
# Fast review:
/quality-review run tests if possible; focus on test quality and architecture boundaries

# Security-sensitive:
/quality-review do not run commands; static review only
```

---

## 5. Decision support & prioritization

### Risk prioritization (now part of `/quality-review` Phase 2)

I use this when:

- planning refactors
    
- reviewing architecture changes
    
- deciding what _not_ to fix
    

It helps me answer:

- what matters most?
    
- what can wait?
    
- what is risky vs noisy?
    

---

## 5.5 Decision rules (updated): Memory vs Skill vs Hook vs Subagent vs One-off prompt

### Choose **project memory** (CLAUDE.md + .claude/rules/) when:
- Claude should *always* know it in this repo (run commands, invariants, conventions)
- It’s stable + team-shared
- You want path-scoped rules (e.g., API rules only under `src/api/**`)

**Anti-rule:** Don’t put procedures here. Memory is guidance, not a workflow engine.

### Choose a **skill** when:
- You’ll do it ≥3 times OR you want a standard output format
- You want a repeatable procedure (refactor-safe, architecture map, review checklist)
- You want an *invocable* workflow (`/review`, `/deploy`)

**Safety:** Set `disable-model-invocation: true` for stateful/dangerous skills (deploy, migrations). Require explicit `/skill-name`.

### Choose a **hook** when:
- Something must happen every time with **zero exceptions**
- It’s deterministic and auditable (format, lint gate, block edits in a folder)

**Default stance:** observe/notify first; automate second.

### Choose a **subagent** when:
- You need isolation (large scans, repo-wide grep, dependency mapping)
- You want parallel workstreams (security + perf + style) without polluting main context
- You want stricter tool access via allow/deny lists

### Choose a **one-off prompt** when:
- You’re exploring / learning / still designing the checklist
- The “right procedure” is not known yet
- You want tutor behavior instead of execution

### Quick examples (pattern matching)

- “Claude keeps forgetting how to run tests in this repo.”
  - ✅ Project memory: add command to `.claude/CLAUDE.md`
  - ❌ Not a skill (it’s not a workflow; it’s a fact)

- “I keep doing the same safe refactor procedure.”
  - ✅ Skill: `/refactor_safe`
  - ❌ Not a hook (you don’t want automation; you want a guided checklist)

- “Every PR must pass `pnpm lint`.”
  - ✅ Hook: run `pnpm lint` (or notify) on relevant event
  - ❌ Not a skill (too easy to forget to invoke)

- “I need a repo-wide scan for ‘where auth is enforced’.”
  - ✅ Subagent: isolate scan + cite paths back to main thread
  - ❌ Not main thread (it will flood context and reduce learning)

- “I’m unsure what approach to take.”
  - ✅ One-off prompt in tutor mode: ask for options + tradeoffs + invariants first

---

## 6. My standard Claude Code session flow

### A) New repo / unfamiliar area

1. `/architecture-arch`
2. `/learning-codebase-mastery tutor`
3. Small manual change + run tests

### B) Refactor or feature work

1. `/planning-spec-from-text` (if input is vague)
2. `/planning-impl-plan`
3. `/safe-changes-impact-check`
4. `/safe-changes-refactor-safe`

### C) Quality & debt assessment

1. `/quality-review` (assessment + prioritization in one skill)

---

## 6.5 Practical session recipes (detailed workflows)

### Recipe 1 — Architecture comprehension (fast + consistent)

In Claude Code:

1. `/arch focus on the realtime inference service. give component map + key execution paths + critical files`
2. Follow-up: "Now list 5 highest-risk refactor points and why."
3. Then: `/refactor_safe` with a very narrow target.

**This recipe ensures:**
- Understanding before action
- Risk-aware refactoring
- Small, verifiable changes

### Recipe 2 — Refactor without chaos

1. `/refactor_safe goal: reduce latency in preprocessing by 20% without changing outputs`
2. You (as reviewer) enforce:
   - "show me exact files you will edit"
   - "what tests prove no behavior change?"
3. Only then let it touch code.

This is the "Claude is a junior dev" model in practice: **you demand a plan, you demand invariants, you demand verification**.

### Recipe 3 — Setup that fits your use-case (architecture → refactor → implement)

**Step A — Create a tight CLAUDE.md (project rules only)**

See section 1.2 above for the detailed template.

**Step B — Create skills that match your day-to-day**

See section 2 above for the six core skills.

**Step C — Use decision-log approach**

Instead of a monolithic `plan.md`, use a lightweight `docs/decision-log/` folder:

- `docs/architecture.md` (generated/maintained with `/arch`)
- `docs/refactors/<date>-<topic>.md` (plan + checkpoints + results)

You still get the benefit of planning, but **scoped to the change**, not a monolith.
    

---

## 7. Decision rules (stop/go gates)

### Patch fast vs Plan + Verify
**Patch fast** if ALL true:
- change is ≤ 1 file or trivially reversible
- invariant is obvious (e.g., typo, rename with compiler help)
- you can run a tight check immediately (unit test / typecheck / lint)

Otherwise: **Plan + Verify**
- write invariants first
- list files to touch
- define checkpoints (each ends in a command or concrete validation)

### When to switch to Tutor mode
Switch to Tutor mode if any are true:
- I can’t explain the call flow in my own words
- I’m reading outputs passively (no predictions, no hypotheses)
- the change touches invariants I don’t understand yet (auth, money, permissions, migrations)

Tutor mode rule:
> Claude asks me questions first; I answer; then Claude corrects with evidence (paths, snippets, commands).


---

## 8. What I deliberately do _not_ do

- I don’t let Claude refactor blindly
    
- I don’t trust scores without confidence
    
- I don’t automate learning
    
- I don’t put workflows into `CLAUDE.md`
    
- I don’t let Claude explore the whole repo unless I ask
    

---

## 9. How I know I’m using Claude well - Weekly calibration checklist (anti-atrophy)

Run this weekly (10 minutes). If you answer “yes” to any, apply the corrective action immediately.

1) Did I accept a multi-file change without reading diffs?
- Fix: next session, require “plan + checkpoints” and review each diff chunk.

2) Could I explain the main execution path *without* Claude?
- Fix: do a 5-minute recall writeup (entrypoint → core modules → outputs). Only then ask Claude to verify.

3) Did I skip writing/confirming invariants (schemas, API contracts, perf budgets)?
- Fix: add a mini “invariants” header to the PR/notes; retrofit 1–2 focused tests.

4) Did I let Claude run commands I didn’t anticipate?
- Fix: tighten permissions/sandbox; add an “ask-first for stateful commands” rule.

5) Am I using skills as a crutch for understanding?
- Fix: invoke tutor mode; make myself do the first implementation step manually.

6) Did I overuse repo-wide scans that I didn’t read?
- Fix: move scans to a subagent + require a citation-style summary (paths + why relevant).

7) Did my CLAUDE.md/.claude/rules grow messy?
- Fix: split by topic; delete stale rules; keep the index short.

8) Did I automate anything “must happen every time” without audit logs?
- Fix: revert; re-add as observe/notify hook first for a week; only then enforce.

---
## 10.  Automation safety: Hooks, permissions, sandboxing (make it boring)

### What hooks are for (and what they are NOT for)
Hooks are deterministic scripts triggered on lifecycle events.
Use them only when something must happen **every time**.

**Good first hooks (low risk)**
- notify/log on tool requests or edits
- run lint/format in read-only or “check” mode
- block edits in protected paths (migrations, infra, prod configs)

**Avoid by default**
- auto-approving stateful commands (git push, rm, migrations, deploy)
- hooks that silently rewrite files
- hooks that depend on flaky network services

### Rollout pattern (guardrail)
1) **Observe**: hook only logs/notifies for 1 week
2) **Constrain**: sandbox boundaries (filesystem + network) for autonomous work
3) **Enforce**: only then add blocking or auto-actions, and keep them narrow

### If you want more autonomy, prefer sandboxing over approvals
- Put Claude in a sandbox with explicit FS/network boundaries.
- Outside the sandbox: always ask.


## Quick project setup (Claude Code) — 30 minutes, learning-first

> Goal: get *fast, safe, and educational* on day 1 without building a big “agent system”.

### 0) Prereqs (2 min)
- Install + login (once per machine). See official quickstart if needed.
- Start in repo root:
  - `claude`

**Stop point:** don’t ask for changes yet. First we map + set invariants.

---

### 1) First 10 minutes: map the repo before touching code
Use one-off prompts (tutor-ish):
- “What does this project do? Cite file paths.”
- “Where is the entry point? Show call flow in 5 bullets with filenames.”
- “What are the top 3 invariants I must not break (tests, contracts, data)?”
- “What’s the fastest ‘tight loop’ command set (test/lint/typecheck)?”

**Guardrail:** if Claude can’t cite paths, ask it to search again and point to exact files.

---

### 2) Create minimal project memory (10 min)
Create these files (start tiny; expand only after repeated friction):

1) `.claude/CLAUDE.md` (index, ~20 lines) (> “Run `/init` first to scaffold files, then immediately trim `CLAUDE.md` into a short index.”)
Include:
- **Commands:** test / lint / format / typecheck (exact commands)
- **3 invariants max:** e.g., “No API breaking change without version + docs update”
- **Pointers:** to rule files

Example skeleton:
- “Run tests: `make test`”
- “Format: `make fmt`”
- “Invariant: schemas in `src/api/schema.ts` are source of truth”
- “See rules: `.claude/rules/testing.md`”

2) `.claude/rules/testing.md` (one topic file)
Include:
- where tests live
- what “done” means
- 1–2 conventions (table tests, naming, integration vs unit)

Optional (only if you *already* know you need it):
- `.claude/rules/security.md` with `paths:` scoping for `src/auth/**` or `src/payments/**`

3) `CLAUDE.local.md` (private notes, gitignored)
Include:
- local setup quirks
- local URLs
- “fast dev loop” commands
- anything you don’t want in git

**Stop point:** re-open Claude session and ask:
- “Summarize my repo rules back to me in 6 bullets; if anything is missing, ask questions.”

---

### 3) Set safe defaults (5 min)
In Claude Code:
- run `/config` and verify you understand what’s enabled at project vs global level.

Decision rule:
- if a workflow can mutate prod/infra/secrets → it must require explicit invocation (no auto).

---

### 4) First change workflow (5–15 min): “plan + verify” by default
Before edits, ask:
- “Propose 2 approaches + tradeoffs.”
- “List invariants + tests to add.”
- “Show a checkpoint plan (each checkpoint ends in a command).”

Then execute in small diffs:
- Checkpoint 1: smallest safe change + run the tight loop
- Checkpoint 2: add/adjust test
- Checkpoint 3: refactor/cleanup

**Guardrail:** if the change touches auth/payments/migrations → switch to tutor mode and require manual review of diffs.

---

### 5) Add your first skill only after repetition (optional day 1)
If you just did a refactor/debug flow you’ll repeat ≥3 times:
- create ONE skill: `/refactor_safe` or `/impact_check`
- keep it procedural (checklist + output format), not a giant policy doc

Safety rule:
- any stateful/dangerous skill (deploy/migrate/rotate keys) must be hidden from auto-invocation and run only explicitly.

---

### 6) Don’t automate yet (hooks come later)
Week 1: only “observe” hooks (log/notify), no silent edits, no auto-approval.
Week 2+: consider enforcement hooks for protected paths only.
