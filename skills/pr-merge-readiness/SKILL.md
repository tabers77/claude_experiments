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

RELEVANCE_PREDICATES:
  # Per-sub-check diff-path globs that determine whether the sub-check runs.
  # If no path in the diff matches any glob in the predicate's `triggers`,
  # the sub-check is skipped with the documented `skip_note`. Conservative
  # default: when uncertain, leave a predicate's triggers list empty
  # (matches nothing → never trips skip → always runs).
  #
  # CRITICAL: the example globs below are tuned to this project's layout.
  # Downstream projects MUST replace them with their own production-code,
  # frontend, auth, and dependency paths. Failing to tune them either
  # (a) silently skips nothing (predicate trigger globs never match the
  # project's real paths) or (b) silently skips everything (predicate
  # trigger globs are too narrow). Verify with one dry-run pre-adoption.

  phase3_smoke:
    # Smoke tier covers platform Python regression baseline. Skip when no
    # platform paths AND no dependency/build/Docker files in diff —
    # dependency or Dockerfile changes can break smoke even without
    # platform-code touched, so they MUST also trigger smoke.
    triggers:
      - "**/intelligence_platform/**"
      - "**/backend/tests/**"
      - "**/pyproject.toml"
      - "**/poetry.lock"
      - "**/requirements*.txt"
      - "**/Dockerfile*"
      - "**/docker-compose*.yml"
    skip_note: "no platform Python paths nor dependency/Docker changes in diff (smoke would exercise dev-merge baseline only)"

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
    # principle anchor). The predicates here apply only to the sub-skill's
    # category-level scans, not to the Skill invocation. Skipped categories
    # are passed as instructions in the Skill call's args.
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

**How configuration is consumed**:
- Phase 3 reads `PRE_COMMIT_RULES_PATH` (first existing file) before falling back to defaults; Phase 3 step 1a evaluates `RELEVANCE_PREDICATES.phase3_*` against the diff before running each sub-check.
- Phase 4 routes test tiers using `HIGH_BLAST_PATHS` (mandatory live tier trigger), `LIVE_UI_TEST_COMMAND` (the actual command to run), `DEV_STACK_PREFLIGHT_URL` (preflight gate), and `DEFAULT_TEST_COMMANDS` (per-tier commands).
- Phase 5 reads `TRACKER_FILES` to bound the diff-anomaly check; Phase 5 step 1a evaluates `RELEVANCE_PREDICATES.phase5_code_diagnosis_categories.skip_*` to instruct the sub-skill which categories to skip (the Skill call itself remains load-bearing and always fires).
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
     "sentiment": "<negative | aspirational | neutral>",
     "applied_at": null,
     "applied_via": null
   }
   ```

   **Sentiment classification** — apply this keyword heuristic at capture time (case-insensitive substring match on the suggestion text). The classification feeds `quality_derived` at ledger time:

   | Sentiment | Trigger keywords (any match wins) | What it means |
   |---|---|---|
   | `negative` | `broken`, `wrong`, `incorrect`, `missed`, `failed`, `bug`, `doesn't`, `does not`, `should not`, `shouldn't`, `regression`, `flaw`, `error`, `mistake` | User is flagging a problem with this run. Counts against `quality_derived`. |
   | `aspirational` | `would be nice`, `consider`, `could also`, `enhancement`, `add`, `nice to have`, `idea:`, `it would be cool`, `we should also`, `extend`, `support` | User is suggesting an enhancement. Does NOT count against `quality_derived`. |
   | `neutral` | none of the above, OR matches in both lists | Default fallback. Does NOT count against `quality_derived`. |

   Resolution rule: if both lists match, classify as `neutral` (cancels out). **Negative wins only when no aspirational keyword also matches** — keeps the heuristic conservative. The user may hand-edit `sentiment` in `run_history.json` later if misclassified; never re-evaluated by the skill.

3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase 4, tag=4-test-routing, sentiment=aspirational): "run targeted unit tests on changed modules"
   ```
4. **Resume** the current phase from where it was. The capture does NOT alter the current run — it only records the suggestion for future review at the audit and threshold-based aggregation later.

**What this is NOT**:

- **NOT a phase override.** "Don't run the live test" without a trigger prefix → Phase 7 resolution flow. With `suggestion:` prefix → captured as a long-term improvement idea but the current run still does whatever its phase logic says.
- **NOT auto-applied.** Captured suggestions live in `run_history.json` for later review. Tier 1 (current): the user manually applies whichever resonate. Future tiers may add tag-based aggregation and threshold-driven proposals; auto-apply is deliberately deferred.
- **NOT a substitute for FAIL counters.** FAIL counters track *what went wrong* (mechanically detected). Suggestions track *what could be better* (user-perceived). They live in different fields and have different lifecycles.

---

## Observer file boundary

This skill includes an observer phase (Phase 10) that writes to `observations.json` and `suggestions.md`. **All other phases (0 through 9) MUST NOT read those files.**

The two files are owned by the observer phase exclusively and exist for cross-run pattern analysis + human review. They are *descriptive* (record what happened across prior runs), not *prescriptive* (do not encode what should happen on this run).

In particular, the agent running domain phases MUST NOT:

- Use `observations.json` content as background context when framing prompts to the user.
- Alter a phase's recommendation, default branching, or option ordering based on prior observations.
- Cite observations to justify a skill behavior in-flight.

The only legitimate path for an observation to change skill behavior is: observer clusters the signal → writes a proposal to `suggestions.md` → human reviews → human edits this `SKILL.md` (or dismisses the proposal). The audit channel and the observer channel remain **isolated by design** — that isolation is what keeps observer's seeded data from silently biasing the skill's defaults.

