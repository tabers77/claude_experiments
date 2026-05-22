---
name: smart-test-selection
description: Decide which pytest tests to run for a specific code diff — preserves full coverage of changed surfaces while pruning irrelevant expensive tests (web, integration, e2e) to cut wall-clock without compromising correctness. Reads the SHA-keyed pytest test cache so prior-run results at the same HEAD SHA are surfaced as cached-pass skips with diff-anchored justification. Keywords test selection, smart tests, relevant tests, test routing, expensive tests, web tests, integration tests, diff-based testing, test scope, test pruning, pytest selection.
metadata:
  pattern: self-learning
  schema-version: 1
---

# Smart Test Selection

Decide which pytest tests to run for a specific code diff. The skill enumerates the project's pytest inventory, maps changed surfaces (files, symbols, markers) to candidate tests, applies cost-aware selection within candidates, reads the SHA-keyed test cache to surface prior-run cached passes, and writes a structured selection plan that downstream pytest invocations consume.

**Load-bearing principle**: Every test skip must be justifiable from the diff alone. The skill never drops a candidate test without recording a diff-anchored reason. Coverage of changed surfaces is preserved verbatim — pruning happens only inside the candidate set chosen by surface-anchored selection, and cache-driven skips cite the SHA + clean-tree state on which the prior result remains valid.

## Inputs

The user invokes the skill with one of:

| Shape | Example | Mode |
|---|---|---|
| Git ref | `origin/dev...HEAD` or `HEAD~3` | `diff` |
| Branch name | `feat/auth-rework` | `branch` |
| (no arg) | uses current uncommitted changes | `current` |
| Structured | `diff: <ref>; budget: 60s; categories: smoke,unit` | `structured` |

If the input matches none of the above, dump the current branch + `git status --short` and ask the user to specify what to diff against. Do not guess.

---

## Project config

Defaults below target a common Python web service with pytest markers. Override per-project by editing this block — every reference to these names elsewhere in the skill resolves to the values defined here. Empty list = the dependent rule never fires; the skill never silently substitutes.

```yaml
TIER_POLICY:
  # When ANY changed file path matches ANY glob in `triggers`, include ALL tests
  # whose marker set intersects `include_markers` as candidates. The policy's
  # `justification` is the diff-anchored reason recorded in the match_reasons.
  # Empty list → tier policy never fires; selection is fully surface-anchored.
  - triggers: ["**/*.py"]
    include_markers: ["smoke"]
    justification: "tier policy: smoke runs on every backend Python change"
  - triggers: ["**/db/**", "**/migrations/**", "**/alembic/**", "**/fixtures/**"]
    include_markers: ["smoke", "unit", "integration"]
    justification: "tier policy: DB-layer changes require smoke+unit+integration"
  - triggers: ["**/orchestrator*.py", "**/business_case_orchestrator*.py", "**/mcp/**", "**/tools/**", "**/registry/**", "**/routes.py"]
    include_markers: ["smoke", "unit", "integration", "live"]
    justification: "tier policy: high-blast paths require full pytest sweep incl. live UI"

NON_PYTEST_CHECKS:
  # Companion checks the parent skill should run alongside pytest. Smart-test-selection
  # does NOT execute these — it emits them in the plan artifact's Companion section.
  # Empty list → no companion checks emitted regardless of diff content.
  - triggers: ["**/*.py"]
    commands: ["ruff check <changed-py-paths>"]
    justification: "static lint on changed Python files"
  - triggers: ["**/*.py"]
    commands: ["mypy <changed-py-paths>"]
    justification: "type check on changed Python files; project-level mypy config required"
  - triggers: ["frontend/**", "**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"]
    commands: ["cd frontend && npm run lint", "cd frontend && npm run typecheck"]
    justification: "frontend lint + typecheck"
  - triggers: ["**/migrations/**", "**/alembic/versions/**"]
    commands: ["alembic upgrade head", "alembic downgrade -1", "alembic upgrade head"]
    justification: "migration up/down round-trip"

LIVE_UI_REQUIRED_PATHS:
  # Path globs that make the live-UI test mandatory in the parent skill's gate.
  # Smart-test-selection records this as a mandatory-include flag in the plan
  # artifact (alongside the live-marked tests it picks); the parent enforces
  # the gate. Empty list → no path-based live-UI requirement.
  - "**/orchestrator*.py"
  - "**/business_case_orchestrator*.py"
  - "**/mcp/**"
  - "**/tools/**"
  - "**/registry/**"
  - "**/routes.py"

CACHE_BYPASS_MARKERS:
  # Pytest markers whose tests depend on EXTERNAL state (running dev stack,
  # live APIs, browser/Playwright session) — outcomes are NOT a pure function
  # of (test code + source code + fixtures + config), so the SHA-keyed cache
  # cannot be trusted to give the same result on a clean tree.
  # Phase 5 annotates each test with one of these markers as `# cache_bypass=true`
  # in the plan artifact. Parents read the annotation and pass `--no-test-cache`
  # for those test IDs when invoking pytest.
  # Empty list → no cache-bypass annotations emitted, regardless of markers.
  - "live"

CACHE_FILE_PATH:
  # Where to find the SHA-keyed pytest cache. First existing path is used; if none
  # exist, the cache lookup gracefully degrades. Default matches pytest_test_cache.py
  # plugin convention in claude-library.
  - "documentation/test-results/<SHA>.json"
```

The `<SHA>` placeholder in `CACHE_FILE_PATH` is substituted at Phase 4 step 1 with the actual `git rev-parse HEAD` value. The `<changed-py-paths>` placeholder in `NON_PYTEST_CHECKS.commands` is substituted at Phase 5 with the space-separated list of changed `.py` files from Phase 1.

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
suggestion: [3-surface-mapping] use the import graph instead of name proximity
improvement: [4-cache-trust] re-verify cache hits before skipping
```

**Capture protocol** (the skill follows this exactly):

