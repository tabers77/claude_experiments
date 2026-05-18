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

---

## 2026-05-13 — Theme: audit-rows-hard-to-read-when-evidence-strings-are-long (bulleted `Phase X [pass] | <long evidence>` format wraps badly in narrow terminals)

**Pattern observed**: convergence trip — one observer observation (this run) + TWO matching user-typed improvement-suggestions (2026-05-08 + 2026-05-13). Per the convergence rule, this fires as a proposal regardless of count, and the doubled user signal strengthens the case.

- **Observation** (`observations.json` ts=`2026-05-13T19:00:00+02:00`, target=`this branch into dev (current=feat/stream_n)`, phase=`8`, category=`output_format_quality`, theme=`audit-rows-hard-to-read-when-evidence-strings-are-long`): verbatim evidence — "User typed (via `suggestion :` trigger-prefix, captured as improvement_suggestions[] entry ts=2026-05-13T19:00:00+02:00, tag=output_format_quality): 'this part is unredable : - Phase 1 [pass] | input parsed: current mode, head=feat/stream_n, base=dev; user input verbatim: \"this branch into dev\" - Phase 2 [pass] | git 2.37.0 lacks `merge-tree --write-tree`; fell back to `git merge-base origin/dev feat/stream_n` → d38c48c (equal to origin/dev HEAD) ⇒ branch is 11 commits ahead, 0 behind, strict fast-forward possible, zero conflicts. Exit 0.' The pasted excerpt shows Phase 1 + Phase 2 audit rows wrapping mid-sentence due to terminal width — bullet markers (`-`), the `Phase X [pass] |` prefix, and the evidence body fragment onto multiple lines that break readability."

- **Matching user-typed improvement-suggestion #1** (`run_history.json:improvement_suggestions[]` ts=`2026-05-08T00:00:00+02:00`, phase=`audit`, tag=`8-audit-table-format`): verbatim text — "render the Phase 8 audit rows as a markdown table (columns: Phase, Status, Evidence) instead of a bulleted 'Phase X [pass] | <evidence>' list — much more readable when evidence strings are long (e.g. full git merge-tree commit hashes)."

- **Matching user-typed improvement-suggestion #2** (`run_history.json:improvement_suggestions[]` ts=`2026-05-13T19:00:00+02:00`, phase=`8`, tag=`output_format_quality`): verbatim text — "this part is unredable : - Phase 1 [pass] | input parsed: current mode, head=feat/stream_n, base=dev; user input verbatim: \"this branch into dev\" - Phase 2 [pass] | git 2.37.0 lacks `merge-tree --write-tree`; fell back to `git merge-base origin/dev feat/stream_n` → d38c48c (equal to origin/dev HEAD) ⇒ branch is 11 commits ahead, 0 behind, strict fast-forward possible, zero conflicts. Exit 0."

**Interpretation**: two independent user-typed signals + one observer observation agree that the bulleted `- Phase X [pass] | <evidence>` format is unreadable when evidence strings approach or exceed terminal width. The 2026-05-08 signal proposed the structural fix (markdown table with `| Phase | Status | Evidence |` columns); the 2026-05-13 signal reaffirms the pain. The remediation is mechanical (re-template Phase 8 step 1) and orthogonal to the audit's load-bearing principles — switching from bullets to a table preserves verbatim evidence + verbatim user quotes (the actual safety contract), it only changes presentation.

**Proposed change to SKILL.md**:

Replace the bulleted audit-row template in Phase 8 step 1 with a markdown-table form. Current text (verbatim from SKILL.md):

```
Each row format: `- Phase X [pass|FAIL] | <evidence>` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input.
```

Proposed replacement:

```
Each row is a markdown-table row with three columns: `| Phase X | pass|FAIL | <evidence> |` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input. Long evidence strings stay on a single logical line (the table cell) and the markdown renderer wraps them; bulleted line-wrapping in terminals breaks readability when evidence approaches 100+ chars.
```

And replace the example block at the top of Phase 8 step 1 (the `Self-audit for run on <input> at <ts>:` template) with the table form:

