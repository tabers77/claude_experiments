# Self-Learning Skills — Design Doc

A pattern for Claude Code skills that **improve their own SKILL.md based on real runs**. Each skill keeps a local `run_history.json` ledger of categorical failure modes; when a counter trips its threshold, the skill auto-edits its body per a stored `remediation_hint`. The git diff is the safety net.

This doc captures the pattern, the schema, the invariants, and how to author one manually. A future `meta-self-learning-skill-gen` skill will automate the generation step.

## Why

Most agent self-improvement work either:
- Reflects in freeform prose (Reflexion-style) — drifts, can't be deduplicated.
- Searches over prompt candidates (DSPy/MIPROv2-style) — needs a metric and an eval set.
- Refines via LLM-as-judge offline (MLflow EDD-style) — separates evals from production runs.

This pattern is different on three axes:
1. **Tagged, not freeform.** Every failure mode is a stable categorical tag with a threshold. Tags accumulate occurrences over runs and trip remediation deterministically.
2. **Online, not offline.** Production runs *are* the eval set. The user is the judge.
3. **Self-edits SKILL.md, not weights or external prompts.** The skill is its own artifact; remediation is a text edit; rollback is `git revert`.

The closest published analog is **LangMem's procedural memory refinement** + **Voyager's growing skill library with self-verification**, but neither targets Claude Code's SKILL.md format or uses tag/threshold mechanics.

## The five invariants

These are what make the pattern work. Every self-learning skill must honor them:

1. **Categorical FAIL tags, not freeform reflection.** `<phase>-<failure-mode-slug>`, stable forever. Tags accumulate occurrences correctly across runs; freeform reflections don't.
2. **Threshold tiering by phase severity.** Load-bearing=1, procedural=2, cosmetic=5. This encodes a Bayesian prior on whether a failure deserves a structural change to the SKILL.md.
3. **Verbatim evidence requirement.** The audit phase cannot paraphrase user input or claim a tool ran without observing the call. `audit-paraphrased-user-input` and `tool-claim-without-call` are themselves tracked FAIL tags — the audit polices the audit.
4. **Auto-apply with git as safety net.** No review queue. Remediation edits the SKILL.md immediately; the user catches bad remediations in their normal commit-review loop.
5. **Per-skill local ledger.** No central state to corrupt. Each skill is its own evolving artifact; lessons don't propagate across skills (intentional — keeps blast radius bounded).

## The architecture

A self-learning skill is a regular Claude Code skill folder with two extra ingredients (three when the optional observer is included):

```
skills/<name>/
├── SKILL.md              # Domain phases (1..N-2) + standardized audit (N-1) + ledger (N) [+ observer (N+1) optional]
├── run_history.json      # Persistent ledger: schema v1 (audit + ledger own this file)
├── observations.json     # OPTIONAL: observer's qualitative ledger (observer phase owns this file)
└── suggestions.md        # OPTIONAL: observer's clustered proposals queue (human-reviewed)
```

The skill's flow:

```
Phase 0       : OPTIONAL — Freshness check (non-blocking nudge when stale + well-used)
Phase 0.5     : Run plan (greenfield/describe only; non-skippable) — reuse/adapt/skip/create over the baseline
Phase 1..N-2  : Domain work (your custom phases — the "baseline")
Phase N-1     : Pre-action self-audit (verbatim evidence, FAIL detection, run-plan reconciliation, approval gate)
Phase N       : Update run-history ledger (append run, increment counters, trip remediation, persist run_plan)
Phase N+1     : OPTIONAL — Observer (qualitative signals, cross-run clustering, suggestion-only)
```

Phases N-1 and N are **standardized** across all self-learning skills. Phase 0.5 is **always-on** for greenfield/describe-generated skills and **absent** in convert-mode (fixed-sequence) skills. Phase N+1 is **optional** — include it when the skill would benefit from a second vantage that catches what the audit's mechanical FAIL detection cannot. The domain phases are 1 through N-2.

## Per-run adaptive execution (Phase 0.5 run plan)

