---
name: pr-merge-readiness
description: Validate a feature branch is ready to merge into dev — clean merge, pre-commit-check rules pass, relevant tests pass (incl. live UI when applicable), no-new-bugs sweep, and any .env/.env.local additions follow best practices. The skill emits a structured verdict — it does NOT run the merge. Keywords PR merge readiness feature branch dev clean merge pre-commit no-new-bugs live test env env.local best practices verdict approval gate.
metadata:
  pattern: self-learning
  schema-version: 1
---

# PR Merge Readiness

End-to-end pre-merge validation for a feature branch targeting `dev`. The skill walks five gates — clean-merge probe, pre-commit-check rules (incl. env-file safety), relevant-tests run, no-new-bugs sweep, and explicit user resolution — then emits a structured verdict. It NEVER runs `git merge` or `gh pr merge`; the user takes that step manually after reading a green verdict.

**Load-bearing principle**: the merge is approved only when all five gates produce verbatim, falsifiable evidence: clean-merge proof, pre-commit-check rules (incl. env-file safety), relevant-tests pass (incl. live UI when applicable), no-new-bugs sweep, and explicit user resolution of every surfaced item.

## Inputs

The user invokes the skill with one of:

| Shape | Example | Mode |
|---|---|---|
| PR number | `123` or `#123` | `pr` |
| Branch name | `feat/gap-002-tool-registry` | `branch` |
| (no arg) | uses current branch | `current` |

If the input is none of the above, dump the current branch name and `gh pr list --head <current>` and ask the user to pick a real target. Do not guess.

---

## Project config

Defaults match a common Python web service. Override per-project by editing this block — every reference to these names elsewhere in the skill resolves to the values defined here. Empty list / null means "skip the dependent check"; the skill never silently substitutes.

```yaml
BASE_BRANCH: dev
  # The branch the feature branch is being merged into. Used in `git merge-tree origin/<BASE_BRANCH> <head>`.

HIGH_BLAST_PATHS:
  # Glob patterns whose diff makes the live UI test mandatory in Phase 4.
  # Empty list → no path-based "high-blast" trigger; live UI runs only when explicitly opted in.
  - "**/routes.py"
  - "**/orchestrator*.py"
  - "**/business_case_orchestrator*.py"
  - "**/mcp/**"
  - "**/tools/**"
  - "**/registry/**"

PRE_COMMIT_RULES_PATH:
  # Path to a project's pre-commit-check skill or doc. First existing path is used.
  # Empty list → skip Phase 3 lookup, use Phase 3 step 2 default checks directly.
  - ".claude/skills/shared-pre-commit-check.md"
  - ".claude/skills/pre-commit-check.md"
  - "documentation/COLLABORATION.md"

TRACKER_FILES:
  # In-repo tracker files whose diff is sanity-checked in Phase 5 step 4.
  # Empty list → skip the diff-anomaly check.
  - "documentation/implementation_docs/BUGS_AND_GAPS.md"

LIVE_UI_TEST_COMMAND: null
  # Command to run the live UI tier in Phase 4. Set to a real command when the project has live UI test infra.
  # Examples:
  #   pytest -m live -v tests/test_live_ui_workflow.py
  #   docker compose -f docker-compose.test.yml run --rm backend pytest -m live -v tests/test_live_ui_workflow.py
  # null → no live UI test infra; Phase 4 records "no live UI infra" and `4-live-test-skipped-without-justification` does NOT trip.

DEV_STACK_PREFLIGHT_URL: null
  # URL Phase 4 hits before running the live UI tier.
  # null → no preflight; treat dev stack reachability as unknown and require user judgment via Phase 7.
  # Example: http://localhost:8000/marketing/projects

DEFAULT_TEST_COMMANDS:
  # Per-tier commands for Phase 4 when no project-specific routing rules apply.
  # Set tier to null to skip that tier entirely on this project.
  smoke: pytest -m smoke
  unit: pytest
  integration: pytest -m integration
  lint_python: ruff check .
  lint_frontend: npm run lint
  typecheck_frontend: npm run typecheck
```

**How configuration is consumed**:
- Phase 3 reads `PRE_COMMIT_RULES_PATH` (first existing file) before falling back to defaults.
- Phase 4 routes test tiers using `HIGH_BLAST_PATHS` (mandatory live tier trigger), `LIVE_UI_TEST_COMMAND` (the actual command to run), `DEV_STACK_PREFLIGHT_URL` (preflight gate), and `DEFAULT_TEST_COMMANDS` (per-tier commands).
- Phase 5 reads `TRACKER_FILES` to bound the diff-anomaly check.
- Phase 8 audit rows cite the resolved values verbatim, not the placeholder names.

**What you should NOT do**:
- Don't reference paths like `routes.py` in the skill body if your project doesn't have them — edit `HIGH_BLAST_PATHS` instead.
- Don't leave `LIVE_UI_TEST_COMMAND` set to an example value when no live infra exists — set it to `null` so the skill records "no live UI infra" honestly.
- Don't change the SKILL.md's phase logic to fit a project quirk — extend the config block with a new key and reference it from the phase.

---

## Mid-run suggestion capture

The user can propose improvements to **this skill itself** at any point during a run, not only at the audit. The skill recognizes specific trigger prefixes; any user message that opens with one is captured verbatim into `improvement_suggestions[]` in `run_history.json`, then the run continues exactly where it was.

**Recognized trigger prefixes** (case-insensitive, on any line):

```
suggestion: <text>
improvement: <text>
for the skill: <text>
[suggestion] <text>
[skill-improvement] <text>
```

**Optional `[tag]` after the prefix**, used later for grouping:

```
suggestion: [4-test-routing] run targeted unit tests on changed modules
improvement: [6-secret-detection] add Stora Enso internal token regex
```