```
Self-audit for run on <input> at <ts>:

| Phase | Status | Evidence |
|-------|--------|----------|
| 1 | pass | input parsed: <mode> <target>; user input verbatim: "<literal quote>" |
| 2 | pass | git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>: exit=<code>; conflicts: <none\|<paths>> |
| 3 | pass\|FAIL | rules-source=<resolved PRE_COMMIT_RULES_PATH or "defaults">; outcomes: smoke=<...>, lint=<...>, protected=<...>, ownership=<...>, safety=<...> |
| 4 | pass\|FAIL | tiers run: <list>; results: <pass/fail/skipped per tier>; test-cache: <verbatim lines or "not wired">; live UI: <ran\|skipped + reason> |
| 5 | pass\|FAIL | claude-library:code-diagnosis Skill call observed: <yes/no>; findings: <count> at <file:line list> |
| 6 | pass\|FAIL | env files in diff: <yes/no>; if yes: secrets-heuristic=<...>, placeholder=<...>, .env.example sync=<...> |
| 7 | pass\|FAIL | unresolved items: <N surfaced> / <M resolved-with-explicit-choice>; user input verbatim: "<literal quote>" |
```

No FAIL detection rule needs to change — this is pure presentation. The load-bearing verbatim-quote rule (`audit-paraphrased-user-input`) still applies inside the table cell exactly as before.

**Status**: applied
**Applied at**: 2026-05-13T19:30:00+02:00
**Applied via**: Replaced Phase 8 step 1 bulleted self-audit template with a three-column markdown table (`| Phase | Status | Evidence |`) and rewrote the row-format sentence accordingly. Pipe characters inside the `Status` and `Evidence` cells are escaped as `\|` for renderer correctness. No FAIL counter changes — purely presentational, the verbatim-quote rule still applies inside cells.

---

## 2026-05-15 — Theme: phase-6-env-review-trivially-passes (Phase 6 has fired in every recorded run since 2026-05-07 and produced "no env files in diff (trivial pass)" every time; user has now explicitly asked to remove the standalone phase)

**Pattern observed**: convergence trip — one observer observation + one matching user-typed improvement-suggestion. Per the convergence rule, this fires as a proposal regardless of count. Cross-run history is unanimous (6/6 runs trivially passed Phase 6) so the empirical signal is strong on its own.

- **Observation** (`observations.json` ts=`2026-05-15T18:00:00+02:00`, target=`merge this branch into dev (current=feat/cicd-pipeline; head=a0e6a007110b585755207e4a58b447d101037c04)`, phase=`6`, category=`redundant_phase`, theme=`phase-6-env-review-trivially-passes`): verbatim cross-run evidence — every recorded run since 2026-05-07 has Phase 6 evidence string containing "no env files in diff (trivial pass)" or equivalent. The load-bearing FAIL rule `6-env-secret-committed` has never tripped (counter still at 0). Six runs across diverse branches (feat/auth-foundation, feat/bug_gap_skill_test, feat/gap_bugs_fixer ×2, feat/stream_n, feat/cicd-pipeline) all touched zero `.env*` files.

- **Matching user-typed improvement-suggestion** (`run_history.json:improvement_suggestions[]` ts=`2026-05-15T18:00:00+02:00`, phase=`audit`, tag=`6-phase-redundant`): verbatim text — "this step was used once 'Phase 6: .env / .env.local review' we should just remove it" (captured via near-miss trigger prefix `suggest:` interpreted as `suggestion:`; intent unambiguous).

**Interpretation**: two independent channels agree that Phase 6 as a *standalone* phase is over-instrumented for this project's actual workflow. However, the load-bearing principle (no secret-in-.env-committed) still needs preserving — pure removal would silently lose protection if a future branch DID stage a `.env.local` with a real secret. The right structural fix is to fold the env-secret check into Phase 3's safety sub-step (where protected-files / migration-number / personal-files checks already live), so the audit no longer renders a separate Phase 6 row when `.env*` files are absent, while the load-bearing detection still fires inside Phase 3 when they are present. This shrinks the audit table from 7 rows to 6 in the common case (zero env diffs) and merges related safety checks under a single phase header.

**Proposed change to SKILL.md** (option A — recommended): **fold Phase 6 into Phase 3's safety sub-step.**