Greenfield- and describe-generated skills are **adaptive**: instead of marching the same fixed phase sequence every run, a non-skippable `Phase 0.5` reads the user's request and builds a **run plan** before any domain phase fires. This is always-on DNA (no interview toggle), exactly like the timing and composition instrumentation. **Convert-mode-retrofitted skills are the one exception** — they stay fixed-sequence so their existing phase order is preserved byte-identical.

**The run-plan model.** Phase 0.5 does four things: (1) quote the user's request verbatim; (2) start from the **baseline** — the domain phases (1..N-2) fixed at generation time, never a blank slate; (3) classify each baseline step as **reuse** / **adapt** (with a one-line `how`) / **skip** (with a one-line `justification` + the step's `tier`), and add **created** steps only when the run genuinely needs work the baseline doesn't cover; (4) emit the plan to run state.

**Non-skippable machinery.** Phase 0.5, the audit, and the ledger can never appear in `run_plan.skipped[]`. Domain steps may be skipped, but **never silently**:
- **Load-bearing** baseline steps may be skipped only with a substantive justification.
- **Procedural/cosmetic** steps skip freely — still recorded.

**Audit reconciliation (the load-bearing change).** The audit walks the run plan, not a fixed phase list: one row per *executed* step (reuse/adapt/create) and one **skip-justification row** per *skipped* baseline step. Two new FAIL rules (load-bearing, threshold=1) enforce it:
- `plan-silent-skip` — a baseline step is absent from both executed rows and skip rows.
- `plan-skipped-load-bearing-step-without-justification` — a load-bearing skip has an empty/placeholder justification.

**Persistence + signal.** The ledger writes `run_plan` into the run's `runs[]` entry (optional field; fixed-sequence skills omit it). This gives the observer real cross-run signal: a baseline step skipped on most runs is a demote candidate (`baseline_step_rarely_used`); a `created` step that recurs is a promote-into-baseline candidate (`recurring_created_step`). Both stay suggestion-only — neither the planner nor the observer auto-edits the baseline.

Template: `library/templates/self-learning-skill/run-plan-phase.md` (the Phase 0.5 body to inline). The generator (`meta-self-learning-skill-gen`) inlines it in Step 8a (sub-step 1.45) for greenfield/describe and skips it entirely in convert mode.

## The observer phase (optional, suggestion-only)

The audit catches *what was told to be tracked* (predefined FAIL tags, deterministic detection, auto-apply). The observer catches *what wasn't*: user friction, redundant phases, scope drift, signs of audit blind spots. It runs **after** the ledger, sees the post-remediation state of `SKILL.md`, and writes only to two new files:

- `observations.json` — append-only ledger of qualitative signals per run (one entry per signal).
- `suggestions.md` — clustered proposals written when ≥3 observations share a category; human-reviewed.

The observer's primary value is **cross-run pattern detection** — themes invisible in a single run become visible once `observations.json` accumulates. It NEVER auto-edits `SKILL.md`; that asymmetry with the audit is deliberate (qualitative judgment is lower-confidence than mechanical detection).

| Aspect | Audit (Phase N-1) | Observer (Phase N+1) |
|---|---|---|
| Detection | Mechanical (deterministic FAIL rules) | Qualitative (LLM judgment) |
| Vantage | Per-run | Cross-run + per-run |
| Confidence | High | Lower |
| Action | Auto-edit `SKILL.md`; git diff is review | Write proposal to `suggestions.md`; user reviews |
| Rollback | `git revert` | Mark `Status: dismissed` |

Full template + schema:
- `library/templates/self-learning-skill/observer-phase.md` — the phase body to inline.
- `library/templates/self-learning-skill/observations_schema_v1.md` — schema for `observations.json` and the `suggestions.md` proposal format.

### Coupling and the planned decoupling path

The observer is currently bolted into the host skill as Phase N+1 — a deliberate prototype choice to keep the change surface small and let the pattern prove itself before we invest in infra. If the observer demonstrates value across multiple skills (real proposals get applied, false-positive rate stays low), the planned next step is to **lift it out** into one of:

1. A standalone `meta-observer-review` skill that the user invokes manually after a run, reading any skill's `observations.json` independently.
2. A `Stop` hook that captures the run automatically and writes the observation entry without needing host-skill cooperation.

