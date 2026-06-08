# Plan — Describe-Mode Generation, Per-Run Adaptive Skills, and a Multi-Level Research Checkpoint

**Status:** IMPLEMENTED (2026-06-08). Parts A, B, C + doc/test sync landed. Open items resolved — see §7.
**Scope:** extends `meta-self-learning-skill-gen` and the self-learning skill pattern.
**Author flow:** drafted interactively; awaiting approval before implementation.

---

## 1. Goals (as agreed)

Three additions, kept independent so they can land and be reviewed in sequence:

- **Part A — Describe-mode generation (additive).** A new dispatch mode where the user *describes the problem and expectations in natural language*; the system qualifies it, gap-fills adaptively, and then funnels into the existing build engine. The current fixed interview stays intact as a separate mode.
- **Part B — Per-run adaptive execution in generated skills.** Every adaptive skill **always starts from the baseline phase set fixed at generation time**, then on each run decides per step: **reuse / adapt / skip / create**, based on the user's prompt. Skips are never silent — the audit records a justification row for each skipped baseline step.
- **Part C — Multi-level research checkpoint.** A cadence-based, suggestion-only checkpoint that, for **Level 1 (the meta generator + the pattern/templates)** and **Level 2 (each generated self-learning skill)**, *orchestrates the repo's existing research skills* and aggregates their findings into per-level improvement suggestions. **Level 3 (normal skills) is explicitly out of scope.**

### Locked decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Describe-mode: replace or add | **Add** as a third dispatch mode (greenfield-interview + convert + describe) |
| 2 | Per-run adaptivity model | **Always start from the generation-time baseline**; per run reuse/adapt/skip/create from it |
| 3 | Skip auditability | Every skipped baseline step gets an explicit **skip-justification audit row**; load-bearing skips require justification |
| 4 | Research checkpoint scope | **L1 + L2 only**; L3 dropped |
| 5 | Research checkpoint implementation | **Orchestrate existing skills** (`/meta-discover-claude-features`, `/quality-upgrade-advisor`, `/quality-strategic-advisor`, `/meta-skill-audit`); web search only for gaps |

---

## 2. Part A — Describe-mode generation

### 2.1 How it's triggered

Extend Step 1 ("Detect starting point") dispatch:
- `describe <free-text>` → new **Describe Mode** (Steps D1–D4 below).
- `convert <path>` → unchanged.
- `improve <name>` → unchanged (still "not supported in v1").
- empty / no subcommand → unchanged greenfield interview (default preserved).

Also add a `skill-rules.json` trigger so a prose problem statement auto-suggests `describe` mode, but never auto-runs it (suggestion only, consistent with the existing activation hook).

### 2.2 Describe-mode steps

Describe mode is a **smarter front-end that produces the exact same internal variable set** the greenfield interview collects (`SKILL_NAME`, `LOAD_BEARING_PRINCIPLE`, terminal action, approval token, inputs, domain phases + tiers, FAIL rules, composition), then **reuses Steps 6.5 → 7 → 8 → 9 → 10 unchanged**. No duplication of the build engine.