1. In Phase 3 step 2 ("Default checks") and step 3 ("Run each rule against the diff"), add a sub-bullet under safety: "`.env*` / `*.pem` / `*.key` files in diff: if present, run the secret-heuristic from current Phase 6 (high-entropy ≥32 chars, `password=` / `secret=` / `api_key=` patterns, .env.example sync, placeholder convention). If any heuristic trips, surface to Phase 7 with FAIL tag `6-env-secret-committed`."
2. In Phase 3 step 4 ("Aggregate outcomes"), extend the row with `env-secrets=<pass|FAIL+files>`.
3. Move the FAIL rule `6-env-secret-committed` from "Domain FAIL rules" to be evaluated as part of the Phase 3 row; keep its tag, threshold, description, and remediation_hint unchanged so existing `run_history.json:fail_counters` continues to map. Phase 8 evidence row 3 becomes `protected=<...>, ownership=<...>, safety=<... + env-secrets=<...>>`.
4. Delete the standalone "## Phase 6 — `.env` / `.env.local` review" section entirely. Re-number subsequent phases (Phase 7→6, Phase 8→7, Phase 9→8, Phase 10→9) OR keep current numbering with Phase 6 marked "(reserved — folded into Phase 3)" to avoid breaking external references. Recommend the latter for minimal disruption.
5. Update the Phase 8 audit table template to drop the Phase 6 row entirely (since its outcome is now inside the Phase 3 row's `safety` field).

**Proposed change to SKILL.md** (option B — alternative): **keep Phase 6 but suppress its audit row when no env files are touched.**

1. In Phase 6 step 1, when the `Select-String -Pattern '\.env(\.[a-z]+)?$'` filter returns zero hits, mark Phase 6 as "phase-skipped-no-env-files" and explicitly do NOT emit a Phase 8 audit row for it.
2. When env files ARE in the diff, Phase 6 runs the full current check set and emits a Phase 8 audit row as it does today.
3. Phase 8 audit template becomes a variable-row table — Phase 6 row appears only when `phase6_status != "phase-skipped-no-env-files"`.

**Recommended**: option A. Folding into Phase 3 is a one-time structural edit; option B preserves the dead phase as a placeholder and adds variable-row logic to Phase 8 just to hide it.

**Status**: applied
**Applied at**: 2026-05-16T00:00:00+02:00
**Applied via**: Implemented option A. Folded the env-secret heuristic table (5 checks: secret heuristic, placeholder convention, .env.example sync, naming convention, .env.local-when-ignored) into Phase 3 step 2's default checks as an env-file safety sub-bullet. Extended Phase 3 step 4 aggregate-outcomes row with `env-secrets=<no-env-files|pass|FAIL+files>`. Replaced standalone Phase 6 section with a reserved placeholder pointing at Phase 3 (kept phase numbering to avoid breaking Phase 7/8/9/10 external references). Dropped Phase 6 row from the Phase 8 audit table and folded its outcome into the Phase 3 row's `env-secrets=` segment. Retained FAIL tag `6-env-secret-committed` (load-bearing, threshold=1) for counter continuity in `run_history.json:fail_counters`; rule description updated to note evaluation now happens within Phase 3 step 2. Updated opening principle ("six gates" → "five gates"), Phase 7 sources list, Phase 7 example-item phase tag (`[phase 6]` → `[phase 3]`), "Phases 1–6" → "Phases 1–5" in Phase 7 auto-pass clause, and Edge cases item 3 accordingly.

---

## 2026-05-18 — Theme: phase-5-findings-need-severity-and-provenance (Phase 5 surfaces code-diagnosis findings in the sub-skill's native Bugs/Smells/Opportunities triage shape; user must explicitly ask whether smells = potential issues or just refactoring before being able to decide what blocks merge)

**Pattern observed**: standalone-threshold trip — three observations of the same theme across three runs (2026-05-11, 2026-05-12, 2026-05-18), each from a different branch (`feat/gap_bugs_fixer`, `feat/gap_bugs_fixer`, `feat/stream_n`). Each occurrence cost 2–3 conversation turns to clarify merge-relevance after the Phase 5 report landed. Three independent run-level evidence points, no convergence required.

- **Observation #1** (`observations.json` ts=`2026-05-11T17:00:00+02:00`, phase=`5`, category=`output_format_quality`): User verbatim mid-Phase-5: 'I need to understand whcich are the issues we have that must be fixed now (high , medium , low prio) before merging and why these issues were not discored in this brach , be brief dont over explain . I need to dunerstand if these issues were already existen issues or we introdued them in this branch , and why there are not regifreted as issue ?' (transcribed verbatim incl. typos).

- **Observation #2** (`observations.json` ts=`2026-05-12T16:30:00+02:00`, phase=`7`, category=`output_format_quality`): User verbatim mid-Phase-7 after I surfaced 3 medium smells from `claude-library:code-diagnosis`: 'I need to undertand if this is something we have introduced or pre existen , how bad it is ? epxlian it in 2 setneces max' (transcribed verbatim incl. typos).

- **Observation #3** (`observations.json` ts=`2026-05-18T18:00:00+02:00`, phase=`5`, category=`output_format_quality`): User verbatim after I delivered the Phase 5 code-diagnosis report (0 bugs / 4 smells / 3 opportunities): 'So you are saying everything looks good , we have not introduced new bugs and there are not potential issues . Youa re just suggesting refactring opportunities ? is that correct ? Because I get a summary at the beginning , a a lot of information that is hard to diggest quickly' (transcribed verbatim incl. typos).

**Interpretation**: three independent user-typed signals across three runs and three different branches agree on the same root pain: Phase 5 reports findings using the sub-skill's native triage shape (Bugs / Smells / Opportunities) without leading with a decision-grade TL;DR that tells the user, in one line, *what blocks merge and what doesn't*. The user's framings vary (`high/med/low priority`, `introduced vs pre-existing`, `bugs vs refactoring`) but the underlying ask is constant: a merge-decision-grade summary up front, not the sub-skill's exploratory taxonomy. The current Phase 5 step 2 ("Surface findings") instructs `For each finding: severity, file:line, one-line description` but does not require a TL;DR header that classifies findings by merge-impact. Three runs of evidence that this is insufficient is enough to warrant a structural fix.

**Proposed change to SKILL.md**:

Augment Phase 5 step 2 ("Surface findings") with a mandatory TL;DR header that classifies findings by *merge-impact*, separate from the sub-skill's triage shape. Insert after the existing "Surface findings in a 'Sweep results' block" sentence:

```
2a. **Lead with a one-line merge-impact TL;DR** before the per-finding
detail. The TL;DR must answer, in a single sentence: "<N1> items block
merge / <N2> items track as follow-up / <N3> items are pure refactoring."
Mapping rule from the sub-skill's triage shape:
  - "blocks merge" = bugs (any severity) + smells severity ≥ medium that
    cite NEW behavior introduced by THIS branch (verify via
    `git blame <file>:<line>` — was the cited line added in
    `origin/<BASE_BRANCH>...<head>`?).
  - "track as follow-up" = smells that cite pre-existing code OR smells
    severity = low.
  - "pure refactoring" = opportunities.

Example TL;DR (verbatim format the user can scan in one second):
  "TL;DR — 0 items block merge, 2 items track as follow-up (filed as
   <tracker-IDs> if accepted), 3 items are pure refactoring."

After the TL;DR, render the existing per-finding table — but order
sections by merge-impact (blocks-merge first, follow-ups second,
refactoring last), NOT by the sub-skill's bug/smell/opportunity order.
```

Augment Phase 5 step 5 ("Any new finding…") to reference the TL;DR:

```
5. Any item in the "blocks merge" bucket of the TL;DR → mark Phase 5
   FAIL and surface to Phase 7. Items in "track as follow-up" or "pure
   refactoring" do NOT auto-route to Phase 7 — they're informational
   unless the user explicitly asks to fix-now or to register as a gap.
```

Add the corresponding entry to Phase 8 FAIL detection rules (procedural, not load-bearing — UX failure mode, not a safety failure):

```
- **`5-findings-table-needs-severity-provenance-columns` FAIL**
  (procedural, threshold=2): Phase 5 surfaced code-diagnosis findings
  without a one-line merge-impact TL;DR header (the "<N1> blocks merge /
  <N2> track as follow-up / <N3> pure refactoring" sentence) preceding
  the per-finding table. Threshold=2 because a single occurrence may be
  the skill's first run on a new project; two means the TL;DR rule is
  drifting.
```

**Status**: applied
**Applied at**: 2026-05-18T19:00:00+02:00
**Applied via**: Inserted Phase 5 step 2a (merge-impact TL;DR header with mapping rule blocks-merge/track-as-follow-up/pure-refactoring and bucket-ordered per-finding table) verbatim from the proposal. Rewrote Phase 5 step 5 to route only the "blocks merge" bucket to Phase 7 (follow-ups and refactoring stay informational unless the user explicitly fix-nows or registers as a gap). Added `5-findings-table-needs-severity-provenance-columns` (procedural, threshold=2) to Phase 8 FAIL detection rules and seeded the matching counter in `run_history.json:fail_counters`.