Authors should treat the observer body as **movable, not load-bearing in its current location**. The schema (`observations.json` + `suggestions.md`) is the load-bearing contract — the phase body is just the prototype carrier.

## The freshness check (Phase 0, optional, non-blocking)

The audit + ledger catch mechanical drift *inside* a run. They don't catch the slower, quieter failure where the **skill's own design** falls behind — Claude Code adds features the skill never adopts, a peer skill grows into overlapping territory, the domain it automates evolves. That kind of rot has no per-run signal; it only becomes visible when someone deliberately steps back and looks.

Phase 0 surfaces that signal automatically.

**Premise**: a skill that has been **both well-used and unreviewed** for a while is overdue for revalidation. Phase 0 prints a one-line nudge when both conditions trip simultaneously, and is silent otherwise.

### Behavior

1. Phase 0 reads `validation_freshness` from `run_history.json`. It does not write.
2. It computes `days_since_validated` and `runs_since` from the block.
3. The nudge fires **only when both** `days_since_validated >= thresholds.days` (default 21, ≈3 weeks) **AND** `runs_since >= thresholds.runs` (default 10).
4. When the nudge fires, the skill prints a one-line pointer to `/meta-discover-claude-features` and `/meta-skill-audit`, then continues to Phase 1.
5. When the nudge does not fire, Phase 0 prints **nothing**. Silence is the success state; affirmations would erode the nudge's signal value over time.
6. Phase 9 (ledger) increments `runs_since_validation` by 1 every run. The user resets it manually by appending a `review_log[]` entry — the skill never self-certifies freshness.

### Why AND-gated (not OR)

`OR` would nudge cold skills (lots of days, no usage → no load) and hot-recent skills (lots of runs, already validated last week → no new signal). `AND` keeps the nudge tied to **skills the user actually relies on AND has had time to drift away from** — exactly the population where rot causes harm.

### Why non-blocking

A hard gate would teach users to disable the check. Revalidation is a deliberate review activity, not something to steal 30 seconds for mid-incident. The signal comes from accumulating staleness pressure across runs, not from one forced stop.

### What "validation" means

When the user appends a `review_log[]` entry, they certify they:
1. Considered whether the skill's design still matches current Claude Code features / community patterns (`type: "research"`, e.g. via `/meta-discover-claude-features`).
2. Confirmed the skill isn't silently overlapping a peer skill (`type: "overlap"`, e.g. via `/meta-skill-audit`).

Either alone is partial; both is `type: "both"`. Any non-empty review resets the counter — a partial pass is better than none.

### Coupling with the rest of the pattern

The freshness check is **structurally independent** of the audit, ledger, suggestion capture, and observer. It only requires `run_history.json` and a Phase 0 slot. The ledger phase writes the counter increment; everything else about freshness is user-driven via manual JSON edits to `review_log[]`.

The freshness body is **movable** in the same sense as the observer: a future `meta-skill-freshness-sweep` skill could read every `run_history.json` in the plugin and report all stale skills at once. The schema (`validation_freshness` block) is the load-bearing contract; the per-skill Phase 0 body is the current prototype carrier.

## Efficiency tracking (always-on instrumentation)

The audit + ledger catch correctness drift; the observer catches design drift; the freshness check catches review-cycle drift. The fourth dimension is **efficiency drift** — the skill takes longer than necessary for the quality it delivers — and unlike the other three, it can't be detected from any single run. You need to compare runs against each other on the same input class, and you need a quality signal to ensure speed wins aren't paid for in correctness.

This is the most important property a skill optimizes for: **achieve the objective in less time without compromising quality**. Every speed gain must be tied to a quality delta, or the skill is just racing to fast trash.

### Instrumentation captured every run (no toggle)

| Field | Stamped by | Used for |
|---|---|---|
| `started_at` | First phase (Phase 0 if present, else Phase 1) | Run duration baseline |
| `phase_durations[<id>]` | Each phase, on exit | Per-phase timing for observer's category-specific signals |
| `ended_at`, `duration_seconds` | Ledger phase | Total wall-clock |
| `quality_derived` | Ledger phase (mechanical compute) | Denominator for trade-off comparison |
| `sentiment` on each captured suggestion | Suggestion-capture block (keyword heuristic) | Feeds `quality_derived` |

