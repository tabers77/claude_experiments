---
name: pr-merge-readiness
description: Validate a feature branch is ready to merge into dev — clean merge, pre-commit-check rules pass, relevant tests pass (incl. live UI when applicable), no-new-bugs sweep, and any .env/.env.local additions follow best practices. The skill emits a structured verdict — it does NOT run the merge. Keywords PR merge readiness feature branch dev clean merge pre-commit no-new-bugs live test env env.local best practices verdict approval gate.
metadata:
  pattern: self-learning
  schema-version: 1
---

# PR Merge Readiness

End-to-end pre-merge validation for a feature branch targeting `dev`. The skill walks six gates — clean-merge probe, pre-commit-check rules, relevant-tests run, no-new-bugs sweep, env-file review, and explicit user resolution — then emits a structured verdict. It NEVER runs `git merge` or `gh pr merge`; the user takes that step manually after reading a green verdict.

**Load-bearing principle**: the merge is approved only when all six gates produce verbatim, falsifiable evidence: clean-merge proof, pre-commit-check rules, relevant-tests pass (incl. live UI when applicable), no-new-bugs sweep, env-file review, and explicit user resolution of every surfaced item.

## Inputs

The user invokes the skill with one of:

| Shape | Example | Mode |
|---|---|---|
| PR number | `123` or `#123` | `pr` |
| Branch name | `feat/gap-002-tool-registry` | `branch` |
| (no arg) | uses current branch | `current` |

If the input is none of the above, dump the current branch name and `gh pr list --head <current>` and ask the user to pick a real target. Do not guess.

---

## Phase 1 — Parse input + identify target

1. **Detect mode**:
   - Argument matches `^#?\d+$` → `pr` mode (strip leading `#`).
   - Argument looks like a branch name (contains `/` or matches `^(feat|fix|chore|docs|refactor|test)/`) → `branch` mode.
   - No argument → `current` mode (use `git rev-parse --abbrev-ref HEAD`).
2. **Resolve `head` and `base`**:
   - `pr` mode: `gh pr view <num> --json headRefName,baseRefName,url,title,state` — capture `head`, `base` (must be `dev`; warn if not), URL, title.
   - `branch`/`current` mode: `head` = the branch; `base` = `dev` (assumed; warn if remote-tracking diverges).
3. **Confirm the branch exists locally and remotely**:
   ```powershell
   git rev-parse --verify "refs/heads/<head>"
   git ls-remote --heads origin <head>
   ```
   If either fails, hard-stop and ask the user how to proceed (push the branch, switch context, abort).
4. **Record the input verbatim** for the audit row — never paraphrase.

## Phase 2 — Clean-merge probe

Verify the feature branch will merge cleanly into `dev` *as it stands right now*. The probe is read-only — it does NOT touch the working tree or create commits.

1. **Fetch latest dev**:
   ```powershell
   git fetch origin dev
   ```
2. **Probe with `git merge-tree`** (the modern three-arg form returns a tree-ish + reports conflicts):
   ```powershell
   git merge-tree --write-tree --name-only origin/dev <head>
   # Capture exit code and stdout
   ```
   - Exit code `0` and empty stdout → **clean**. Pass.
   - Exit code non-zero OR stdout contains paths → **conflicts**. List the conflicting paths verbatim. Mark FAIL (`2-merge-conflict-not-blocked`) and proceed to Phase 7 with a hard "must resolve before merge" item.
3. **Capture evidence verbatim** for the audit: the command run and the first/last few lines of output (or "empty stdout, exit 0").

## Phase 3 — Pre-commit-check rules sweep

