---
name: meta-self-learning-skill-gen
description: Generate a self-learning Claude Code skill through interactive interview. Walks the user through naming, terminal action, approval token, domain phases, and optional FAIL rules, then assembles a working SKILL.md (with audit + ledger phases inlined) and a bootstrapped run_history.json under skills/<name>/. Use when authoring a new self-learning skill, when the manual template-assembly process feels too tedious, or when you want a guided generation flow. Keywords self-learning skill generate audit ledger run_history fail counter threshold scaffolding self-improving meta skill generator.
---

# Meta — Self-Learning Skill Generator

**Purpose**: interview the user about a new self-learning skill domain, then generate a complete `skills/<name>/` folder with a working SKILL.md (audit + ledger phases inlined and parameterized) and a bootstrapped run_history.json.

**Use when**:
- Authoring a new self-learning skill from scratch.
- The manual template-assembly procedure in `documentation/SELF_LEARNING_SKILLS.md` feels tedious.
- You want a guided flow that handles all placeholder substitutions, audit row formatting, and JSON bootstrapping for you.

**Not for**:
- Editing an existing self-learning skill — open its SKILL.md directly.
- Generating non-self-learning (regular) skills — copy from `skills/<existing-skill>/` and edit by hand.

**Pattern reference**: `documentation/SELF_LEARNING_SKILLS.md` (full design doc, invariants, threshold tiering).

**Templates this skill consumes**:
- `library/templates/self-learning-skill/SKILL.md.tpl` — frame
- `library/templates/self-learning-skill/audit-phase.md` — audit body (Phase N-1)
- `library/templates/self-learning-skill/ledger-phase.md` — ledger body (Phase N) — emits timing + `quality_derived` UNCONDITIONALLY (no toggle)
- `library/templates/self-learning-skill/run_history_schema_v1.md` — schema + bootstrap JSON (includes timing + sentiment fields)
- `library/templates/self-learning-skill/freshness-phase.md` — freshness body (Phase 0, default opt-in, consumed in Step 5.4 / 8a.4)
- `library/templates/self-learning-skill/suggestion-capture.md` — mid-run user-suggestion capture block with sentiment auto-classification (consumed in Step 5.5 / 8a.5)
- `library/templates/self-learning-skill/observer-phase.md` — observer body with efficiency categories + trade-off detector (Phase N+1, OPTIONAL, consumed in Step 5.6 / 8a.7)
- `library/templates/self-learning-skill/observations_schema_v1.md` — observer schema + bootstrap JSON for `observations.json` and `suggestions.md`

**Always-on instrumentation** (every generated skill inherits this; no interview toggle):
- Each domain phase stamps its own `phase_durations[<id>] = seconds_elapsed` to in-memory run state on exit.
- Phase 0 (or Phase 1 if no Phase 0) stamps `started_at` once at run start.
- The ledger phase computes `ended_at`, `duration_seconds`, and `quality_derived`, and writes all four fields plus `phase_durations` into the `runs[]` entry for this run.
- The suggestion-capture block auto-classifies `sentiment` on every captured suggestion using the keyword heuristic in `suggestion-capture.md`.
- These are NOT optional toggles. Generated skills always emit timing and sentiment. The data is harmless when unused; an opt-out would mean some skills can't participate in efficiency analysis.

---

## Philosophy

Self-learning skills are non-trivial to assemble by hand: substitutions span four template files, the audit phase needs a custom row per domain phase, the run_history.json bootstrap has nested seed rules, and a missed placeholder breaks the skill silently.

This generator removes the tedium so the user only makes **decisions** — what's the principle? what's the terminal action? what are the phases? — and the skill handles the assembly mechanically.

The interview is the value. Resist the urge to skip questions; each one corresponds to a load-bearing design decision in the resulting skill.

---

## Process

### Step 1 — Detect starting point

1. **Check arguments and dispatch**:
   - If the user passed `convert <path-to-skill-dir-or-SKILL.md>`: jump to the **Convert Mode** section below (Steps C1–C8). Greenfield Steps 2–10 do NOT run.
   - If the user passed `improve <skill-name>`: respond "Improve mode is not yet supported in v1. To modify an existing self-learning skill, open its SKILL.md directly." and stop.
   - Otherwise: continue with greenfield generation (Steps 2–10).