0. **Ownership rule (single source of truth)**: when this skill is invoked with `invocation_mode=composed`, the suggestion still gets captured **only into the deepest active skill's `improvement_suggestions[]`** — i.e. THIS skill's file, not the parent's. The parent's ledger phase looks up child suggestions cross-file at `quality_derived` computation time. Never duplicate a suggestion across two skill files; storage redundancy makes manual edits ambiguous.

   The captured entry records `parent` and `parent_run_ts` (when composed) so the parent can correlate it back to the right parent run. When standalone, both fields are null.

1. **Detect the prefix** at the start of the user's message (any of the five forms above; `[tag]` between the prefix and the text is optional). Anything that does NOT start with one of these prefixes is treated as normal conversation — *not* a suggestion. Mid-run overrides ("don't run the expensive web tests") still go through the Phase 4 budget/category resolution path, not this capture path.
2. **Record verbatim** into `improvement_suggestions[]`:
   ```json
   {
     "ts": "<iso8601-now>",
     "target": "<run input>",
     "phase": "<current phase number when the user spoke up>",
     "tag": "<optional, parsed from [brackets]>",
     "text": "<everything after the prefix and optional tag>",
     "sentiment": "<negative | aspirational | neutral>",
     "parent": "<parent skill name when composed, null when standalone>",
     "parent_run_ts": "<parent's started_at iso8601 when composed, null when standalone>",
     "applied_at": null,
     "applied_via": null
   }
   ```

   `parent` and `parent_run_ts` are populated from the same args the ledger phase parses for `invocation_mode`. Both null on standalone runs.

   **Sentiment classification** — apply the keyword heuristic at capture time (case-insensitive substring match on the suggestion text):

   | Sentiment | Trigger keywords (any match wins) |
   |---|---|
   | `negative` | `broken`, `wrong`, `incorrect`, `missed`, `failed`, `bug`, `doesn't`, `does not`, `should not`, `shouldn't`, `regression`, `flaw`, `error`, `mistake` |
   | `aspirational` | `would be nice`, `consider`, `could also`, `enhancement`, `add`, `nice to have`, `idea:`, `it would be cool`, `we should also`, `extend`, `support` |
   | `neutral` | none of the above, OR matches in both lists |

   Negative wins only when no aspirational keyword also matches — conservative classification.