All five fields are OPTIONAL in the schema — pre-instrumentation runs simply opt out of efficiency analysis. The observer ignores them, never coerces absence to a positive signal.

### Quality is derived, not asked

There is deliberately no explicit "rate this run 1–5" prompt at audit-time. The signal we need — *did this run achieve the user's objective?* — is already implicit in two existing channels:

- **`outcome` + `phases_failed[]`** — closed with zero FAILs is the mechanical pass.
- **Sentiment of `improvement_suggestions[]` captured during the run window** — a suggestion classified `negative` (keywords: *broken, wrong, missed, failed, bug,* etc.) means the user is flagging a problem with this run. `aspirational` and `neutral` don't count against quality.

The ledger combines them into one of four rolled-up values:

| `quality_derived` | Condition |
|---|---|
| `clean` | closed + 0 FAILs + 0 negative suggestions in this run's window |
| `partial` | closed + (FAILs OR negative suggestions) |
| `failed` | aborted |
| `incomplete` | paused / in-progress |

Sentiment classification is a **conservative keyword heuristic** — negative wins only when no aspirational keyword also matches. The user can hand-edit `sentiment` in `run_history.json` if the heuristic misclassifies; the skill never re-evaluates a captured suggestion.

### The trade-off detector

In the observer phase (Phase N+1), step 2a clusters prior runs by input-class similarity (e.g., `scope=lite` vs `scope=full` for `pr-merge-readiness`) and computes the cohort median duration. A run files an observation when **both** are true:

- Wall-clock deviates by >1.5× the median (slow run) OR <0.5× the median (fast run)
- Quality moved in the *wrong* direction relative to the cohort (slow + not-better, or fast + worse)

Slow-but-better runs and fast-but-equal runs are NOT observations — they're just variance. Tying every speed delta to a quality delta is what prevents the optimization from collapsing into "drop the careful checks for speed."

### Five efficiency-focused observer categories

Added to the standard category table:

- `phase_scope_too_broad_for_input` — full-scope routine ran when input class justified narrower
- `serializable_as_parallel` — sequential phases with no data dependency between them
- `redundant_work_with_prior_phase` — work recomputed from an earlier phase
- `over_thorough_for_input_class` — heavy phase ran on tiny input; skill lacks input-class dispatch
- `missed_cached_result` — work whose result already exists in `runs[]` for the same shape

The observer's clustering threshold (default 3) and theme-similarity check apply unchanged — these new categories just feed it richer signals.

### Why efficiency proposals stay suggestion-only

`fail_counters` remediations auto-apply because they say *do MORE checking* — worst case is added noise. Efficiency remediations say *do LESS work* — worst case is silently dropping a check that was load-bearing for an input class the skill hasn't seen yet. Asymmetric risk. Suggestion-only mode keeps the human in the loop precisely where the asymmetry lives.

## Composition: parent and child skills

Self-learning skills can call other self-learning skills. The naïve composition — child fires every phase including freshness and observer — produces noise (two nudges per user-facing run) and split signal (two `observations.json` files cluster on disjoint subsets of the same run). The protocol below avoids both without weakening anyone's audit.

### The `invocation_mode` arg

When a parent invokes a child via the Skill tool, it passes a single semicolon-separated arg string:

```
invocation_mode=composed; parent=<parent-skill-name>; parent_run_ts=<iso8601 of parent's started_at>
```

The child parses this at run start (before Phase 0 fires). When absent or set to anything other than `composed`, the child defaults to `invocation_mode=standalone` and behaves as it does when invoked directly by the user.

### Which phases skip when composed

| Phase | Composed behavior | Reason |
|---|---|---|
| Phase 0 — Freshness | **Skipped** (body only; `started_at` still stamps) | Parent's freshness phase is the user-facing nudge; one per user-facing run is enough |
| Domain phases | **Fire unchanged** | The work the user invoked the parent for |
| Timing instrumentation | **Fires unchanged** | Both ledgers benefit from per-phase durations |
| Audit | **Fires unchanged** | Audit is load-bearing; never skipped under any condition |
| Ledger | **Fires unchanged**; records `invocation_mode`, `parent`, `parent_run_ts` | Child's history accumulates regardless of how it was invoked |
| Observer | **Skipped** when composed | Parent's observer is the single cross-run pattern detector for this user-facing run; child's observer fires on standalone invocations only |