**Capture protocol** (the skill follows this exactly):

1. **Detect the prefix** at the start of the user's message (any of the five forms above; `[tag]` between the prefix and the text is optional). Anything that does NOT start with one of these prefixes is treated as normal conversation — *not* a suggestion. Mid-run overrides ("don't run the live test for this branch") still go through the existing Phase 7 user-resolution flow, not this capture path.
2. **Record verbatim** into `improvement_suggestions[]`:
   ```json
   {
     "ts": "<iso8601-now>",
     "target": "<run input>",
     "phase": "<current phase number when the user spoke up>",
     "tag": "<optional, parsed from [brackets]>",
     "text": "<everything after the prefix and optional tag>",
     "applied_at": null,
     "applied_via": null
   }
   ```
3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase 4, tag=4-test-routing): "run targeted unit tests on changed modules"
   ```
4. **Resume** the current phase from where it was. The capture does NOT alter the current run — it only records the suggestion for future review at the audit and threshold-based aggregation later.

**What this is NOT**:

- **NOT a phase override.** "Don't run the live test" without a trigger prefix → Phase 7 resolution flow. With `suggestion:` prefix → captured as a long-term improvement idea but the current run still does whatever its phase logic says.
- **NOT auto-applied.** Captured suggestions live in `run_history.json` for later review. Tier 1 (current): the user manually applies whichever resonate. Future tiers may add tag-based aggregation and threshold-driven proposals; auto-apply is deliberately deferred.
- **NOT a substitute for FAIL counters.** FAIL counters track *what went wrong* (mechanically detected). Suggestions track *what could be better* (user-perceived). They live in different fields and have different lifecycles.

---

## Observer file boundary

This skill includes an observer phase (Phase 10) that writes to `observations.json` and `suggestions.md`. **All other phases (1 through 9) MUST NOT read those files.**

The two files are owned by the observer phase exclusively and exist for cross-run pattern analysis + human review. They are *descriptive* (record what happened across prior runs), not *prescriptive* (do not encode what should happen on this run).

In particular, the agent running domain phases MUST NOT:

- Use `observations.json` content as background context when framing prompts to the user.
- Alter a phase's recommendation, default branching, or option ordering based on prior observations.
- Cite observations to justify a skill behavior in-flight.

The only legitimate path for an observation to change skill behavior is: observer clusters the signal → writes a proposal to `suggestions.md` → human reviews → human edits this `SKILL.md` (or dismisses the proposal). The audit channel and the observer channel remain **isolated by design** — that isolation is what keeps observer's seeded data from silently biasing the skill's defaults.

If you are an LLM/agent running this skill: treat `observations.json` and `suggestions.md` as if they did not exist until you reach Phase 10. Reading them earlier is a load-bearing violation, and there is no FAIL tag for it because the file content is silent — the only safeguard is this rule.

---

## Phase 1 — Parse input + identify target

1. **Detect mode**:
   - Argument matches `^#?\d+$` → `pr` mode (strip leading `#`).
   - Argument looks like a branch name (contains `/` or matches `^(feat|fix|chore|docs|refactor|test)/`) → `branch` mode.
   - No argument → `current` mode (use `git rev-parse --abbrev-ref HEAD`).
2. **Resolve `head` and `base`**:
   - `pr` mode: `gh pr view <num> --json headRefName,baseRefName,url,title,state` — capture `head`, `base` (must equal `BASE_BRANCH` from the config block; warn if not), URL, title.
   - `branch`/`current` mode: `head` = the branch; `base` = `BASE_BRANCH` (assumed; warn if remote-tracking diverges or if a peer config like `.github/PULL_REQUEST_TEMPLATE.md` suggests a different default).
3. **Confirm the branch exists locally and remotely**:
   ```powershell
   git rev-parse --verify "refs/heads/<head>"
   git ls-remote --heads origin <head>
   ```
   If either fails, hard-stop and ask the user how to proceed (push the branch, switch context, abort).
4. **Record the input verbatim** for the audit row — never paraphrase.

## Phase 2 — Clean-merge probe

Verify the feature branch will merge cleanly into `BASE_BRANCH` *as it stands right now*. The probe is read-only — it does NOT touch the working tree or create commits.

1. **Fetch latest base**:
   ```powershell
   git fetch origin <BASE_BRANCH>
   ```
2. **Probe with `git merge-tree`** (the modern three-arg form returns a tree-ish + reports conflicts):
   ```powershell
   git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>
   # Capture exit code and stdout
   ```
   - Exit code `0` and empty stdout → **clean**. Pass.
   - Exit code non-zero OR stdout contains paths → **conflicts**. List the conflicting paths verbatim. Mark FAIL (`2-merge-conflict-not-blocked`) and proceed to Phase 7 with a hard "must resolve before merge" item.
3. **Capture evidence verbatim** for the audit: the command run (with `<BASE_BRANCH>` resolved) and the first/last few lines of output (or "empty stdout, exit 0").

## Phase 3 — Pre-commit-check rules sweep

Apply the project's pre-commit-check rules (resolved from `PRE_COMMIT_RULES_PATH`) to the diff between `origin/<BASE_BRANCH>` and `<head>`. The skill does NOT re-define the rules — it consumes whichever rules file the config points at so updates flow through automatically.