If you are an LLM/agent running this skill: treat `observations.json` and `suggestions.md` as if they did not exist until you reach Phase 10. Reading them earlier is a load-bearing violation, and there is no FAIL tag for it because the file content is silent — the only safeguard is this rule.

---

## Phase 0 — Freshness check (non-blocking) + run-start instrumentation

Before running any domain work, briefly check how stale this skill has gotten AND stamp the run's `started_at` timestamp for efficiency tracking. Both are non-blocking.

**Stamp `started_at` first** (before anything else): record the current ISO 8601 timestamp into in-memory run state. Phase 9 (ledger) will read it back and write it to `runs[].started_at` along with the rest of the timing fields. Do NOT persist it to disk here — Phase 9 owns the write.

Then the freshness check below proceeds.

The premise: a skill that gets used heavily but never reviewed against the current state of Claude Code, peer skills, or its own domain will silently rot. The audit + ledger catch mechanical drift inside a run; this phase catches **the skill's own design** falling behind across runs.

1. **Read** `skills/pr-merge-readiness/run_history.json` → `validation_freshness`.
   - If the file is missing or the block is missing, initialize the block in-memory with:
     ```json
     {
       "created_at": "<now-iso8601>",
       "last_validated_at": "<now-iso8601>",
       "last_research_at": null,
       "last_overlap_check_at": null,
       "runs_since_validation": 0,
       "thresholds": { "runs": 10, "days": 21 },
       "review_log": []
     }
     ```
   - Phase 9 (ledger) will persist this on first write. Phase 0 itself does NOT write to disk.

2. **Compute staleness**:
   - `days_since_validated = floor((now - last_validated_at) / 86400)` (in days).
   - `runs_since = validation_freshness.runs_since_validation`.

3. **Nudge condition — both must be true (AND, not OR)**:
   - `days_since_validated >= thresholds.days` (default 21), AND
   - `runs_since >= thresholds.runs` (default 10).

