# Observer retrospective — `pr-merge-readiness`

**Purpose**: a paper test of the proposed observer phase against `pr-merge-readiness`'s existing `run_history.json`. The question this memo answers: *would the observer have surfaced anything beyond what the existing audit + mid-run-suggestion-capture already caught?*

If yes, the observer has marginal value — proceed to a live re-run with the phase scaffolded in.
If no, the prototype is redundant noise — pull back.

**Sources read**:
- `skills/pr-merge-readiness/run_history.json` (2 closed runs, both GREEN, 0 FAIL tags tripped, 2 mid-run improvement suggestions captured at audit time)
- `skills/pr-merge-readiness/SKILL.md` (9 phases — domain 1–7, audit 8, ledger 9)

## Existing-system baseline (what was already captured)

| Mechanism | What it caught | Evidence |
|---|---|---|
| Audit FAIL counters | Nothing — 0 trips across 2 runs | All 9 seeded counters at `count: 0` |
| `runs[].notes` | Rich qualitative narrative per run (verbatim) | Both runs include 2–4 sentence notes citing specific commands, paths, counts |
| `improvement_suggestions[]` | 2 user-typed suggestions during run 2's audit phase | `5-impl-vs-tracker-check`, `8-audit-table-format` |
| `friction_log[]` | Empty | Schema present but never written |

The audit machinery is sound — both runs hit GREEN with the existing FAIL rules and the user explicitly confirmed approval (`merge approved` verbatim). No mechanical drift to fix.

The interesting surface area is what the audit was **never told to look for**.

## Themes the observer would have surfaced

### Theme A — Dev-stack staleness friction (cross-run, would-cluster-at-3)

**Pattern:** Both runs encountered stale-container-missing-dependency friction before the live UI tier could run. Run 2's `notes` field explicitly cross-references run 1: *"same root-cause class as the 2026-05-07 run"*.

**Verbatim evidence:**
- Run 1 (2026-05-07): *"Phase 4 live UI case 1 sales_negotiator_db_only PASSED 310.21s after dev-stack rebuild (stale container missing fastapi-azure-auth dep — dep correctly declared on the branch)."*
- Run 2 (2026-05-08): *"Phase 4 after backend image rebuild (stale container had been missing fastapi-azure-auth + new pyproject per-file-ignore; same root-cause class as the 2026-05-07 run)"*

**Observer classification:** `dev_env_friction`, count = 2 → below the default cluster threshold (3) but above the noise floor.

**Why audit missed it:** there is no FAIL rule for "the dev container was stale." It's an environmental concern, not a SKILL.md logic concern. The audit was never designed for it.

**Observer's recommended action at this point:**
- Record both observations in `observations.json` under category `dev_env_friction`.
- Do NOT yet write to `suggestions.md` (below threshold).
- Append to `run_history.json:friction_log[]` — that's exactly what `friction_log` is for, and the schema is in place but currently unused. The observer would notice that gap and act on it.

**At a third run with the same theme:** observer trips threshold, writes to `suggestions.md` proposing either (a) a stale-container preflight in Phase 4 (compare image's installed-deps vs. branch's `pyproject.toml`), or (b) an explicit `friction_log` entry with mitigation options.

### Theme B — Implementation-vs-tracker drift (single-run, user-confirmed, high-signal)

**Pattern:** Run 2 surfaced a tracker-file inconsistency the existing diff-anomaly check (Phase 5 step 4) caught only because `BUGS_AND_GAPS.md` was in the configured `TRACKER_FILES`. The user *separately* typed a suggestion in the audit phase asking for this to run by default.

**Verbatim evidence:**
- Observer signal (run 2 notes): *"tracker-file diff anomaly surfaced — diff did not touch BUGS_AND_GAPS.md despite COMPLETED_STREAMS.md adding closure narratives for W-7-prep-c, V-L2, V-L3, SP-7"*
- User suggestion (run 2 audit): *"before surfacing actions in Phase 7, verify what was actually implemented in the branch matches the documentation tracker (BUGS_AND_GAPS.md). This implementation-vs-docs check should run by default as part of Phase 5, not be skipped."*

**Why this is the strongest observer signal in this dataset:** the qualitative observation (extracted by the observer) and the explicit user suggestion (captured by the existing mid-run protocol) **converge on the same theme**. When two independent channels agree, the proposal is high-confidence even at count = 1.

**Observer classification:** `missing_audit_category`, with `proposed_audit_tag: "5-tracker-closure-without-row-removal"` — this *is* mechanically detectable: when any path in `TRACKER_FILES` adds closure-narrative tokens (`Closed`, `Stream complete`, etc.) without a corresponding row-deletion in `BUGS_AND_GAPS.md`, mark FAIL. Observer would propose this as a new audit FAIL tag, not just a SKILL.md prose edit.

**Observer's recommended action:** write to `suggestions.md` immediately despite count = 1, **referencing both the observation and the matching `improvement_suggestions[]` entry**. The convergence overrides the cluster-of-3 default — that's an authoring rule worth adding to `observer-phase.md`: "single observation + matching `improvement_suggestions[]` entry = high-confidence proposal, write immediately."

> **Authoring note for the template:** consider adding this convergence rule explicitly to `observer-phase.md` step 4 ("clustering check"). Two independent channels confirming = ≥ 3 same-channel observations confirming.

### Theme C — Output format quality (user-only, below threshold)

**Pattern:** Run 2 user suggestion: *"render the Phase 8 audit rows as a markdown table (columns: Phase, Status, Evidence) instead of a bulleted 'Phase X [pass] | <evidence>' list — much more readable when evidence strings are long"*.