1. **Locate the rules**: walk `PRE_COMMIT_RULES_PATH` in order; `Read` the first existing file. Capture which path was used. If `PRE_COMMIT_RULES_PATH` is empty OR none of the listed paths exist, surface a clear note in the verdict (`"no pre-commit-check rules file found at configured paths; falling back to default checks"`) and run the default checks below.
2. **Default checks** (when no rules file is found):
   - Smoke tests pass (`DEFAULT_TEST_COMMANDS.smoke`).
   - Lint clean on changed files (`DEFAULT_TEST_COMMANDS.lint_python` and/or `DEFAULT_TEST_COMMANDS.lint_frontend`, depending on which file types are in the diff).
   - No protected files staged (configurable per project; common defaults: `CLAUDE.md`, `.gitignore`, top-level docs).
   - **Env-file safety**: detect `.env*` / `*.pem` / `*.key` / `id_rsa` in the diff via `git diff --name-only origin/<BASE_BRANCH>...<head> | Select-String -Pattern '\.env(\.[a-z]+)?$|\.(pem|key)$|id_rsa'`. If any are present, for each file run the env-secret heuristic:

     | Check | What to look for | Trip condition |
     |---|---|---|
     | Secret heuristic | values matching high-entropy ≥32 chars, hex/base64 ≥32 chars, `password=` / `secret=` / `api_key=` with non-placeholder values, or known key prefixes (AKIA, AIza, sk-, etc.) | Any value matches → `6-env-secret-committed` FAIL |
     | Placeholder convention | placeholders use one of: `<your-key-here>`, `change-me`, `REPLACE_ME`, empty string | Real values where placeholder expected → FAIL |
     | `.env.example` sync | when a new var is added to `.env` / `.env.local`, the same var name appears in `.env.example` | Missing → surface to Phase 7 (procedural, not load-bearing) |
     | Naming convention | UPPER_SNAKE_CASE; consistent prefixes for grouped vars | Mixed case or no prefix when peers have one → surface to Phase 7 |
     | `.env.local` not committed when ignored | `.env.local` typically in `.gitignore`; if it IS in the diff, confirm intentional | Staged + ignored → hard surface to Phase 7 |

     If no `.env*` / `*.pem` / `*.key` files are in the diff, record `env-secrets=no-env-files` and skip the heuristic table.
3. **Run each rule against the diff** between `origin/<BASE_BRANCH>` and `<head>`:
   ```powershell
   git diff --name-only origin/<BASE_BRANCH>...<head>
   ```
   For each rule, capture the command run + its output verbatim.
4. **Aggregate outcomes** as a per-rule table for the audit:
   ```
   rules-source=<path|defaults>, smoke=<pass|FAIL+counts>, lint=<pass|FAIL+files>,
   protected=<none|<list>>, ownership=<ok|warn>, safety=<ok|FAIL>,
   env-secrets=<no-env-files|pass|FAIL+files>
   ```
5. Any rule failure → mark Phase 3 FAIL and surface to Phase 7. Env-secret heuristic trips → `6-env-secret-committed` FAIL (counter retained from former Phase 6 — see Phase 8 FAIL detection rules).

## Phase 4 — Relevant-tests run (incl. live UI gate)

Run the test tiers that actually exercise the changed surface — not the full suite. Routing is driven by the config block; project-specific paths and commands live there, not here.

**Test-cache integration**: the project is expected to have wired up the SHA-keyed pytest cache plugin (see `documentation/TEST_CACHE_SETUP.md` in the claude-library plugin). When wired, every pytest command below transparently **deselects tests already passed for the current HEAD SHA on a clean tree** and **records fresh results** to `documentation/test-results/<sha>.json` — no per-tier plumbing needed; the plugin lives in pytest's lifecycle hooks. The cache file is intended to be committed alongside the code change so teammates pulling the same SHA inherit the cache. If the project hasn't opted in, every tier runs the full set unchanged. Each pytest tier below produces a terminal line like `[test-cache] skipped N tests …` or `[test-cache] recorded N results …` (or `[test-cache] disabled: <reason>`); capture that line verbatim into step 4 telemetry.