4. **When the nudge fires**, print exactly this one-line block at the top of the run (before Phase 1's first output), then continue to Phase 1:

   ```
   ⚠ Freshness: `pr-merge-readiness` last validated <days_since_validated>d ago, <runs_since> runs since.
     Consider running, when you have a moment:
       /meta-discover-claude-features  — research improvements in this skill's domain
       /meta-skill-audit               — overlap check vs. other skills
     Then append a review_log[] entry to skills/pr-merge-readiness/run_history.json → validation_freshness
     and bump last_validated_at + reset runs_since_validation to 0.
   ```

   **When the nudge does NOT fire** (one or both conditions false), print nothing at all. Silence is the success state — do NOT print "freshness OK" or any other affirmation.

5. **Proceed to Phase 1 unconditionally.** The freshness check is never a hard gate. Even if the user has ignored the nudge for 100 runs, Phase 1 still runs. The user owns the decision to revalidate; this phase only surfaces the signal.

---

## Per-phase timing instrumentation (global rule)

Every domain phase (1 through 8) AND the observer phase (10) is responsible for stamping its own elapsed time as it exits:

- At the **start** of each phase, record `phase_start = now`.
- At the **end** of each phase, record `phase_durations[<phase-id>] = floor((now - phase_start) seconds)`. Half-numbered sub-phases (e.g. `5.5`) record under their literal id; do NOT roll them up into the parent.
- Keep `phase_durations` in in-memory run state alongside `started_at`. Phase 9 (ledger) reads the full map and writes it to `runs[].phase_durations`.

This is **mechanical, not load-bearing** — no FAIL tag covers a missed stamp, and absent timing data simply excludes the run from the observer's efficiency comparison. But it is the input to every speed-vs-quality observation, so the skill should stamp them faithfully.

The ledger phase (9) does NOT stamp its own duration — Phase 9 IS the ledger write; timing the writer creates a circular dependency. Its time is folded into the gap between Phase 8's end stamp and `ended_at`.

---

## Phase 1 — Parse input + identify target

1. **Detect mode**:
   - Argument matches `^#?\d+$` → `pr` mode (strip leading `#`).
   - Argument looks like a branch name (contains `/` or matches `^(feat|fix|chore|docs|refactor|test)/`) → `branch` mode.
   - No argument → `current` mode (use `git rev-parse --abbrev-ref HEAD`).
2. **Resolve `head` and `base`**:
   - `pr` mode: `gh pr view <num> --json headRefName,baseRefName,url,title,state` — capture `head`, `base` (must equal `BASE_BRANCH` from the config block; warn if not), URL, title.
   - `branch`/`current` mode: `head` = the branch; `base` = `BASE_BRANCH` (assumed; warn if remote-tracking diverges or if a peer config like `.github/PULL_REQUEST_TEMPLATE.md` suggests a different default).

2a. **Defensive: shallow-clone check**. BEFORE any merge-base / rev-list / merge-tree probe is interpreted, run:

   ```powershell
   git rev-parse --is-shallow-repository
   ```

   If it returns `true`, the local clone is shallow (typical on Azure DevOps Pipeline checkouts with `fetchDepth: 1`, or any CI-provided shallow clone). Run `git fetch --unshallow origin` and re-verify; do NOT report ancestry findings (e.g. "orphan branch", "no merge base", absurdly small `rev-list --count`) until the clone is unshallowed. A shallow clone makes `git merge-base origin/<BASE_BRANCH> <head>` return `no merge base` and `git rev-list --count origin/<BASE_BRANCH>` return absurdly small values that mimic an orphaned base branch — these are clone artifacts, not real history. Record the outcome verbatim in the Phase 1 audit row evidence: `shallow-clone=<yes-unshallowed|no>`.

3. **Confirm the branch exists locally and remotely**:
   ```powershell
   git rev-parse --verify "refs/heads/<head>"
   git ls-remote --heads origin <head>
   ```
   If either fails, hard-stop and ask the user how to proceed (push the branch, switch context, abort).
4. **Record the input verbatim** for the audit row — never paraphrase.

5. **Diff-scope classifier**. Compute the diff scope from `git diff --name-only origin/<BASE_BRANCH>...<head>`:

   - **Lite-eligible** when ALL of:
     - Total changed files ≤ 10 AND
     - No diff path matches any glob in `HIGH_BLAST_PATHS` AND
     - No diff path matches `**/db/migrations/**` or `**/alembic/versions/**` AND
     - No diff path matches `**/auth/**`, `**/authz/**`, or `**/security/**` AND
     - No `.env*` / `*.pem` / `*.key` / `id_rsa` files in diff AND
     - Diff is dominated by docs / infra / config / test-fixtures / skill-files (production-code `.py` / `.ts` / `.tsx` file count ≤ 2).
   - **Full-mode** otherwise.

   Record the classifier outcome verbatim in the Phase 1 audit row evidence: `scope=lite|full; reason=<the matching condition>`.

   Lite-mode is informational, NOT a permission to skip load-bearing gates. Phase 2 (clean-merge), Phase 5 (no-new-bugs sweep with the Skill call), and Phase 7 (user-resolution gate) ALWAYS fire verbatim — the lite-mode budget applies only to OUTPUT VERBOSITY in Phases 3, 4, 5 reporting, and 8.

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

1a. **Per-sub-check relevance prefilter**: for each sub-check defined in `RELEVANCE_PREDICATES.phase3_*`, evaluate the predicate against the diff path list (`git diff --name-only origin/<BASE_BRANCH>...<head>`). If no diff path matches any glob in the predicate's `triggers`, mark the sub-check as `skipped (irrelevant)` and record the `skip_note` verbatim for the Phase 3 step 4 aggregate row. Do NOT run the sub-check.

   The relevance prefilter NEVER applies to:
   - Phase 2 clean-merge probe (load-bearing).
   - Phase 5 code-diagnosis Skill call itself (load-bearing — the prefilter inside Phase 5 only suppresses sub-skill CATEGORY scans, not the Skill invocation).
   - Phase 7 user-resolution gate (load-bearing — any item already surfaced by an earlier phase still requires explicit choice; only the prefilter suppression is recorded as evidence).

   Conservative-by-default: when a predicate's `triggers` list is empty, the predicate matches nothing and the sub-check always runs. Tune predicates per project — see the config block's CRITICAL note.

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
   rules-source=<path|defaults>, smoke=<pass|skipped:<note>|FAIL+counts>,
   lint=<pass|skipped:<note>|FAIL+files>, protected=<none|<list>>,
   ownership=<ok|warn>, safety=<ok|FAIL>,
   env-secrets=<no-env-files|pass|FAIL+files>,
   relevance-skipped=<none|<comma-list of "<sub-check>:<skip_note>">>
   ```

   `relevance-skipped` lists every sub-check the Phase 3 step 1a prefilter suppressed, citing the `skip_note` verbatim. If the prefilter suppressed nothing this run, emit `relevance-skipped=none` (do NOT omit the field — its presence is what the FAIL counter checks).
5. Any rule failure → mark Phase 3 FAIL and surface to Phase 7. Env-secret heuristic trips → `6-env-secret-committed` FAIL (counter retained from former Phase 6 — see Phase 8 FAIL detection rules).

## Phase 4 — Relevant-tests run (incl. live UI gate)

Run the test tiers that actually exercise the changed surface — not the full suite. **Selection is delegated to `claude-library:smart-test-selection`** (composed child); this phase consumes its artifact and is responsible only for EXECUTION, the live-UI mandatory gate, and per-tier telemetry. The decision tree that used to live here moved into smart-test-selection's `TIER_POLICY` config block — project-specific paths and commands now live there.

**Test-cache integration**: the project is expected to have wired up the SHA-keyed pytest cache plugin (see `documentation/TEST_CACHE_SETUP.md` in the claude-library plugin). When wired, every pytest command below transparently **deselects tests already passed for the current HEAD SHA on a clean tree** and **records fresh results** to `documentation/test-results/<sha>.json` — no per-tier plumbing needed; the plugin lives in pytest's lifecycle hooks. The cache file is intended to be committed alongside the code change so teammates pulling the same SHA inherit the cache. If the project hasn't opted in, every tier runs the full set unchanged. Each pytest tier below produces a terminal line like `[test-cache] skipped N tests …` or `[test-cache] recorded N results …` (or `[test-cache] disabled: <reason>`); capture that line verbatim into step 4 telemetry.

1. **Invoke smart-test-selection (composed) to produce the selection plan**. Pass the parent invocation args so the child skips its Phase 0 freshness check and Phase 8 observer (composition protocol):

   ```
   Skill(
     skill="claude-library:smart-test-selection",
     args="invocation_mode=composed; parent=pr-merge-readiness; parent_run_ts=<this run's started_at>; diff=origin/<BASE_BRANCH>...<head>"
   )
   ```

   The child writes its plan to `documentation/test-plans/<fingerprint>.md`. Capture the artifact path; do NOT re-implement the tier-routing decision tree here — it lives in smart-test-selection's `TIER_POLICY` block. If the Skill call returns a non-success status, hard-stop and surface the failure to Phase 7.

1a. **Consume the artifact**. Read `documentation/test-plans/<fingerprint>.md` and parse three sections:

   - `Tests to run` — one pytest node ID per line. Lines ending with `# cache_bypass=true` indicate state-dependent tests; for those IDs, invoke pytest with `--no-test-cache` so external state (running dev stack, live APIs) is re-verified rather than trusted from a prior-SHA cache hit. Plain lines run with the cache normally.
   - `Companion non-pytest checks` — one command per bullet (ruff, mypy, npm lint/typecheck, alembic round-trip, etc.). Run each in order. These are NOT pytest invocations; the cache plugin doesn't apply.
   - `Live UI required` (header field, `y|n` + triggering paths) — feeds the mandatory gate in step 2.

   Group pytest IDs by their owning marker tier (smoke / unit / integration / live) using `pytest --collect-only --co <ids>` to preserve the per-tier telemetry shape expected in step 4. Run each tier as a single `pytest <ids...>` invocation when possible; isolate live-tier IDs into a separate invocation so `--no-test-cache` is applied only to them.

1b. **Frontend / migration commands** are emitted by the child as Companion non-pytest checks — run them via the step 1a loop. There is no separate "frontend" or "migration" branch here anymore; the child's `NON_PYTEST_CHECKS` config drives which commands appear in the artifact.

2. **Live UI test sub-gate** — enforced HERE (parent), not in the child. If the artifact's `Live UI required` header is `y` (smart-test-selection detected a `LIVE_UI_REQUIRED_PATHS` match), the live UI test is **mandatory** unless one of these honest exceptions applies:
   - `LIVE_UI_TEST_COMMAND` is `null` → record `"live UI tier: no infra configured (LIVE_UI_TEST_COMMAND=null)"`. This is NOT a `4-live-test-skipped-without-justification` failure — the skill respects the project's stated absence of live infra.
   - `DEV_STACK_PREFLIGHT_URL` is set AND the preflight call (`curl -fs <DEV_STACK_PREFLIGHT_URL>`) returns non-2xx → record the failed URL + status code, skip cleanly.
   - The user provides an explicit skip reason via Phase 7 (recorded verbatim).

   Skipping without one of these → `4-live-test-skipped-without-justification` FAIL. The live UI tier is always invoked with `--no-test-cache` because every live-marked test in the plan carries the `# cache_bypass=true` annotation (enforced by smart-test-selection's `5-cache-bypass-marker-missing` FAIL rule).
3. **Optional blast-radius probe**: when the artifact's `Live UI required` header is `y` (i.e., a high-blast path was touched), invoke `claude-library:safe-changes-impact-check` and fold its findings into Phase 5/7. This is a recommendation, not mandatory.
4. **Capture per-tier telemetry** for the audit: tier name, exact command run (with config values resolved), wall-clock, pass count, fail count, skipped count, the **verbatim `[test-cache] …` line** emitted by the pytest plugin for that tier (or `"[test-cache] not wired"` when the project hasn't opted in), AND a reference to the plan artifact path so the auditor can trace selection back to smart-test-selection's evidence chain.

## Phase 5 — No-new-bugs sweep

This is the principle-anchor — the skill cannot mark Phase 5 `pass` without an observed `Skill` call.

1. **Run `claude-library:code-diagnosis`** on the changed files only — path-scoped, NOT full-repo. The exact tool call must be observable in the session trace; narration is not evidence.

   ```
   Skill(skill="claude-library:code-diagnosis", paths=<list-of-changed-files>)
   ```

1a. **Per-category relevance prefilter**: the Skill call above is load-bearing and ALWAYS fires. Within the Skill call's args, evaluate each `RELEVANCE_PREDICATES.phase5_code_diagnosis_categories.skip_*` predicate against the diff path list. For each tripped predicate (no diff path matches any glob in `triggers`), include an explicit `skip_categories=[...]` instruction in the Skill call's prompt so the sub-skill suppresses that category's scan, and record the `skip_note` verbatim. Skipped categories appear as one-line skip notes in the Phase 5 report (and in the Phase 8 audit row's Phase 5 evidence string). Categories not listed in `RELEVANCE_PREDICATES` (e.g. Bugs, Smells, Opportunities) always run — those are the principle-anchor categories.

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

   **Lite-mode rendering** (when Phase 1 step 5 classified `scope=lite`): render only the TL;DR sentence + the "blocks merge" bucket detail rows. The "track as follow-up" and "pure refactoring" buckets are mentioned by count only, expandable on user request (e.g., "show me the smells"). The full per-finding table renders only when `scope=full` OR the user asks for it explicitly.

3. **Optional**: when Phase 4 step 3 flagged the change as high-blast, also invoke `claude-library:quality-bug-sweep` for the comprehensive scan. Default: skip unless high-blast.
4. **Diff-anomaly check**: for each path in `TRACKER_FILES`, `git diff origin/<BASE_BRANCH>...<head> -- <tracker-path>`. Confirm only expected rows changed; unexpected diffs are surfaced to Phase 7. If `TRACKER_FILES` is empty, skip this step and record `"diff-anomaly check skipped: no TRACKER_FILES configured"`.
4b. **Tracker closure-pairing reconciliation**: for each path in `TRACKER_FILES`, diff the file against `origin/<BASE_BRANCH>`. If the diff *adds* a closure narrative (heuristic: a new paragraph mentioning a tracker ID like `W-*`, `V-*`, `SP-*`, `GAP-NNN` *and* outcome language such as "closed", "fixed", "resolved", "shipped"), confirm that the corresponding tracker row in the project's bug/gap tracker (typically the OTHER `TRACKER_FILE` — e.g. `BUGS_AND_GAPS.md` when `COMPLETED_STREAMS.md` got the closure narrative) was *removed* in the same diff. If the row is still present, surface to Phase 7 as a hard item with FAIL tag `5-tracker-closure-without-row-removal`. If `TRACKER_FILES` has fewer than 2 entries (so there's no "other" tracker to pair against), skip cleanly and record `"tracker closure-pairing skipped: needs >=2 TRACKER_FILES"`.

4c. **Closure-narrative falsifiable-claim reconciliation**: closure narratives often contain truth-claims (e.g. `"All 1075 unit + integration tests pass post-change"`, `"smoke tier clean"`, `"no regressions"`). The tracker-pairing check (4b) verifies the row-removal *presence* but does NOT test the *truth* of these claims. For each closure-narrative paragraph added in any `TRACKER_FILES` path (and in `COMPLETED_STREAMS.md` when present in the diff), parse the paragraph for falsifiable phrases using these regex candidates (case-insensitive, applied to the added text):

   - `\b\d{2,5}\s+(unit|integration|smoke)?\s*tests?\s+pass` (e.g. "1075 tests pass", "418 smoke tests pass")
   - `\bno regressions?\b`
   - `\bsmoke (?:tier\s+)?clean\b`
   - `\ball tests pass\b`
   - `\bN/?A failures?\b`
   - `\btier\s+\w+\s+clean\b`

   For each matched claim, reconcile against Phase 4's actual evidence in THIS session:

   - If Phase 4 has run the corresponding tier (e.g. claim mentions "smoke" and Phase 4 ran smoke), compare: actual `passed`/`failed` counts must agree with the claim. If Phase 4 results contradict the claim (e.g. claim says "all tests pass" but smoke had 2/422 failures), surface to Phase 7 as a hard item with FAIL tag `5-closure-narrative-falsifiable-claims-not-reconciled` (load-bearing). Acceptance of a false claim is exactly the silent-confidence failure mode this skill exists to catch.
   - If Phase 4 has NOT run the tier the claim mentions (e.g. claim says "1075 unit + integration tests pass" but Phase 4 ran smoke only this session per scope/relevance choices), surface to Phase 7 as an unresolved item demanding either (a) re-run the corresponding tier in this session, or (b) explicit user acceptance of the claim with a verbatim justification recorded.
   - Record every matched claim verbatim in the Phase 5 sub-report alongside the Phase 4 actual-result row (or `"no Phase 4 evidence for this tier"`), so the user can scan the reconciliation table without re-deriving it.

   If no closure-narrative paragraph is added in this diff, record `"closure-narrative reconciliation skipped: no closure narratives added"` and proceed.

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
   - the fix description is one of: missing-import, deprecation comment update, follow-up tracker row, removed-dead-code, narrow exception handler, fail-loud assertion AND
   - **the item was introduced by THIS branch.** Mechanical check: for each cited `<file>:<line>` in the surfaced item, run `git blame -L <line>,<line> -- <file>` and confirm the commit hash is reachable from `origin/<BASE_BRANCH>...HEAD` (i.e., in this branch's diff). If at least one cited file:line was introduced by the branch, the precondition fires. If every cited line predates `origin/<BASE_BRANCH>`, the precondition does NOT fire (pre-existing tech debt — keep current ranking behavior).

   When the recommendation gate fires, the option block must read:

   1. **Fix it now (recommended)** — <one-line description> *(branch-introduced + cheap fix; closing before merge is cheaper than filing a follow-up)*
   2. Skip with logged justification
   3. Block the merge
   4. Abort the run

   When the recommendation gate does NOT fire (any precondition fails), the skill STILL marks exactly one option as `(recommended)` using the softer-heuristic fallback below, and appends a one-line rationale to the recommended option. The four-option list itself remains the same:

   - **block the merge** — verdict will be RED. Skill records the reason and proceeds to audit.
   - **fix it now** — user describes the fix; skill applies it (or asks the user to apply); loops back to the originating phase.
   - **skip with logged justification** — user provides a one-line reason. Recorded verbatim in the audit and the run-history ledger.
   - **abort the run** — clean exit; no verdict produced.

   **Softer-heuristic recommendation fallback** (applies whenever the narrow Recommendation gate doesn't fire — every multi-option Phase 7 prompt MUST mark exactly one option as `(recommended)` with a one-line rationale):

   1. Pick the option with the smallest blast-radius that resolves the surfaced item (e.g. `skip with logged justification` is smaller blast-radius than `block the merge`; `fix it now` only beats both when the fix scope is bounded enough to apply confidently).
   2. If multiple options have similar blast-radius, prefer the one that aligns with this PR's stated intent — e.g. `fix it now` for tightly-scoped feature PRs; `skip with logged justification` for close-out PRs where the surfaced item is out-of-scope.
   3. **Branch-introduced bias** (applied AHEAD of the historical tie-breaker): if the surfaced item has at least one cited `<file>:<line>` whose `git blame` shows the line was introduced in `origin/<BASE_BRANCH>...HEAD`, bias the recommendation toward `fix it now`. Rationale on the option line: "branch-introduced; closing before merge is cheaper than filing a follow-up." This catches branch-new items that fail the narrow gate on one of the OTHER four preconditions (e.g., >15 LOC, smoke >60s, or category outside the canonical small-fix list) — `fix it now` is still usually the right default for new regressions, just not as confidently as when all 5 narrow-gate preconditions match.
   4. Tie-breaker: choose the option chosen most often for this surfaced-item type in past runs (read from `run_history.json:runs[].notes` for similar item phrasings; if no prior signal exists, default to `skip with logged justification` as the smallest-blast-radius generic).

   The option block (whether narrow-gate-fired or fallback) must always have exactly ONE option marked `(recommended)` with the rationale appended on the same line. Silence on a recommendation is NOT acceptable — neutral option blocks force a "which is best and why?" round-trip that this rule exists to short-circuit.

2a. **Pre-edit verification (for tightening fixes only)** — fires after the user selects a `Fix it now` option AND BEFORE the edit is applied. Skip this step entirely for non-tightening fixes (purely additive edits, deletions, comment updates).

   **Tightening-fix detector** (mechanical). A proposed edit is a "tightening fix" if ANY of these patterns match the BEFORE→AFTER of the user-approved change:

   | Class | Before | After |
   |---|---|---|
   | Operator strictness | `!=` (or `is not`) | `==` (or `is`) |
   | Membership collapse | `not in (<set>)` or `in (<a>, <b>, ...)` | `== <single-value>` |
   | Range tightening | `>= 0`, `>= N`, `<= N` | `> 0`, `> N`, `< N` |
   | Whitelist narrowing | `<value> in {<a>, <b>, <c>}` | `<value> in {<a>}` |
   | Pattern strictness | broad substring match, e.g. `"401" in resp.text` | exact equality, e.g. `resp.status_code == 401` |

   If the proposed edit does NOT match any pattern, treat as non-tightening and proceed to the existing edit-and-apply flow.

   **Verification sequence** (when tightening detected):

   1. **Identify the assertion target.** Locate the test (or curl/probe) whose assertion the edit modifies. The test name is the file+function the edit lives in OR a sibling test that exercises the same code path.
   2. **Run the test/probe in its CURRENT (pre-edit) state** and capture the actual observable value:
      - For pytest assertions: run the single test via `pytest <node-id> -v` and parse the assertion line.
      - For curl/HTTP probes: run the curl and capture the status code + first body line.
      - For Python REPL checks: import + invoke + observe.
   3. **Compare the actual value to the user-approved precise value.**
      - If they MATCH: proceed to apply the edit. Record the verified actual value in the audit row for traceability.
      - If they DISAGREE: do NOT apply the edit. Surface the discrepancy to the user verbatim:
        ```
        Pre-edit verification: actual return is <X> but the tightened expected value is <Y>.
        Applying the edit would cause the test to fail.

        Options:
          1. Adjust the precise expected value to <X> (recommended — matches observable behavior)
          2. Investigate why actual != intended (the underlying code may be wrong, not the test)
          3. Skip the fix; file as gap for follow-up
        ```
        Loop back to user choice. Do NOT loop into apply-then-revert under any circumstance.

   **Why this exists.** Tightening edits have an asymmetric failure mode: a loosening fix can't fail at runtime (it admits more states), but a tightening fix can fail if the assumed precise value is wrong. Apply-then-revert costs file ops, sensitive-file hook fires, and user trust. Running the failing-state test FIRST is cheap (one pytest invocation) and prevents the ceremony entirely.

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
   | 1 | pass | input parsed: <mode> <target>; user input verbatim: "<literal quote>"; shallow-clone=<yes-unshallowed\|no>; scope=<lite\|full>; reason=<matching condition> |
   | 2 | pass | git merge-tree --write-tree --name-only origin/<BASE_BRANCH> <head>: exit=<code>; conflicts: <none\|<paths>> |
   | 3 | pass\|FAIL | rules-source=<resolved PRE_COMMIT_RULES_PATH or "defaults">; outcomes: smoke=<...>, lint=<...>, protected=<...>, ownership=<...>, safety=<...>, env-secrets=<no-env-files\|pass\|FAIL+files>, relevance-skipped=<none\|<sub-check>:<skip_note>; ...> |
   | 4 | pass\|FAIL | tiers run: <list>; results: <pass/fail/skipped per tier>; test-cache: <verbatim lines or "not wired">; live UI: <ran\|skipped + reason> |
   | 5 | pass\|FAIL | claude-library:code-diagnosis Skill call observed: <yes/no>; findings: <count> at <file:line list> |
   | 7 | pass\|FAIL | unresolved items: <N surfaced> / <M resolved-with-explicit-choice>; user input verbatim: "<literal quote>" |
   ```

   Phase 6 is intentionally omitted from the audit table — the env-secret heuristic was folded into Phase 3's safety sub-step on 2026-05-16 (see Phase 6 reserved note). Its outcome appears as the `env-secrets=` segment of the Phase 3 row.

   Each row is a markdown-table row with three columns: `| Phase X | pass|FAIL | <evidence> |` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input. Long evidence strings stay on a single logical line (the table cell) and the markdown renderer wraps them; bulleted line-wrapping in terminals breaks readability when evidence approaches 100+ chars.

   **Lite-mode audit row format** (when Phase 1 step 5 classified `scope=lite`): render the audit table with a condensed Evidence column — 1-2 sentences per row, NOT verbatim command output. The verbatim-quote rule for user input is preserved (`audit-paraphrased-user-input` still trips inside cells). Specifically:

   - Phase 3 evidence may collapse the 7-field aggregate to one line: `rules=<source>; lint=<status>; protected=<count>; safety=<status>; env-secrets=<status>`.
   - Phase 4 evidence may collapse to one line per tier: `smoke=<pass/fail/skip counts in Ns>; <other tiers> not run (reason)`.
   - Phase 5 evidence may collapse to TL;DR-only: `Skill(code-diagnosis) observed; TL;DR: <N1> blocks merge / <N2> follow-up / <N3> refactoring`.

   When `scope=full`, the audit row format remains the current verbose form.

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
   - **`5-closure-narrative-falsifiable-claims-not-reconciled` FAIL** (load-bearing, threshold=1): Phase 5 sub-step 4c detected a closure-narrative paragraph containing a falsifiable claim (e.g. "N tests pass", "no regressions", "tier X clean") that was NOT reconciled against Phase 4's actual evidence in this session — either Phase 4 contradicted the claim and the discrepancy was not surfaced to Phase 7, OR Phase 4 did not run the claimed tier and the user did not explicitly accept the unverified claim with a verbatim justification. Load-bearing because silent acceptance of a false claim is exactly the failure mode the skill exists to catch.
   - **`5-findings-table-needs-severity-provenance-columns` FAIL** (procedural, threshold=2): Phase 5 surfaced code-diagnosis findings without a one-line merge-impact TL;DR header (the `"<N1> blocks merge / <N2> track as follow-up / <N3> pure refactoring"` sentence) preceding the per-finding table. Threshold=2 because a single occurrence may be the skill's first run on a new project; two means the TL;DR rule is drifting.
   - **`6-env-secret-committed` FAIL** (load-bearing, threshold=1, evaluated within Phase 3 step 2's env-file safety sub-step): diff added a `.env*` line whose value matches the secret heuristic (high-entropy ≥32 chars, contains `password=`/`secret=`/`api_key=` with non-placeholder value, hex/base64 strings ≥32 chars, or known key prefixes such as AKIA / AIza / sk-) rather than a placeholder. Tag retained for counter continuity after the standalone Phase 6 was folded into Phase 3 on 2026-05-16.
   - **`7-implicit-skip-no-justification` FAIL** (load-bearing, threshold=1): `surfaced > resolved-with-explicit-choice`. Count = (surfaced − resolved).
   - **`7-recommendation-gate-not-applied` FAIL** (procedural, threshold=2): Phase 7 surfaced an item meeting all five `Fix it now (recommended)` preconditions but did NOT mark fix-now as recommended in the option block. Threshold=2 because a single occurrence may be a borderline precondition call; two means the gate logic is drifting.
   - **`7-fix-now-default-for-branch-introduced-cheap-fixes` FAIL** (procedural, threshold=2): Phase 7 surfaced an item meeting the 4 original narrow-gate preconditions (LOC ≤15, code/docs only, smoke ≤60s, canonical small-fix category) AND `git blame` shows at least one cited file:line is in `origin/<BASE_BRANCH>...HEAD` BUT the option block landed `(recommended)` on `File as gap` or `Skip with logged justification` instead of `Fix it now`. Detection: re-run the git blame check at audit time on each cited file:line; if branch-introduced + all 4 narrow preconditions match but `(recommended)` was elsewhere, fail. Threshold=2 because a single occurrence may be a deliberate user override; two means the ranking logic is drifting in the wrong direction.
   - **`7-fix-now-applied-without-failing-state-observation` FAIL** (procedural, threshold=2): a Phase 7 `Fix it now` flow applied a tightening edit (per the tightening-fix detector in Phase 7 step 2a) WITHOUT recording the pre-edit verification sequence in the audit row evidence. Detection: scan the audit row for the Phase 7 step 2a evidence ("Pre-edit verification: actual=<X>, expected=<Y>, match=<y|n>"); if the row applied a tightening edit and that evidence string is absent, fail. Threshold=2 because a single occurrence may be a non-tightening edit the detector misclassified; two means the verification step is being skipped — the very failure mode this step exists to prevent.
   - **`1-scope-classifier-not-applied` FAIL** (procedural, threshold=2): Phase 1 audit row missing the `scope=lite|full; reason=<...>` evidence segment introduced by the 2026-05-19 scope-classifier remediation. Threshold=2 because a single occurrence may be the skill's first run on a new project before the operator has internalized the classifier; two means the gate logic is drifting.
   - **`3-or-5-relevance-prefilter-not-applied` FAIL** (procedural, threshold=2): Phase 3 or Phase 5 ran a sub-check whose `RELEVANCE_PREDICATES` predicate would have tripped given the diff content, but the prefilter step (Phase 3 step 1a or Phase 5 step 1a) was not invoked — i.e. the Phase 3 aggregate row is missing the `relevance-skipped=...` field entirely (not just `relevance-skipped=none`), OR Phase 5 evidence does not mention category skips when a predicate's triggers had zero diff-path matches. Threshold=2 because a single occurrence may be the skill's first run on a project before the predicates are tuned; two means the prefilter step is being bypassed.
   - **`1-shallow-clone-not-unshallowed` FAIL** (procedural, threshold=2): Phase 1 step 2a was not invoked OR `git rev-parse --is-shallow-repository` returned `true` and the clone was not unshallowed before Phase 1 step 3 / Phase 2's ancestry probes ran. Detected when the Phase 1 audit row is missing the `shallow-clone=<yes-unshallowed|no>` evidence segment, OR the row records `shallow-clone=yes-not-unshallowed`. Threshold=2 because a single occurrence may be the skill's first run on a new host before the operator has internalized the check; two means the gate is drifting.
   - **`7-recommendation-default-on-all-multi-option-prompts` FAIL** (procedural, threshold=2): Phase 7 rendered a multi-option prompt without marking exactly one option as `(recommended)` plus a one-line rationale (whether by the narrow Recommendation gate or the softer-heuristic fallback). Detected when the audit's Phase 7 evidence shows a surfaced item resolved through a neutral option block. Threshold=2 because a single occurrence may be a borderline call; two means the broadened recommendation rule is drifting.

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

2. **Append** the run summary to `runs[]` with full timing + quality fields:
   ```json
   {
     "ts": "<iso8601-now>",
     "target": "<input>",
     "outcome": "<closed|paused|aborted|in-progress>",
     "phases_failed": ["<tag>", ...],
     "started_at": "<from in-memory state, stamped by Phase 0>",
     "ended_at": "<iso8601-now>",
     "duration_seconds": <ended_at - started_at, integer seconds>,
     "phase_durations": {"1": <s>, "2": <s>, "...": "..."},
     "quality_derived": "<clean|partial|failed|incomplete>"
   }
   ```

   **`quality_derived` is computed mechanically** — no user prompt:
   - `clean` ← `outcome == "closed"` AND `phases_failed` is empty AND **no `improvement_suggestions[]` entry** with `sentiment == "negative"` exists whose `target == <this run's input>` AND whose `ts` falls within `[started_at, ended_at]`.
   - `partial` ← `outcome == "closed"` AND (`phases_failed` non-empty OR at least one matching negative suggestion exists).
   - `failed` ← `outcome == "aborted"`.
   - `incomplete` ← `outcome == "paused"` OR `"in-progress"`.

   If `started_at` is missing (run was launched before this instrumentation existed), omit all five timing/quality fields for this run — the observer will skip it from efficiency comparison. Do NOT fabricate timing data.

3. **For each FAIL tag** observed in this run:
   - Increment `fail_counters[<tag>].count` by 1.
   - Append to `fail_counters[<tag>].occurrences[]`: `{ts, target, detail}` where `detail` is a one-line description of the specific occurrence (what command ran, what evidence was missing, what user input was paraphrased — be concrete).
   - If the tag is new, create the entry. Pick `threshold` by phase severity:
     - **Load-bearing phase** → threshold = **1** (fix on first occurrence; the failure defeats a core principle).
     - **Procedural phase** → threshold = **2** (one is noise; two is drift).
     - **Cosmetic phase** → threshold = **5** (low cost; wait for a clear pattern).

4. **Persist captured suggestions**. Any entries added to `improvement_suggestions[]` during this run (mid-run captures + Phase 8 step 5 final-call entries) are written to the ledger as part of the same `Write` call. The array is append-only — never overwrite or drop existing entries.

4a. **Update `validation_freshness`**. This is the ONLY phase that writes to `validation_freshness`:
   - If the block is missing, initialize it with the Phase 0 default shape (see Phase 0 step 1).
   - Increment `validation_freshness.runs_since_validation` by 1.
   - Do NOT modify `last_validated_at`, `last_research_at`, `last_overlap_check_at`, `thresholds`, or `review_log[]` — those are user-owned. The skill never self-certifies freshness; only the user does, by appending a `review_log[]` entry and resetting the counter manually.

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
   | `boundary_violation` | a domain phase (0–9) referenced or used content from `observations.json` / `suggestions.md` (which it must not read) | Phase 2's user prompt framing visibly originated in observer-file content; the skill cited a prior observation in-flight to justify a recommendation |
   | `phase_scope_too_broad_for_input` | a phase ran a full-scope routine when the input class would have justified a narrower scope (e.g. lite-mode existed but wasn't taken) | Phase 5 ran the full no-new-bugs sweep on a docs-only diff that Phase 1 had already classified `scope=lite` |
   | `serializable_as_parallel` | two phases ran sequentially that have no data dependency on each other and could parallelize | Phase 3 (pre-commit-check sweep) and Phase 4 (relevant-tests run) ran back-to-back, neither using the other's output |
   | `redundant_work_with_prior_phase` | a phase recomputed something an earlier phase already produced; the second phase's evidence cites the same fact the first one captured | Phase 5's evidence row quotes the same diff path set that Phase 1 already classified |
   | `over_thorough_for_input_class` | a long-running phase fired on a tiny input where its full pass isn't load-bearing; skill lacks input-class dispatch | Phase 4 ran 8 tiers of tests on a single-line README change |
   | `missed_cached_result` | a phase did work whose exact result is already recorded in `runs[]` for the same target / commit / input shape | Phase 2 (clean-merge probe) re-ran `git merge-tree` for a target whose result was identical in the run 30 minutes earlier |

2a. **Efficiency trade-off detector** — runs only when this run has `duration_seconds` and `quality_derived` populated. Skip entirely otherwise (no fabricated signal on pre-instrumentation runs).

   1. Group prior runs in `runs[]` by **input-class similarity** to this run's target. For pr-merge-readiness, use `scope=lite` vs `scope=full` from the Phase 1 classifier as the cohort split. Within each scope cohort, cluster by `outcome` AND `quality_derived` tier.
   2. Compute the median `duration_seconds` of the matching cohort (need ≥ 3 prior cohort members — otherwise skip; one prior run is not a baseline).
   3. **File an observation** under `phase_scope_too_broad_for_input` (or a more specific category if evidence points clearly at one — e.g. `redundant_work_with_prior_phase` if a phase clearly re-ran work captured earlier) when **both** are true:
      - `this_run.duration_seconds > 1.5 × cohort_median`
      - `this_run.quality_derived` is NOT strictly better than `cohort_median_quality` (ordering: `clean > partial > failed > incomplete`).
   4. **Also file an observation** when **both** are true (inverse failure — fast at the cost of quality):
      - `this_run.duration_seconds < 0.5 × cohort_median`
      - `this_run.quality_derived` is strictly worse than `cohort_median_quality`.

   Each filed observation's `evidence` field MUST include the exact numbers: this run's duration, cohort median, this run's `quality_derived`, cohort median's `quality_derived`, and the cohort size. No paraphrase. The trade-off detector exists specifically to prevent "race to fast trash" — every speed delta is tied to a quality delta before observation.

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