The split is principled: **load-bearing phases never skip** (audit, ledger, timing); **user-facing surfaces skip** (freshness nudge, observer) because the parent owns the user-facing layer.

### Sentiment ownership when composed

A suggestion captured while inside the child's phase belongs to the **child's** `improvement_suggestions[]` only. There is exactly one source of truth — never duplicate across two skill files; that makes manual edits ambiguous.

The parent's ledger phase looks up the child's suggestions cross-file when computing `quality_derived` for the parent's run: it reads each composed child's `run_history.json`, filters entries where `parent == this_parent` AND `parent_run_ts == this_parent.started_at`, counts negative-sentiment matches, and folds them into the parent's roll-up. Single-write, dual-read.

If a child's file is unreachable when the parent reads it (file missing, parse error), the parent logs the friction to its own `friction_log[]` and proceeds — never blocks the ledger write on a missing child.

### Why composed child observer cross-run analysis still has runway

A natural concern: if `smart-test-selection` is mostly invoked composed (inside `pr-merge-readiness`), its observer rarely runs — does it lose its self-learning loop?

Answer: the observer only fires on **standalone** invocations of the child. But standalone runs still happen — for ad-hoc test-list debugging, CI invocations, or any future skill that calls the child differently than `pr-merge-readiness` does. When standalone, the observer sees the **entire** `runs[]` array including all composed runs. The composition fields (`invocation_mode`, `parent`) let it filter the cohort intentionally — e.g., "give me median duration of standalone runs only" vs. "give me median across all runs." The child accumulates cross-run pattern data continuously; only the *observer pass* is deferred to standalone moments, which keeps the user-facing surface clean.

### Why the protocol lives in the templates (not per-skill)

The `invocation_mode` parsing, the conditional skips, and the cross-skill sentiment lookup all live in the template files (`freshness-phase.md`, `observer-phase.md`, `ledger-phase.md`, `suggestion-capture.md`, `run_history_schema_v1.md`). Generated skills inherit the protocol automatically; convert-mode retrofits land it on existing skills the same way. There is no per-skill flag to flip — the protocol is DNA, like timing and sentiment.

## The schema

`run_history.json` is the persistent ledger. Full schema documented at:

→ `library/templates/self-learning-skill/run_history_schema_v1.md`

Headline shape:

```json
{
  "version": 1,
  "fail_counters": {
    "<tag>": {
      "count": 0,
      "threshold": 1,
      "phase": "audit",
      "description": "...",
      "occurrences": [{"ts": "...", "target": "...", "detail": "..."}],
      "remediation_hint": "...",
      "applied_at": null
    }
  },
  "runs": [{"ts": "...", "target": "...", "outcome": "closed", "phases_failed": ["<tag>"]}],
  "friction_log": []
}
```

## Universal seed FAIL rules

Every generated self-learning skill ships with these three tags pre-populated (count=0). They apply to any skill that interacts with a user via tool calls:

| Tag | Phase | Threshold | What it catches |
|---|---|---|---|
| `audit-paraphrased-user-input` | audit | 1 (load-bearing) | Audit row paraphrases user intent rather than quoting verbatim. |
| `audit-no-explicit-approval-wait` | audit | 2 (procedural) | Skill advanced past a user-gate without observing the literal approval token. |
| `tool-claim-without-call` | any | 1 (load-bearing) | SKILL.md text claims a tool/skill ran but no corresponding call was observed. |

Domain-specific tags accumulate from real runs. Don't pre-invent tags you can't currently detect mechanically — they'll drift.

## How to author a self-learning skill (manual route)

Until `meta-self-learning-skill-gen` exists, follow this checklist:

### 1. Decide the basics
- **Skill name** (kebab-case, matches folder).
- **Terminal action** — commit / deploy / doc-edit / test-pass.
- **Approval token** — the literal string the user must type to advance past the audit (e.g. `audit approved`, `commit`, `deploy now`).
- **Load-bearing principle** — the one rule the skill must never violate. This is the north star for tier classification.

