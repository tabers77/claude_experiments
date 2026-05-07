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
- `library/templates/self-learning-skill/ledger-phase.md` — ledger body (Phase N)
- `library/templates/self-learning-skill/run_history_schema_v1.md` — schema + bootstrap JSON

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
2. **Read the four templates** (you'll substitute from them later):
   - `library/templates/self-learning-skill/SKILL.md.tpl`
   - `library/templates/self-learning-skill/audit-phase.md`
   - `library/templates/self-learning-skill/ledger-phase.md`
   - `library/templates/self-learning-skill/run_history_schema_v1.md`

   If any template is missing, abort with a clear error pointing to the path. Do NOT try to repair or invent template content.

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

### Step 7 — Show generation plan and wait for `generate` token

Before writing any files, present the full plan:

```
=== Generation plan ===

Skill folder:    <target_dir>/<name>/
                 (resolved from Step 2 location choice: <plugin|project|user|custom>)
Files to create:
  - <target_dir>/<name>/SKILL.md          (assembled from .tpl + audit-phase.md + ledger-phase.md)
  - <target_dir>/<name>/run_history.json  (bootstrap from run_history_schema_v1.md "Initial state")

Frontmatter:
  name: <name>
  description: <description> <keywords>

Phase structure:
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

Mid-run suggestion capture: <enabled|disabled>
  When enabled, the SKILL.md gets a "Mid-run suggestion capture" block after the
  Inputs section, and run_history.json includes an improvement_suggestions[] array.

Audit row shapes (one per domain phase, applied in audit phase):
  Phase 1: <evidence shape — verbatim quote slot if input-consuming>
  Phase 2: ...

run_history.json seed counters:
  - audit-paraphrased-user-input (universal, threshold=1, load-bearing)
  - audit-no-explicit-approval-wait (universal, threshold=2, procedural)
  - tool-claim-without-call (universal, threshold=1, load-bearing)
  <+ any domain rules from Step 6>

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

6. **Fill the trailing sections** (`Edge cases`, `Plugin skills composed`, `Out of scope`, `Usage`) with sensible defaults if the user didn't provide them. For first-time skills, populate `Usage` with at least one `/<skill-name> <example>` invocation drawn from the inputs.

#### 8b — Build run_history.json

1. Use the **"Initial state"** JSON snippet from `run_history_schema_v1.md` verbatim as the base.
2. **Apply suggestion-capture toggle** (from Step 5.5):
   - If `suggestion_capture_enabled` is `true`: keep the `"improvement_suggestions": []` line as it appears in the canonical Initial state.
   - If `suggestion_capture_enabled` is `false`: drop the `"improvement_suggestions": []` line entirely AND remove the trailing comma from the previous line so the JSON stays valid.
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

#### 8c — Write both files

```
Write <target_dir>/<name>/SKILL.md
Write <target_dir>/<name>/run_history.json
```

(`<target_dir>` resolved in Step 2: plugin → `<CWD>/skills`, project → `<CWD>/.claude/skills`, user → `~/.claude/skills`, custom → user-provided.)

Show the user the absolute file paths and a short preview of each (frontmatter + first 30 lines for SKILL.md; full content for run_history.json).

### Step 9 — Validate the generated files

Run these mechanical checks. Fail loudly on any miss — DO NOT silently proceed.

1. **No orphan placeholders**: `Grep` the generated SKILL.md for `{{` — must return zero matches. If any placeholder remains, surface its location and offer to fix.
2. **JSON is valid v1**: parse `run_history.json` (mentally or via `python -c "import json; ..."`). Confirm `version == 1`, `fail_counters` is an object, `runs` and `friction_log` are arrays.
3. **Audit phase has correct row count**: count `- Phase` lines in the audit block — must equal the number of domain phases.
4. **Approval gate uses the literal token**: confirm the audit phase contains the exact approval token from Step 3 wrapped in backticks.
5. **Ledger phase is the last phase**: no `## Phase` heading appears after the ledger block.
6. **Phase numbering is contiguous**: 1, 2, ..., N with no gaps. Sub-phases (1.5, 5.5) are allowed but flag for review.
7. **Suggestion-capture consistency**: confirm SKILL.md and run_history.json agree.
   - If `suggestion_capture_enabled` is true: SKILL.md MUST contain `## Mid-run suggestion capture` heading AND `run_history.json` MUST contain `"improvement_suggestions": []`.
   - If false: SKILL.md MUST NOT contain that heading AND `run_history.json` MUST NOT contain that key.
   Mismatch → fail loudly and report which side disagrees.

If all seven pass, print:

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

### Step C5 — Show conversion plan and wait for `convert` token

Present the diff plan before writing anything. Be explicit about what is preserved versus what is added:

```
=== Conversion plan for skills/<name>/ ===

Frontmatter changes:
  + metadata.pattern: self-learning
  + metadata.schema-version: 1
  (name, description, and any other existing fields unchanged)

Phase additions (existing <N> domain phases preserved BYTE-IDENTICAL):
  + Phase <N+1> — Pre-action self-audit (CHECKPOINT, blocking)
      Approval token: `<token>`
      Audit rows: <N> (one per existing domain phase)
      Verbatim-quote rows: <count of input-consuming phases>
      FAIL detection rules: 3 universal + <count> domain
  + Phase <N+2> — Update the run-history ledger
      Writes to: skills/<name>/run_history.json

Files to create:
  + skills/<name>/run_history.json (bootstrap from schema v1 "Initial state")

Files to modify:
  ~ skills/<name>/SKILL.md
      - Add metadata block to frontmatter
      - Append two phases after the current last phase
      - Append "Self-learning checklist" section if missing

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
2. **Append the audit phase** after the last existing domain phase. Use the body of `library/templates/self-learning-skill/audit-phase.md` with substitutions from C3/C4. Audit row count must equal the number of existing domain phases; rows for input-consuming phases include the verbatim-quote slot. Use the chosen heading prefix (`Phase` or `Step`) consistently.
3. **Append the ledger phase** after the audit phase. Use `ledger-phase.md` with `{{SKILL_PATH}} → skills/<name>` substitution.
4. **Append the "Self-learning checklist" section** at the bottom of the SKILL.md if it isn't already present (copy from `SKILL.md.tpl`'s tail).
5. **Write `skills/<name>/run_history.json`** from the schema v1 "Initial state" snippet, plus any domain FAIL rules from C4.

Use `Edit` (not `Write`) for the SKILL.md changes so existing content is preserved precisely. Use `Write` for the new `run_history.json`.

### Step C7 — Validate the converted skill

Run the same six mechanical checks as greenfield Step 9 (no orphan placeholders, JSON is valid v1, audit row count matches domain phase count, approval token is literal-and-quoted, ledger is the last phase, phase numbering is contiguous). Add two convert-specific checks:

7. **Original phase bodies preserved byte-identical** — diff each pre-existing phase block against the post-conversion file. Content must match exactly except for any tier annotation added in headings.
8. **Frontmatter still parses** — confirm the new `metadata` block didn't break any existing field. Every key from the pre-conversion frontmatter must still resolve to the same value.

If all eight pass, print:

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