**Observer classification:** `output_format_quality`, count = 0 (this is user-typed, not observer-extracted). Observer would *not* count it as its own observation but **would reference it** if a future observation in the same category emerged (e.g., observer notices an evidence string runs > 200 chars in run 3's audit).

**Why this matters for the design:** the observer's value isn't to replicate `improvement_suggestions[]` — it's to identify when its own qualitative scans **align with** existing user suggestions, raising confidence. This memo confirms that path is real (Theme B is the worked example).

### Theme D — Skipped-test rationale (cross-run, low-signal)

**Pattern:** Both runs report non-zero skipped test counts without a recorded "why":
- Run 1: not reported in detail (live UI was the focus)
- Run 2: *"smoke 401 passed / 1 skipped, targeted 7 passed / 4 skipped"*

**Observer classification:** `missing_audit_category`, count = 1 — observer would record but not yet propose. The audit doesn't surface skip rationale because no FAIL rule covers it.

**At threshold:** observer would propose a Phase 4 sub-step that captures `pytest --co -q -m skipped` rationale per skipped test, or a config block to opt out per project.

### Theme E — Pre-existing-vs-regression check (cross-run, procedural)

**Pattern:** Run 2 explicitly notes the user did a manual "is this lint failure new?" check: *"ruff scoped to changed files = 4 errors (...) verified pre-existing on origin/dev → not regressions"*. The audit didn't surface this — the user did it on their own, manually.

**Observer classification:** `missing_audit_category`, count = 1 → recorded, below threshold.

**At threshold:** propose a Phase 3 sub-step that runs lint on `origin/<BASE_BRANCH>` first and diffs against `<head>`'s lint output, mechanically distinguishing pre-existing from regression-introduced findings.

## Cross-channel convergence summary

| Theme | Observer category | Observer count | User suggestion match | Confidence |
|---|---|---|---|---|
| A. Dev-stack staleness | `dev_env_friction` | 2 | None | Medium (cross-run) |
| B. Tracker drift | `missing_audit_category` | 1 | YES (`5-impl-vs-tracker-check`) | **High (convergence)** |
| C. Audit table format | `output_format_quality` | 0 | YES (`8-audit-table-format`) | Low (user-only) |
| D. Skipped-test rationale | `missing_audit_category` | 1 | None | Low |
| E. Lint pre-existing check | `missing_audit_category` | 1 | None | Low |

## What the observer would have written for these 2 runs

**`observations.json` after run 2:** ~5–7 entries (Themes A×2, B×1, D×1, E×1, plus possibly 1–2 more from finer-grained scanning).

**`suggestions.md` after run 2:** **1 proposal** — Theme B, written despite count = 1 because of channel convergence. Proposed addition: a new audit FAIL tag `5-tracker-closure-without-row-removal` with mechanical detection conditions, plus a Phase 5 sub-step running it.

**`run_history.json:friction_log[]` after run 2:** 1 entry written by the observer for Theme A (`dev_env_friction` doesn't belong in `suggestions.md` because no SKILL.md edit fixes a stale container — it belongs in `friction_log` per the existing schema's intent).

## Verdict on the prototype

**Proceed to the live re-run.** The retrospective surfaces three concrete value points the audit could not have caught:

1. **Theme B is high-confidence already** — convergence between the observer's qualitative scan of run notes and the user's explicit suggestion. The observer would have written a proposal at run 2, several runs ahead of when the user themselves would have escalated.
2. **Theme A demonstrates `friction_log` discovery** — the schema field exists but is unused; observer's existence creates a writer for it. That's a structural improvement to the self-learning pattern as a whole.
3. **Convergence-rule authoring insight** — Theme B revealed a template-level improvement to `observer-phase.md` itself: *single observation + matching `improvement_suggestions[]` = treat as ≥ threshold*. This rule would be hard to derive without doing the retrospective, and is now in this memo to be folded into the template before the live re-run.

## Adjustments to fold into `observer-phase.md` before the live re-run

1. **Convergence rule** — append to step 4 (clustering check): *"if observer records ≥1 observation in a category AND `improvement_suggestions[]` contains an entry matching the same theme, treat as cluster-tripped regardless of `{{CLUSTER_THRESHOLD}}`."*
2. **`friction_log[]` writer path** — extend step 8's hard limits: observer MAY append to `run_history.json:friction_log[]` (and only that field) when the observation category is `dev_env_friction`. This is an exception to "never write to `run_history.json`" — narrow, justified, prevents unused-schema rot.
3. **`observations.json` initial state in this skill** — when the live re-run starts, scaffold `observations.json` with the 5–7 retrospective observations as seed entries (back-dated `ts` matching the original run timestamps, `run_ref` matching the existing `runs[]`). This bootstraps the cross-run pattern detection rather than starting from zero.

These three adjustments are small enough to apply before scaffolding the observer into `pr-merge-readiness`. The first two are template-wide; the third is skill-specific bootstrap.

## Out of scope for this memo

- Modifying `meta-self-learning-skill-gen` to scaffold the observer phase by default — deferred until the prototype proves itself in a live re-run.
- Modifying `pr-merge-readiness/SKILL.md` to include Phase 10 — that's the live re-run task, not part of the retrospective.
- Generalizing observer to read other self-learning skills' run histories cross-skill — the design doc explicitly keeps lessons per-skill at v1.

## Recommended next step

If the user agrees with this verdict:

1. Apply the three adjustments above to `library/templates/self-learning-skill/observer-phase.md`.
2. Scaffold the observer into `skills/pr-merge-readiness/SKILL.md` as Phase 10.
3. Initialize `skills/pr-merge-readiness/observations.json` with the retrospective seed entries.
4. Initialize an empty `skills/pr-merge-readiness/suggestions.md`.
5. Run the skill on a real PR or branch and compare what observer surfaces vs. what audit surfaces in real time.