3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase X, tag=<tag-or-none>, sentiment=<negative|aspirational|neutral>): "<verbatim text>"
   ```
4. **Resume** the current phase from where it was. The capture does NOT alter the current run.

---

## Observer file boundary

This skill includes an observer phase (Phase 8) that writes to `observations.json` and `suggestions.md`. **All other phases (0 through 7) MUST NOT read those files.**

The two files are owned by the observer phase exclusively and exist for cross-run pattern analysis + human review. They are *descriptive* (record what happened across prior runs), not *prescriptive* (do not encode what should happen on this run).

In particular, the agent running domain phases MUST NOT:

- Use `observations.json` content as background context when framing prompts to the user.
- Alter a phase's recommendation, default branching, or option ordering based on prior observations.
- Cite observations to justify a skill behavior in-flight.

The only legitimate path for an observation to change skill behavior is: observer clusters the signal → writes a proposal to `suggestions.md` → human reviews → human edits this `SKILL.md` (or dismisses the proposal). The audit channel and the observer channel remain **isolated by design**.

If you are an LLM/agent running this skill: treat `observations.json` and `suggestions.md` as if they did not exist until you reach Phase 8. Reading them earlier is a load-bearing violation, and there is no FAIL tag for it because the file content is silent — the only safeguard is this rule.

---

## Phase 0 — Freshness check (non-blocking)

Before running any domain work, briefly check how stale this skill has gotten. The check is **informational only** — it never blocks a run, and Phase 1 always proceeds after it.

The premise: a skill that gets used heavily but never reviewed against the current state of Claude Code, peer skills, or its own domain will silently rot. The audit + ledger catch mechanical drift inside a run; this phase catches **the skill's own design** falling behind across runs.

0. **Composition check — skip the freshness body entirely when invoked from another skill.** Parse the skill's invocation args for `invocation_mode=composed` (semicolon-separated `key=value` format). When present, **skip steps 1–4 of this phase** and proceed directly to step 5 (proceed to Phase 1). The parent skill's own freshness check is the user-facing nudge; firing a second one here would be noise. Still stamp `started_at` for timing instrumentation — that fires unconditionally regardless of invocation mode.

   Default when the arg is absent or set to anything other than `composed` is `standalone` — all freshness steps below fire.

1. **Read** `skills/smart-test-selection/run_history.json` → `validation_freshness`.
   - If the file is missing or the block is missing, initialize the block in-memory with default thresholds (runs=10, days=21).
   - Persistence happens in Phase 7 (ledger).

2. **Compute staleness**:
   - `days_since_validated = floor((now - last_validated_at) / 86400)`.
   - `runs_since = validation_freshness.runs_since_validation`.

3. **Nudge condition — both must be true (AND, not OR)**:
   - `days_since_validated >= thresholds.days` (default 21), AND
   - `runs_since >= thresholds.runs` (default 10).

4. **When the nudge fires**, print exactly this one-line block before Phase 1's first output, then continue:

   ```
   ⚠ Freshness: `smart-test-selection` last validated <days_since_validated>d ago, <runs_since> runs since.
     Consider running, when you have a moment:
       /meta-discover-claude-features  — research improvements in this skill's domain
       /meta-skill-audit               — overlap check vs. other skills
     Then append a review_log[] entry to skills/smart-test-selection/run_history.json → validation_freshness
     and bump last_validated_at + reset runs_since_validation to 0.
   ```

   **When the nudge does NOT fire**, print nothing. Silence is the success state.

5. **Proceed to Phase 1 unconditionally** — even if the nudge fires, the freshness check is never a hard gate.

**Run-start instrumentation (always fires, regardless of composition mode)**: stamp `started_at = now-iso8601` into in-memory run state at the very top of Phase 0 (before any of the steps above). The ledger phase (Phase 7) reads it back to compute `duration_seconds`.

**Parse invocation args at run start (always fires, regardless of composition mode)**: detect `invocation_mode=composed; parent=<name>; parent_run_ts=<iso8601>` in the args string. Default = `standalone` with `parent=null`, `parent_run_ts=null`. These three values are recorded by Phase 7 (ledger) on every run entry and on every captured suggestion.

---

## Per-phase timing instrumentation (global rule)

Every domain phase (1 through 5) AND the observer phase (8) is responsible for stamping its own elapsed time as it exits:

- At the **start** of each phase, record `phase_start = now`.
- At the **end** of each phase, record `phase_durations[<phase-id>] = floor((now - phase_start) seconds)`. Half-numbered sub-phases (e.g. `4.5`) record under their literal id.
- Keep `phase_durations` in in-memory run state alongside `started_at`. Phase 7 (ledger) reads the full map and writes it to `runs[].phase_durations`.

The audit (Phase 6) and ledger (Phase 7) do NOT stamp durations — their time is folded into the gap between Phase 5's end stamp and `ended_at` set by Phase 7.

---

## Phase 1 — Parse input + resolve diff scope

Detect the input mode, resolve the diff to a concrete file/symbol list, and record the verbatim input for the audit row.

1. **Detect mode**:
   - Argument matches `^[A-Za-z0-9_/.~-]+(\.\.\.?[A-Za-z0-9_/.~-]+)?$` containing `...` or `..` → `diff` mode (git revspec).
   - Argument looks like a branch name (contains `/` or matches `^(feat|fix|chore|docs|refactor|test)/`) → `branch` mode (resolve to `origin/<base>...<branch>`; default base from project config or `main`).
   - Argument starts with `diff:` and contains `;` separators → `structured` mode (parse `diff: <ref>; budget: <s>; categories: <list>`).
   - No argument → `current` mode (use `git diff --name-only HEAD` to capture uncommitted changes).
   - None of the above → dump `git rev-parse --abbrev-ref HEAD` + `git status --short` and ask the user to specify. Do NOT guess.

2. **Resolve to a concrete file list**:
   - `diff` / `branch` mode: `git diff --name-only <range>` → list of changed paths.
   - `current` mode: `git diff --name-only HEAD` → uncommitted changed paths. If empty, also run `git status --short` and ask the user whether they meant a staged-only diff.

3. **Extract changed symbols where possible** (best-effort, not load-bearing):
   - For each `.py` file in the diff, lightweight parse: top-level function names, class names, top-level import lines. Skip on parse failure — never block the phase.
   - For each `.ts`/`.tsx`/`.js`/`.jsx` file: top-level `export` names.
   - For other file types: just the file path counts as the surface.

4. **Record verbatim input** to in-memory state for the audit row. Stamp `phase_durations["1"]` on exit.

5. **Emit Phase 1 summary**:
   ```
   Phase 1: mode=<mode>, <N> changed files, <M> changed symbols extracted (best-effort).
   User input verbatim: "<literal-arg-or-(no-arg)>"
   ```

---

## Phase 2 — Inventory candidate tests

Enumerate the full pytest test inventory with markers and (where available) historical cost estimates.

1. **Run pytest collection**:
   ```
   pytest --collect-only -q --no-header
   ```
   Capture stdout (one test ID per line in `nodeid` format like `tests/test_foo.py::test_bar`), exit code, and wall-clock.

2. **Parse markers** for each collected test:
   - Re-run `pytest --collect-only -q --markers tests/` if needed, OR parse the original collection output if it included marker info.
   - For each test, record the marker set (e.g. `{smoke, unit, slow, integration, web, e2e, live}`). Empty set is valid — most unit tests are unmarked.

3. **Attach historical cost estimate** (best-effort):
   - Read prior `runs[]` from this skill's `run_history.json` → look up median wall-clock per test from prior `phase_durations` if available. Skill bootstraps cost = null until enough runs accumulate.
   - When no historical data, fall back to marker-based defaults: `unit=0.5s, smoke=1s, integration=5s, web=10s, live=30s, e2e=60s` (override per-project as cost data accumulates).

4. **Build candidate-inventory map**: `test_id → {file, marker_set, est_cost_seconds}`.

5. **Validate collection success**:
   - Exit code != 0 → mark Phase 2 FAIL with tag `2-test-inventory-stale`, surface stderr to user, ask whether to abort or proceed with whatever was collected.
   - Test count == 0 → same FAIL tag.

6. Stamp `phase_durations["2"]` on exit. Emit Phase 2 summary:
   ```
   Phase 2: pytest --collect-only returned <N> tests in <S> seconds; exit=<code>; <M> distinct markers across inventory.
   ```

---

## Phase 3 — Map changed surfaces to candidate tests

For each changed file/symbol from Phase 1, identify candidate tests in the inventory that exercise it. Output the candidates list.

1. **Apply five matching strategies** (a candidate matches if ANY strategy fires):
   - **Import graph**: a test imports a module whose source path is in the changed set. Use `ast.parse` on each test file to extract imports, resolve to source paths.
   - **Name proximity**: a test in `tests/test_<X>.py` matches when `src/<X>.py` (or `<X>/__init__.py`) is in the changed set. Also handle nested layouts (`tests/<pkg>/test_<X>.py` ↔ `src/<pkg>/<X>.py`).
   - **Marker tag**: a test marked `@pytest.mark.<tag>` matches when any changed path matches `**/<tag>/**` or contains `<tag>` in the filename stem. Skill-configurable per project.
   - **Tier policy**: for each rule in `TIER_POLICY`, when ANY changed file path matches ANY glob in `rule.triggers`, include ALL tests whose marker set intersects `rule.include_markers`. The `match_reasons` entry for each included test is `tier-policy: <justification> (triggered by path <p>)` — the policy's `justification` IS the diff-anchored reason. This preserves parent-skill routing behavior: a single backend Python change pulls in the entire smoke tier; a DB-layer change adds unit + integration; a high-blast path adds live. When `TIER_POLICY` is empty (config opt-out), this strategy contributes nothing and selection is fully surface-anchored — the original aggressive mode.
   - **Historic correlation**: when prior `runs[]` data exists, a test that has caught failures historically for changes touching the same file is automatically included even without a current surface match. Threshold: 2+ prior catches → auto-include with rationale `"historic correlation"`. Bootstraps as zero until data accumulates.

2. **Build candidates list**: union of all strategy hits. For each candidate, record which strategy(ies) matched as `match_reasons: [<strategy>, ...]`. A test included by multiple strategies (e.g. tier-policy + import-graph) records all reasons — useful later when the user wants to see why a test was kept after cost-aware pruning.

3. **Compute live-UI mandatory flag** (forwarded to the artifact in Phase 5, not enforced here): if any changed path matches a glob in `LIVE_UI_REQUIRED_PATHS`, set `live_ui_required = true` and record the triggering path(s). Smart-test-selection records this flag; the parent skill's gate logic decides whether to block on it.

4. **Sanity check** — for each changed surface, confirm at least one candidate covers it. If a surface has zero candidates AND the inventory contains a test whose `nodeid` would plausibly cover it (heuristic: filename overlap, function-name overlap), mark this run's Phase 3 with the `3-changed-surface-missing-from-candidates` FAIL tag and surface the orphan surface to Phase 7's resolution gate.

5. **Tier-policy sanity check** — for each rule in `TIER_POLICY` whose `triggers` matched at least one changed path, confirm that at least one test with marker ∈ `rule.include_markers` ended up in the candidates list (when such tests exist in the Phase 2 inventory). If a rule fired but contributed zero candidates, mark Phase 3 FAIL with `3-tier-policy-not-applied`.

6. Stamp `phase_durations["3"]` on exit. Emit Phase 3 summary:
   ```
   Phase 3: <M> candidates from <K> changed surfaces; strategies hit: import=<a>, name-proximity=<b>, marker=<c>, tier-policy=<d>, historic=<e>; orphan surfaces: <count>; live_ui_required=<y|n>.
   ```

---

## Phase 4 — Apply cost-aware selection (with SHA-keyed cache read)

Within the candidate set from Phase 3, partition into three buckets: `cached-pass`, `to-run`, `pruned-by-cost`. Every skip records a diff-anchored reason. Consumes the optional `budget` arg from `structured` input mode.

1. **Read SHA-keyed cache** (if available):
   1. `git rev-parse HEAD` → `SHA`. If shallow clone, run `git fetch --unshallow` first.
   2. `git status --porcelain` — if dirty (any output), SKIP cache. The cache is only valid on a clean tree.
   3. Locate the cache file: walk up from CWD to find a `documentation/test-results/<SHA>.json` (the convention used by `scripts/pytest_test_cache.py` opt-in target repos). If not found, treat as no cache.
   4. Parse the JSON; expected shape: `{tests: {<nodeid>: {outcome: "passed"|"failed", duration: <s>, ts: <iso>}}}`.

2. **Partition candidates against the cache**:
   - `cache_entry exists AND outcome == "passed" AND clean_tree` → bucket `cached-pass`. Skip reason: `"cached-pass at SHA <SHA> on clean tree"`.
   - `cache_entry exists AND outcome == "failed"` → bucket `to-run`. Reason for not skipping: `"prior fail at SHA <SHA>; re-run to verify after potential fix"`.
   - `cache_entry missing OR dirty_tree` → bucket `to-run` initially (subject to step 3 budget pruning).

3. **Cost-aware pruning** (only for the `to-run` bucket, never for `cached-pass`):
   - If `structured` input included a `budget: <seconds>` value, compute the cumulative cost of the `to-run` set. When over budget:
     - Group candidates by changed surface they cover. Within each group, keep the cheapest test and prune the rest. Skip reason for each pruned test: `"candidate for surface <path>; pruned because <cheaper-test-id> also covers <path> (est cost <s> vs <s>)"`.
     - If still over budget after intra-surface pruning, surface the remaining budget overrun to Phase 7's resolution gate — do NOT silently drop coverage.
   - If no budget arg, no cost-pruning fires. All non-cached candidates run.

4. **Validate every skip has a diff-anchored reason** — for each entry in `cached-pass` or `pruned-by-cost`, the `reason` string must contain at least one of: an SHA, a changed file path, a changed surface name, or another test-id explaining the substitution. Any skip lacking that → mark Phase 4 FAIL with `4-skip-without-diff-anchored-reason`.

5. **Validate cached-pass entries against the cache file** (paranoia check): for each `cached-pass` entry, confirm the cache file actually contains that test-id with `outcome=passed`. If not, mark Phase 4 FAIL with `4-cached-skip-without-clean-tree-or-sha-match`.

6. Stamp `phase_durations["4"]` on exit. Emit Phase 4 summary:
   ```
   Phase 4: cached-pass=<a>, to-run=<b>, pruned-by-cost=<c>; SHA=<sha-or-NONE>; clean_tree=<y|n>; budget=<s-or-NONE>; user input verbatim (if structured mode): "<literal-arg>"
   ```

---

## Phase 5 — Write selection plan artifact

Write the structured selection plan to a file and surface it to the user. This is the **terminal action** — fires after Phase 6 (audit) approves with `tests approved`.

1. **Compute a diff fingerprint** for the artifact filename: SHA-256 of (sorted changed file list + HEAD SHA + sorted candidate test-ids), first 12 hex chars.

2. **Write the artifact** to `documentation/test-plans/<fingerprint>.md` (create parent dirs if needed). Use this format:

   ```markdown
   # Test selection plan — <fingerprint>

   **Generated by**: `smart-test-selection`
   **HEAD SHA**: <SHA>
   **Diff scope**: <mode>, <input-verbatim>
   **Clean tree**: <y|n>
   **Live UI required**: <y|n> (triggered by: <path-list-or-NONE>)
   **Wall-clock estimate**: ~<S> seconds (vs ~<S_no_cache> without cache)

   ## Tests to run (<count>)

   ```
   <test-id-1>
   <test-id-2>
   <test-id-3>  # cache_bypass=true
   ...
   ```

   Each line is a pytest node ID. Lines ending with `# cache_bypass=true` indicate
   tests whose marker set intersects `CACHE_BYPASS_MARKERS` — the parent skill MUST
   invoke pytest for those IDs with `--no-test-cache` so external state (running
   dev stack, live APIs, browser sessions) is re-verified rather than trusted from
   a prior-SHA cache hit. Lines without the annotation participate in the cache
   normally.

   ## Cached-pass at this SHA (<count>) — diff-anchored skips

   - `<test-id>` — <skip reason>
   - ...

   ## Pruned by cost (<count>) — diff-anchored skips

   - `<test-id>` — <skip reason>
   - ...

   ## Companion non-pytest checks (for the invoking caller to run)

   Smart-test-selection does NOT execute these — it emits the checklist so the
   parent skill (or user) has one artifact for both pytest plan + companion checks.
   For each rule in `NON_PYTEST_CHECKS` whose triggers match the diff, one bullet:

   - `<command-with-placeholders-substituted>` — <justification> (triggered by path <p>)
   - ...

   ## Orphan changed surfaces (<count>) — needs user resolution

   - <changed-path> — no candidate test found in inventory
   - ...
   ```

   **Companion checks generation rules**:
   - Walk every rule in `NON_PYTEST_CHECKS`. For each rule, if ANY changed file path matches ANY glob in `rule.triggers`, emit one bullet per command in `rule.commands`.
   - Substitute `<changed-py-paths>` with the space-separated list of changed `.py` files (from Phase 1's file list, filtered to `*.py`). If no `.py` files in diff but the placeholder is present, omit that command (the rule's trigger may have matched on a non-Python file).
   - Each bullet's `justification` and `triggered by path` come verbatim from the rule's `justification` field and the first matching diff path.
   - When `NON_PYTEST_CHECKS` is empty OR no rule matches, the section header still appears with `"(none — no NON_PYTEST_CHECKS rules matched the diff)"` so the parent skill can confirm the section was considered, not silently dropped.

   **Cache-bypass annotation rules** (for the "Tests to run" section):
   - For each test ID emitted in "Tests to run", look up its marker set from the Phase 2 inventory.
   - If the marker set intersects `CACHE_BYPASS_MARKERS` (any single marker match wins), append `  # cache_bypass=true` to the line (two spaces before the `#` for readability).
   - Tests with no markers, or markers not in `CACHE_BYPASS_MARKERS`, emit as plain pytest node IDs (no annotation).
   - When `CACHE_BYPASS_MARKERS` is empty, NO annotations are emitted regardless of markers — the section is plain node IDs only.
   - The annotation is the SINGLE SOURCE OF TRUTH for which tests bypass the cache. Parent skills MUST NOT independently re-derive this from marker introspection — they read the annotation and honor it.

3. **Validate the artifact is pytest-runnable**: pick 3 random entries from the `Tests to run` list and confirm `pytest --collect-only --co --pyargs <id>` returns each one. If any sample fails, mark Phase 5 FAIL with `5-artifact-not-pytest-runnable`.

4. **Display the artifact path + summary to the user** for review:
   ```
   Plan written: documentation/test-plans/<fingerprint>.md
   To run: <N> tests (~<S>s estimated)
   Cached-pass: <M> (~<S_saved>s saved at SHA <SHA>)
   Pruned: <K>
   Live UI required: <y|n>
   Companion non-pytest checks: <C> (run alongside pytest)
   Orphans: <count> (needs your attention if > 0)
   ```

5. Stamp `phase_durations["5"]` on exit. The file-write IS the terminal action — gate it on the Phase 6 audit's approval token `tests approved`.

---

## Phase 6 — Pre-action self-audit (CHECKPOINT, blocking)

The audit runs **before** the file-write. File-write cannot fire until the user explicitly confirms or corrects every audit row. Goal: verbatim, falsifiable evidence — never the skill's interpretation of user intent.

1. **Walk every phase that ran in this session** and emit a structured block. Each verdict MUST cite **objective evidence**: a tool call observed, a command output, a file diff, or a **literal quote** from the user. **Never paraphrase user input.** If the user said "tests approved" with no per-item resolution, record `user said: "tests approved" (no per-item resolution)` — do NOT invent a justification, do NOT summarise intent.

   ```
   Self-audit for run on <input> at <ts>:
   - Phase 1 [pass|FAIL] | input parsed (mode=<mode>); <N> files, <M> symbols; user input verbatim: "<literal quote>"
   - Phase 2 [pass|FAIL] | pytest --collect-only: <N> tests in <S>s, exit=<code>; <M> markers
   - Phase 3 [pass|FAIL] | <M> candidates from <K> surfaces; strategies hit: import=<a>, name-proximity=<b>, marker=<c>, tier-policy=<d>, historic=<e>; orphans=<count>; tier-policy-rules-fired=<f>/<g>; live_ui_required=<y|n>
   - Phase 4 [pass|FAIL] | partition cached-pass=<a>/to-run=<b>/pruned=<c> at SHA <sha>; clean_tree=<y|n>; budget=<s-or-NONE>; user input verbatim (if structured): "<literal quote>"
   - Phase 5 [pass|FAIL] | artifact at documentation/test-plans/<fp>.md; pytest-runnability sample 3/3 pass; companion-checks=<C>; cache-bypass-annotated=<B>; wall-clock estimate <S>s
   ```

   Each row format: `- Phase X [pass|FAIL] | <evidence>` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input.

2. **FAIL detection rules** — these trigger automatically; the skill cannot mark `pass` without satisfying them:

   **Universal FAIL rules** (every self-learning skill inherits these):
   - **`audit-paraphrased-user-input`** (load-bearing, threshold=1): any audit row that paraphrases user intent rather than quoting verbatim.
   - **`audit-no-explicit-approval-wait`** (procedural, threshold=2): skill advanced past a user-gate phase without observing the literal approval token.
   - **`tool-claim-without-call`** (load-bearing, threshold=1): audit row says "ran X" / "invoked Y" but no corresponding tool call observed in this session.

   **Domain FAIL rules** (specific to this skill):

   - **`2-test-inventory-stale` FAIL** (procedural, threshold=2): `pytest --collect-only` exited non-zero OR returned 0 tests. Detection: capture exit code AND stdout test count.
   - **`3-changed-surface-missing-from-candidates` FAIL** (load-bearing, threshold=1): a changed surface from Phase 1 has at least one matching test in the Phase 2 inventory but no candidate in the Phase 3 candidates list covers it. Detection: for each changed surface, check if the inventory contains any test whose nodeid plausibly matches (filename or symbol overlap) AND check that test made it into the candidates list.
   - **`3-tier-policy-not-applied` FAIL** (procedural, threshold=2): a `TIER_POLICY` rule's `triggers` matched ≥1 changed path BUT no test with marker ∈ `rule.include_markers` ended up in the candidates list (when such tests exist in the Phase 2 inventory). Detection: Phase 3 step 5. Procedural because a single occurrence may be a config-tuning mismatch; two means the strategy is silently broken — the very issue we built it to prevent.
   - **`4-skip-without-diff-anchored-reason` FAIL** (load-bearing, threshold=1): a skip entry in `cached-pass` or `pruned-by-cost` has a `reason` field that does not contain any of: an SHA, a changed file path, a changed surface name, another test-id explaining the substitution, OR a `TIER_POLICY` justification phrase. Detection: regex scan each skip reason for these tokens.
   - **`4-cached-skip-without-clean-tree-or-sha-match` FAIL** (load-bearing, threshold=1): a test marked `cached-pass` in the plan but the cache file doesn't actually contain it at the current SHA, OR the working tree was dirty at lookup time. Detection: re-read cache file, confirm each cached-pass entry exists with `outcome=passed`, confirm `git status --porcelain` was empty at Phase 4 step 1 time.
   - **`5-artifact-not-pytest-runnable` FAIL** (load-bearing, threshold=1): a random sample of 3 IDs from the artifact's `Tests to run` list failed `pytest --collect-only --co <id>` validation. Detection: Phase 5 step 3.
   - **`5-companion-checks-section-missing` FAIL** (procedural, threshold=2): a `NON_PYTEST_CHECKS` rule's `triggers` matched ≥1 changed path BUT the artifact's `Companion non-pytest checks` section is missing the corresponding command bullet. Detection: re-parse the written artifact; for each matching rule, confirm ≥1 bullet whose justification matches the rule's `justification` is present. Procedural threshold=2 because one miss may be a config edge case; two means the emitter is dropping checks.
   - **`5-cache-bypass-marker-missing` FAIL** (procedural, threshold=2): a test whose marker set intersects `CACHE_BYPASS_MARKERS` appeared in the artifact's `Tests to run` list WITHOUT the trailing `# cache_bypass=true` annotation. Detection: re-parse the written artifact's "Tests to run" section; for each test ID without an annotation, look up its markers from the Phase 2 inventory; if any marker is in `CACHE_BYPASS_MARKERS`, mark FAIL. Procedural threshold=2 because one miss may be a marker-string mismatch (e.g. project added a new state-dependent marker without updating config); two means the annotator is silently dropping cache-bypass declarations — exactly the failure mode this rule exists to catch.

3. **Show the audit and ask the user to confirm OR correct every row.** The audit is NOT approved on silence or partial answer. The skill must wait for the user to:
   - **confirm** each row as written, OR
   - **dictate corrections** (which the skill applies verbatim and re-displays the audit), OR
   - **mark a row FAIL with a tag** (which the skill records).

4. **Approval gate**: the file-write cannot fire until the user explicitly types `tests approved` (case-insensitive). Silence, "looks good", "ok", "proceed", or partial responses are NOT approval.

5. **Suggestion review (final-call)** — *runs only after the approval token is received, before the ledger phase fires*. Surface every entry captured during this run via the suggestion-capture protocol, then offer the user a final chance to add more:

   ```
   Suggestions captured during this run (N total):
     1. [phase X, tag=<tag-or-none>] "<verbatim text>"
     2. [phase Y, tag=<tag-or-none>] "<verbatim text>"
     ...

   Any final suggestions to add? Use the same trigger-prefix syntax (or type `done` to skip):
     - suggestion: <text>
     - improvement: <text>
     - for the skill: <text>
     - [suggestion] <text>
   ```

   Append any final entries to `improvement_suggestions[]` with the same shape as mid-run captures; the `phase` field for these final-call entries is `"audit"`. If the user types `done`, proceed to Phase 7. Silence is NOT advancement — wait for `done`.

## Phase 7 — Update the run-history ledger

Persist the audit so failure patterns become evidence over time.

1. **Read** `skills/smart-test-selection/run_history.json`. Initialize if missing per the schema.

2. **Append** the run summary to `runs[]`. Include the timing, quality, and composition fields:
   ```json
   {
     "ts": "<iso8601 of this ledger write — same as ended_at>",
     "target": "<input>",
     "outcome": "<closed|paused|aborted|in-progress>",
     "phases_failed": ["<tag>", ...],
     "started_at": "<iso8601 captured at run start in Phase 0>",
     "ended_at": "<iso8601-now>",
     "duration_seconds": <ended_at - started_at, integer seconds>,
     "phase_durations": {"1": <s>, "2": <s>, "3": <s>, "4": <s>, "5": <s>, "8": <s>},
     "quality_derived": "<clean|partial|failed|incomplete>",
     "invocation_mode": "<standalone | composed>",
     "parent": "<parent-skill-name | null>",
     "parent_run_ts": "<iso8601 of parent's started_at | null>"
   }
   ```

   **`quality_derived` is computed mechanically**:
   - `clean` ← `outcome == "closed"` AND `phases_failed` empty AND no `negative`-sentiment suggestion exists for this run's window.
   - `partial` ← `outcome == "closed"` AND (`phases_failed` non-empty OR negative suggestion exists).
   - `failed` ← `outcome == "aborted"`.
   - `incomplete` ← `outcome == "paused"` OR `"in-progress"`.

   **Cross-skill lookup (only when this run is a PARENT — `invocation_mode == "standalone"`)**: for parent runs of THIS skill — which is rare since this skill is usually composed — also check each composed child's `run_history.json` for negative-sentiment entries within `[started_at, ended_at]` whose `parent_run_ts == this_run.started_at`. This skill currently composes no children, so this lookup is a no-op in practice but is preserved for forward compatibility.

   **When `invocation_mode == "composed"`**: skip cross-skill lookup. Compute `quality_derived` from this skill's own `improvement_suggestions[]` only.

3. **For each FAIL tag** observed in this run:
   - Increment `fail_counters[<tag>].count` by 1.
   - Append `{ts, target, detail}` to `fail_counters[<tag>].occurrences[]` (trim to last 20).
   - If the tag is new, create the entry with threshold per tier (load-bearing=1, procedural=2, cosmetic=5).

4. **Persist captured suggestions**. Any entries added to `improvement_suggestions[]` during this run (mid-run captures + Phase 6 step 5 final-call entries) are written as part of the same `Write` call. Append-only.

4a. **Update `validation_freshness`**: increment `runs_since_validation` by 1. Do NOT modify `last_validated_at`, `last_research_at`, `last_overlap_check_at`, or `review_log[]` — those are user-owned.

5. **Write the file** with the `Write` tool.

6. **Print run-end summary**:
   ```
   Run summary: outcome=<closed|paused|aborted>, FAIL tags=<count>, suggestions=<this-run-count> (total log: <all-time-count>)
   Review suggestions at: skills/smart-test-selection/run_history.json → improvement_suggestions[]
   ```

7. **Threshold check** — for any counter where `count >= threshold`, print a fix proposal block and auto-apply the SKILL.md edit per `remediation_hint`. Reset counter to 0; set `applied_at`; optionally fill `applied_via`. Conflict handling: serial application, oldest tag first.

## Phase 8 — Post-ledger observer (suggestion-only)

The observer runs **after** the ledger has written `run_history.json` and any audit-tripped remediations have been auto-applied. Its job is to surface qualitative signals the audit's mechanical FAIL detection cannot catch, and — once enough observations accumulate — propose changes for manual review.

The observer NEVER edits `SKILL.md`. It writes only to `observations.json` and `suggestions.md`.

0. **Composition check — skip the observer body entirely when invoked from another skill.** Parse the invocation args for `invocation_mode=composed`. When present, skip steps 1–7 and return cleanly. The parent skill's observer is the single cross-run pattern detector for this user-facing run.

   Composed runs are still recorded in `runs[]` with `invocation_mode: "composed"`. Cross-run pattern detection for this skill is deferred until standalone invocation.

1. **Read state**:
   - `skills/smart-test-selection/observations.json` — initialize per schema if missing.
   - `skills/smart-test-selection/run_history.json` — for the just-finished run and prior runs.

2. **Walk the just-finished run from a different vantage than the audit.** Categories to scan for:

   | Category slug | What to look for |
   |---|---|
   | `user_friction` | re-asked questions, repeated corrections, "you missed", visible frustration |
   | `redundant_phase` | phase Y duplicates phase X's output |
   | `scope_drift` | the skill ventured outside its frontmatter description |
   | `missing_audit_category` | a recurring qualitative concern with no FAIL tag covering it |
   | `dev_env_friction` | environmental setup pain that recurs across runs |
   | `output_format_quality` | UX-only signal: format/readability of the skill's output |
   | `boundary_violation` | a domain phase referenced `observations.json` / `suggestions.md` |
   | `phase_scope_too_broad_for_input` | a phase ran a full-scope routine when narrower would suffice |
   | `serializable_as_parallel` | two phases ran sequentially with no data dependency |
   | `redundant_work_with_prior_phase` | a phase recomputed something earlier already produced |
   | `over_thorough_for_input_class` | long-running phase on tiny input |
   | `missed_cached_result` | work whose result already exists in `runs[]` for the same input shape |

2a. **Efficiency trade-off detector** — runs only when this run has `duration_seconds` and `quality_derived` populated. Group prior runs by input-class similarity (default: by `outcome` AND `quality_derived` tier; this skill can additionally segment by `mode` from Phase 1 — `diff`/`branch`/`current`/`structured`). Compute cohort median (need ≥ 3 prior cohort members).

   **File observation** when:
   - `duration_seconds > 1.5 × cohort_median` AND quality NOT strictly better than median → `phase_scope_too_broad_for_input` (or more specific category).
   - `duration_seconds < 0.5 × cohort_median` AND quality strictly worse than median → inverse failure (race-to-fast-trash detector).

   Evidence MUST include exact numbers: this run's duration, cohort median, both quality_derived values, cohort size.

3. **Append observations** to `observations.json`. Verbatim evidence only. Zero observations is valid.

   ```json
   {
     "ts": "<iso8601-now>",
     "run_ref": "<ts of matching runs[] entry>",
     "target": "<run input>",
     "category": "<slug>",
     "_theme_slug": "<optional sub-theme>",
     "phase": "<phase number or 'cross-phase'>",
     "evidence": "<verbatim quote / observed event>",
     "interpretation": "<one-line reasoning>",
     "proposed_audit_tag": "<optional new FAIL tag or null>",
     "invocation_mode": "<standalone | composed>",
     "parent": "<parent skill name or null>"
   }
   ```

4. **Cross-run clustering check** — for each category, count unaddressed observations. If `count >= 3` (default threshold), trip a proposal pass. **Convergence rule**: 1 observation + matching `improvement_suggestions[]` entry by tag or theme also trips, regardless of count.

5. **Write proposal to `suggestions.md`** for each tripped category. Format per `observer-phase.md`. Status: `unreviewed`.

6. **Append to `review_log[]`** in `observations.json`.

7. **Print observer summary**:
   ```
   Observer: <count> new observations recorded; <count> proposals written to suggestions.md (<unreviewed-total> unreviewed)
   ```

8. **Hard limits**:
   - Observer NEVER edits `SKILL.md`.
   - Observer NEVER paraphrases evidence.
   - Observer NEVER invents observations.
   - Observer NEVER auto-applies.
   - Observer touches `run_history.json` ONLY to append a single `friction_log[]` entry when category is `dev_env_friction`.
   - Observer does NOT block run closure.

Stamp `phase_durations["8"]` on exit.

---

## Edge cases

1. **Empty diff** — `git diff` returns no changed files. Phase 1 emits a summary noting empty diff; Phase 3 returns zero candidates; Phase 4 partition is all-empty; Phase 5 writes a plan with `Tests to run: 0` and notes the empty diff in the header. Audit and ledger fire normally.
2. **Pytest collection errors mid-inventory** — Phase 2 partial collection. Mark `2-test-inventory-stale` FAIL; ask user whether to abort or proceed with partial inventory.
3. **No cache file at HEAD SHA** — fully expected on first invocation in a repo or after a fresh commit. Phase 4 step 1 gracefully degrades: `cached-pass` bucket is empty, all candidates go to `to-run`.
4. **Dirty working tree** — Phase 4 step 1 skips cache lookup entirely. Plan still writes; all candidates go to `to-run`.
5. **Shallow clone** — Phase 4 step 1 sub-step 1 first runs `git fetch --unshallow` so SHA resolution is reliable. If unshallow fails (e.g., network), log to `friction_log[]` and proceed with whatever SHA `git rev-parse HEAD` returns; cache lookup may still work.
6. **Budget arg larger than full-set cost** — no pruning fires; plan runs everything. Phase 4 summary still emits the budget value for traceability.
7. **Pytest config (`pyproject.toml`/`conftest.py`) excludes some tests** — `pytest --collect-only` already honors config; the skill operates on the inventory pytest actually exposes.

## Plugin skills composed by this skill

| Skill | Phase | Trigger |
|---|---|---|
| *(none — populate by hand if/when you discover compositions on first runs)* |  |  |

## Plugin skills NOT composed

- `safe-changes-impact-check` — operates at architectural blast-radius scope; this skill operates at file/symbol level. Different granularity.
- `code-diagnosis` — answers "is the code correct?"; this skill answers "which tests verify the change?" Adjacent but orthogonal.
- `quality-bug-sweep` — full-project scan; this skill is diff-scoped.

## Out of scope (v1)

- **Running pytest itself.** This skill emits a selection plan; downstream (user, parent skill, CI) runs `pytest <test-ids>` against the plan.
- **Mutating the SHA-keyed cache.** Read-only access. Writing happens via the existing `scripts/pytest_test_cache.py` pytest plugin, triggered by whoever runs pytest after this skill.
- **Cross-language test inventories** beyond Python pytest. Future versions may extend to other test runners; v1 is pytest-only.
- **Test prioritization beyond cost-aware pruning.** Smart ordering (run-likely-to-fail-first) is future work; v1 emits an unordered list.

## Usage

```
/smart-test-selection                                       # uses current uncommitted changes
/smart-test-selection origin/dev...HEAD                     # diff mode
/smart-test-selection feat/auth-rework                      # branch mode
/smart-test-selection "diff: HEAD~3; budget: 60s"           # structured mode
/smart-test-selection "diff: HEAD; categories: smoke,unit"  # structured mode with category filter
```

The skill walks Phases 0–8 and asks for explicit `tests approved` before writing the plan artifact. Failure patterns accumulate in `run_history.json`; when a counter trips its threshold, the skill auto-edits its own SKILL.md per the `remediation_hint`.

When invoked from another self-learning skill (e.g. `pr-merge-readiness` Phase 4), the parent passes `invocation_mode=composed; parent=<parent-skill>; parent_run_ts=<iso8601>` in the args string. Phase 0 (freshness) and Phase 8 (observer) skip their bodies in that case; audit, ledger, and timing fire regardless.

---

## Self-learning checklist (before shipping)

- [ ] `run_history.json` exists at the skill's root, initialized with the universal seed FAIL rules + 5 domain rules + `validation_freshness` block.
- [ ] The audit phase (Phase 6) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every phase that consumes user input (Phase 1, Phase 4 with structured input) has a row format that records the input **verbatim**, never paraphrased.
- [ ] The terminal action (Phase 5 file-write) requires the literal `tests approved` token from Phase 6 — silence, "ok", "looks good" do NOT advance.
- [ ] Threshold tiers match phase severity: load-bearing=1, procedural=2, cosmetic=5.
- [ ] Phase 0 — Freshness check is present BEFORE Phase 1 with composition-skip wiring.
- [ ] `validation_freshness` block initialized with thresholds runs=10, days=21.
- [ ] Ledger phase (Phase 7) contains the `runs_since_validation` increment step.
- [ ] `observations.json` exists at the skill's root, initialized with the schema v1 "Initial state" (empty `observations[]` and `review_log[]`).
- [ ] `suggestions.md` exists at the skill's root, header only, no proposals at bootstrap.
- [ ] Observer phase (Phase 8) is the LAST phase. No phase fires after it.
- [ ] `Observer file boundary` callout is present near the top of the SKILL.md (between Inputs/capture block and Phase 0). Without it, the prohibition against domain phases reading observer files is not enforced.
- [ ] Composition protocol wired: Phase 0 + Phase 8 skip when `invocation_mode == composed`. Ledger records `invocation_mode`, `parent`, `parent_run_ts`. Capture records `parent`, `parent_run_ts`.
