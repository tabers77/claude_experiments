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
