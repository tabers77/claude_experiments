# `pr-merge-readiness` — Observer suggestions

This file is written by the **observer phase** (Phase 10) when cross-run clustering trips. Each section below is an unreviewed proposal generated from ≥3 observations sharing a theme (or 1 observation + matching `improvement_suggestions[]` entry — the convergence rule).

The user reviews each section and flips `Status: unreviewed` to either `applied` or `dismissed`. When applied, the user fills `Applied at:` (ISO 8601) and `Applied via:` (one-line description of the SKILL.md edit), then mirrors the same values into the matching `review_log[]` entry of `observations.json`.

The observer never edits this file's existing sections — it only appends new proposals. Existing sections are owned by the human reviewer.

## State as of bootstrap (2026-05-08)

`observations.json` was seeded with 5 retrospective entries from runs 1–2 (auth-foundation, bug-gap-skill-test). Sub-cluster counts at bootstrap (within each category, grouped by `_theme_slug`):

| Category | Theme | Count | Notes |
|---|---|---|---|
| `dev_env_friction` | `dev-stack-staleness` | 2 | Cross-run pattern at 2/3 threshold. One more occurrence flips to a `friction_log[]` proposal (per the observer's narrow exception). No SKILL.md edit proposed — environmental, not skill-logic. |
| `missing_audit_category` | `tracker-closure-drift` | 1 | **Will trip the convergence rule on the first live observer run** because `improvement_suggestions[].tag = 5-impl-vs-tracker-check` already exists with matching theme. Proposed audit tag: `5-tracker-closure-without-row-removal`. |
| `missing_audit_category` | `pre-existing-vs-regression` | 1 | Below threshold. Proposed audit tag: `3-pre-existing-vs-regression-not-distinguished`. |
| `missing_audit_category` | `skipped-test-rationale` | 1 | Below threshold. Weak signal; observer would not propose at bootstrap. |

No proposals are written at bootstrap — `review_log[]` is empty so the first live observer run can naturally trigger clustering against the seeded data. On that run, the convergence rule should fire for `tracker-closure-drift` and write the first proposal here citing both the seed observation and the matching `improvement_suggestions[]` entry verbatim.

---

<!--
Observer-written proposals appear below this line.
Each proposal follows the format documented in SKILL.md Phase 10 step 5.
-->

## 2026-05-11 — Theme: tracker-closure-drift (closure narratives added to `COMPLETED_STREAMS.md` without corresponding row removal in `BUGS_AND_GAPS.md`)

**Pattern observed**: convergence trip — one seeded observation + one matching user-typed improvement-suggestion. Per the convergence rule, this fires as a proposal regardless of count.

- **Observation** (`observations.json` ts=`2026-05-08T00:00:00+02:00`, target=`this branch into dev (current=feat/bug_gap_skill_test)`, phase=`5`, category=`missing_audit_category`, theme=`tracker-closure-drift`): verbatim evidence — "tracker-file diff anomaly surfaced — diff did not touch BUGS_AND_GAPS.md despite COMPLETED_STREAMS.md adding closure narratives for W-7-prep-c, V-L2, V-L3, SP-7. Item 1 fixed in working tree (BUGS_AND_GAPS.md rewritten: rows for W-7-prep-c/V-L2/V-L3/SP-7 removed, Section 2 19→16 rows, Section 3 13→12 rows, priority chain cleaned, Last-updated bumped to 2026-05-08)."

- **Matching user-typed improvement-suggestion** (`run_history.json:improvement_suggestions[]` ts=`2026-05-08T00:00:00+02:00`, phase=`audit`, tag=`5-impl-vs-tracker-check`): verbatim text — "before surfacing actions in Phase 7, verify what was actually implemented in the branch matches the documentation tracker (BUGS_AND_GAPS.md). This implementation-vs-docs check should run by default as part of Phase 5, not be skipped."

**Interpretation**: two independent channels (the observer's qualitative pattern-spot and the user's explicit feedback) agree that Phase 5 should mechanically reconcile tracker-file edits against documented closures *before* declaring no-new-bugs. Closure narratives added in `COMPLETED_STREAMS.md` without matching row deletions in `BUGS_AND_GAPS.md` represent a documentation-vs-implementation drift class that the current skill catches only by code-diagnosis intuition, not by mechanical pairing. The proposed audit tag (`5-tracker-closure-without-row-removal`) names a falsifiable check: for each `TRACKER_FILE` in the config, grep the diff for added closure paragraphs and verify the corresponding row was removed in the same commit.

**Proposed change to SKILL.md**:

Insert a new Phase 5 sub-step (after the existing step 4 diff-anomaly check) wired to the configurable `TRACKER_FILES`:

```
4b. **Tracker closure-pairing reconciliation**: for each path in `TRACKER_FILES`,
   diff the file against `origin/<BASE_BRANCH>`. If the diff *adds* a closure
   narrative (heuristic: a new paragraph mentioning a tracker ID like `W-*`,
   `V-*`, `SP-*`, `GAP-NNN` *and* outcome language such as "closed", "fixed",
   "resolved", "shipped"), confirm that the corresponding tracker row in the
   project's bug/gap tracker (typically the OTHER `TRACKER_FILE` — e.g.
   `BUGS_AND_GAPS.md` when `COMPLETED_STREAMS.md` got the closure narrative)
   was *removed* in the same diff. If the row is still present, surface to
   Phase 7 as a hard item with FAIL tag `5-tracker-closure-without-row-removal`.
   If `TRACKER_FILES` has fewer than 2 entries (so there's no "other" tracker
   to pair against), skip cleanly and record "tracker closure-pairing skipped:
   needs >=2 TRACKER_FILES".
```

Add the corresponding entry to Phase 8 FAIL detection rules:

```
- **`5-tracker-closure-without-row-removal` FAIL** (load-bearing, threshold=1):
  Phase 5 sub-step 4b detected a closure narrative added to one TRACKER_FILE
  without a matching row removal in the paired tracker. Load-bearing because
  it defeats the documentation-implementation pairing invariant.
```

**Status**: applied
**Applied at**: 2026-05-12T18:00:00+02:00
**Applied via**: Inserted Phase 5 step 4b (tracker closure-pairing reconciliation) verbatim from the proposal, plus added `5-tracker-closure-without-row-removal` (load-bearing, threshold=1) to Phase 8 FAIL detection rules and seeded the matching counter in `run_history.json:fail_counters`.

---

## 2026-05-12 — Theme: phase-7-default-recommend-in-session-fix-for-trivial-changes (Phase 7 surfaces `fix-now` as 1-of-4 options with no default recommendation, even for trivial safe fixes)

**Pattern observed**: convergence trip — one observer observation (this run) + one matching user-typed improvement-suggestion (this run). Per the convergence rule, this fires as a proposal regardless of count.

- **Observation** (`observations.json` ts=`2026-05-12T16:30:00+02:00`, target=`merge this branch into dev (current=feat/gap_bugs_fixer)`, phase=`7`, category=`missing_audit_category`, theme=`phase-7-default-recommend-in-session-fix-for-trivial-changes`): verbatim evidence — "Mid-flow, the Phase 7 surface for item 4 (3 medium smells in agent_generator.py) presented 4 options ordered `[Skip — track as follow-up, Skip + show tracker diff, Fix smell #3 now, Block merge]` — the `fix-now` option appeared 3rd of 4 with no skill-side recommendation, despite the smells being one-line additions with no behavior change. The user then re-asked twice (`should we register this a gap or not , it is unclear what you recommend here and why`; `I need to undertand if we can fix this quilcy before proceeding`) before I explicitly recommended `#1 + #2 + #3(a)`."

- **Matching user-typed improvement-suggestion** (`run_history.json:improvement_suggestions[]` ts=`2026-05-12T16:30:00+02:00`, phase=`7`, no tag): verbatim text — "if fixes are small and we are 100% sure they wont introduce new bugs then we should prefer to suggest to solve this in the same session"

**Interpretation**: two independent channels (the observer's pattern-spot of the Phase 7 option-ordering + the user's explicit feedback) agree that Phase 7 should default-recommend `fix-now` for trivial safe items rather than treating all four options symmetrically. The current SKILL.md text (Phase 7 step 2) lists `block-merge / fix-now / skip-with-justification / abort` without any triage logic on what "trivial" or "safe" means; the operator (Claude) is left to decide ad-hoc whether to recommend in-session fix, and in this run did so only after the user pushed back twice. A small triage rule with falsifiable preconditions would short-circuit this.

**Proposed change to SKILL.md**:

Augment Phase 7 step 2 to add an explicit recommendation gate before listing the four options. Insert after the existing "For each item, ask the user explicitly for a choice from this set" sentence:

```
**Recommendation gate (before listing options)**: when a surfaced item
meets ALL of the following preconditions, the skill MUST default-recommend
`fix-now` and list it as the first option visually:

  - the fix touches ≤ N lines (suggested N=15) AND
  - the fix is in code or docs only (no schema migrations, no infra
    config, no security boundary) AND
  - a re-run of the relevant test tier after the fix is feasible within
    this session (smoke tier ≤ 60s) AND
  - the fix description is one of: missing-import, deprecation comment
    update, follow-up tracker row, removed-dead-code, narrow exception
    handler, fail-loud assertion.

When the recommendation gate fires, the option block must read:
  1. **Fix it now (recommended)** — <one-line description>
  2. Skip with logged justification
  3. Block the merge
  4. Abort the run

When the recommendation gate does NOT fire (any precondition fails), the
existing symmetric four-option list is used and the skill does not
recommend a default.
```

Add the corresponding entry to Phase 8 FAIL detection rules (procedural, not load-bearing — UX guidance is not safety-critical):

```
- **`7-recommendation-gate-not-applied` FAIL** (procedural, threshold=2):
  Phase 7 surfaced an item meeting all four `Fix it now (recommended)`
  preconditions but did NOT mark fix-now as recommended in the option
  block. Threshold=2 because a single occurrence may be a borderline
  precondition call; two means the gate logic is drifting.
```

**Status**: applied
**Applied at**: 2026-05-12T18:00:00+02:00
**Applied via**: Augmented Phase 7 step 2 with the Recommendation gate (four preconditions: ≤15 lines, code/docs only, smoke re-run ≤60s, fix matches canonical small-fix categories) and the reordered option block that lists `Fix it now (recommended)` first when the gate fires. Added `7-recommendation-gate-not-applied` (procedural, threshold=2) to Phase 8 FAIL detection rules and seeded the matching counter in `run_history.json:fail_counters`.