### 2. Sketch the domain phases
Aim for 5–10 phases. Each needs:
- Trigger (what activates it).
- Exit condition (what evidence proves it ran).
- Evidence shape that maps to an audit row.

For phases that consume user input, the evidence shape **must** include a verbatim quote slot.

### 3. Pick threshold tiers per phase
For each phase, classify load-bearing / procedural / cosmetic. This determines the threshold for any FAIL tag that lands in that phase.

### 4. Generate the skill folder
Copy `library/templates/self-learning-skill/SKILL.md.tpl` to `skills/<name>/SKILL.md`. Fill in the placeholders. Where the template says "Insert here: the body of audit-phase.md / ledger-phase.md", literally inline the body of those files with placeholder substitutions.

Initialize `skills/<name>/run_history.json` from the "Initial state" snippet in `run_history_schema_v1.md`.

### 5. Validate the structure
Run through this checklist (also embedded at the bottom of `SKILL.md.tpl`):

- [ ] `run_history.json` exists, initialized with the three universal seed tags.
- [ ] Audit phase (Phase N-1) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every user-input phase records input verbatim.
- [ ] Terminal action requires the literal approval token.
- [ ] Threshold tiers match phase severity.
- [ ] Ledger phase is the last phase.

### 6. Smoke run
Invoke the skill on a real task. Verify:
- Audit phase fires before the terminal action.
- Audit lists every phase with evidence.
- Approval gate blocks the terminal action until you type the literal token.
- Ledger phase writes `run_history.json` correctly.

### 7. Iterate from real runs
Don't pre-invent domain FAIL rules. Run the skill on real tasks; when a failure mode emerges, add a new tag with the appropriate threshold. The pattern's whole point is that real runs surface the right rules over time.

## Worked example

`shared-bug-gap-fix` (in the `intelligence-platform` repo) is the reference implementation. Phases 1–7.5 are domain work; Phase 8 is the audit; Phase 10 is the ledger (Phase 9 is the closure commit, sandwiched between audit and ledger because the commit is the terminal action). Its `run_history.json` shows three real remediations applied:

- `8.2.5-no-approval-wait` → restructured Phase 8/9 so commit cannot fire without literal token.
- `9-paraphrased-user-input` → tightened audit to mandate verbatim quotes; added `9-paraphrased-user-input` as a self-tracking FAIL.
- `6-routing-too-coarse-for-trivial-fix` → added Phase 5.5 (test-scope analysis) governing Phase 6.

Each remediation was applied automatically, reviewed in the user's normal commit flow, and reset the counter. The pattern works.

## The research checkpoint (L1/L2 levels, orchestration, freshness coupling)

The freshness check (Phase 0) is **passive** — it nudges the user when a skill is stale and well-used, but does nothing itself. The `meta-research-checkpoint` skill is its **active counterpart**: a suggestion-only, cadence-based sweep that actually does the research and resets the counter.

**Two levels** (Level 3 — normal, non-self-learning skills — is explicitly out of scope):
- **Level 1 — the meta layer.** Targets `meta-self-learning-skill-gen`, the `library/templates/self-learning-skill/*` template set, and this design doc. Orchestrates `/meta-discover-claude-features` (new Claude Code capabilities the pattern could adopt) + `/meta-skill-audit` (overlap) + `/quality-strategic-advisor` (pattern-level ideas).
- **Level 2 — each generated self-learning skill.** Enumerates skills with `metadata.pattern: self-learning` (or a sibling `run_history.json`), selects those **due** by the `validation_freshness` AND-gate (or `--all`/`--skill` to force), and for each orchestrates `/meta-discover-claude-features` + `/quality-upgrade-advisor` scoped to that skill's domain + `/meta-skill-audit`.

**Orchestration, not reimplementation.** The checkpoint invokes the repo's existing research skills (passing `invocation_mode=composed` so their own freshness/observer phases don't double-fire) and only falls back to raw web search for gaps. Findings aggregate into `documentation/RESEARCH_CHECKPOINT.md` (dated, append-only sections, each citing the source skill).