- **D1 — Capture intent verbatim.** Record the user's problem statement + expectations *verbatim* (this becomes the first audit-able artifact; never paraphrase).
- **D2 — Qualify.** Reuse the convert-mode eligibility logic (Step C2's six criteria) adapted to a *description* rather than an existing SKILL.md:
  - clear terminal action? identifiable repeatable phases? a load-bearing rule? consumes user input? deterministic (not pure Q&A)? stable/repeated enough to be worth auditing?
  - Print a scorecard + verdict. **Not a fit** → stop and recommend a normal (non-self-learning) skill instead, explaining the strongest blocker. **Borderline** → surface gaps, ask whether to continue.
- **D3 — Adaptive gap-fill loop.** Infer as many generation variables as possible from the description, then ask **only for what's missing or ambiguous**, looping until complete. Each inferred value is shown as **proposed** (user accepts/edits); each unknown is **needs-input**. This is the "ask until we have enough" behavior — driven by the gap set, not a fixed script.
- **D4 — Hand off to the build engine.** Run Step 6.5 (composition discovery) → Step 7 (`generate` confirmation gate) → Step 8 (build) → Step 9 (validate) → Step 10 (smoke-test guidance). Adaptive-execution toggle (Part B) defaults **on** for describe-generated skills.

### 2.3 Files touched (Part A)

- `skills/meta-self-learning-skill-gen/SKILL.md` — add Describe Mode section (Steps D1–D4) + dispatch line in Step 1.
- `skill-rules.json` — add a describe-mode suggestion trigger.

---

## 3. Part B — Per-run adaptive execution in generated skills

This is the foundational change — it modifies the **templates**, so every adaptive skill inherits it regardless of which mode generated it.

### 3.1 The run-plan model

A new always-on (when the toggle is set) phase is added near the front of every adaptive skill:

> **Phase 0.5 — Understand this run's expectations & build the run plan**
> (numbered `0.5` to sit between the freshness check at Phase 0 and domain Phase 1 **without renumbering domain phases** — keeps phase-keyed FAIL tags stable.)

It does exactly four things:
1. Read and quote the user's request verbatim.
2. **Start from the baseline** = the domain phases fixed at generation time. Never a blank slate.
3. Classify each baseline step: **reuse** (run as-is), **adapt** (run, modified for this run's intent), or **skip** (with a one-line justification). Add **created** steps only when the run genuinely needs work the baseline doesn't cover.
4. Emit the run plan to in-memory run state for the audit and ledger to consume.

**Never skippable:** Phase 0.5 (planning), the audit, and the ledger. These are the machinery, not domain work. **Load-bearing baseline steps** may be skipped *only* with an explicit justification; procedural/cosmetic steps skip freely (still recorded).

### 3.2 Audit reconciliation (the load-bearing change)

Today `audit-phase.md` emits **one row per domain phase**, and the generator validates a fixed row count. With adaptivity, the audit instead walks the **run plan**:

- One row per **executed** step (reused / adapted / created) — same verbatim-evidence rules as today.
- One **skip-justification row** per **skipped baseline step**: `- Phase X [skipped] | reason: "<justification>"`.
- A baseline step that appears in **neither** the executed rows **nor** the skip rows is a **silent skip** → automatic FAIL.

Two new FAIL rules seeded into the audit template (and `run_history.json` initial state) for adaptive skills:

| Tag | Tier | Threshold | Detection |
|---|---|---|---|
| `plan-silent-skip` | load-bearing | 1 | A baseline step is absent from both executed rows and skip rows. |
| `plan-skipped-load-bearing-step-without-justification` | load-bearing | 1 | A load-bearing baseline step is in the skip set with an empty/placeholder justification. |

### 3.3 Schema change (`run_history_schema_v1.md`)

Add an **optional** `run_plan` object to `runs[]` entries (backward-compatible, like the timing fields):

```json
"run_plan": {
  "baseline_steps": ["1","2","3"],
  "reused":  ["1"],
  "adapted": [{"step":"2","how":"<one line>"}],
  "skipped": [{"step":"3","justification":"<one line>","tier":"procedural"}],
  "created": [{"step":"3b","why":"<one line>"}]
}
```

This gives the observer real signal: a baseline step skipped on most runs → propose demoting/removing it; a created step that recurs → propose promoting it into the baseline. (Observer stays suggestion-only.)

### 3.4 Generator validation change (Step 9)

- Check 3 ("audit row count == domain phase count") becomes toggle-aware: when adaptive execution is on, validate instead that the audit phase contains the **run-plan walk** instruction and **skip-justification handling**, and that `plan-silent-skip` + `plan-skipped-load-bearing-step-without-justification` are seeded in `run_history.json`.
- New check: Phase 0.5 exists, is non-skippable, and precedes domain Phase 1; audit + ledger remain non-skippable.

### 3.5 Toggle vs. always-on

**RESOLVED → always-on DNA (no toggle).** Per decision 7.1, adaptivity is universal for greenfield/describe-generated skills, exactly like the timing/composition instrumentation — there is no `adaptive_execution_enabled` interview question. The escape hatch for "I want a rigid fixed-sequence skill" is **convert mode** (decision 7.5), which never adds Phase 0.5. Implemented via the dedicated `run-plan-phase.md` template inlined at Step 8a sub-step 1.45.

### 3.6 Files touched (Part B)

- `library/templates/self-learning-skill/SKILL.md.tpl` — add Phase 0.5 block; note non-skippable invariants.
- `library/templates/self-learning-skill/audit-phase.md` — run-plan walk + skip-justification rows + 2 new FAIL rules.
- `library/templates/self-learning-skill/ledger-phase.md` — write `run_plan` into the `runs[]` entry.
- `library/templates/self-learning-skill/run_history_schema_v1.md` — document optional `run_plan`; add the 2 FAIL tags to "Initial state" (adaptive skills only).
- `library/templates/self-learning-skill/observer-phase.md` — add categories: `baseline_step_rarely_used` (skip-heavy step), `recurring_created_step` (promote candidate).
- `skills/meta-self-learning-skill-gen/SKILL.md` — Step 5.x interview toggle; Step 8 inlining of Phase 0.5; Step 9 validation updates.

---

## 4. Part C — Multi-level research checkpoint

### 4.1 New skill: `meta-research-checkpoint`

Suggestion-only. Never auto-edits any skill. Output is a report plus entries in existing per-skill ledgers.

**Levels:**
- **Level 1 — the meta layer.** Targets: `meta-self-learning-skill-gen/SKILL.md`, the `library/templates/self-learning-skill/*` template set, and `documentation/SELF_LEARNING_SKILLS.md`. Orchestrates `/meta-discover-claude-features` (new Claude Code capabilities the pattern could adopt) + `/meta-skill-audit` (overlap) + `/quality-strategic-advisor` (pattern-level ideas).
- **Level 2 — each generated self-learning skill.** Enumerate skills with `metadata.pattern: self-learning` (or a sibling `run_history.json`). For each, orchestrate `/meta-discover-claude-features` and `/quality-upgrade-advisor` scoped to that skill's domain + `/meta-skill-audit` for overlap.

### 4.2 Reuse the freshness block as the "due" oracle

The existing `validation_freshness` block already answers *"is this skill stale?"* via the AND-gate (`runs_since_validation >= thresholds.runs` AND `days >= thresholds.days`). The checkpoint:
- Selects L2 skills that are **due** by that same gate (or `--all` to force).
- After researching a skill, **appends a `review_log[]` entry** (`type: research`) and **resets `runs_since_validation` to 0** — this is the *active counterpart* to the passive Phase 0 nudge. Freshness check = "you're overdue"; checkpoint = "here's the research, counter reset."

This closes the loop cleanly with zero new per-skill state: the freshness check opens it, the checkpoint satisfies it.

### 4.3 Cadence

- Primary: on-demand — `/meta-research-checkpoint [--level 1|2|all] [--all]`.
- Optional scheduled cadence via the existing `schedule` skill (cron) — documented, not baked in.

### 4.4 Output

- `documentation/RESEARCH_CHECKPOINT.md` — per-level aggregated suggestions (dated, append-only sections), citing which orchestrated skill produced each finding.
- For L2 skills with an observer, optionally append proposals to that skill's `suggestions.md` queue so they flow through the existing human-review path.

### 4.5 Files touched (Part C)

- `skills/meta-research-checkpoint/SKILL.md` — new skill.
- `skill-rules.json` — activation trigger.
- (Output dir) `documentation/RESEARCH_CHECKPOINT.md` — created on first run.

---

## 5. Documentation & test sync (required by repo rules)

- `documentation/SELF_LEARNING_SKILLS.md` — new sections: "Per-run adaptive execution (run-plan model + audit reconciliation)" and "The research checkpoint (L1/L2 levels, orchestration, freshness coupling)".
- `CLAUDE.md` — Available Skills table (+`meta-research-checkpoint`), directory tree, Architecture notes.
- `README.md` — mirror the same.
- `tests/test_skills.py` — bump expected skill count by 1. **Verify actual count first** (see open item 7.2).

---

## 6. Implementation sequence

1. **Part B (templates + schema + generator validation).** Foundational — both describe mode and the checkpoint assume it.
2. **Part A (describe dispatch mode).** Reuses the build engine; emits adaptive skills by default.
3. **Part C (`meta-research-checkpoint`).** Independent; couples to the freshness block.
4. **Docs + tests sync.** In the same change set per repo rule 7.
5. **Smoke test:** generate one skill via describe mode, run it twice with different prompts to exercise reuse/skip/create + skip-justification audit rows; run the checkpoint at `--level 1` and against one L2 skill.

---

## 7. Open items — RESOLVED (2026-06-08)

- **7.1 Adaptive toggle vs. always-on.** → **ALWAYS-ON DNA** (no toggle) for greenfield/describe, like timing/composition. Implemented via a dedicated `run-plan-phase.md` template inlined at Step 8a.45. Locked decision #2 superseded accordingly.
- **7.2 Skill-count discrepancy.** → Resolved. Empty `skills/log-decision/` (no SKILL.md, an accidental scaffold) was **deleted**. True count is **29** (greenfield/describe/convert + the new `meta-research-checkpoint`, with `pr-merge-readiness`/`smart-test-selection` that were already present but undocumented). `tests/test_skills.py` floor bumped 26 → 29; CLAUDE.md header and table updated to 29.
- **7.3 Phase numbering.** → **Phase 0.5** (no renumbering of domain phases — keeps FAIL-tag phase keys stable).
- **7.4 Checkpoint output destination.** → Central `documentation/RESEARCH_CHECKPOINT.md` (append-only) + optional observer `suggestions.md` feed for L2 skills that have an observer.
- **7.5 Convert mode.** → Convert stays **fixed-sequence** (no Phase 0.5, no run-plan reconciliation in the audit, no `run_plan` in the ledger, no `plan-*` FAIL tags). The shared `audit-phase.md`/`ledger-phase.md`/schema carry the adaptive blocks; greenfield/describe keep them, convert strips them (Steps C6.3/C6.4/C6.8, C7).
