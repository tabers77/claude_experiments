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

**Status**: unreviewed
**Applied at**: null
**Applied via**: null