**Freshness coupling closes the loop with zero new per-skill state.** After researching an L2 skill, the checkpoint appends a `validation_freshness.review_log[]` entry (`type: research`), sets `last_validated_at`/`last_research_at`, and resets `runs_since_validation` to 0. The freshness check opens the loop ("you're overdue"); the checkpoint satisfies it ("here's the research, counter reset"). These three writes (the report, the freshness reset, and optional observer `suggestions.md` proposals) are the **only** things the checkpoint writes — it never edits a skill's SKILL.md, frontmatter, or logic.

**Cadence:** primarily on-demand (`/meta-research-checkpoint [--level 1|2|all] [--all] [--skill <name>]`); optionally scheduled via the `schedule` skill (cron). The AND-gate keeps scheduled runs cheap — fresh skills are skipped.

## What's NOT in this design

Decisions deliberately kept simple at v1:

| Out of scope | Why | Future option |
|---|---|---|
| Cross-skill learning | Each skill is its own RL agent. Lessons in one skill don't propagate. | A shared `meta/fail-rules.json` registry could be added later if patterns repeat. |
| Frontmatter / description auto-edits | Wrong keywords could mis-route. Body-only edits are safer and recoverable. | Could be opted in per-skill once we trust the body-edit cycle. |
| Bayesian search over remediation candidates | Adds optimization complexity and a metric requirement. The deterministic threshold-trip is interpretable and good enough. | DSPy-style optimization could be layered on if remediations become combinatorial. |
| Eval set / replay traces | Production runs *are* the eval. The user is the judge. | If quality plateaus, an offline replay harness could be added without disturbing the pattern. |
| Approval queue for remediations | Adds friction, slows iteration. Git diff is the review mechanism. | Could be added per-skill if a skill keeps producing bad remediations. |

## Open questions for v2

- **Ledger pruning.** `occurrences[]` will grow unbounded over years. Recommendation: keep last 20 per tag + rolling stats. Not yet enforced.
- **Tag retirement.** When a remediation is auto-applied, the tag stays in the file with `applied_at` set. Should retired tags be moved to a separate `retired_tags` section after some period?
- **Schema evolution.** When v2 schema lands, what's the migration path? Auto-upgrade on read, or require manual? Currently the schema doc says "skills must refuse to write a file whose version they don't recognize" — that's safe but pushes migration to the user.

These don't block v1. Surface them when they matter.

## References

- Voyager (Wang et al., 2023) — growing skill library with self-verification: https://arxiv.org/abs/2305.16291
- Reflexion (Shinn et al., 2023) — verbal reflection in episodic memory: https://arxiv.org/abs/2303.11366
- Self-Refine (Madaan et al., 2023) — intra-task iterative refinement: https://arxiv.org/abs/2303.17651
- LangMem — procedural memory refinement, productized: https://www.letta.com/blog/agent-memory
- Anthropic — Building Skills for Claude (PDF guide): https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
- DSPy MIPROv2 — Bayesian search over prompt candidates (contrast with deterministic threshold approach): https://dspy.ai/api/optimizers/MIPROv2/

## Templates in this repo

- `library/templates/self-learning-skill/SKILL.md.tpl` — full SKILL.md template
- `library/templates/self-learning-skill/run-plan-phase.md` — run-plan boilerplate (Phase 0.5, ALWAYS-ON for greenfield/describe)
- `library/templates/self-learning-skill/freshness-phase.md` — freshness boilerplate (Phase 0, OPTIONAL, default opt-in)
- `library/templates/self-learning-skill/audit-phase.md` — audit boilerplate (Phase N-1)
- `library/templates/self-learning-skill/ledger-phase.md` — ledger boilerplate (Phase N)
- `library/templates/self-learning-skill/observer-phase.md` — observer boilerplate (Phase N+1, OPTIONAL)
- `library/templates/self-learning-skill/run_history_schema_v1.md` — `run_history.json` schema reference + bootstrap JSON
- `library/templates/self-learning-skill/observations_schema_v1.md` — `observations.json` schema + `suggestions.md` format
- `library/templates/self-learning-skill/suggestion-capture.md` — mid-run user-suggestion capture block