Apply the rules from `shared-pre-commit-check` (or the project's local equivalent) to the diff between `origin/dev` and `<head>`. The skill does NOT re-define the rules — it consumes the existing skill's body so updates flow through automatically.

1. **Locate the rules**: `Read` `shared-pre-commit-check.md` (or `.claude/skills/shared-pre-commit-check.md`) if present in the project. If absent, surface a clear note in the verdict ("no shared-pre-commit-check found; falling back to default checks") and run the default checks below.
2. **Default checks** (when no project-specific rules file is found):
   - Smoke tests pass (`pytest -m smoke` or project equivalent).
   - Lint clean on changed files (`ruff check`, `npm run lint`, etc.).
   - No protected files staged (configurable per project; common defaults: `CLAUDE.md`, `.gitignore`, top-level docs).
   - No secrets/credentials staged (`.env`, `.env.local`, `*.pem`, `id_rsa`, etc.).
3. **Run each rule against the diff** between `origin/dev` and `<head>`:
   ```powershell
   git diff --name-only origin/dev...<head>
   ```
   For each rule, capture the command run + its output verbatim.
4. **Aggregate outcomes** as a per-rule table for the audit:
   ```
   smoke=<pass|FAIL+counts>, lint=<pass|FAIL+files>,
   protected=<none|<list>>, ownership=<ok|warn>, safety=<ok|FAIL>
   ```
5. Any rule failure → mark Phase 3 FAIL and surface to Phase 7.

## Phase 4 — Relevant-tests run (incl. live UI gate)

Run the test tiers that actually exercise the changed surface — not the full suite (per the same routing philosophy as `shared-bug-gap-fix` Phase 6).

1. **Compute the changed surface**: `git diff --name-only origin/dev...<head>`. Bucket files by extension and path:
   - Frontend (`frontend/src/`, `*.tsx`, `*.ts`): run `npm run lint && npm run typecheck` (no frontend test infra unless one is configured).
   - Backend Python — pure logic, no DB: `pytest -m smoke`.
   - Backend Python — DB / SQL / fixtures: `pytest -m "smoke or unit or integration"` against an isolated DB (test container if the project has one).
   - Backend Python — high-blast (`routes.py`, `services/orchestrator.py`, `mcp/`, registries, tool definitions): also run the live UI test (e.g. `pytest -m live -v <live-workflow-test>`).
   - Migrations (`db/migrations/`): smoke + integration + alembic up/down round-trip.
2. **Live UI test sub-gate**: if the diff touches any UI-exercising backend code path (`routes.py`, `services/orchestrator.py`, `mcp/`, tool definitions registered in the live workflow), the live UI test is **mandatory** unless:
   - The dev stack preflight check fails (e.g., `curl -fs http://localhost:8000/<healthcheck>` returns non-2xx) — skip cleanly with a note ("live UI tier skipped: dev stack unreachable, preflight failed at <url>").
   - The user provides an explicit skip reason (recorded verbatim in Phase 7 resolution gate).
   Skipping without one of these → `4-live-test-skipped-without-justification` FAIL.
3. **Optional blast-radius probe**: when the diff touches high-blast surfaces, invoke `claude-library:safe-changes-impact-check` and fold its findings into Phase 5/7. This is a recommendation, not mandatory.
4. **Capture per-tier telemetry** for the audit: tier name, command run, wall-clock, pass count, fail count, skipped count.

## Phase 5 — No-new-bugs sweep

This is the principle-anchor — the skill cannot mark Phase 5 `pass` without an observed `Skill` call.

1. **Run `claude-library:code-diagnosis`** on the changed files only — path-scoped, NOT full-repo. The exact tool call must be observable in the session trace; narration is not evidence.

   ```
   Skill(skill="claude-library:code-diagnosis", paths=<list-of-changed-files>)
   ```

2. **Surface findings** in a "Sweep results" block. For each finding: severity, file:line, one-line description.
3. **Optional**: when Phase 4 step 3 flagged the change as high-blast, also invoke `claude-library:quality-bug-sweep` for the comprehensive scan. Default: skip unless high-blast.
4. **Diff-anomaly check**: `git diff origin/dev...<head> -- <project-tracker-file>` (e.g. `documentation/implementation_docs/BUGS_AND_GAPS.md` if the project uses a tracker). Confirm only expected rows changed; unexpected diffs are surfaced to Phase 7.
5. Any new finding (especially severity ≥ medium) → mark Phase 5 FAIL and surface to Phase 7. The user — not the skill — decides whether to skip, fix, or track.

## Phase 6 — `.env` / `.env.local` review

Fires only when the diff touches `.env*` files. Otherwise: pass trivially with `env files in diff: no`.

1. **Detect env files in the diff**:
   ```powershell
   git diff --name-only origin/dev...<head> | Select-String -Pattern '\.env(\.[a-z]+)?$'
   ```
2. **For each env file in the diff**, run all the checks below and capture outcomes verbatim:

   | Check | What to look for | Trip condition |
   |---|---|---|
   | Secret heuristic | values that look like real secrets (high-entropy ≥32 chars, hex/base64 strings, `password=` / `secret=` / `api_key=` with non-placeholder values) | Any value matches → `6-env-secret-committed` FAIL |
   | Placeholder convention | placeholders use one of: `<your-key-here>`, `change-me`, `REPLACE_ME`, empty string | Real values present where placeholder expected → FAIL |
   | `.env.example` sync | when a new var is added to `.env`/`.env.local`, the same var name appears in `.env.example` | Missing → surface to Phase 7 (procedural, not load-bearing) |
   | Naming convention | UPPER_SNAKE_CASE; consistent prefixes for grouped vars | Mixed case or no prefix when peers have one → surface to Phase 7 |
   | `.env.local` not committed when ignored | `.env.local` typically in `.gitignore`; if it IS in the diff, confirm intentional | Staged + ignored → hard surface to Phase 7 |

3. **Summarize for the audit**:
   ```
   env files in diff: <list>
   secrets heuristic: <pass|FAIL + offending file:line>
   placeholder convention: <pass|FAIL>
   .env.example sync: <ok|missing-vars: <list>>
   ```

## Phase 7 — User resolution gate (HARD-STOP before audit)

Before the audit can run, every unresolved item from Phases 1–6 must be addressed by an explicit user choice. The skill is bad at judging "fine to skip"; the user knows what they care about.

1. **List every unresolved item** in a numbered table. Sources: Phase 2 conflicts, Phase 3 rule failures, Phase 4 test failures or skipped tiers, Phase 5 diagnosis findings, Phase 6 env-review issues, plan deviations.

   ```
   Unresolved items before verdict:
   1. [phase 2] merge conflict in services/orchestrator.py:142
   2. [phase 4] live UI tier skipped — diff touches routes.py:67
   3. [phase 5] code-diagnosis flagged unused import in tools/foo.py:1 (low)
   4. [phase 6] .env.local has API_KEY=sk-real-looking-value (looks like secret)
   ```

2. **For each item, ask the user explicitly** for a choice from this set:
   - **block the merge** — verdict will be RED. Skill records the reason and proceeds to audit.
   - **fix it now** — user describes the fix; skill applies it (or asks the user to apply); loops back to the originating phase.
   - **skip with logged justification** — user provides a one-line reason. Recorded verbatim in the audit and the run-history ledger.
   - **abort the run** — clean exit; no verdict produced.

3. **Loop until the user explicitly types "proceed to audit"** (or equivalent literal token). Silence, "looks good", "ok" do NOT advance.

4. **Empty list is the only auto-pass.** If Phases 1–6 all reported `pass` with zero unresolved items, print "No unresolved items — proceeding to audit" and continue. Do not invent items; do not skip the print.

5. **Record the user's input verbatim** for the audit row. Quote literal strings, never paraphrase intent.

---

## Phase 8 — Pre-action self-audit (CHECKPOINT, blocking)

The audit runs **before** the print. Print cannot fire until the user explicitly confirms or corrects every audit row. Goal: verbatim, falsifiable evidence — never the skill's interpretation of user intent.

1. **Walk every phase that ran in this session** and emit a structured block. Each verdict MUST cite **objective evidence**: a tool call observed, a command output, a file diff, or a **literal quote** from the user. **Never paraphrase user input.** If the user said "merge approved" with no per-item resolution, record `user said: "merge approved" (no per-item resolution)` — do NOT invent a justification, do NOT summarise intent.

   ```
   Self-audit for run on <input> at <ts>:
   - Phase 1 [pass]      | input parsed: <mode> <target>; user input verbatim: "<literal quote>"
   - Phase 2 [pass|FAIL] | git merge-tree --write-tree --name-only origin/dev <head>: exit=<code>; conflicts: <none|<paths>>
   - Phase 3 [pass|FAIL] | shared-pre-commit-check rule outcomes: smoke=<...>, lint=<...>, protected=<...>, ownership=<...>, safety=<...>
   - Phase 4 [pass|FAIL] | tiers run: <list>; results: <pass/fail/skipped counts per tier>; live UI: <ran|skipped + reason>
   - Phase 5 [pass|FAIL] | claude-library:code-diagnosis Skill call observed: <yes/no>; findings: <count> at <file:line list>
   - Phase 6 [pass|FAIL] | env files in diff: <yes/no>; if yes: secrets-heuristic=<pass|FAIL+evidence>, placeholder=<pass|FAIL>, .env.example sync=<ok|missing>
   - Phase 7 [pass|FAIL] | unresolved items: <N surfaced> / <M resolved-with-explicit-choice>; user input verbatim: "<literal quote>"
   ```

   Each row format: `- Phase X [pass|FAIL] | <evidence>` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input.

2. **FAIL detection rules** — these trigger automatically; the skill cannot mark `pass` without satisfying them:

   **Universal FAIL rules** (every self-learning skill inherits these):
   - **`audit-paraphrased-user-input`** (load-bearing, threshold=1): any audit row that paraphrases user intent rather than quoting verbatim.
   - **`audit-no-explicit-approval-wait`** (procedural, threshold=2): skill advanced past a user-gate phase without observing the literal approval token.
   - **`tool-claim-without-call`** (load-bearing, threshold=1): audit row says "ran X" / "invoked Y" but no corresponding tool call observed in this session.

   **Domain FAIL rules** (specific to this skill):

   - **`2-merge-conflict-not-blocked` FAIL** (load-bearing, threshold=1): Phase 2 marked `pass` but `git merge-tree` output contains conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) OR exit code was non-zero.
   - **`4-live-test-skipped-without-justification` FAIL** (load-bearing, threshold=1): live UI test skipped AND diff touched UI-exercising backend (`routes.py`, `services/orchestrator.py`, `mcp/`, tool definitions) AND no user-provided skip reason recorded AND dev-stack preflight did NOT explicitly fail.
   - **`5-code-diagnosis-narration-only` FAIL** (load-bearing, threshold=1): Phase 5 narrated diagnosis findings without an observed `Skill(skill="claude-library:code-diagnosis", ...)` tool call in this session.
   - **`6-env-secret-committed` FAIL** (load-bearing, threshold=1): diff added a `.env*` line whose value matches the secret heuristic (high-entropy ≥32 chars, contains `password=`/`secret=`/`api_key=` with non-placeholder value, hex/base64 strings ≥32 chars) rather than a placeholder.
   - **`7-implicit-skip-no-justification` FAIL** (load-bearing, threshold=1): `surfaced > resolved-with-explicit-choice`. Count = (surfaced − resolved).