2. **Read the templates** (you'll substitute from them later). The first four are mandatory; the rest are loaded on demand based on Step 5.4 / 5.5 / 5.6 toggles:
   - `library/templates/self-learning-skill/SKILL.md.tpl`
   - `library/templates/self-learning-skill/audit-phase.md`
   - `library/templates/self-learning-skill/ledger-phase.md`
   - `library/templates/self-learning-skill/run_history_schema_v1.md`
   - `library/templates/self-learning-skill/freshness-phase.md` (read when Step 5.4 enables the freshness check — default y)
   - `library/templates/self-learning-skill/suggestion-capture.md` (read when Step 5.5 enables suggestion-capture)
   - `library/templates/self-learning-skill/observer-phase.md` (read when Step 5.6 enables observer)
   - `library/templates/self-learning-skill/observations_schema_v1.md` (read when Step 5.6 enables observer)

   If any required template is missing, abort with a clear error pointing to the path. Do NOT try to repair or invent template content.

### Step 2 — Interview: identity + location

Ask all five questions at once, let the user answer in bulk:

```
I'll generate a self-learning skill for you. First, the basics:

0. Where should this skill live? Pick one:
   - plugin   — `skills/<name>/` in this plugin repo (loadable across projects via `--plugin-dir`)
   - project  — `.claude/skills/<name>/` in the current project (project-specific)
   - user     — `~/.claude/skills/<name>/` (personal, across all your projects)
   - custom   — provide an absolute path to a directory; the skill folder will be created inside it

1. Skill name? (kebab-case, e.g. `log-decision`. Must not collide with an existing skill at the chosen location.)
2. One-sentence description? (what the skill does — will go in the YAML description)
3. Trigger keywords? (comma-separated, used by skill auto-routing)
4. Load-bearing principle? (the one rule the skill must NEVER violate — guides tier classification later)
```

**Validate the location** and resolve to an absolute `target_dir` for use in later steps:
- `plugin` → `target_dir = <CWD>/skills`. Confirm CWD looks like a plugin repo (contains `.claude-plugin/plugin.json` OR a populated `skills/` dir with peer skills). If CWD is not a plugin repo, warn and ask the user to confirm or switch to `project`.
- `project` → `target_dir = <CWD>/.claude/skills`. Create `<CWD>/.claude/skills/` with `mkdir -p` if missing. Confirm CWD is a git repository (contains `.git/`).
- `user` → `target_dir = ~/.claude/skills` (resolve `~` to the actual home dir). Create if missing.
- `custom` → ask the user for an absolute path to a parent directory (NOT including `<name>`). Validate the parent directory exists and is writable. The skill folder will be created at `<custom-path>/<name>/`.

**Validate the name**:
- Must match `^[a-z][a-z0-9-]+$` (kebab-case, no underscores).
- Use `Glob` `<target_dir>/<name>/` to confirm the directory doesn't already exist. If it does, stop and ask the user for a different name. **Never overwrite an existing skill folder under any circumstance.**

**Carry `target_dir` forward** through Steps 7, 8c, 9, and 10 — every reference to `skills/<name>/` in the rest of this doc means `<target_dir>/<name>/`.

### Step 3 — Interview: terminal action and approval token

```
What's the terminal action? (the final state-changing operation the skill performs)
  - commit          (writes a git commit; most common)
  - deploy          (publishes / pushes / releases)
  - doc-edit        (writes a doc file as the final artifact)
  - file-write      (writes a non-doc file as final artifact)
  - api-call        (makes an external API call)
  - other (specify)

What literal token must the user type to fire the terminal action?
  Examples: `commit`, `audit approved`, `deploy now`, `approved`
  This is the approval gate. Silence, "ok", "looks good", "proceed" will NOT advance.
```

**Validate**: the approval token should be 1–4 words, lowercase, no punctuation. Warn the user if it's longer or contains special characters.

### Step 4 — Interview: inputs

```
What inputs does the skill accept? Pick one or more shapes:
  - free-text       (e.g. "use psycopg3 over asyncpg, rationale: perf")
  - ID pattern      (e.g. `W-7-prep-c`, `GAP-002` — give the regex)
  - file path       (e.g. `documentation/foo.md`)
  - structured      (e.g. `decision: X | rationale: Y` with explicit markers)

For each shape: a short example. If none of these fit, describe the shape in your own words.
What should the skill do if input doesn't match any shape? (e.g., "ask the user to restate")
```

Capture each shape as a row for the SKILL.md `## Inputs` table.

### Step 5 — Interview: domain phases

Domain phases are everything before the audit (Phase N-1) and ledger (Phase N). Typically 2–8 phases.

First ask:

```
How many domain phases will the skill have, before the audit and ledger?
  Typical range: 2 (parse + apply) to 8 (parse + verify + plan + implement + test + sweep + ...)
  If unsure, start with 3 — you can always extend the SKILL.md later.
```

Then loop through each phase. For phase `i` (1-indexed):

```
--- Phase i ---
1. Name? (e.g. "Parse the input", "Implement the fix", "Pre-commit sweep")
2. What does this phase do? (1–3 sentences — will become the phase body)
3. Tier? (load-bearing / procedural / cosmetic — drives FAIL threshold for any rule landing in this phase)
   - load-bearing: violates the skill's core principle if it fails. threshold=1.
   - procedural: drift if it recurs but one occurrence may be noise. threshold=2.
   - cosmetic: low cost when missed. threshold=5.
4. Does this phase consume user input? (y/n)
   If y: the audit row for this phase MUST quote the input verbatim, never paraphrase.
5. Is this the terminal-action phase (the one whose approval token fires the commit/deploy/etc.)? (y/n)
   Typically only the LAST domain phase is the terminal-action phase, immediately before the audit.
   Note: simple skills can collapse audit + terminal-action into one phase — answer `n` here, and
   the audit phase's approval gate will fire the terminal action directly. Complex skills (like
   `shared-bug-gap-fix`) keep them separate.
```

After collecting all phases, summarize:

```
Phases captured:
  Phase 1 — <name> (<tier>, consumes-input=<y/n>, terminal=<y/n>)
  Phase 2 — <name> ...
  ...
  Phase <N-1> — Pre-action self-audit (auto-generated)
  Phase <N>   — Update run-history ledger (auto-generated)

Confirm? [y/n]
```

If `n`, allow the user to edit phase names/tiers/flags before proceeding. Loop until `y`.

### Step 5.4 — Interview: Phase 0 freshness check

```
Should this skill include the Phase 0 freshness check? (y/n, default y)
  When enabled, the skill runs a non-blocking Phase 0 that prints a one-line
  nudge if the skill is both old (>= 21 days since last validated) and well-used
  (>= 10 runs since last validated). The nudge points the user at:
    /meta-discover-claude-features  — research improvements in the skill's domain
    /meta-skill-audit               — overlap check vs. other skills
  Silence is the success state — the phase prints nothing when fresh and never
  blocks Phase 1.

  Default y. Opt-out only when:
    - The skill has a deliberately frozen surface (e.g. one-shot generator that
      shouldn't be evolving its design).
    - The skill is internal scaffolding the user never invokes directly.
```

If `y`, also ask:

```
Override default thresholds? (y/n, default n — keeps runs=10, days=21)
  Tune lower for hot skills run multiple times per day; raise the days threshold
  for quiet skills with stable surfaces. Both numbers must be positive integers.
```

If the user opts to override, capture:
- `freshness_threshold_runs: <int>` (default 10)
- `freshness_threshold_days: <int>` (default 21)

Otherwise carry the defaults forward.

Carry `freshness_enabled: <true|false>` and the two threshold values forward to Steps 7, 8a, 8b, 8c, and 9.

### Step 5.5 — Interview: mid-run suggestion capture

```
Should this skill include the Mid-run suggestion capture block? (y/n, default y)
  When enabled, users can propose improvements to the skill at any point during
  a run via trigger prefixes (`suggestion:`, `improvement:`, `for the skill:`,
  `[suggestion]`, `[skill-improvement]`). Each is captured verbatim into
  improvement_suggestions[] in run_history.json. The audit phase also gets a
  final-call review step.

  Default y. Opt-out only for skills where it doesn't fit:
    - Pure interview/Q&A skills with no execution loop.
    - Single-domain-phase skills (no in-run context to capture).
    - One-shot generators where the artifact is the entire output.
```

Carry `suggestion_capture_enabled: <true|false>` forward to Steps 7, 8a, 8b, 9.

### Step 5.6 — Interview: observer phase (Phase N+1, OPTIONAL prototype pattern)

```
Should this skill include the Observer phase (Phase N+1)? (y/n, default n)

  When enabled, a post-ledger phase records qualitative signals the audit's
  mechanical FAIL detection cannot catch — user friction, redundant phases,
  scope drift, signs of missing audit categories — and surfaces clustered
  proposals to a `suggestions.md` file. Suggestion-only; never auto-edits SKILL.md.
  Two new files are created at the skill's root: `observations.json` (per-run
  ledger) and `suggestions.md` (clustered proposals queue).

  Default n. The pattern is a prototype (see `documentation/SELF_LEARNING_SKILLS.md`
  in the claude_experiments repo). Enable when:
    - The skill will run frequently (cross-run pattern detection has runway).
    - The skill consumes meaningful user input (Phase 7-style resolution gates).
    - You want a second vantage on what audit can't reach.

  IMPORTANT: if you enable observer but disable suggestion-capture (Step 5.5),
  the convergence rule cannot fire (it requires `improvement_suggestions[]`).
  Recommend enabling both together. Warn the user if they choose
  observer=y AND suggestion_capture=n.
```

If the user answers `y`:

```
What cluster threshold should trigger a proposal write to suggestions.md?
  Default: 3 (one is anecdote, two could be coincidence, three is a pattern).
  Tune up (not down) for skills with very high run cadence — lower thresholds
  produce noisy suggestions.md files that erode trust in proposals.
```

Carry forward:
- `observer_enabled: <true|false>`
- `cluster_threshold: <int>` (only meaningful when `observer_enabled` is true)

If `observer_enabled` is `true` AND `suggestion_capture_enabled` is `false`, print this warning before proceeding to Step 6:

```
⚠ Observer enabled without suggestion-capture. The convergence rule (observer
  observation + matching user-typed `improvement_suggestions[]` entry → trip
  regardless of cluster threshold) cannot fire for this skill. Observer will
  still work via cross-run clustering at the threshold you chose, but you'll
  miss the strongest signal class. Recommend revisiting Step 5.5 to enable
  suggestion-capture as well. Continue anyway? [y/n]
```

Wait for explicit `y` to continue, or let the user revisit Step 5.5.

### Step 6 — Interview: optional domain FAIL rules

```
Do you have any KNOWN failure modes from prior pain that should be seeded? (y/n)
  These are domain-specific FAIL tags beyond the three universal seeds
  (audit-paraphrased-user-input, audit-no-explicit-approval-wait, tool-claim-without-call).

  If unsure, answer `n`. The pattern is intentionally designed to LET tags accumulate
  from real runs — pre-inventing tags you can't currently detect mechanically tends to drift.
```

If `y`, loop:

```
--- FAIL rule ---
1. Tag? (lowercase-hyphenated, format `<phase>-<failure-mode-slug>`, e.g. `7.5-implicit-skip-no-justification`)
2. Phase? (which domain phase does this apply to)
3. Description? (one sentence — what failure does this catch)
4. Detection condition? (mechanical — checkable without judgment, e.g. "surfaced > resolved-with-explicit-choice")
5. Tier? (load-bearing=1 / procedural=2 / cosmetic=5)
6. Remediation hint? (what SKILL.md edit should auto-apply when this trips — be specific: file + line + before/after)

Add another? (y/n)
```

### Step 6.5 — Discover composable skills (suggest-only)

The interview now has enough signal — phases, phase bodies, principle — to mechanically suggest which existing skills the new skill could compose at runtime. This step is **suggest-only**: the user accepts, edits, or skips each match; nothing is auto-wired.

**Skip conditions** (print one line and continue to Step 7):
- User types `skip composition discovery` at any prompt in this step.
- All three scopes turn up zero skills (very early bootstrap of a plugin).
- No candidate clears medium confidence across any phase.

#### 6.5.1 — Scan three scopes

`Glob` `<root>/*/SKILL.md` in each scope, then `Read` the frontmatter (`name` + `description`) of each match.

| Scope | Root |
|---|---|
| Plugin    | parent of this meta-skill's own directory (its peer `skills/` directory) |
| User      | `~/.claude/skills/` (resolve `~` to actual home dir; skip silently if missing) |
| Project   | parent of `<target_dir>` when `location ≠ plugin`; same as plugin scope otherwise |

De-duplicate by skill `name` across scopes (plugin > user > project precedence). Exclude the not-yet-existing new skill being generated.

#### 6.5.2 — Match phases + principle against candidate descriptions

For each (phase, candidate) pair:
1. Tokenize `<phase name> + <phase body>` (lowercase; drop stopwords: `the`, `is`, `a`, `of`, `to`, `and`, `or`, `for`, `in`, `on`, `with`, `this`, `that`, `it`, `as`, `at`, `by`, `from`, `be`).
2. Tokenize the candidate's frontmatter `description` the same way.
3. Count distinct content-bearing token overlaps.

Confidence tiers:
- **high**: ≥3 token matches AND the candidate description names the phase's intent verb (`sweep`, `diagnose`, `impact`, `refactor`, `commit`, `plan`, `review`, `audit`, etc.).
- **medium**: 1–2 token matches, OR intent-verb match without 3 tokens.
- **low**: <1 content-bearing match. Drop — do not show.

Also match the **load-bearing principle** globally: candidates whose description aligns with the principle (e.g., principle "no new bugs introduced" → `quality-bug-sweep`, `code-diagnosis`) attach to the phases where their work would land, not as a separate global block.

#### 6.5.3 — Present per-phase suggestions

Display one block per phase with ≥1 medium-or-higher candidate. Phases with zero matches above low tier are skipped silently:

```
Phase i — <phase name>
  [high]   <namespace>:<skill-name> — <trigger drawn from candidate description>
  [medium] <namespace>:<skill-name> — <trigger>
```

Namespace prefix: `claude-library:` for plugin scope, no prefix for project-local, the user's own convention (ask once at scope-scan time) for user-global.

#### 6.5.4 — Accept / edit / skip per phase

For each phase block, ask:

```
Phase i — accept which suggestions?
  - accept all high-tier
  - accept specific (give the names)
  - edit (provide your own trigger text per accepted skill)
  - skip (no compositions for this phase)
```

Capture user-accepted entries into a structure carried forward to Steps 7, 8a, and 9:

```
composed_skills = [
  {"skill": "claude-library:safe-changes-impact-check", "phase": "3", "trigger": "Change touches orchestrator/MCP/migrations/auth/registries"},
  {"skill": "claude-library:code-diagnosis", "phase": "7", "trigger": "Always, path-scoped on changed files"}
]
```

Empty `composed_skills` is valid — the new skill simply ships with no composition table.

#### 6.5.5 — Explicit exclusions (optional)

After per-phase acceptance, ask once more:

```
Any candidates to explicitly call out as NOT composed (with reason)?
  Format: <skill-name> — <one-line reason>
  Example: planning-impl-plan — the interview IS the plan; nesting would loop
  Type `done` when finished.
```

Capture into `not_composed = [{"skill": "...", "reason": "..."}]`. Empty is valid.

### Step 7 — Show generation plan and wait for `generate` token

Before writing any files, present the full plan:

```
=== Generation plan ===

Skill folder:    <target_dir>/<name>/
                 (resolved from Step 2 location choice: <plugin|project|user|custom>)
Files to create:
  - <target_dir>/<name>/SKILL.md          (assembled from .tpl + audit-phase.md + ledger-phase.md [+ observer-phase.md])
  - <target_dir>/<name>/run_history.json  (bootstrap from run_history_schema_v1.md "Initial state")
  <only if observer_enabled is true:>
  - <target_dir>/<name>/observations.json (bootstrap from observations_schema_v1.md "Initial state")
  - <target_dir>/<name>/suggestions.md    (header only, no proposals at bootstrap)

Frontmatter:
  name: <name>
  description: <description> <keywords>

Phase structure:
  <only if freshness_enabled is true:>
  Phase 0   — Freshness check (non-blocking, runs/days thresholds=<runs>/<days>)
  Phase 1 — <name>  (<tier>)
  Phase 2 — <name>  (<tier>)
  ...
  Phase <N-1> — Pre-action self-audit (CHECKPOINT, blocking)
    Approval token: `<token>`
    FAIL detection rules: 3 universal + <count> domain
    Suggestion review (final-call): <enabled|disabled>
  Phase <N> — Update the run-history ledger
    Writes to: <target_dir>/<name>/run_history.json
    Persists improvement_suggestions[]: <enabled|disabled>
  <only if observer_enabled is true:>
  Phase <N+1> — Post-ledger observer (suggestion-only)
    Writes to: <target_dir>/<name>/observations.json + suggestions.md
    Cluster threshold: <cluster_threshold>
    Convergence rule active: <true if suggestion_capture_enabled else false>

Freshness check (Phase 0): <enabled|disabled>
  When enabled, the SKILL.md gets a non-blocking Phase 0 that nudges the user
  to revalidate (research + overlap check) when the skill has been used >= 10
  times AND >= 21 days have passed since last validation. run_history.json
  gets a `validation_freshness` block initialized to defaults.

Efficiency instrumentation: always-on (no toggle)
  Every generated skill emits: per-phase `phase_durations`, total
  `started_at`/`ended_at`/`duration_seconds`, mechanically-derived
  `quality_derived`, and `sentiment` on every captured suggestion. These feed
  the observer's trade-off detector (when observer is enabled) and remain
  harmless when no observer consumes them.

Mid-run suggestion capture: <enabled|disabled>
  When enabled, the SKILL.md gets a "Mid-run suggestion capture" block after the
  Inputs section, and run_history.json includes an improvement_suggestions[] array.

Observer phase: <enabled|disabled>
  When enabled, a post-ledger Phase N+1 records qualitative signals and surfaces
  clustered proposals to suggestions.md. Suggestion-only; never auto-edits SKILL.md.
  Bootstraps observations.json (empty per schema v1) and suggestions.md (header only).

Audit row shapes (one per domain phase, applied in audit phase):
  Phase 1: <evidence shape — verbatim quote slot if input-consuming>
  Phase 2: ...

run_history.json seed counters:
  - audit-paraphrased-user-input (universal, threshold=1, load-bearing)
  - audit-no-explicit-approval-wait (universal, threshold=2, procedural)
  - tool-claim-without-call (universal, threshold=1, load-bearing)
  <+ any domain rules from Step 6>

Plugin skills composed (from Step 6.5):
  <one row per composed_skills entry: "Phase <i>: <skill> (trigger: <trigger>)">
  <print "(none — populate by hand later)" when composed_skills is empty>

Plugin skills explicitly NOT composed (from Step 6.5):
  <one row per not_composed entry: "<skill> — <reason>">
  <omit this entire block when not_composed is empty>

Type `generate` to proceed. Anything else aborts.
```

**Wait for the explicit literal `generate`** (case-insensitive). Silence, "ok", "yes", "proceed" do NOT advance. If the user types anything else, ask whether they want to revise the plan or abort.

### Step 8 — Generate the skill files

When `generate` is received:

#### 8a — Build SKILL.md content

1. **Start from `SKILL.md.tpl`** and apply substitutions:
   - `{{SKILL_NAME}}` → from Step 2
   - `{{SKILL_TITLE}}` → human-readable title (Title Case of the skill name, e.g. `log-decision` → `Log Decision`)
   - `{{ONE_LINE_DESCRIPTION}}` → from Step 2
   - `{{TRIGGER_KEYWORDS}}` → from Step 2 (comma-separated list)
   - `{{ONE_PARAGRAPH_PURPOSE}}` → expand the one-line description into 2–3 sentences using the load-bearing principle as context
   - `{{LOAD_BEARING_PRINCIPLE}}` → from Step 2
   - `{{INPUT_ROWS}}` → table rows from Step 4
   - `{{INPUT_FALLBACK_BEHAVIOR}}` → from Step 4
   - `{{N_MINUS_1}}` → audit phase number (= total domain phases + 1)
   - `{{N}}` → ledger phase number (= total domain phases + 2)

1.4. **Inline the Phase 0 freshness check** if `freshness_enabled` is true (Step 5.4). Replace the `## Phase 0 — Freshness check (non-blocking)` placeholder block in the template (the one with the "Insert here" comment) with the body of `library/templates/self-learning-skill/freshness-phase.md` — the section that starts with `## Phase 0 — Freshness check (non-blocking)` and ends just before the next `---` horizontal rule (do NOT include the "Authoring notes" tail). Apply substitutions in the inlined text:
   - `{{SKILL_NAME}}` → from Step 2
   - `{{SKILL_PATH}}` → `<target_dir>/<name>` resolved to a relative path from the project root

   If `freshness_enabled` is false, remove the entire Phase 0 placeholder block (heading + "Insert here" callout) so Phase 1 becomes the first phase. Also remove the surrounding `<!-- PHASE 0 ... -->` comment block above the placeholder.

1.5. **Inline the Mid-run suggestion capture block** if `suggestion_capture_enabled` is true (Step 5.5). Insert the body of `library/templates/self-learning-skill/suggestion-capture.md` — the section that starts with `## Mid-run suggestion capture` and ends just before the next `---` horizontal rule — between the `## Inputs` section and the first domain phase (i.e., right before the `---` divider that precedes Phase 1). Apply substitutions:
   - `{{SKILL_NAME}}` → from Step 2
   - `{{SKILL_PATH}}` → `<target_dir>/<name>` resolved to a relative path from the project root

   Skip this step entirely if `suggestion_capture_enabled` is false.

2. **Replace the domain phases section.** The template has placeholder blocks for `Phase 1` and `Phase 2` plus a comment "...add as many domain phases as needed...". Replace this entire section with one block per domain phase from Step 5:

   ```
   ## Phase i — <name>

   <body — from Step 5 question 2, formatted as numbered steps if appropriate>
   ```

3. **Inline the audit body.** Find the `## Phase {{N_MINUS_1}} — Pre-action self-audit` placeholder block (with the "Insert here" comment). Replace it with the body of `audit-phase.md` — specifically, the section that starts with `## Phase {{N}} — Pre-action self-audit (CHECKPOINT, blocking)` and ends just before the next `---` horizontal rule. Apply substitutions in the inlined text:
   - `{{N}}` → audit phase number
   - `{{TERMINAL_ACTION}}` → from Step 3
   - `{{TERMINAL_ACTION_CAPITALIZED}}` → capitalized form
   - `{{APPROVAL_TOKEN}}` → from Step 3
   - `{{PHASE_AUDIT_ROWS}}` → one row per domain phase. Format each as:
     ```
     - Phase i [pass] | <evidence shape>
     ```
     For input-consuming phases (Step 5 question 4 = y), include a verbatim-quote slot:
     ```
     - Phase i [pass] | <description>; user input verbatim: "<literal quote>"
     ```
   - `{{DOMAIN_FAIL_RULES}}` → from Step 6, formatted as bullet list. If Step 6 was skipped, write: `(none yet — accumulating from real runs)`.

4. **Inline the ledger body.** Find the `## Phase {{N}} — Update the run-history ledger` placeholder block. Replace with the body of `ledger-phase.md` — the section that starts with `## Phase {{N}} — Update the run-history ledger` and ends just before the next `---` horizontal rule. Apply substitutions:
   - `{{N}}` → ledger phase number
   - `{{SKILL_PATH}}` → `skills/<name>`
   - `{{TERMINAL_ACTION}}` → from Step 3

5. **Strip template scaffolding comments.** Remove all `<!-- ... -->` HTML comment blocks that exist only to explain the template structure (the long blocks under "DOMAIN PHASES" and "STANDARDIZED LAST TWO PHASES"). The generated SKILL.md is the artifact, not the template — its readers don't need template guidance.

6. **Fill the trailing sections from collected data**:
   - `Plugin skills composed by this skill` — render one table row per `composed_skills` entry (Step 6.5.4): columns `Skill | Phase | Trigger`. When `composed_skills` is empty, write the table header plus a single placeholder row "*(none — populate by hand if/when you discover compositions on first runs)*" so the section's shape is preserved.
   - `Plugin skills NOT composed` — render one bullet per `not_composed` entry (Step 6.5.5): `- <skill> — <reason>`. Omit this section entirely when `not_composed` is empty.
   - `Edge cases`, `Out of scope`, `Usage` — populate with sensible defaults if the user didn't provide them. For first-time skills, populate `Usage` with at least one `/<skill-name> <example>` invocation drawn from the inputs.

7. **Inline the observer pattern (TWO sections, both required)** if `observer_enabled` is true (Step 5.6). The observer pattern requires inlining two distinct sections from `library/templates/self-learning-skill/observer-phase.md` — see its "Two sections to inline" notice. Inlining only one of the two is a structural error.

   **7a. Inline the `Observer file boundary` callout near the top of the SKILL.md.** Copy the markdown block under the template's "Companion: Observer file boundary callout" section (the fenced ` ```markdown ... ``` ` block — copy its contents only, not the fence). Insert it as a new top-level section between the Mid-run suggestion capture block (when `suggestion_capture_enabled` is true) or the `## Inputs` section (when capture is disabled) AND the first domain phase. Apply substitutions:
      - `{{N}}` → observer phase number (= ledger phase number + 1; one higher than the ledger)

      This callout is what prevents the leak where an LLM running the skill reads `observations.json` during a domain phase and lets it bias the framing.

   **7b. Inline the observer Phase body as the LAST phase.** Insert the section that starts with `## Phase {{N}} — Post-ledger observer (suggestion-only)` and ends just before the next `---` horizontal rule (i.e., before "## Authoring notes") — as a new top-level section AFTER the inlined ledger phase, BEFORE the trailing `Edge cases` section. Apply substitutions in the inlined text:
      - `{{N}}` → observer phase number (= ledger phase number + 1; same as 7a)
      - `{{SKILL_PATH}}` → `<target_dir>/<name>` resolved to a relative path from the project root
      - `{{CLUSTER_THRESHOLD}}` → from Step 5.6 (default 3)

   **7c. Update the trailing `## Self-learning checklist (before shipping)` section** to include the observer-specific checks:
   - [ ] `observations.json` exists at the skill's root, initialized with the schema v1 "Initial state" structure (empty `observations[]` and `review_log[]`).
   - [ ] `suggestions.md` exists at the skill's root, header only, no proposals at bootstrap.
   - [ ] Observer phase (Phase N+1) is the LAST phase. No phase fires after it.
   - [ ] **`Observer file boundary` callout is present near the top of the SKILL.md** (between Inputs/capture block and Phase 1). Without this callout, the prohibition against domain phases reading observer files is not enforced.
   - [ ] If `suggestion_capture_enabled` is also true, the convergence rule note in the observer phase body is intact (does NOT say "field is missing").

   Skip this entire sub-step (7a, 7b, and 7c) if `observer_enabled` is false.

#### 8b — Build run_history.json

1. Use the **"Initial state"** JSON snippet from `run_history_schema_v1.md` verbatim as the base.
2. **Apply suggestion-capture toggle** (from Step 5.5):
   - If `suggestion_capture_enabled` is `true`: keep the `"improvement_suggestions": []` line as it appears in the canonical Initial state.
   - If `suggestion_capture_enabled` is `false`: drop the `"improvement_suggestions": []` line entirely AND remove the trailing comma from the previous line so the JSON stays valid.

2a. **Apply freshness toggle** (from Step 5.4):
   - If `freshness_enabled` is `true`: keep the `"validation_freshness": { ... }` block. Substitute `created_at` and `last_validated_at` with the current ISO 8601 UTC timestamp. Substitute `thresholds.runs` with `freshness_threshold_runs` (default 10) and `thresholds.days` with `freshness_threshold_days` (default 21).
   - If `freshness_enabled` is `false`: drop the `"validation_freshness": { ... }` block entirely AND remove the trailing comma from the previous line so the JSON stays valid.
3. If Step 6 added domain FAIL rules, append each to the `fail_counters` object with:
   ```json
   "<tag>": {
     "count": 0,
     "threshold": <from-tier>,
     "phase": "<from-step-6>",
     "description": "<from-step-6>",
     "occurrences": [],
     "remediation_hint": "<from-step-6>",
     "applied_at": null
   }
   ```
4. Validate that the resulting JSON parses (mentally walk it for matching braces/quotes).

#### 8b.5 — Build observations.json and suggestions.md (only when `observer_enabled` is true)

Skip this entire sub-step if `observer_enabled` is false.

1. **`observations.json`**: use the **"Initial state"** JSON snippet from `observations_schema_v1.md` verbatim (top-level: `version: 1`, empty `observations[]`, empty `review_log[]`). Greenfield skills do NOT seed observations — that's only for retrofitted skills with prior `runs[]` history.

2. **`suggestions.md`**: write a header-only file with this content (substitute `<skill-name>` and `<cluster-threshold>`):

   ```markdown
   # `<skill-name>` — Observer suggestions

   This file is written by the **observer phase** (the last phase of this skill) when cross-run clustering trips. Each section below is an unreviewed proposal generated from ≥<cluster-threshold> observations sharing a theme (or 1 observation + matching `improvement_suggestions[]` entry — the convergence rule).

   The user reviews each section and flips `Status: unreviewed` to either `applied` or `dismissed`. When applied, the user fills `Applied at:` (ISO 8601) and `Applied via:` (one-line description of the SKILL.md edit), then mirrors the same values into the matching `review_log[]` entry of `observations.json`.

   The observer never edits this file's existing sections — it only appends new proposals. Existing sections are owned by the human reviewer.

   ---

   <!--
   Observer-written proposals appear below this line.
   Each proposal follows the format documented in the SKILL.md observer phase, step 5.
   -->
   ```

3. Validate the JSON (`observations.json`) parses; the markdown (`suggestions.md`) is freeform and does not need validation beyond the heading being present.

#### 8c — Write the files

Mandatory:
```
Write <target_dir>/<name>/SKILL.md
Write <target_dir>/<name>/run_history.json
```

Conditional (only when `observer_enabled` is true):
```
Write <target_dir>/<name>/observations.json
Write <target_dir>/<name>/suggestions.md
```

(`<target_dir>` resolved in Step 2: plugin → `<CWD>/skills`, project → `<CWD>/.claude/skills`, user → `~/.claude/skills`, custom → user-provided.)

Show the user the absolute file paths and a short preview of each (frontmatter + first 30 lines for SKILL.md; full content for run_history.json; full content for observations.json and suggestions.md when present).

### Step 9 — Validate the generated files

Run these mechanical checks. Fail loudly on any miss — DO NOT silently proceed.

1. **No orphan placeholders**: `Grep` the generated SKILL.md for `{{` — must return zero matches. If any placeholder remains, surface its location and offer to fix.
2. **JSON is valid v1**: parse `run_history.json` (mentally or via `python -c "import json; ..."`). Confirm `version == 1`, `fail_counters` is an object, `runs` and `friction_log` are arrays.
3. **Audit phase has correct row count**: count `- Phase` lines in the audit block — must equal the number of domain phases.
4. **Approval gate uses the literal token**: confirm the audit phase contains the exact approval token from Step 3 wrapped in backticks.
5. **Last phase is correct**: if `observer_enabled` is false, the ledger is the last phase — no `## Phase` heading appears after the ledger block. If `observer_enabled` is true, the observer is the last phase — no `## Phase` heading appears after the observer block.
6. **Phase numbering is contiguous**: 1, 2, ..., N with no gaps. Sub-phases (1.5, 5.5) are allowed but flag for review.
7. **Suggestion-capture consistency**: confirm SKILL.md and run_history.json agree.
   - If `suggestion_capture_enabled` is true: SKILL.md MUST contain `## Mid-run suggestion capture` heading AND `run_history.json` MUST contain `"improvement_suggestions": []`.
   - If false: SKILL.md MUST NOT contain that heading AND `run_history.json` MUST NOT contain that key.
   Mismatch → fail loudly and report which side disagrees.

8. **Observer-phase consistency**: confirm SKILL.md and the observer files agree.
   - If `observer_enabled` is true: SKILL.md MUST contain a `## Phase <N+1> — Post-ledger observer` heading (where `<N+1>` is the ledger phase number + 1) AND a separate `## Observer file boundary` callout placed near the top (before the first `## Phase` heading) AND both `observations.json` and `suggestions.md` MUST exist at the skill root. `observations.json` MUST be valid v1 (`version: 1`, empty `observations[]`, empty `review_log[]`). `suggestions.md` MUST contain the `# <skill-name> — Observer suggestions` heading. The boundary callout MUST appear textually before the first `## Phase` heading — if it appears after, fail (it would arrive too late to gate Claude's read).
   - If false: SKILL.md MUST NOT contain a Phase N+1 observer heading, MUST NOT contain `## Observer file boundary`, AND neither `observations.json` nor `suggestions.md` should exist.
   Mismatch → fail loudly and report which side disagrees.

9. **Observer ↔ suggestion-capture coherence**: when `observer_enabled` is true, scan the observer phase body for the convergence-rule note. Confirm it matches the suggestion-capture toggle:
   - If `suggestion_capture_enabled` is true: the note must NOT say "field is missing" / "does not apply".
   - If false: the note SHOULD acknowledge that the convergence rule cannot fire for this skill (it's allowed but should be marked).
   Mismatch is a soft warning, not a hard fail.

10a. **Freshness-phase consistency**: confirm SKILL.md and run_history.json agree on the freshness toggle.
   - If `freshness_enabled` is true: SKILL.md MUST contain a `## Phase 0 — Freshness check` heading placed BEFORE the first domain phase, AND `run_history.json` MUST contain a `validation_freshness` block with `runs_since_validation: 0`, the correct threshold values, and ISO 8601 timestamps for `created_at`/`last_validated_at`. The ledger phase body MUST contain the increment step (search for `runs_since_validation` in the ledger section).
   - If false: SKILL.md MUST NOT contain a Phase 0 freshness heading AND `run_history.json` MUST NOT contain `validation_freshness`.
   Mismatch → fail loudly and report which side disagrees.

10b. **Efficiency instrumentation present**: confirm SKILL.md and templates wired the always-on instrumentation correctly. This check runs unconditionally — there is no toggle.
   - The first phase (Phase 0 if freshness is enabled, else Phase 1) MUST contain a step that stamps `started_at` to the run-start timestamp before doing any work.
   - Every domain phase (1..N-2) MUST contain a step that stamps its own `phase_durations[<id>] = seconds_elapsed` as it exits. Grep the SKILL.md for `phase_durations` — count must be >= number of domain phases.
   - The ledger phase MUST emit `started_at`, `ended_at`, `duration_seconds`, `phase_durations`, and `quality_derived` in the `runs[]` entry (search for all five field names in the ledger section).
   - When suggestion-capture is enabled, the capture body MUST include the sentiment classification step (search for `sentiment:` field in the capture block).
   Mismatch → fail loudly. Pre-instrumentation runs in the JSON are fine (forward-only), but the SKILL.md itself MUST be fully instrumented.

10. **Composition table well-formed**: when `composed_skills` (Step 6.5.4) is non-empty, the generated SKILL.md MUST contain a `Plugin skills composed by this skill` table with exactly one row per `composed_skills` entry. Each row must have a non-empty Skill, Phase, and Trigger cell. When `not_composed` (Step 6.5.5) is non-empty, the generated SKILL.md MUST contain a `Plugin skills NOT composed` bullet list with exactly one bullet per entry. Empty `composed_skills` and `not_composed` are valid: the composition table is rendered with the "(none — populate by hand if/when you discover compositions on first runs)" placeholder row; the not-composed block is omitted entirely. Mismatch (declared in interview but missing in file, or vice versa) → fail loudly and report which side disagrees.

If all checks (1–7 always; 8–9 when observer_enabled; 10a always (toggle-symmetric); 10b always (efficiency instrumentation); 10 when `composed_skills` or `not_composed` is non-empty) pass, print:

```
✓ Generation validated. Skill ready to invoke.
```

### Step 10 — Closure: smoke-test guidance

Tell the user how to verify the skill works end-to-end:

```
Smoke test:
1. Invoke the skill: /<skill-name> <example-input>
2. Watch each domain phase report what it did, with evidence.
3. The audit phase should:
   - List one row per domain phase, with verbatim quotes for any user input.
   - Block until you type the literal `<approval-token>` token. Try saying "ok" first — it must NOT advance.
4. After the terminal action fires, the ledger should write a new entry under
   skills/<skill-name>/run_history.json → runs[], with outcome "closed" and phases_failed: [].

If the audit paraphrases your input instead of quoting it verbatim, that's an
`audit-paraphrased-user-input` failure — counter increments, threshold=1 → next run
auto-edits the SKILL.md per the stored remediation hint.

Want to invoke the skill now? Tell me your example input and I'll walk through the smoke test.
```

---

## Convert Mode — Promote an existing skill to self-learning

This mode runs as a **separate dispatch** from greenfield generation. It takes the path of an existing (non-self-learning) skill, evaluates whether retrofitting the audit + ledger pattern makes sense, and applies the conversion in place.

**Invoke**: `/meta-self-learning-skill-gen convert <path-to-skill-dir-or-SKILL.md>`

The greenfield interview (Steps 2–10) is replaced by an eligibility scan + a much shorter targeted interview, since most of the skill's structure (phases, inputs, principle) is extracted from the existing SKILL.md. The user only confirms proposals and fills the gaps the audit + ledger pattern requires (terminal action, approval token, per-phase tier).

### Step C1 — Locate, load, and refuse no-ops

1. Resolve the input path:
   - Directory → expect `<path>/SKILL.md`.
   - File → treat as the SKILL.md directly.
   - Neither resolves → abort with the path tried.
2. Read the SKILL.md fully.
3. Refuse to convert if the skill is **already self-learning**. Detect via any of:
   - Frontmatter `metadata.pattern: self-learning`.
   - Sibling `run_history.json` exists.
   - A phase titled "Pre-action self-audit" or "Update the run-history ledger" already present.
   On hit, stop with: "This skill is already self-learning. Edit its SKILL.md directly — improve mode is out of scope at v1."

### Step C2 — Eligibility evaluation

Score the skill against six criteria. **Convertible** if 4+ pass; **borderline** if 3; **not a fit** if ≤2.

| # | Criterion | How to check |
|---|---|---|
| 1 | Has a clear terminal action | Body mentions `git commit`, `gh`, `deploy`, `Write` of a final artifact, API call, etc. |
| 2 | Has identifiable phases or steps | Multiple `## Phase`, `## Step`, or numbered headings present |
| 3 | Has a load-bearing rule | Body uses "must", "never", "always", "verbatim", "do not paraphrase" — something to anchor the principle on |
| 4 | Consumes user input | Skill takes free-text, IDs, paths, or structured input from the user |
| 5 | Deterministic enough | Not pure interview/Q&A or open-ended chat (those don't benefit from audit) |
| 6 | Stable surface | Not marked draft/experimental/v0 and not actively being rewritten |

Print the scorecard with verdict + a one-sentence justification per criterion. If **not a fit**, stop and explain the strongest blocker — do NOT proceed to a useless conversion. If **borderline**, surface the failing criteria and ask the user whether to continue anyway.

### Step C3 — Extract candidate values from the existing SKILL.md

Pull as much as possible mechanically before asking the user anything:

- `SKILL_NAME` → from frontmatter `name`.
- `ONE_LINE_DESCRIPTION` → from frontmatter `description` (first sentence).
- `TRIGGER_KEYWORDS` → from frontmatter description tail or any `Keywords:` line.
- `LOAD_BEARING_PRINCIPLE` → propose from the strongest "must"/"never" sentence in the body. Mark as **proposed**.
- Domain phases → enumerate every existing `## Phase N — Name` (or `## Step N — Name`) heading; preserve numbering and bodies as-is. Note the heading prefix used (`Phase` vs `Step`) — convert mode keeps it.
- Inputs → extract from any existing `## Inputs` table or input description.
- `TERMINAL_ACTION` → infer from the last domain phase's verbs (commit / deploy / write / api-call). Mark as **proposed**.
- `APPROVAL_TOKEN` → if a literal token is already enforced in the body (e.g. `audit approved`, `confirmed`, `proceed`), use it; otherwise mark **needs-user-input**.

Print the extracted summary. Only the **proposed** and **needs-user-input** items will be re-asked in C4.

### Step C4 — Targeted interview (only the gaps)

Ask only what extraction couldn't unambiguously cover:

1. **Confirm the load-bearing principle** — accept, edit, or replace the proposed line.
2. **Confirm the terminal action and approval token** — accept proposals or override. Same validation as greenfield Step 3 (token = 1–4 words, lowercase, no punctuation).
3. **Tier each existing domain phase** (load-bearing=1 / procedural=2 / cosmetic=5). This is the one place convert mode still requires real judgment — existing SKILL.md doesn't carry tier metadata.
4. **For each input-consuming phase, confirm verbatim-quote enforcement.** If a phase currently summarizes user input rather than quoting it, the audit row will fail `audit-paraphrased-user-input` on first run. Flag this so the user understands the audit is INTENTIONALLY going to bite — it's the system working.
5. **Optional domain FAIL rules** — same as greenfield Step 6. Recommended default: skip and let the ledger accumulate from real runs.
6. **Heading-prefix sanity check** — if existing skill uses `## Step` instead of `## Phase`, ask: keep `Step` (default — preserves byte-identical existing content) or normalize to `Phase`.
6a. **Phase 0 freshness toggle** — same as greenfield Step 5.4. Default y. Carry `freshness_enabled` and the two threshold values forward. For convert mode, the freshness phase is inserted as a new Phase 0 ahead of the existing Phase 1; no existing phase numbering changes.

7. **Mid-run suggestion capture toggle** — same as greenfield Step 5.5. Default y. Carry `suggestion_capture_enabled` forward.
8. **Observer phase toggle** — same as greenfield Step 5.6. Default n. Carry `observer_enabled` and `cluster_threshold` forward. Apply the same warning if observer is enabled but suggestion-capture is disabled.
9. **Retrospective seeding for observer** — only ask when `observer_enabled` is true AND the existing skill has prior runs in `run_history.json`. Offer: "Pre-populate `observations.json` with seed observations derived from a paper retrospective on the existing `runs[]`? [y/n, default y]". When `y`, the conversion plan in C5 will include a retrospective seeding step that creates back-dated observation entries; when `n`, the file is initialized empty.

### Step C4.5 — Discover composable skills (convert mode, additive only)

Convert mode reuses greenfield Step 6.5's scanning and matching logic with one difference: the existing skill may already have a `Plugin skills composed by this skill` table. The step is **additive only** — it never removes or rewrites existing rows, only proposes new ones.

1. **Parse existing composition** from the loaded SKILL.md: read the `Plugin skills composed by this skill` table (if present) and the `Plugin skills NOT composed` block (if present). Capture as `existing_composed_skills` and `existing_not_composed`, preserving the original row shape verbatim.
2. **Run the same scan as Steps 6.5.1–6.5.2** against the existing skill's domain phases and load-bearing principle.
3. **Filter candidates**: drop any candidate whose skill name already appears in `existing_composed_skills` OR `existing_not_composed` — the author already decided about it. Surface only genuinely new candidates.
4. **Present per-phase suggestions** as in Step 6.5.3, with a header noting "additive only — existing rows preserved".
5. **Accept / edit / skip per phase**, capturing into `new_composed_skills`. These will be appended to the existing table in C6, not replace it.
6. **Optional exclusions** — same prompt as Step 6.5.5, captured into `new_not_composed` and appended to the existing not-composed block.

Skip the entire step (print one line, continue to C5) when no new candidates clear medium confidence.

### Step C5 — Show conversion plan and wait for `convert` token

Present the diff plan before writing anything. Be explicit about what is preserved versus what is added:

```
=== Conversion plan for skills/<name>/ ===

Frontmatter changes:
  + metadata.pattern: self-learning
  + metadata.schema-version: 1
  (name, description, and any other existing fields unchanged)

Phase additions (existing <N> domain phases preserved BYTE-IDENTICAL):
  <only if freshness_enabled is true:>
  + Phase 0   — Freshness check (non-blocking, inserted BEFORE existing Phase 1)
      Thresholds: runs=<runs>, days=<days>
  + Phase <N+1> — Pre-action self-audit (CHECKPOINT, blocking)
      Approval token: `<token>`
      Audit rows: <N> (one per existing domain phase)
      Verbatim-quote rows: <count of input-consuming phases>
      FAIL detection rules: 3 universal + <count> domain
      Suggestion review (final-call): <enabled if suggestion_capture_enabled else disabled>
  + Phase <N+2> — Update the run-history ledger
      Writes to: skills/<name>/run_history.json
      Persists improvement_suggestions[]: <enabled|disabled>
  <only if observer_enabled is true:>
  + Phase <N+3> — Post-ledger observer (suggestion-only)
      Writes to: skills/<name>/observations.json + suggestions.md
      Cluster threshold: <cluster_threshold>
      Convergence rule active: <true if suggestion_capture_enabled else false>
      Retrospective seed: <enabled|disabled> (from C4 step 9)

Freshness check (Phase 0): <enabled|disabled>
  When enabled, the SKILL.md gets a non-blocking Phase 0 inserted BEFORE the
  existing Phase 1 (existing phases keep their numbering). run_history.json
  gets a `validation_freshness` block initialized to defaults.

Efficiency instrumentation: always-on (no toggle)
  Convert mode also adds timing + quality_derived emission to the existing
  ledger phase and sentiment auto-classification to the suggestion-capture
  block. Existing `runs[]` entries are NOT backfilled with timing data —
  forward-only — and the observer skips them from efficiency comparison.

Mid-run suggestion capture: <enabled|disabled>
  When enabled, the SKILL.md gets a "Mid-run suggestion capture" block inserted
  between the existing Inputs section and the first existing domain phase, and
  run_history.json includes an improvement_suggestions[] array.

Observer phase: <enabled|disabled>
  When enabled, a post-ledger Phase <N+3> records qualitative signals and surfaces
  clustered proposals to suggestions.md. Bootstraps observations.json (with seed
  observations from retrospective on existing runs[] when retrospective seeding
  is enabled, otherwise empty) and suggestions.md (header + bootstrap state table).

Files to create:
  + skills/<name>/run_history.json (bootstrap from schema v1 "Initial state")
  <only if observer_enabled is true:>
  + skills/<name>/observations.json (seeded if retrospective seeding=enabled, else empty)
  + skills/<name>/suggestions.md (header + bootstrap state table)

Files to modify:
  ~ skills/<name>/SKILL.md
      - Add metadata block to frontmatter
      - Insert "Mid-run suggestion capture" block (if suggestion_capture_enabled)
      - Append audit + ledger phases after the current last phase
      - Append observer phase after the ledger (if observer_enabled)
      - Append composition additions (from C4.5): new rows to
        `Plugin skills composed by this skill`; new bullets to
        `Plugin skills NOT composed`. Additive only — existing preserved.
      - Append "Self-learning checklist" section if missing

Plugin skills composed — additions only (from Step C4.5):
  <one row per new_composed_skills entry: "Phase <i>: <skill> (trigger: <trigger>)">
  <omit this block when new_composed_skills is empty>

Plugin skills NOT composed — additions only (from Step C4.5):
  <one bullet per new_not_composed entry: "- <skill> — <reason>">
  <omit this block when new_not_composed is empty>

Phases NOT changed:
  - Existing phase bodies preserved verbatim. No renaming, no renumbering.
  - The current last phase that contained the terminal action is now gated by
    the audit phase's `<token>` approval — its body fires only after approval.

Type `convert` to apply. Anything else aborts.
```

**Wait for the literal `convert` token** (case-insensitive). Same gate semantics as greenfield's `generate`: silence, "ok", "yes", "proceed" do NOT advance.

### Step C6 — Apply the conversion

When `convert` is received:

1. **Edit the SKILL.md frontmatter** with `Edit` to add the `metadata` block. Preserve every other field exactly.
1a. **Insert the Phase 0 freshness check** if `freshness_enabled` is true. Use `Edit` to insert the body of `library/templates/self-learning-skill/freshness-phase.md` (the section starting with `## Phase 0 — Freshness check (non-blocking)` and ending just before the next `---`) ABOVE the existing first domain phase. Apply `{{SKILL_NAME}}` and `{{SKILL_PATH}}` substitutions. Existing phase headings are NOT renumbered — the freshness phase takes the previously-unused Phase 0 slot. Skip if disabled.

2. **Insert the Mid-run suggestion capture block** if `suggestion_capture_enabled` is true. Use `Edit` to insert the body of `library/templates/self-learning-skill/suggestion-capture.md` (the `## Mid-run suggestion capture` section, before the next `---`) between the existing `## Inputs` section and the first existing domain phase. Apply `{{SKILL_NAME}}` and `{{SKILL_PATH}}` substitutions. Skip if disabled.
3. **Append the audit phase** after the last existing domain phase. Use the body of `library/templates/self-learning-skill/audit-phase.md` with substitutions from C3/C4. Audit row count must equal the number of existing domain phases; rows for input-consuming phases include the verbatim-quote slot. Use the chosen heading prefix (`Phase` or `Step`) consistently. Include the suggestion-review final-call sub-step when `suggestion_capture_enabled` is true; omit when disabled.
4. **Append the ledger phase** after the audit phase. Use `ledger-phase.md` with `{{SKILL_PATH}} → skills/<name>` substitution. Include the "Persist captured suggestions" step + suggestions line in run-end summary when `suggestion_capture_enabled` is true.
5. **Append the observer pattern (TWO sections, both required)** if `observer_enabled` is true. Use `library/templates/self-learning-skill/observer-phase.md` (see "Two sections to inline" in that template):
   - **5a.** Insert the `Observer file boundary` callout near the top of the SKILL.md — between the Mid-run suggestion capture block (or Inputs section if capture is disabled) and the first existing domain phase. Apply `{{N}}` substitution. This is what prevents domain phases from reading observer files.
   - **5b.** Append the observer Phase body after the ledger phase. Apply `{{N}}`, `{{SKILL_PATH}}`, `{{CLUSTER_THRESHOLD}}` substitutions.

   Skip both 5a and 5b if `observer_enabled` is false.
6. **Apply composition additions** (from C4.5). Skip when both `new_composed_skills` and `new_not_composed` are empty. Otherwise use `Edit` to:
   - Append each `new_composed_skills` row to the existing `Plugin skills composed by this skill` table (or create the section if missing entirely).
   - Append each `new_not_composed` entry to the existing `Plugin skills NOT composed` bullet list (or create it if missing).
   - Existing rows and bullets are preserved byte-identical — convert mode is additive only.
7. **Append the "Self-learning checklist" section** at the bottom of the SKILL.md if it isn't already present (copy from `SKILL.md.tpl`'s tail).
8. **Write `skills/<name>/run_history.json`** from the schema v1 "Initial state" snippet, plus any domain FAIL rules from C4. Include the `improvement_suggestions: []` field when `suggestion_capture_enabled` is true; omit otherwise. Include the `validation_freshness` block when `freshness_enabled` is true (substituting `created_at`/`last_validated_at` with the current ISO 8601 UTC timestamp and applying the chosen thresholds); omit otherwise.
9. **Write `skills/<name>/observations.json`** if `observer_enabled` is true:
   - **Empty** (per `observations_schema_v1.md` "Initial state") when retrospective seeding is disabled OR the existing `run_history.json` has no `runs[]` entries.
   - **Seeded** when retrospective seeding is enabled AND `runs[]` has entries: do a paper retrospective on each `runs[].notes`, `friction_log[]`, and any `improvement_suggestions[]` entries; produce 1+ seed `observations[]` entries with back-dated `ts` matching original run timestamps, verbatim evidence (no paraphrase), and category slugs from the standard table. `review_log[]` stays empty so the first live observer run can naturally trigger clustering against the seeded data.
10. **Write `skills/<name>/suggestions.md`** if `observer_enabled` is true. Use the header-only template from greenfield Step 8b.5 step 2. When retrospective seeding produced seed observations, ALSO append a "State as of bootstrap (\<date\>)" table summarizing sub-cluster counts per `_theme_slug` within each category — same shape as `pr-merge-readiness/suggestions.md` and `shared-bug-gap-fix/suggestions.md`.

Use `Edit` (not `Write`) for the SKILL.md changes so existing content is preserved precisely. Use `Write` for new files (`run_history.json`, `observations.json`, `suggestions.md`).

### Step C7 — Validate the converted skill

Run the same checks as greenfield Step 9 (1–7 always; 8–9 when observer_enabled; 10 when `new_composed_skills` or `new_not_composed` is non-empty). Add two convert-specific checks:

10. **Original phase bodies preserved byte-identical** — diff each pre-existing phase block against the post-conversion file. Content must match exactly except for any tier annotation added in headings.
11. **Frontmatter still parses** — confirm the new `metadata` block didn't break any existing field. Every key from the pre-conversion frontmatter must still resolve to the same value.

Note: in convert mode, the observer phase (when enabled) becomes Phase `<existing_N + 3>` — i.e., one higher than the new ledger which is itself `<existing_N + 2>`. Validation check 5 ("ledger is the last phase") is replaced with "observer is the last phase if observer_enabled, else ledger is the last phase" — convert mode uses whichever is final based on the toggle.

Note: in convert mode, the freshness phase (when enabled) takes the previously-unused Phase 0 slot — existing Phase 1 keeps its number. Validation check 10a fires here too: SKILL.md and `run_history.json` must agree on the freshness toggle.

If all applicable checks pass, print:

```
✓ Conversion validated. Skill ready for first audited invocation.
```

### Step C8 — Closure: first-invocation reminder

```
Smoke test (same shape as greenfield):
1. Invoke the skill on a representative real input.
2. Watch the audit phase fire — it should list <N> rows, one per original phase,
   with verbatim quotes for any input-consuming phase.
3. Block on `<approval-token>` — silence and "ok" must NOT advance.
4. After the terminal action, confirm a new entry appears under
   skills/<name>/run_history.json → runs[].

Convert-mode caveat: any phase that previously paraphrased user input will fail
`audit-paraphrased-user-input` on first run. That's the system working as
designed — counter trips at threshold=1, and the next invocation auto-edits the
offending phase per the stored remediation hint.
```

### Convert-mode edge cases

1. **Existing skill is a single phase** — borderline. Audit needs at least one row, which works, but a one-phase skill rarely benefits from the pattern. Warn and confirm.
2. **Existing skill mixes domain work and terminal action in the last phase** — recommend (don't force) splitting them so the audit can sit cleanly in between. Acceptable to keep them whole; the audit + approval token simply gates entry to that combined phase.
3. **Existing skill has no clear input-consuming phase** — the verbatim-quote rule still seeds in `run_history.json` but never trips. That's fine.
4. **Existing skill uses unconventional headings** (e.g. `### 1.`, `### Step One:`) — abort with a clear message asking the user to first normalize the headings to `## Phase N — Name` or `## Step N — Name`. Do NOT try to auto-rewrite headings.
5. **Existing skill is in the plugin's library/templates path** — refuse. Templates are not real skills.

---

## Edge cases

1. **Name collision**: Step 2 catches this; ask for a different name. Never overwrite.
2. **One domain phase**: allow but warn — most useful self-learning skills have at least 2.
3. **Many phases (10+)**: allowed without warning. `shared-bug-gap-fix` has 10.
4. **`other` terminal action**: ask for a one-line description; use it as-is.
5. **Template missing or malformed**: abort with the specific path. Do NOT repair the template.
6. **Substitution failure** (expected placeholder not found in template): abort and report which placeholder was expected from which file. The user must fix the template manually before re-running.
7. **User aborts at the `generate` gate**: clean exit, no files written, no partial state preserved. The user can re-invoke from scratch.

## Out of scope (v1)

- **Improve Mode** — modifying an existing self-learning skill via this generator. Edit the SKILL.md directly.
- **Cross-skill learning** — sharing FAIL rules across skills. Each generated skill keeps its own ledger.
- **Frontmatter auto-edits in generated skills** — auto-apply only edits the SKILL.md body, not YAML frontmatter.
- **Self-learning the meta-skill itself** — this skill is a regular skill at v1. Once it has been used to generate 2–3 real skills, it can be promoted to self-learning so it improves its own interview/generation logic.

## Plugin skills NOT composed

- `meta-claude-md-gen` — different artifact (CLAUDE.md, not SKILL.md).
- `planning-impl-plan` — the interview structure IS the plan; nesting would loop.

## Usage

```
/meta-self-learning-skill-gen                              # greenfield: interview + generate a new skill
/meta-self-learning-skill-gen convert <path-to-skill>      # convert: promote an existing skill to self-learning
```

**Greenfield** walks Steps 1–10 with explicit gates and requires the literal `generate` token. The final result is a working `skills/<name>/` folder you can invoke immediately.

**Convert** walks Steps C1–C8 instead, runs eligibility evaluation, extracts as much structure as possible from the existing SKILL.md, asks only for the gaps the audit + ledger pattern requires, and applies the conversion in place after the literal `convert` token. Existing phase bodies are preserved byte-identical.