1. **Compute the changed surface**: `git diff --name-only origin/<BASE_BRANCH>...<head>`. Bucket files by extension and `HIGH_BLAST_PATHS` membership:
   - Frontend (`*.tsx`, `*.ts`, `*.jsx`, `*.js`, `**/frontend/**`): run `DEFAULT_TEST_COMMANDS.lint_frontend && DEFAULT_TEST_COMMANDS.typecheck_frontend`.
   - Backend Python — no match against `HIGH_BLAST_PATHS`, no DB layer touched: run `DEFAULT_TEST_COMMANDS.smoke`.
   - Backend Python — DB / SQL / fixtures (paths matching `**/db/**`, `**/migrations/**`, `**/fixtures/**`): `DEFAULT_TEST_COMMANDS.smoke` + `DEFAULT_TEST_COMMANDS.unit` + `DEFAULT_TEST_COMMANDS.integration` against an isolated DB (test container if the project has one).
   - Backend Python — **high-blast** (any diff path matches a glob in `HIGH_BLAST_PATHS`): run the broader tiers AND the live UI test (`LIVE_UI_TEST_COMMAND`).
   - Migrations (`**/migrations/**` or paths matching the project's migration glob): smoke + integration + alembic up/down round-trip.
2. **Live UI test sub-gate**: if any diff path matches `HIGH_BLAST_PATHS`, the live UI test is **mandatory** unless one of these honest exceptions applies:
   - `LIVE_UI_TEST_COMMAND` is `null` → record `"live UI tier: no infra configured (LIVE_UI_TEST_COMMAND=null)"`. This is NOT a `4-live-test-skipped-without-justification` failure — the skill respects the project's stated absence of live infra.
   - `DEV_STACK_PREFLIGHT_URL` is set AND the preflight call (`curl -fs <DEV_STACK_PREFLIGHT_URL>`) returns non-2xx → record the failed URL + status code, skip cleanly.
   - The user provides an explicit skip reason via Phase 7 (recorded verbatim).

   Skipping without one of these → `4-live-test-skipped-without-justification` FAIL. **The live UI tier should be invoked with `--no-test-cache`** so it always runs fresh — UI tests usually depend on external state (a running dev stack) that the SHA alone doesn't capture.
3. **Optional blast-radius probe**: when any diff path matches `HIGH_BLAST_PATHS`, invoke `claude-library:safe-changes-impact-check` and fold its findings into Phase 5/7. This is a recommendation, not mandatory.
4. **Capture per-tier telemetry** for the audit: tier name, exact command run (with config values resolved), wall-clock, pass count, fail count, skipped count, and the **verbatim `[test-cache] …` line** emitted by the pytest plugin for that tier (or `"[test-cache] not wired"` when the project hasn't opted in).

## Phase 5 — No-new-bugs sweep

This is the principle-anchor — the skill cannot mark Phase 5 `pass` without an observed `Skill` call.

1. **Run `claude-library:code-diagnosis`** on the changed files only — path-scoped, NOT full-repo. The exact tool call must be observable in the session trace; narration is not evidence.

   ```
   Skill(skill="claude-library:code-diagnosis", paths=<list-of-changed-files>)
   ```

2. **Surface findings** in a "Sweep results" block. For each finding: severity, file:line, one-line description.

2a. **Lead with a one-line merge-impact TL;DR** before the per-finding detail. The TL;DR must answer, in a single sentence: `"<N1> items block merge / <N2> items track as follow-up / <N3> items are pure refactoring."` Mapping rule from the sub-skill's triage shape:

   - **"blocks merge"** = bugs (any severity) + smells severity ≥ medium that cite NEW behavior introduced by THIS branch (verify via `git blame <file>:<line>` — was the cited line added in `origin/<BASE_BRANCH>...<head>`?).
   - **"track as follow-up"** = smells that cite pre-existing code OR smells severity = low.
   - **"pure refactoring"** = opportunities.

   Example TL;DR (verbatim format the user can scan in one second):

   ```
   TL;DR — 0 items block merge, 2 items track as follow-up (filed as <tracker-IDs> if accepted), 3 items are pure refactoring.
   ```

   After the TL;DR, render the existing per-finding table — but order sections by merge-impact (blocks-merge first, follow-ups second, refactoring last), NOT by the sub-skill's bug/smell/opportunity order.

3. **Optional**: when Phase 4 step 3 flagged the change as high-blast, also invoke `claude-library:quality-bug-sweep` for the comprehensive scan. Default: skip unless high-blast.
4. **Diff-anomaly check**: for each path in `TRACKER_FILES`, `git diff origin/<BASE_BRANCH>...<head> -- <tracker-path>`. Confirm only expected rows changed; unexpected diffs are surfaced to Phase 7. If `TRACKER_FILES` is empty, skip this step and record `"diff-anomaly check skipped: no TRACKER_FILES configured"`.
4b. **Tracker closure-pairing reconciliation**: for each path in `TRACKER_FILES`, diff the file against `origin/<BASE_BRANCH>`. If the diff *adds* a closure narrative (heuristic: a new paragraph mentioning a tracker ID like `W-*`, `V-*`, `SP-*`, `GAP-NNN` *and* outcome language such as "closed", "fixed", "resolved", "shipped"), confirm that the corresponding tracker row in the project's bug/gap tracker (typically the OTHER `TRACKER_FILE` — e.g. `BUGS_AND_GAPS.md` when `COMPLETED_STREAMS.md` got the closure narrative) was *removed* in the same diff. If the row is still present, surface to Phase 7 as a hard item with FAIL tag `5-tracker-closure-without-row-removal`. If `TRACKER_FILES` has fewer than 2 entries (so there's no "other" tracker to pair against), skip cleanly and record `"tracker closure-pairing skipped: needs >=2 TRACKER_FILES"`.
5. Any item in the **"blocks merge"** bucket of the TL;DR → mark Phase 5 FAIL and surface to Phase 7. Items in **"track as follow-up"** or **"pure refactoring"** do NOT auto-route to Phase 7 — they are informational unless the user explicitly asks to fix-now or to register as a gap.

## Phase 6 — (reserved — folded into Phase 3)

Phase 6 was previously a standalone `.env` / `.env.local` review. Empirically it produced "no env files in diff (trivial pass)" on every recorded run since 2026-05-07 (six consecutive runs across diverse branches; `6-env-secret-committed` counter never tripped). Per the 2026-05-15 observer convergence proposal, the env-secret heuristic was folded into Phase 3's safety sub-step (where protected-files, migration-number, and personal-file checks already live) so the audit no longer renders a separate phase row for what is almost always a no-op.

The load-bearing FAIL tag `6-env-secret-committed` is **preserved** for counter continuity — its detection logic now runs as part of Phase 3 step 2's env-file safety check, and Phase 8's audit row for Phase 3 reports `env-secrets=<no-env-files|pass|FAIL+files>`.

This phase number is intentionally left as a reserved placeholder rather than re-numbered (Phase 7→6, etc.) to avoid breaking external references to Phase 7/8/9/10. Skip directly to Phase 7.

## Phase 7 — User resolution gate (HARD-STOP before audit)

Before the audit can run, every unresolved item from Phases 1–5 must be addressed by an explicit user choice. The skill is bad at judging "fine to skip"; the user knows what they care about.

1. **List every unresolved item** in a numbered table. Sources: Phase 2 conflicts, Phase 3 rule failures (incl. env-file safety / env-secret heuristic trips, folded from former Phase 6), Phase 4 test failures or skipped tiers, Phase 5 diagnosis findings, plan deviations.

   ```
   Unresolved items before verdict:
   1. [phase 2] merge conflict in services/orchestrator.py:142
   2. [phase 4] live UI tier skipped — diff touches routes.py:67
   3. [phase 5] code-diagnosis flagged unused import in tools/foo.py:1 (low)
   4. [phase 3] .env.local has API_KEY=sk-real-looking-value (env-secret heuristic FAIL)
   ```

2. **For each item, ask the user explicitly** for a choice from this set.

   **Recommendation gate (before listing options)**: when a surfaced item meets ALL of the following preconditions, the skill MUST default-recommend `fix-now` and list it as the first option visually:

   - the fix touches ≤ 15 lines AND
   - the fix is in code or docs only (no schema migrations, no infra config, no security boundary) AND
   - a re-run of the relevant test tier after the fix is feasible within this session (smoke tier ≤ 60s) AND
   - the fix description is one of: missing-import, deprecation comment update, follow-up tracker row, removed-dead-code, narrow exception handler, fail-loud assertion.

   When the recommendation gate fires, the option block must read:

   1. **Fix it now (recommended)** — <one-line description>
   2. Skip with logged justification
   3. Block the merge
   4. Abort the run

   When the recommendation gate does NOT fire (any precondition fails), the existing symmetric four-option list is used and the skill does not recommend a default:

   - **block the merge** — verdict will be RED. Skill records the reason and proceeds to audit.
   - **fix it now** — user describes the fix; skill applies it (or asks the user to apply); loops back to the originating phase.
   - **skip with logged justification** — user provides a one-line reason. Recorded verbatim in the audit and the run-history ledger.
   - **abort the run** — clean exit; no verdict produced.

3. **Loop until the user explicitly types "proceed to audit"** (or equivalent literal token). Silence, "looks good", "ok" do NOT advance.

4. **Empty list is the only auto-pass.** If Phases 1–5 all reported `pass` with zero unresolved items, print "No unresolved items — proceeding to audit" and continue. Do not invent items; do not skip the print.

5. **Record the user's input verbatim** for the audit row. Quote literal strings, never paraphrase intent.

---

## Phase 8 — Pre-action self-audit (CHECKPOINT, blocking)

The audit runs **before** the print. Print cannot fire until the user explicitly confirms or corrects every audit row. Goal: verbatim, falsifiable evidence — never the skill's interpretation of user intent.

1. **Walk every phase that ran in this session** and emit a structured block. Each verdict MUST cite **objective evidence**: a tool call observed, a command output, a file diff, or a **literal quote** from the user. **Never paraphrase user input.** If the user said "merge approved" with no per-item resolution, record `user said: "merge approved" (no per-item resolution)` — do NOT invent a justification, do NOT summarise intent.

   ```
   Self-audit for run on <input> at <ts>:

   | Phase | Status | Evidence |
   |-------|--------|----------|
   | 1 | pass | input parsed: <mode> <target>; user input verbatim: "<literal quote>" |
   | 2 | pass | git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>: exit=<code>; conflicts: <none\|<paths>> |
   | 3 | pass\|FAIL | rules-source=<resolved PRE_COMMIT_RULES_PATH or "defaults">; outcomes: smoke=<...>, lint=<...>, protected=<...>, ownership=<...>, safety=<...>, env-secrets=<no-env-files\|pass\|FAIL+files> |
   | 4 | pass\|FAIL | tiers run: <list>; results: <pass/fail/skipped per tier>; test-cache: <verbatim lines or "not wired">; live UI: <ran\|skipped + reason> |
   | 5 | pass\|FAIL | claude-library:code-diagnosis Skill call observed: <yes/no>; findings: <count> at <file:line list> |
   | 7 | pass\|FAIL | unresolved items: <N surfaced> / <M resolved-with-explicit-choice>; user input verbatim: "<literal quote>" |
   ```

   Phase 6 is intentionally omitted from the audit table — the env-secret heuristic was folded into Phase 3's safety sub-step on 2026-05-16 (see Phase 6 reserved note). Its outcome appears as the `env-secrets=` segment of the Phase 3 row.

   Each row is a markdown-table row with three columns: `| Phase X | pass|FAIL | <evidence> |` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input. Long evidence strings stay on a single logical line (the table cell) and the markdown renderer wraps them; bulleted line-wrapping in terminals breaks readability when evidence approaches 100+ chars.

2. **FAIL detection rules** — these trigger automatically; the skill cannot mark `pass` without satisfying them:

   **Universal FAIL rules** (every self-learning skill inherits these):
   - **`audit-paraphrased-user-input`** (load-bearing, threshold=1): any audit row that paraphrases user intent rather than quoting verbatim.
   - **`audit-no-explicit-approval-wait`** (procedural, threshold=2): skill advanced past a user-gate phase without observing the literal approval token.
   - **`tool-claim-without-call`** (load-bearing, threshold=1): audit row says "ran X" / "invoked Y" but no corresponding tool call observed in this session.

   **Domain FAIL rules** (specific to this skill):

   - **`2-merge-conflict-not-blocked` FAIL** (load-bearing, threshold=1): Phase 2 marked `pass` but `git merge-tree` output contains conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) OR exit code was non-zero.
   - **`4-live-test-skipped-without-justification` FAIL** (load-bearing, threshold=1): live UI test skipped AND any diff path matches a glob in `HIGH_BLAST_PATHS` AND `LIVE_UI_TEST_COMMAND` is non-null AND no user-provided skip reason recorded AND `DEV_STACK_PREFLIGHT_URL` preflight (when set) did NOT explicitly fail.
   - **`5-code-diagnosis-narration-only` FAIL** (load-bearing, threshold=1): Phase 5 narrated diagnosis findings without an observed `Skill(skill="claude-library:code-diagnosis", ...)` tool call in this session.
   - **`5-tracker-closure-without-row-removal` FAIL** (load-bearing, threshold=1): Phase 5 sub-step 4b detected a closure narrative added to one `TRACKER_FILE` without a matching row removal in the paired tracker. Load-bearing because it defeats the documentation-implementation pairing invariant.
   - **`5-findings-table-needs-severity-provenance-columns` FAIL** (procedural, threshold=2): Phase 5 surfaced code-diagnosis findings without a one-line merge-impact TL;DR header (the `"<N1> blocks merge / <N2> track as follow-up / <N3> pure refactoring"` sentence) preceding the per-finding table. Threshold=2 because a single occurrence may be the skill's first run on a new project; two means the TL;DR rule is drifting.
   - **`6-env-secret-committed` FAIL** (load-bearing, threshold=1, evaluated within Phase 3 step 2's env-file safety sub-step): diff added a `.env*` line whose value matches the secret heuristic (high-entropy ≥32 chars, contains `password=`/`secret=`/`api_key=` with non-placeholder value, hex/base64 strings ≥32 chars, or known key prefixes such as AKIA / AIza / sk-) rather than a placeholder. Tag retained for counter continuity after the standalone Phase 6 was folded into Phase 3 on 2026-05-16.
   - **`7-implicit-skip-no-justification` FAIL** (load-bearing, threshold=1): `surfaced > resolved-with-explicit-choice`. Count = (surfaced − resolved).
   - **`7-recommendation-gate-not-applied` FAIL** (procedural, threshold=2): Phase 7 surfaced an item meeting all four `Fix it now (recommended)` preconditions but did NOT mark fix-now as recommended in the option block. Threshold=2 because a single occurrence may be a borderline precondition call; two means the gate logic is drifting.

3. **Show the audit and ask the user to confirm OR correct every row.** The audit is NOT approved on silence or partial answer. The skill must wait for the user to:
   - **confirm** each row as written, OR
   - **dictate corrections** (which the skill applies verbatim and re-displays the audit), OR
   - **mark a row FAIL with a tag** (which the skill records).

4. **Approval gate**: the print phase cannot fire until the user explicitly types `merge approved` (case-insensitive). Silence, "looks good", "ok", "proceed", or partial responses are NOT approval.

5. **Suggestion review (final-call)** — *runs only after approval token is received, before Phase 9 fires*. Surface every entry captured during this run via the Mid-run suggestion capture protocol, then offer the user a final chance to add more:

   ```
   Suggestions captured during this run (N total):
     1. [phase 4, tag=4-test-routing] "run targeted unit tests on changed modules"
     2. [phase 6, no tag]              "add Stora Enso internal token regex"
     3. [phase 7, tag=7-batch-resolve] "let user resolve multiple items as a batch"

   Any final suggestions to add? Use the same trigger-prefix syntax (or type `done` to skip):
     - suggestion: <text>
     - improvement: <text>
     - for the skill: <text>
     - [suggestion] <text>
   ```

   Append any final entries to `improvement_suggestions[]` with the same shape as mid-run captures; the `phase` field for these final-call entries is `"audit"`. If the user types `done` (or equivalent literal token), proceed to Phase 9. If the user adds more, capture each, then re-prompt until `done`. Silence is NOT advancement — wait for `done`.

After the suggestion review (whether anything was added or not), the skill prints the structured verdict (GREEN — proceed to merge | RED — blocked, with reasons) and ends. The user runs the actual `git merge` / `gh pr merge` manually.

## Phase 9 — Update the run-history ledger

Persist the audit so failure patterns become evidence over time.

1. **Read** `skills/pr-merge-readiness/run_history.json`. Initialize if missing per the schema in `library/templates/self-learning-skill/run_history_schema_v1.md`. Use the seed FAIL rules from that schema doc as the starting `fail_counters`.

2. **Append** the run summary to `runs[]`:
   ```json
   {"ts": "<iso8601>", "target": "<input>", "outcome": "<closed|paused|aborted|in-progress>", "phases_failed": ["<tag>", ...]}
   ```

3. **For each FAIL tag** observed in this run:
   - Increment `fail_counters[<tag>].count` by 1.
   - Append to `fail_counters[<tag>].occurrences[]`: `{ts, target, detail}` where `detail` is a one-line description of the specific occurrence (what command ran, what evidence was missing, what user input was paraphrased — be concrete).
   - If the tag is new, create the entry. Pick `threshold` by phase severity:
     - **Load-bearing phase** → threshold = **1** (fix on first occurrence; the failure defeats a core principle).
     - **Procedural phase** → threshold = **2** (one is noise; two is drift).
     - **Cosmetic phase** → threshold = **5** (low cost; wait for a clear pattern).

4. **Persist captured suggestions**. Any entries added to `improvement_suggestions[]` during this run (mid-run captures + Phase 8 step 5 final-call entries) are written to the ledger as part of the same `Write` call. The array is append-only — never overwrite or drop existing entries.

5. **Write the file** with the `Write` tool. The verdict-print already happened in Phase 8 — leave the ledger update unstaged for the user to commit alongside any manual cleanup.

6. **Print run-end summary** including suggestions:
   ```
   Run summary: outcome=<closed|paused|aborted>, FAIL tags=<count>, suggestions=<this-run-count> (total log: <all-time-count>)
   Review suggestions at: skills/pr-merge-readiness/run_history.json → improvement_suggestions[]
   ```

7. **Threshold check** — for any counter where `count >= threshold`:
   - Print a **fix proposal** block: the failure pattern, the recommended SKILL.md edit (specific file + line + before/after diff drawn from `remediation_hint`), the tag.
   - **Apply automatically** (Mode B): make the SKILL.md edit. The user reviews the change in their normal commit-review loop.
   - After applying: reset the counter to 0; set `applied_at` to the current timestamp; optionally fill `applied_via` with a one-line description of the structural change made.
   - **Conflict handling**: if multiple tags trip in the same run, apply remediations serially (oldest tag first by `occurrences[0].ts`). Surface conflicts to the user — never silently overwrite a remediation that another tag just wrote.

## Phase 10 — Post-ledger observer (suggestion-only, retrofitted prototype)

The observer runs **after** the ledger has written `run_history.json` and any audit-tripped remediations have been auto-applied. Its job is to surface qualitative signals the audit's mechanical FAIL detection cannot catch, and — once enough observations accumulate — propose changes for manual review.

The observer NEVER edits `SKILL.md`. It writes only to `observations.json` (per-run notes) and `suggestions.md` (clustered proposals). The user reviews `suggestions.md` and decides whether to integrate any proposal.

This phase is OPTIONAL and was retrofitted to this skill from `library/templates/self-learning-skill/observer-phase.md`. See `documentation/SELF_LEARNING_SKILLS.md` for design details. It is bolted in as a prototype; if the pattern proves valuable, the planned next step is to lift the observer body out into a standalone `meta-observer-review` skill or a `Stop` hook.

1. **Read state**:
   - `skills/pr-merge-readiness/observations.json` — initialize per the schema if missing. This file was bootstrapped with seed entries derived from a paper retrospective on runs 1–2 of `run_history.json` (see `documentation/OBSERVER_RETROSPECTIVE_PR_MERGE_READINESS.md`).
   - `skills/pr-merge-readiness/run_history.json` — for the run that just finished (last entry in `runs[]`) and prior runs (for cross-run context, including `friction_log[]` and `improvement_suggestions[]`).

2. **Walk the just-finished run from a different vantage than the audit.** The audit reports mechanical FAIL conditions; the observer looks for qualitative signals the audit was never told to look for. Categories to scan for (extend per skill, never invent observations to fill space):

   | Category slug | What to look for | Example signal (from this skill's history) |
   |---|---|---|
   | `user_friction` | re-asked questions, repeated corrections, "no, I meant", visible frustration | user typed three corrections to the same audit row before approving |
   | `redundant_phase` | phase Y duplicates phase X's output; user explicitly skipped a phase | Phase 4 surfaced findings already listed in Phase 3 |
   | `scope_drift` | the skill ventured outside its frontmatter `description` | a merge-readiness skill started auto-fixing code |
   | `missing_audit_category` | a recurring qualitative concern with no FAIL tag covering it | tracker-file diff anomaly noted by user but not by any audit row |
   | `dev_env_friction` | environmental setup pain that recurs across runs | "stale container missing dep" mentioned in two runs' notes |
   | `output_format_quality` | UX-only signal: format/readability of the skill's output | audit row evidence string too long to scan visually |
   | `cross_phase_redundancy` | two phases share evidence the user only had to provide once | Phase 1 and Phase 3 both quoted the same user input |
   | `boundary_violation` | a domain phase (1–9) referenced or used content from `observations.json` / `suggestions.md` (which it must not read) | Phase 2's user prompt framing visibly originated in observer-file content; the skill cited a prior observation in-flight to justify a recommendation |

3. **Append observations** to `observations.json`. Each observation MUST cite verbatim evidence — never paraphrase user input. **Zero observations is a valid output.** Do NOT invent signals to demonstrate the observer is doing work.

   Each observation row:
   ```json
   {
     "ts": "<iso8601-now>",
     "run_ref": "<ts of the matching runs[] entry in run_history.json>",
     "target": "<run input>",
     "category": "<slug from the table above, or new slug if a novel signal>",
     "_theme_slug": "<optional sub-theme slug for theme-similarity check; lowercase-hyphenated, stable forever; omit when the parent category alone is sufficient>",
     "phase": "<phase number where signal appeared, or 'cross-phase'>",
     "evidence": "<verbatim quote / observed event>",
     "interpretation": "<one-line reasoning for why this signal matters>",
     "proposed_audit_tag": "<optional new FAIL tag the audit could track, or null>"
   }
   ```

4. **Cross-run clustering check** — for each category in `observations.json`:
   - Count entries whose `applied_at` (in any subsequent `review_log` entry) is null.
   - If `count >= 3`, this category trips a proposal pass.
   - **Convergence rule (overrides threshold)**: if observer recorded ≥1 unaddressed observation in a category AND `run_history.json:improvement_suggestions[]` contains a user-typed entry whose `tag` or `text` matches the same theme, treat the category as cluster-tripped regardless of count. Two independent channels agreeing is stronger evidence than 3 same-channel observations. When the convergence rule trips, the proposal in `suggestions.md` MUST cite both the observation `ts` values AND the matching `improvement_suggestions[]` entry verbatim.
   - **Theme-similarity check (before writing a proposal)**: a single category often contains observations describing distinct underlying themes (e.g., `missing_audit_category` covering both "tracker-closure-drift" and "skipped-test-rationale"). Before writing a proposal, group the observations within the tripped category by underlying theme — same root-cause, same recommended remediation. Only sub-clusters with count ≥ 3 (or convergence) trigger a proposal. Sub-clusters below threshold remain in `observations.json` until they grow. Do NOT lump unrelated themes into one proposal.

5. **Write proposal to `suggestions.md`** for each tripped (sub-)cluster:
   - Append a new section with the clustered theme (one line), the observations as evidence (verbatim, with `ts` references), the observer's interpretation, and a specific proposed `SKILL.md` edit (or "no specific edit yet — propose new audit tag `<slug>`").
   - Status: `unreviewed`. The user manually flips this to `applied` or `dismissed` after reading.

   Proposal format (markdown):
   ```markdown
   ## <iso8601-date> — Theme: <clustered theme>

   **Pattern observed in N runs:**
   - <run 1 ts>: <verbatim evidence>
   - <run 2 ts>: <verbatim evidence>
   - <run 3 ts>: <verbatim evidence>

   **Interpretation:** <observer's one-paragraph reasoning>

   **Proposed change to SKILL.md:**
   - <specific edit suggestion: file + section + before/after>, OR
   - "No specific edit; recommend adding a new audit FAIL tag `<slug>` covering <condition>."

   **Status:** unreviewed
   **Applied at:** null
   **Applied via:** null
   ```

6. **Append to `review_log[]`** in `observations.json`:
   ```json
   {
     "ts": "<iso8601-now>",
     "trigger": "threshold | manual",
     "clustered_theme": "<short description>",
     "category": "<the category slug that tripped>",
     "observations_referenced": ["<ts1>", "<ts2>", "<ts3>"],
     "suggestion_written_to": "skills/pr-merge-readiness/suggestions.md",
     "applied_at": null,
     "applied_via": null
   }
   ```

7. **Print observer summary**:
   ```
   Observer: <count> new observations recorded; <count> proposals written to suggestions.md (<unreviewed-total> unreviewed in log)
   ```

8. **Hard limits** (do NOT relax these without revisiting the design doc):
   - Observer NEVER edits `SKILL.md`. Only `observations.json` and `suggestions.md`.
   - Observer NEVER paraphrases user input — verbatim quotes only, same rule the audit enforces.
   - Observer NEVER invents observations to demonstrate value. Zero observations is a valid run.
   - Observer NEVER auto-applies a proposal. `suggestions.md` is read-write for the human, not the skill.
   - Observer NEVER writes to `run_history.json` **with one narrow exception**: when an observation's category is `dev_env_friction`, the observer MAY append a single corresponding entry to `run_history.json:friction_log[]`. This is permitted because the schema's `friction_log` field exists exactly for this signal class, and environmental friction has no SKILL.md edit that fixes it — `suggestions.md` is the wrong destination. Observer touches NO other field of `run_history.json`.
   - Observer DOES NOT block the run from closing. By the time it fires, the ledger has already written and the verdict-print is done. If the observer errors, the run is still considered closed.

---

## Edge cases

1. **PR or branch resolves to base ≠ `dev`**: warn the user. The skill's load-bearing principle assumes `dev` is the merge target; allow override via explicit user confirmation, but require a quote for the audit.
2. **Branch only exists locally (no remote)**: Phase 1 step 3 hard-stops; the skill needs `origin/<head>` for `git merge-tree`. User pushes the branch first or aborts.
3. **No `.env*` files in diff**: Phase 3's env-file safety sub-step (folded from former Phase 6) records `env-secrets=no-env-files` and the audit emits no separate phase row. Do not invent issues to surface.
4. **No `claude-library:code-diagnosis` available** (e.g., plugin not loaded): hard-stop in Phase 5 with a clear message — the load-bearing principle CANNOT be satisfied without the call. Tell the user how to load the plugin.
5. **User's project has its own pre-commit-check skill under a different name**: edit `PRE_COMMIT_RULES_PATH` in the config block to point at the project's actual rules file. Do NOT ask at runtime — the config is the single place to change this.
6. **Live UI test infrastructure not present in the project**: Phase 4 step 2 records "no live UI test infrastructure found"; this is NOT a `4-live-test-skipped-without-justification` failure — the rule applies only when the test exists and was skipped.
7. **User aborts at Phase 7 or Phase 8**: clean exit. Run-history ledger still gets a `runs[]` entry with `outcome: "aborted"` and the phases that failed. No verdict printed.

## Plugin skills composed by this skill

| Skill | Phase | Trigger |
|---|---|---|
| `claude-library:code-diagnosis` | 5 | Always, path-scoped on changed files (load-bearing) |
| `claude-library:safe-changes-impact-check` | 4 | Only if diff touches high-blast surfaces (orchestrator, MCP, routes, migrations, registries, settings, auth) |
| `claude-library:quality-bug-sweep` | 5 | Optional, only if Phase 4 flagged the change as high-blast |

**Not composed** (deliberate):
- `commit-ready` — different terminal action (commit, not verdict-print) and different scope (single working tree, not branch-vs-base).
- `planning-impl-plan` — this skill is a verifier, not a planner; nesting would loop.
- `safe-changes-refactor-safe` — this skill validates an already-implemented branch; refactor invariants belong upstream.

## Out of scope

- **Running the merge**: the skill prints a verdict; the user runs `git merge` / `gh pr merge` manually.
- **PR creation**: assumes the PR (or branch) already exists.
- **GitHub Actions / CI integration**: results from CI are not consumed; the skill runs its own probes.
- **Linear / Jira sync**: the verdict is printed only; no external sync.
- **Auto-fixing surfaced issues**: Phase 7 lets the user pick `fix it now` and apply manually; the skill never silently rewrites code.

## Usage

Tell Claude one of:

```
/pr-merge-readiness 123                            # PR mode
/pr-merge-readiness #123                           # PR mode (with hash)
/pr-merge-readiness feat/gap-002-tool-registry     # branch mode
/pr-merge-readiness                                # current branch
```

The skill walks Phases 1–9 and asks for explicit approval before printing the verdict. Failure patterns accumulate in `run_history.json`; when a counter trips its threshold, the skill auto-edits its own SKILL.md per the `remediation_hint` and the user reviews the edit in their normal commit-review loop.

---

## Self-learning checklist (before shipping)

Before the first invocation of this skill, verify:

- [ ] `run_history.json` exists at the skill's root, initialized with the universal seed FAIL rules from `library/templates/self-learning-skill/run_history_schema_v1.md` ("Initial state" section) plus the 5 domain rules listed in Phase 8.
- [ ] The audit phase (Phase 8) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every phase that consumes user input (Phases 1 and 7) has a row format that records the input **verbatim**, never paraphrased.
- [ ] The verdict-print requires the literal `merge approved` token — silence, "ok", "looks good" do NOT advance.
- [ ] At least one domain FAIL rule exists (5 are seeded).
- [ ] Threshold tiers match phase severity: load-bearing=1, procedural=2, cosmetic=5.
- [ ] The ledger phase (Phase 9) is the last phase. No phase fires after it.