3. **Show the audit and ask the user to confirm OR correct every row.** The audit is NOT approved on silence or partial answer. The skill must wait for the user to:
   - **confirm** each row as written, OR
   - **dictate corrections** (which the skill applies verbatim and re-displays the audit), OR
   - **mark a row FAIL with a tag** (which the skill records).

4. **Approval gate**: the print phase cannot fire until the user explicitly types `merge approved` (case-insensitive). Silence, "looks good", "ok", "proceed", or partial responses are NOT approval. After approval, the skill prints the structured verdict (GREEN — proceed to merge | RED — blocked, with reasons) and ends. The user runs the actual `git merge` / `gh pr merge` manually.

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

4. **Write the file** with the `Write` tool. The verdict-print already happened in Phase 8 — leave the ledger update unstaged for the user to commit alongside any manual cleanup.

5. **Threshold check** — for any counter where `count >= threshold`:
   - Print a **fix proposal** block: the failure pattern, the recommended SKILL.md edit (specific file + line + before/after diff drawn from `remediation_hint`), the tag.
   - **Apply automatically** (Mode B): make the SKILL.md edit. The user reviews the change in their normal commit-review loop.
   - After applying: reset the counter to 0; set `applied_at` to the current timestamp; optionally fill `applied_via` with a one-line description of the structural change made.
   - **Conflict handling**: if multiple tags trip in the same run, apply remediations serially (oldest tag first by `occurrences[0].ts`). Surface conflicts to the user — never silently overwrite a remediation that another tag just wrote.

---

## Edge cases

1. **PR or branch resolves to base ≠ `dev`**: warn the user. The skill's load-bearing principle assumes `dev` is the merge target; allow override via explicit user confirmation, but require a quote for the audit.
2. **Branch only exists locally (no remote)**: Phase 1 step 3 hard-stops; the skill needs `origin/<head>` for `git merge-tree`. User pushes the branch first or aborts.
3. **No `.env*` files in diff**: Phase 6 passes trivially with one row in the audit (`env files in diff: no`). Do not invent issues to surface.
4. **No `claude-library:code-diagnosis` available** (e.g., plugin not loaded): hard-stop in Phase 5 with a clear message — the load-bearing principle CANNOT be satisfied without the call. Tell the user how to load the plugin.
5. **User's project has its own pre-commit-check skill under a different name**: ask the user where the rules live; default to `shared-pre-commit-check.md` if present.
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
