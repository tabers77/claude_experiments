# `pr-merge-readiness` — Observer suggestions

This file is written by the **observer phase** (Phase 10) when cross-run clustering trips. Each section below is an unreviewed proposal generated from ≥3 observations sharing a theme (or 1 observation + matching `improvement_suggestions[]` entry — the convergence rule).

The user reviews each section and flips `Status: unreviewed` to either `applied` or `dismissed`. When applied, the user fills `Applied at:` (ISO 8601) and `Applied via:` (one-line description of the SKILL.md edit), then mirrors the same values into the matching `review_log[]` entry of `observations.json`.

The observer never edits this file's existing sections — it only appends new proposals. Existing sections are owned by the human reviewer.

## State as of bootstrap (2026-05-08)

`observations.json` was seeded with 5 retrospective entries from runs 1–2 (auth-foundation, bug-gap-skill-test). Sub-cluster counts at bootstrap (within each category, grouped by `_theme_slug`):

| Category | Theme | Count | Notes |
|---|---|---|---|
| `dev_env_friction` | `dev-stack-staleness` | 3 | Threshold 3/3 reached on 2026-06-12 (feat/auth-route-protection: test container bakes pyproject.toml, so branch's `no_auth_override` marker warns as unknown across all tiers). Recorded to `run_history.json:friction_log[]` per the observer's narrow exception — no SKILL.md edit (environmental). Project-side fix candidate: mount `./backend/pyproject.toml:/app/pyproject.toml:ro` in docker-compose.test.yml. |
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

## 2026-05-19 — Theme: scale-skill-ceremony-to-pr-scope (full 9-phase ceremony fires verbatim for low-stakes diffs — docs+infra+1-conftest, ≤10 files, no production code — and the user perceives the process as "extreme long time")

**Pattern observed:**

- 2026-05-19T19:00:00+02:00 (this run, `feat-pytest_chache_test → dev`, 7 files / +102/-0, zero production code): user verbatim mid-run after the Phase 5 code-diagnosis report landed — *"I dont udnerstand what I need to fix now , what is bad , can I actually continue ? Also the process should adapt to the case , this case : we have documentation files , md file the docker compose test and a skill that chahged and this process is taking extreme long time"* (transcribed verbatim incl. typos). The full ceremony ran: Phase 1 mode-detect, Phase 2 fast-forward probe, Phase 3 rules sweep, Phase 4 smoke run, Phase 5 code-diagnosis (1 bug + 5 smells + 2 opportunities surfaced via the sub-skill's native triage shape — 70 lines of markdown for one actionable bug), Phase 7 surfaced 1 item via AskUserQuestion, Phase 8 audit table with 7 rows, Phase 9 ledger write, Phase 10 observer. All prior brevity remediations (2026-05-13 audit-table format, 2026-05-16 Phase 6 fold-into-3, 2026-05-18 Phase 5 TL;DR) were in effect.

- 2026-05-19T17:00:00+02:00 (`feat/auth-closeout → dev`, prior run, captured as `improvement_suggestions[]`, `applied_at=null`): user verbatim — *"when giving suggestion of next steps it should be easier to digest and clear for the user which are the best options"* — citing the same meta-pain from the next-steps-clarity angle. The suggestion remained unapplied at this observer's run time, providing the convergence-rule second channel.

**Interpretation:**

All three prior remediations in the brevity / output-quality theme (2026-05-13 audit-table conversion, 2026-05-16 Phase 6 fold, 2026-05-18 Phase 5 TL;DR) targeted output *format* — making each phase's individual output more scannable. None targeted whether the *full ceremony* should fire for low-stakes diffs. For a 7-file docs+infra change with zero production code paths, every phase still walks verbatim: Phase 1 introspection, Phase 2 probe, Phase 3 rules sweep with 7-line aggregate, Phase 4 smoke (~46s), Phase 5 Skill+sub-skill report, Phase 7 menu, Phase 8 audit, Phase 9 ledger, Phase 10 observer. The user's "extreme long time" reaction is not about any single phase's verbosity — it's about the *gestalt* of 9 phases each producing 5-30 lines of output for a change whose load-bearing surface is one container env-var. Convergence rule basis: 1 observer observation (`scope_drift / scale-skill-ceremony-to-pr-scope`) + 1 matching unapplied `improvement_suggestions[]` entry (2026-05-19T17:00:00, same theme from the next-steps-clarity angle).

**Proposed change to SKILL.md:**

Introduce a Phase 1 sub-step (1.5) that classifies the diff scope and chooses a "lite" vs. "full" execution mode for the rest of the ceremony. The classifier and the lite-mode budget are mechanical and falsifiable, so the gate trips deterministically.

`Phase 1 step 5 — Scope classifier (NEW)`:

```
5. **Diff-scope classifier**. Compute the diff scope from
   `git diff --name-only origin/<BASE_BRANCH>...<head>`:

   - **Lite-eligible** when ALL of:
     - Total changed files ≤ 10
     - No diff path matches any glob in `HIGH_BLAST_PATHS`
     - No diff path matches `**/db/migrations/**` or `**/alembic/versions/**`
     - No diff path matches `**/auth/**`, `**/authz/**`, or `**/security/**`
     - No `.env*` / `*.pem` / `*.key` / `id_rsa` files in diff
     - Diff is dominated by docs / infra / config / test-fixtures /
       skill-files (production-code .py / .ts / .tsx file count ≤ 2)

   - **Full-mode** otherwise.

   Record the classifier outcome verbatim in the Phase 1 audit row
   evidence: `scope=lite|full; reason=<the matching condition>`.

   Lite-mode is informational, NOT a permission to skip load-bearing
   gates. Phase 2 (clean-merge), Phase 5 (no-new-bugs sweep with the
   Skill call), and Phase 7 (user-resolution gate) ALWAYS fire verbatim
   — the lite-mode budget applies only to OUTPUT VERBOSITY in Phases
   3, 4, 5 reporting, and 8.
```

`Phase 8 step 1 — Lite-mode audit row format (NEW sub-rule)`:

```
When `scope=lite` from Phase 1, render the audit table with a
condensed Evidence column: 1-2 sentences per row, NOT verbatim command
output. The verbatim-quote rule for user input is preserved
(`audit-paraphrased-user-input` still trips). Specifically:

  - Phase 3 evidence may collapse the 7-field aggregate to one line:
    `rules=<source>; lint=<status>; protected=<count>; safety=<status>; env-secrets=<status>`
  - Phase 4 evidence may collapse to one line per tier:
    `smoke=<pass/fail/skip counts in Ns>; <other tiers> not run (reason)`
  - Phase 5 evidence may collapse to TL;DR-only:
    `Skill(code-diagnosis) observed; TL;DR: <N1> blocks merge / <N2> follow-up / <N3> refactoring`

When `scope=full`, the audit row format remains the current verbose form.
```

`Phase 5 step 2a — Lite-mode TL;DR-first rendering`:

```
When `scope=lite`, render only the TL;DR sentence + the "blocks merge"
bucket detail rows. The "track as follow-up" and "pure refactoring"
buckets are mentioned by count only, expandable on user request
(e.g., "show me the smells"). The full Phase 5 table renders only
when `scope=full` OR the user asks for it explicitly.
```

`Phase 8 step 2 — Add FAIL rule:`

```
- **`1-scope-classifier-not-applied`** (procedural, threshold=2):
  Phase 1 audit row missing the `scope=lite|full; reason=<...>`
  evidence segment. Threshold=2 because a single occurrence may be
  the skill's first run on a new project before the operator has
  internalized the classifier; two means the gate logic is drifting.
```

`Phase 9 ledger schema — Add fail_counter:`

```json
"1-scope-classifier-not-applied": {
  "count": 0,
  "threshold": 2,
  "phase": "1",
  "description": "Phase 1 audit row missing the `scope=lite|full; reason=<...>` evidence segment introduced by the 2026-05-19 scope-classifier remediation.",
  "occurrences": [],
  "remediation_hint": "Phase 1 step 5 must run the diff-scope classifier and emit `scope=lite|full; reason=<matching condition>` into the Phase 1 audit row evidence. The classifier is mechanical: 6 conditions, all-of for lite-eligibility. The audit row format change in Phase 8 step 1 enforces shorter evidence when scope=lite.",
  "applied_at": null
}
```

**Why this remediation rather than the alternatives:**

- (a) "Skip phases for small PRs": rejected — load-bearing gates (clean-merge probe, code-diagnosis Skill call, user-resolution) must always fire. Skipping them defeats the principle anchor.
- (b) "Brevity-mode flag controlled by user": rejected — the user shouldn't have to remember to flip a flag; the skill should classify the diff and choose.
- (c) Adopted approach: classify-first, then condense OUTPUT VERBOSITY in non-load-bearing phases. Keeps all gates honest, just stops reporting them at full verbosity when the surface is small.

**Status:** applied
**Applied at:** 2026-05-20T00:00:00+02:00
**Applied via:** Implemented the adopted approach (classify-first, condense output verbosity in non-load-bearing phases). Phase 1 step 5 (diff-scope classifier with 6 all-of preconditions for lite-eligibility) inserted verbatim from the proposal; Phase 5 step 2a augmented with a "Lite-mode rendering" paragraph (TL;DR + blocks-merge bucket only when `scope=lite`; follow-up/refactoring buckets mentioned by count, expandable on user request); Phase 8 step 1 augmented with a "Lite-mode audit row format" sub-rule (condensed Evidence column for Phases 3/4/5 when `scope=lite`; verbatim-quote rule preserved inside cells); Phase 8 step 2 FAIL rule `1-scope-classifier-not-applied` (procedural, threshold=2) added alongside the existing domain FAIL rules. Counter seeded in `run_history.json:fail_counters` with the documented `remediation_hint`. Matching unapplied `improvement_suggestions[]` entry (2026-05-19T17:00:00) marked applied with the same applied_via summary.

---

## 2026-05-20 — Theme: phase-content-relevance-prefilter (user asks the skill to identify per-sub-step relevance before doing the work — skip the sub-check entirely when not applicable, not just condense its report)

**Pattern observed**: convergence trip — one observer observation (this run) + TWO matching user-typed improvement-suggestions (same run, sister suggestions for Phase 3 and Phase 5). Per the convergence rule, this fires as a proposal regardless of count, and the same-run paired suggestions strengthen the case (the user thought through it enough to file two phase-specific instances).

- **Observation** (`observations.json` ts=`2026-05-20T17:30:00+02:00`, target=`this branch into dev (current=feat/bug-bot-pipeline; head=a74beed; base=dev)`, phase=`cross-phase`, category=`missing_audit_category`, theme=`phase-content-relevance-prefilter`): verbatim evidence — "This run's smoke tier ran for 37.44s (418 passed) despite zero `intelligence_platform/` or `backend/` paths in the 13-file diff (3 bot scripts under scripts/bot/, 1 ADO YAML, 1 SKILL.md + 1 run_history.json under .claude/skills/shared-bug-gap-fix-ci/, 2 docs MDs, 1 .bot-skiplist, 4 JSON fixtures) — smoke verified the dev-merge regression baseline only, exercising nothing the branch itself changed."

- **Matching user-typed improvement-suggestion #1** (`run_history.json:improvement_suggestions[]` ts=`2026-05-20T17:00:00+02:00`, phase=`audit`, tag=`3-relevance-prefilter`): verbatim text — "In Phase 3 — Pre-commit-check rules, we should be able to identify which parts of this check is relevant for the operation, like smoke tests are not always relevant, so we should be able to quickly identify which stages from pre-commit is relevant so we can save time"

- **Matching user-typed improvement-suggestion #2** (`run_history.json:improvement_suggestions[]` ts=`2026-05-20T17:00:00+02:00`, phase=`audit`, tag=`5-relevance-prefilter`): verbatim text — "Also when running operations like Phase 5 — No-new-bugs sweep .. we should first identify if the process/step is relevant for the case"

**Interpretation**: The 2026-05-19 lite-mode remediation classified diff scope and condensed OUTPUT VERBOSITY for non-load-bearing phases (Phases 3, 4, 5 reporting, and 8 audit cells when `scope=lite`). It did NOT change what work gets done — every phase still runs its sub-checks verbatim. The user has now spotted the next-level inefficiency: when the diff demonstrably does not exercise a sub-check's surface (e.g. smoke covers platform Python code; no platform Python in diff → smoke is exercising nothing the branch changed), the sub-check is providing zero branch-specific signal and could be skipped entirely. The two paired suggestions name the pattern in two concrete phases (Phase 3 pre-commit sub-checks; Phase 5 code-diagnosis scope), and the underlying ask is general: every phase that does work should have a per-sub-check relevance predicate evaluated against the diff before doing the work.

Important distinction from the 2026-05-19 lite-mode remediation:
- **Lite-mode (already applied)**: `scope=lite` condenses *what's shown to the user*; all sub-checks still run.
- **Relevance prefilter (this proposal)**: each sub-check has a diff-content predicate that determines whether the sub-check runs at all.

These compose: a diff with `scope=lite` AND a sub-check that the relevance prefilter skips would produce a one-line "Phase 3 smoke=skipped (no platform code in diff)" audit row instead of running 37s of tests and emitting a verbose `smoke=418/1` line.

Load-bearing principle preserved: the relevance predicate is conservative-by-default. When in doubt, the sub-check runs. The predicate trips skip only when the diff is verifiably orthogonal to the sub-check's surface (e.g. smoke covers Python code in `intelligence_platform/` and `backend/tests/`; if those paths are ABSENT from the diff, smoke would be exercising orthogonal code that the branch didn't change — skip is safe). Conservative defaults mean the predicate is a positive whitelist of paths-that-trigger, not a blacklist of paths-that-skip.

**Proposed change to SKILL.md**:

Augment each phase that does meaningful work with a per-sub-check relevance predicate. Define the predicates in the config block alongside `HIGH_BLAST_PATHS` and `DEFAULT_TEST_COMMANDS`, so projects can tune them per repo:

```yaml
RELEVANCE_PREDICATES:
  # Per-sub-check diff-path globs that determine whether the sub-check runs.
  # If no path in the diff matches any glob in the predicate's triggers,
  # the sub-check is skipped with the documented skip_note. Conservative
  # default: when uncertain, leave the predicate empty (matches nothing →
  # always run).

  phase3_smoke:
    # Smoke tier covers platform Python. Skip when no platform paths in diff.
    triggers:
      - "**/intelligence_platform/**"
      - "**/backend/tests/**"
    skip_note: "no platform Python paths in diff (smoke would exercise dev-merge baseline only)"

  phase3_lint_python:
    # Ruff already scoped to changed Python files internally; this predicate
    # only avoids invoking the tool when no Python files changed at all.
    triggers:
      - "**/*.py"
    skip_note: "no .py files in diff"

  phase3_lint_frontend:
    triggers:
      - "**/frontend/**"
      - "**/*.ts"
      - "**/*.tsx"
      - "**/*.js"
      - "**/*.jsx"
    skip_note: "no frontend paths in diff"

  phase5_code_diagnosis_categories:
    # Code-diagnosis Skill call itself remains LOAD-BEARING (no-new-bugs
    # principle anchor). The relevance predicate here applies only to the
    # sub-skill's CATEGORY scan, not to the Skill invocation.
    # Categories: Bugs, Smells, Opportunities, Performance, Security.
    skip_security_category:
      # Security category scans for input validation / injection / hardcoded
      # secrets / unsafe deserialization / missing access control. Skip when
      # no auth/security/routes paths in diff.
      triggers:
        - "**/auth/**"
        - "**/authz/**"
        - "**/security/**"
        - "**/routes.py"
        - "**/dependencies.py"
      skip_note: "no auth/security/routes paths in diff (security category not applicable)"
    skip_performance_category:
      # Performance category scans for N+1, blocking calls in async, missing
      # caching. Skip when no Python service code in diff.
      triggers:
        - "**/services/**"
        - "**/tools/**"
        - "**/registry/**"
        - "**/mcp/**"
      skip_note: "no service/tool/registry/mcp paths in diff (performance category not applicable)"
```

Augment Phase 3 step 1 ("Locate the rules"), inserting a new sub-step BEFORE the sub-checks run:

```
1a. **Per-sub-check relevance prefilter** (NEW): for each sub-check defined
   in `RELEVANCE_PREDICATES`, evaluate the predicate against the diff
   path list. If no diff path matches any glob in the predicate's
   `triggers`, mark the sub-check as `skipped (irrelevant)` and record
   the `skip_note` verbatim into the Phase 3 step 4 aggregate row. Do
   NOT run the sub-check.

   The relevance prefilter NEVER applies to:
     - Phase 2 clean-merge probe (load-bearing)
     - Phase 5 code-diagnosis Skill call itself (load-bearing — the
       relevance prefilter inside Phase 5 only suppresses sub-skill
       CATEGORY scans, not the Skill invocation)
     - Phase 7 user-resolution gate (load-bearing — any item already
       surfaced by an earlier phase still requires explicit choice;
       only the prefilter suppression is recorded as evidence)
```

Augment Phase 5 step 1 ("Run `claude-library:code-diagnosis`"):

```
1a. **Per-category relevance prefilter** (NEW): the Skill call is
   load-bearing and ALWAYS fires. Within the Skill call, evaluate each
   sub-category predicate in `RELEVANCE_PREDICATES.phase5_code_diagnosis_categories.skip_*`
   against the diff. For each tripped predicate, instruct the sub-skill
   to skip that category's scan and record the `skip_note`. The output
   continues to list the categories that DID run; skipped categories
   appear as one-line skip notes in the Phase 5 report (and in the
   Phase 8 audit row's Phase 5 evidence string).
```

Augment Phase 3 step 4 (aggregate-outcomes row), adding a new field:

```
Aggregate row may now include a `relevance-skipped=<comma-list>` field
listing any sub-checks suppressed by the relevance prefilter, with the
verbatim `skip_note` for each. Example:

  rules-source=<path|defaults>, smoke=<pass|skipped:no-platform-paths|FAIL+counts>,
  lint=<pass|skipped:no-py-files|FAIL+files>, protected=<...>, ownership=<...>,
  safety=<...>, env-secrets=<...>, relevance-skipped=<phase3_smoke:no-platform-Python-paths;phase3_lint_frontend:no-frontend-paths>
```

Augment Phase 8 step 2 (FAIL detection rules) with a new procedural rule:

```
- **`3-or-5-relevance-prefilter-not-applied`** (procedural, threshold=2):
  Phase 3 or Phase 5 ran a sub-check whose `RELEVANCE_PREDICATES`
  predicate would have tripped given the diff content, but the
  prefilter step was not invoked (audit row shows the sub-check ran but
  `relevance-skipped` is absent or empty when it should contain the
  sub-check). Threshold=2 because a single occurrence may be the
  skill's first run on a project before the predicates are tuned; two
  means the prefilter step is being bypassed.
```

Add the corresponding counter to `run_history.json:fail_counters`:

```json
"3-or-5-relevance-prefilter-not-applied": {
  "count": 0,
  "threshold": 2,
  "phase": "3 or 5",
  "description": "Phase 3 or Phase 5 ran a sub-check whose RELEVANCE_PREDICATES predicate would have tripped given the diff content, but the prefilter step was not invoked.",
  "occurrences": [],
  "remediation_hint": "At Phase 3 step 1 entry and Phase 5 step 1 entry, evaluate each sub-check's predicate against the diff path list. If predicate.triggers contains zero matches, mark the sub-check as skipped with the predicate's skip_note. Record the suppression in the Phase 3 step 4 aggregate row's `relevance-skipped=...` segment. The audit row must show either the sub-check's outcome OR a non-empty `relevance-skipped=...` listing it.",
  "applied_at": null
}
```

**Why this approach over alternatives**:

- (a) "User-toggle to skip individual sub-checks": rejected — same anti-pattern as a brevity-mode flag; the user shouldn't have to remember which sub-checks to skip per diff.
- (b) "Compute everything, suppress reports in output": rejected — that's what the 2026-05-19 lite-mode already does; the user is explicitly asking for the work to be skipped, not just hidden.
- (c) "Hard-code the predicates in SKILL.md": rejected — paths are project-specific; configuration belongs in the config block.
- (d) Adopted approach: declarative per-sub-check predicates in the config block; mechanically evaluated against the diff path list; conservative defaults; load-bearing gates exempt.

**Status**: applied
**Applied at**: 2026-05-20T20:00:00+02:00
**Applied via**: Implemented the adopted approach (declarative per-sub-check predicates in the config block; mechanically evaluated against the diff path list; conservative defaults; load-bearing gates exempt) with two reviewer-flagged caveats: (1) the config block carries a CRITICAL note that downstream projects MUST tune the example globs (intelligence_platform / backend/tests / frontend / auth / etc.) for their own layout, otherwise the prefilter silently skips nothing or everything; (2) `phase3_smoke.triggers` was extended beyond the proposed list to include `pyproject.toml`, `poetry.lock`, `requirements*.txt`, `Dockerfile*`, and `docker-compose*.yml`, because dependency or build-image changes can break smoke even without platform-code touched and the proposal's narrower trigger list would have silently skipped smoke on env-only branches. Concrete edits: RELEVANCE_PREDICATES config block added; Phase 3 step 1a (per-sub-check relevance prefilter with load-bearing exemptions for Phase 2 / Phase 5 Skill call / Phase 7) added; Phase 3 step 4 aggregate row extended with `relevance-skipped=<none|<sub-check>:<skip_note>; ...>`; Phase 5 step 1a (per-category relevance prefilter — Skill call itself remains load-bearing, only sub-skill category scans like Security / Performance can skip via Skill-call args); Phase 8 step 1 audit-table Phase 3 row updated with the new `relevance-skipped=...` segment; Phase 8 step 2 FAIL rule `3-or-5-relevance-prefilter-not-applied` (procedural, threshold=2) added; counter seeded in `run_history.json:fail_counters` with `remediation_hint` citing the smoke-trigger safety net. Both matching `improvement_suggestions[]` entries (2026-05-20T17:00:00 tag=`3-relevance-prefilter` + tag=`5-relevance-prefilter`) marked applied with mirroring summaries.




---

## 2026-05-21 — Theme: shallow-clone-not-detected

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-05-21T11:00:00 (run feat/mcp_tools_exposure): Phase 1 step 3 ran `git rev-list --count origin/dev` (returned 1) and `git merge-base origin/dev <head>` (returned 'no merge base'). Skill reported origin/dev as a 1-commit orphan branch. User verbatim: "ok , no this is a bigger problem . You are saying that bug-bot pipeline changed the git history of dev ? in dev history in devops I see all the commits , why are you saying you only see 1 commit ?". Root cause: shallow clone — `git rev-parse --is-shallow-repository` returned `true`; parent commit object not in local pack. After `git fetch --unshallow origin`, dev correctly showed 384 commits.
- Matching `improvement_suggestions[]` entry (tag=`2-shallow-clone-check`, verbatim): "you gave fail red flags regarding the dev branch and this brnach miss match".

**Interpretation:** Phase 1 has no defensive check against shallow-clone state. Any operator running this skill from an Azure DevOps Pipeline checkout (default `fetchDepth: 1`) or a CI-provided shallow clone will hit the same false "orphan branch" alarm. The check is one bash line; the cost of skipping it is a false alarm that has now caused real user panic.

**Proposed change to SKILL.md:**
- In Phase 1, BEFORE step 3's branch-existence checks, insert a new step 2a: "Defensive: run `git rev-parse --is-shallow-repository`. If it returns `true`, run `git fetch --unshallow origin` and re-check. A shallow clone makes subsequent merge-base / rev-list / merge-tree probes return absurdly small or 'no merge base' results that mimic an orphan branch — do NOT report ancestry findings until the clone is unshallowed."
- Optionally add audit FAIL tag `1-shallow-clone-not-unshallowed` (procedural, threshold=2) so future runs that skip the defensive check get caught.

**Status:** applied
**Applied at:** 2026-05-21T12:00:00+02:00
**Applied via:** Inserted Phase 1 step 2a (shallow-clone defensive check via `git rev-parse --is-shallow-repository` → `git fetch --unshallow origin` when shallow) verbatim from the proposal. Extended the Phase 8 step 1 Phase 1 audit-row template with `shallow-clone=<yes-unshallowed|no>` evidence segment. Added `1-shallow-clone-not-unshallowed` FAIL rule (procedural, threshold=2) to Phase 8 step 2 and seeded the counter in `run_history.json:fail_counters` with the documented `remediation_hint`. Matching `improvement_suggestions[]` entry (2026-05-21T10:50:00, tag=`2-shallow-clone-check`) will be marked applied in the same edit session.

---

## 2026-05-21 — Theme: options-without-recommendation

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-05-21T11:00:00 (run feat/mcp_tools_exposure): Phase 7 surfaced 4 unresolved items and rendered four AskUserQuestion blocks. The Recommendation gate fired only on item #4 (the canonical-small-fix precondition match); the other three used a neutral four-option list. User verbatim: "which is th ebest option and why ?".
- Matching `improvement_suggestions[]` entry (tag=`7-always-recommend-with-rationale`, verbatim): "when you give options you should give a recommendation of which is the best option and why".

**Interpretation:** Phase 7 step 2's Recommendation gate has 4 narrow preconditions (≤15 lines, code/docs only, smoke ≤60s, canonical-small-fix category). Items outside those preconditions get a NEUTRAL option block. The user wants a recommendation on EVERY multi-option prompt, not just the small-fix subset. A neutral list forces a "which is best?" round-trip — wasted time + tokens that the skill could save.

**Proposed change to SKILL.md:**
- Broaden Phase 7 step 2's recommendation rule. When the narrow Recommendation gate does NOT fire (current behavior: symmetric four-option list), the skill should STILL mark one option as recommended based on a softer heuristic. Suggested heuristic order:
  1. The option with smallest blast-radius that resolves the surfaced item.
  2. If multiple options have similar blast-radius, prefer the one that aligns with this PR's stated intent (e.g. `fix-now` for tightly-scoped feature PRs).
  3. Tie-breaker: the option chosen most often for this surfaced-item type in past runs (read from run_history).
- The option block should always have exactly one option marked `(recommended)` with a one-line rationale appended.
- Optionally add audit FAIL tag `7-recommendation-default-on-all-multi-option-prompts` (procedural, threshold=2) to catch future regressions where the skill renders a neutral option list.

**Status:** applied
**Applied at:** 2026-05-21T12:00:00+02:00
**Applied via:** Broadened Phase 7 step 2's recommendation rule per the proposal — every multi-option Phase 7 prompt must now mark exactly one option as `(recommended)` with a one-line rationale, regardless of whether the narrow Recommendation gate's four preconditions fire. When the gate does not fire, a softer-heuristic fallback selects the recommended option (1: smallest blast-radius that resolves the surfaced item; 2: alignment with PR intent; 3: tie-break by most-chosen option in past run_history). Added `7-recommendation-default-on-all-multi-option-prompts` FAIL rule (procedural, threshold=2) to Phase 8 step 2 and seeded the counter in `run_history.json:fail_counters` with the documented `remediation_hint`. Matching `improvement_suggestions[]` entry (2026-05-21T10:50:00, tag=`7-always-recommend-with-rationale`) will be marked applied in the same edit session.

---

## 2026-05-21 — Theme: prior-closure-narrative-vs-actual-state-not-reconciled

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-05-21T11:00:00 (run feat/mcp_tools_exposure): The M-M1 closure narrative in COMPLETED_STREAMS.md (added by THIS branch) asserts "All 1075 unit + integration tests pass post-change". Phase 5 step 4b tracker-pairing PASSED on grounds of row-removal symmetry. BUT the smoke tier in this run failed 2/422 (the very tests the M-M1 work added) — the over-permissive assertion `status not in (401, 403)` in `test_mcp_valid_bearer_is_accepted` let 404 pass for the wrong reason, masking a mount-path bug. The narrative's truth-claim was false at the time it was written, and the skill silently accepted it.
- Matching `improvement_suggestions[]` entry (tag=`skill-vs-prior-claim-reconciliation`, verbatim): "first in this branch we introduced all the changes related to mcp, we ran all tests, we confirmed everything was correct, later when I invoke pre merge readiness branch you discover that some tests don't pass — very confusing and making me lose a lot of time and tokens".

**Interpretation:** The skill treats closure narratives as DOCUMENTATION ARTIFACTS (presence-checked for tracker pairing) rather than as FALSIFIABLE CLAIMS (truth-checked against this run's evidence). When a closure narrative asserts a test result, the skill could re-run the same tier in-session and compare. This converts narrative claims from hypotheses-to-accept into hypotheses-to-test.

**Proposed change to SKILL.md:**
- In Phase 5, add step 4c — closure-narrative claim reconciliation:
  - For each closure-narrative paragraph in TRACKER_FILES diff, parse for falsifiable phrases. Regex candidates: `\b\d{2,5}\s+(unit|integration|smoke)?\s*tests?\s+pass`, `\bno regressions?\b`, `\bsmoke (?:tier\s+)?clean\b`, `\ball tests pass\b`, `\bN/?A failures?\b`.
  - For each matched claim, run the corresponding tier in this session if Phase 4 hasn't already, and compare. If actual results contradict the claim, surface the discrepancy as a Phase 7 unresolved item (load-bearing: prior over-claim becomes false confidence the user might rely on for the merge decision).
- Cheaper alternative: add a Phase 5 sub-report row that quotes each closure-narrative claim verbatim alongside the Phase 4 actual result, and surfaces ANY narrative claim to Phase 7 for explicit user reconciliation — even if the skill itself doesn't re-run the tier.
- Add audit FAIL tag `5-closure-narrative-falsifiable-claims-not-reconciled` (load-bearing, threshold=1) because acceptance of a false claim is exactly the silent-confidence failure mode the skill is supposed to catch.

**Status:** applied
**Applied at:** 2026-05-21T12:00:00+02:00
**Applied via:** Inserted Phase 5 step 4c (closure-narrative falsifiable-claim reconciliation) per the primary proposal — for each closure-narrative paragraph added in any TRACKER_FILES path (and in COMPLETED_STREAMS.md when in diff), parse for falsifiable claims using the documented regex candidates (`\b\d{2,5}\s+(unit|integration|smoke)?\s*tests?\s+pass`, `\bno regressions?\b`, `\bsmoke (?:tier\s+)?clean\b`, `\ball tests pass\b`, `\bN/?A failures?\b`, `\btier\s+\w+\s+clean\b`). Reconcile each claim against Phase 4 actuals: contradictions surface to Phase 7 as load-bearing FAIL; tier-missing claims surface as unresolved items demanding (a) re-run the tier in-session or (b) explicit verbatim user acceptance. Added `5-closure-narrative-falsifiable-claims-not-reconciled` FAIL rule (load-bearing, threshold=1) to Phase 8 step 2 and seeded the counter in `run_history.json:fail_counters`. Matching `improvement_suggestions[]` entry (2026-05-21T10:50:00, tag=`skill-vs-prior-claim-reconciliation`) will be marked applied in the same edit session.

---

## 2026-05-22 — Theme: phase7-recommendation-misranks-fix-now-when-branch-introduced

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-05-22T13:25:00Z (run bot/o-l6-20260522): My initial Phase 7 AskUserQuestion led with `File smell #1 only (recommended)` and listed `Fix smell #1 in-session` as the fourth, non-recommended option. The smell had been introduced by THIS branch (verifiable via the diff) and met all four Recommendation-gate preconditions (2 LOC change, test code only, smoke <60s, matches "fail-loud assertion" canonical category). User pushed back twice in a row — first verbatim "so you added a gap to document ? in theory we are removing a gap and adding a gap , so we are even ?", then verbatim "I dont understand if T-L5 was introduced by tthis rabcnh , and can we fix it in thsi run direclty ?" — before I converged on `Fix in-session, drop T-L5 row (recommended)` in a third AskUserQuestion.
- Matching `improvement_suggestions[]` entry (tag=`7-fix-in-session-default-when-branch-introduced`, verbatim): "why you did not suggested to fix the gap in this branch , I lost time asking you , and making you coming to the conclusion".

**Interpretation:** The current Recommendation gate evaluates *whether* a fix is cheap enough for in-session execution (4 preconditions covering LOC, code/docs scope, smoke time, fix category), but does not consider *whether* the issue was introduced by THIS branch vs is pre-existing tech debt. Both classes pass through the same option-ranking logic — `(recommended)` lands on whatever the softer-heuristic fallback picks (typically the "smallest blast-radius that resolves the surfaced item", which for follow-up smells often defaults to `File as gap` rather than `Fix now`). For branch-introduced issues, this is exactly backwards: the cost of leaving a new regression in the merge is higher than the cost of a 2-LOC fix, and the user's expectation is that the skill catches and fixes the bug it just surfaced.

**Proposed change to SKILL.md:**
- In Phase 7 step 2's narrow Recommendation gate, add a fifth precondition: `item was introduced by this branch (verifiable via git blame: at least one cited file:line falls within `git diff origin/<BASE_BRANCH>...HEAD` for the cited file)`. When all five fire, default-recommend `Fix it now` as option #1 with the rationale "branch-introduced + cheap fix; closing before merge is cheaper than filing a follow-up".
- In the softer-heuristic fallback (when the narrow gate does NOT fire), preserve current logic for pre-existing items but bias toward `Fix it now` whenever the cited file:line is in the current branch's diff — same git-blame check as above, used as a tie-breaker ahead of "smallest blast-radius".
- Optionally add audit FAIL tag `7-fix-now-default-for-branch-introduced-cheap-fixes` (procedural, threshold=2) to catch future regressions where a branch-introduced cheap-fix item was surfaced with `File as gap` recommended over `Fix now`.

**Status:** applied
**Applied at:** 2026-05-22T00:00:00+02:00
**Applied via:** Added 5th precondition (branch-introduced via `git blame -L <line>,<line> -- <file>` against `origin/<BASE_BRANCH>...HEAD`) to Phase 7 narrow Recommendation gate. When all 5 fire, default-recommend `Fix it now` with rationale "branch-introduced + cheap fix; closing before merge is cheaper than filing a follow-up". Added branch-introduced bias as step 3 of the softer-heuristic fallback (ahead of the historical-frequency tie-breaker). Added FAIL tag `7-fix-now-default-for-branch-introduced-cheap-fixes` (procedural, threshold=2) to Phase 8 audit and seeded the counter in `run_history.json`.

---

## 2026-05-22 — Theme: skill-applied-fix-without-pre-edit-verification

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-05-22T13:25:00Z (run bot/o-l6-20260522): After user approved `Fix in-session, drop T-L5 row (recommended)` for the over-permissive `!= 200` assertion, I edited `test_api_auth_smoke.py:108-113` tightening to `== 401` WITHOUT first running the failing-state test to observe what status code the unauthenticated call actually returns in the test container. The edit was rejected on re-run (actual return: 500 "Authentication not configured" because `ENTRA_APP_TENANT_ID`/`ENTRA_APP_CLIENT_ID` aren't loaded in tests), forcing a revert. The auth-sensitive PreToolUse hook fired twice (once on the edit, once on the revert). Net: 2 edits + 1 revert + 1 re-test wasted ~3 minutes for no net change to the merged state.
- Matching `improvement_suggestions[]` entry (tag=`verify-actual-state-before-tightening-assertions`, sentiment=negative, verbatim): "you made a huge mistakae changing a file , an dn then reverting , this is very bad".

**Interpretation:** Phase 7's fix-now flow currently treats user approval as the only gate before applying the edit. For *tightening* fixes specifically (replacing a permissive predicate with a precise one — e.g. `!= 200` → `== 401`, `not in (401, 403)` → `== 200`), the precise expected value is a SECOND assumption that needs verification before the edit lands. If the user's mental model of the precise value disagrees with the actual observable behavior, the edit fails on re-run and must be reverted. The asymmetry: a *loosening* fix can't fail at runtime (it admits more states), but a *tightening* fix can fail if the assumed precise value is wrong.

**Proposed change to SKILL.md:**
- In Phase 7 step 2, after the user selects a `Fix it now` option, add a sub-step: **2a. Pre-edit verification (for tightening fixes only)**. Define a "tightening fix" as one that replaces a comparison operator with a stricter one (`!=` → `==`, `not in (...)` → `==`, `>= 0` → `> 0`, etc.) or replaces a multi-valued whitelist with a single-value match. Before applying the edit:
  1. Run the relevant test (or curl/probe) in its current failing state, capture the actual value.
  2. Compare the actual value to the user's proposed precise value.
  3. If they agree, apply the edit. If they disagree, surface the discrepancy back to the user: "Actual return was <X>; tightening to <Y> will fail. Adjust the precise expected value, or skip the fix?"
- The verification step is cheap (1 test invocation in container) and prevents the edit+revert ceremony.
- Optionally add audit FAIL tag `7-fix-now-applied-without-failing-state-observation` (procedural, threshold=2) to catch future regressions where a tightening edit was applied without a recorded pre-edit verification run.

**Status:** applied
**Applied at:** 2026-05-22T00:00:00+02:00
**Applied via:** Added Phase 7 step 2a (`Pre-edit verification (for tightening fixes only)`). Includes mechanical tightening-fix detector (operator strictness `!=` → `==`, membership collapse `not in (...)` → `==`, range tightening `>= 0` → `> 0`, whitelist narrowing, pattern strictness substring → exact equality) and a verification sequence that runs the failing-state test/probe BEFORE applying the edit. When actual ≠ proposed precise value, surfaces the discrepancy to the user with three options (adjust precise to actual / investigate underlying code / skip and file as gap) instead of applying-then-reverting. Added FAIL tag `7-fix-now-applied-without-failing-state-observation` (procedural, threshold=2) to Phase 8 audit and seeded the counter in `run_history.json`.

---

## 2026-06-09 — Theme: implementation-md-status-not-checked-by-default

**Pattern observed in 1 run + 1 matching user suggestion (convergence rule):**
- 2026-06-09T09:10:44Z (run feat/documents → dev): The skill passed Phase 3's protected-files check by confirming `implementation.md` was NOT in the diff (correct per CLAUDE.md doc-sync + protected-files rules), but never proactively reported whether the doc *reflects* the implemented work. User asked mid-Phase-8 (verbatim): "is documentation\implementation_docs\implementation.md up to date after this impletation ?". On check: Stream P still marked 🟡 with all 12 P-steps ❌, and the implementation had diverged materially from the documented plan (Azure Document Intelligence not Docling; text-embedding-3-large@1536 not ada-002; single `uploaded-docs` collection not per-project; migrations 0029+0030 not 0030-only; a personal-project document space built even though the plan parked "my files"/Option C as *deferred* at lines 321/340).
- Matching `improvement_suggestions[]` entry (tag=`0-always-check-implementation-md-status`, sentiment=neutral, verbatim): "we should aleys check the status of the impletmation file , and I THINK IT SHOULD be updateed in this branch since the next step will be to merge to dev directly".

**Interpretation:** Two coupled but separable signals.
1. **Missing report (additive, clearly in scope for a SKILL.md edit).** When a branch implements a roadmap stream, the skill should *read* the relevant `implementation.md` section and *report* (a) whether step statuses still show ❌/🟡 despite the work being done, and (b) whether the implementation diverged from the documented plan — surfacing both to Phase 7 as an informational item. Today the protected-files check only confirms the file is *absent* from the diff, which the user reads as "not checked."
2. **In-branch-vs-dev policy question (HUMAN ADJUDICATION — do NOT self-edit).** The user believes the status flip should happen *in this branch* because the merge model is a direct `git merge --ff-only feat/X dev` (here: 0 behind dev), so editing `implementation.md` on the branch *is* editing it on dev. This **contradicts** the documented CLAUDE.md *Documentation Sync Rule* ("Never on a feature branch — status updates happen directly on `dev` after the feature PR merges") and the `shared-pre-commit-check.md` protected-files list. Resolving signal 2 may require a **CLAUDE.md rule change**, not a SKILL.md change — the observer must not encode a behavior that overrides a documented project rule without a human deciding the rule itself should change.

**Proposed change to SKILL.md:**
- **For signal 1 (recommend adopting):** Add a Phase 3 (or Phase 5) sub-step — *"Roadmap-doc status check"*: when the diff touches files that implement a stream documented in `documentation/implementation_docs/implementation.md`, read the matching stream section and report to Phase 7 (informational, non-blocking): the stream's current status marker, any steps still ❌ despite being implemented in this diff, and any plan-vs-implementation divergences detected. Optionally add a procedural audit tag `3-implementation-md-status-not-reported` (threshold=2) so the report becomes a tracked default.
- **For signal 2 (DO NOT auto-apply — route to human):** Surface to the repo owner the question of whether, for this project's direct-ff-to-dev merge model, the protected-files / doc-sync rule should permit (or require) the `implementation.md` status flip to land *in the feature branch*. If the owner agrees, the change belongs in **CLAUDE.md + `shared-pre-commit-check.md` first**, and only then should this skill's Phase 3 protected-files handling be relaxed to match. Until then, the skill should keep treating `implementation.md` as protected on feature branches and recommend the dev-side update — but now *with the divergence notes* from signal 1 so the dev-side commit is accurate.

**Status:** unreviewed
**Applied at:** null
**Applied via:** null

## 2026-06-24 — Theme: git-version-compat-not-handled-in-skill

**Pattern observed in 5 runs:**
- 2026-05-11T17:00:00+02:00: `git merge-tree --write-tree` exit 129 (git <2.38), ad-hoc fallback to old-form merge-tree.
- 2026-05-20T17:30:00+02:00: same exit-129 fallback recorded.
- 2026-06-16T14:33:40Z: exit 129 → old-form merge-tree + worktree merge probe.
- 2026-06-18T13:15:31Z: exit 129 → old-form merge-tree + rev-list descendant check.
- 2026-06-24T12:51:55Z: exit 129 → old-form `git merge-tree bf59bbb origin/dev HEAD` (0 conflicts) + authoritative `git merge --no-commit --no-ff origin/dev` (exit 0, 0 unmerged, aborted clean).
- 2026-06-24T14:14:04Z: exit 129 → old-form `git merge-tree bf59bbb origin/dev HEAD` reported **0 conflict markers (FALSE CLEAN)**, but authoritative `git merge --no-commit --no-ff origin/dev` caught a real `CONFLICT (modify/delete) routes.py` (exit 1, 1 unmerged). The text-marker scan structurally cannot see modify/delete conflicts (they carry no `<<<<<<<` markers). **Had the operator trusted the old-form marker scan alone, the skill would have green-lit a merge that drops Stream S security code.**

**Interpretation:** SKILL.md Phase 2 step 2 prescribes `git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>` as the primary probe. This host runs git 2.37, where `--write-tree` does not exist — the command exits 129 (usage error) on *every* run, and the operator improvises a fallback each time. It has never once succeeded on this host across 5 recorded runs. The fallback works, so it is non-blocking, but the prescribed-then-failing primary path is pure recurring friction and makes the Phase 2 audit-row evidence inconsistent run-to-run.

**Proposed change to SKILL.md:**
- In Phase 2, BEFORE the merge-tree probe, add a step: "Detect the git version (`git --version`). If ≥ 2.38, use `git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>`. If < 2.38, skip straight to the old-form `git merge-tree $(git merge-base origin/<BASE_BRANCH> <head>) origin/<BASE_BRANCH> <head>` conflict-marker scan **plus** an authoritative worktree probe (`git merge --no-commit --no-ff origin/<BASE_BRANCH>` → inspect unmerged paths → `git merge --abort`)." This removes the guaranteed exit-129 on older git and makes the Phase 2 evidence shape deterministic per host.
- Alternatively, add audit FAIL tag `2-git-version-fallback-not-automatic` (procedural, threshold=2) for when Phase 2 runs the unsupported form without a version pre-check.
- **Strengthened by the 2026-06-24T14:14:04Z run:** make the authoritative `git merge --no-commit --no-ff` probe MANDATORY on every run (not just the old-git fallback). The text-marker scan structurally misses modify/delete conflicts — relying on `merge-tree` marker output alone can false-clean a real conflict.

**Status:** unreviewed
**Applied at:** null
**Applied via:** null

## 2026-06-24 — Theme: relevance-predicate-globs-drift-from-real-paths (RELEVANCE_PREDICATES trigger globs silently stop matching after refactors, wrongly skipping load-bearing-adjacent checks)

**Pattern observed in 3 runs (2 channels):**
- 2026-06-09T16:47:30+02:00: `skip_performance_category` triggers (`services/`, `tools/`, `registry/`, `mcp/`) omit common DB-query file locations — a diff touching only those would wrongly skip the performance category.
- 2026-06-10T08:09:15Z: second independent occurrence of the same performance-predicate gap.
- 2026-06-24T14:14:04Z: `skip_security_category` trigger `**/routes.py` matches a *file* named routes.py, not files inside a `routes/` package. After this run's god-file→package split, the glob matched ZERO changed paths and would have skipped the security category on freshly-ported **project-access enforcement** code. Operator overrode and ran security explicitly.

**Interpretation:** `RELEVANCE_PREDICATES` trigger globs are a hand-maintained positive whitelist. They are brittle to two forces: (a) incomplete enumeration (the performance case — real DB-query dirs never listed), and (b) layout refactors that invalidate a path literal (the security case — `**/routes.py` dies the moment `routes.py` becomes `routes/`). Both produce the same failure: a stale glob silently suppresses a security/performance scan on exactly the code that needed it. The prefilter is "conservative-by-default" only if the globs are correct; a stale glob inverts that — it skips by omission. This is the dangerous direction (false skip), not the safe one (false run).

**Proposed change to SKILL.md:**
- In Phase 3 step 1a and Phase 5 step 1a, add a **fail-safe override**: before honoring a `skip_*` predicate, also test the changed paths against a coarse content signal for that category — for security, any changed file whose path contains `auth`, `authz`, `security`, `route`, `permission`, `access`, `policy`, OR whose diff body adds/removes `Depends(`, `HTTPException(403`, `is_admin`, `_enforce_`, `_can_access` → force the security category to RUN regardless of the glob predicate. The glob whitelist may only *trigger* a check, never *suppress* one that the content signal demands.
- Alternatively (lighter): document in the config block's CRITICAL note that path-literal globs like `**/routes.py` MUST be re-tuned after any package/layout refactor, and add audit FAIL tag `3-or-5-predicate-glob-stale-after-refactor` (procedural, threshold=2) for when the operator manually overrides a predicate's skip decision (the override itself is the signal the glob is stale).
- Project-specific follow-up for *this* repo: broaden `skip_security_category.triggers` from `**/routes.py` to `**/routes.py` + `**/routes/**` so the predicate survives the routes-package split this run validated.

**Status:** unreviewed
**Applied at:** null
**Applied via:** null
