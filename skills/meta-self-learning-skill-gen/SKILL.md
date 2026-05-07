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

1. **Check arguments**: if the user passed `improve <skill-name>`, respond: "Improve mode is not yet supported in v1. To modify an existing self-learning skill, open its SKILL.md directly." and stop.
2. **Read the four templates** (you'll substitute from them later):
   - `library/templates/self-learning-skill/SKILL.md.tpl`
   - `library/templates/self-learning-skill/audit-phase.md`
   - `library/templates/self-learning-skill/ledger-phase.md`
   - `library/templates/self-learning-skill/run_history_schema_v1.md`

   If any template is missing, abort with a clear error pointing to the path. Do NOT try to repair or invent template content.

### Step 2 — Interview: identity

Ask all four questions at once, let the user answer in bulk:

```
I'll generate a self-learning skill for you. First, the basics:

1. Skill name? (kebab-case, e.g. `log-decision`. Must not collide with an existing skill in skills/.)
2. One-sentence description? (what the skill does — will go in the YAML description)
3. Trigger keywords? (comma-separated, used by skill auto-routing)
4. Load-bearing principle? (the one rule the skill must NEVER violate — guides tier classification later)
```

**Validate the name**:
- Must match `^[a-z][a-z0-9-]+$` (kebab-case, no underscores).
- Use `Glob` `skills/<name>/` to confirm the directory doesn't already exist. If it does, stop and ask the user for a different name. **Never overwrite an existing skill folder under any circumstance.**

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

Skill folder:    skills/<name>/
Files to create:
  - skills/<name>/SKILL.md          (assembled from .tpl + audit-phase.md + ledger-phase.md)
  - skills/<name>/run_history.json  (bootstrap from run_history_schema_v1.md "Initial state")

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
  Phase <N> — Update the run-history ledger
    Writes to: skills/<name>/run_history.json

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
2. If Step 6 added domain FAIL rules, append each to the `fail_counters` object with:
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
3. Validate that the resulting JSON parses (mentally walk it for matching braces/quotes).

#### 8c — Write both files

```
Write skills/<name>/SKILL.md
Write skills/<name>/run_history.json
```

Show the user the file paths and a short preview of each (frontmatter + first 30 lines for SKILL.md; full content for run_history.json).

### Step 9 — Validate the generated files

Run these mechanical checks. Fail loudly on any miss — DO NOT silently proceed.

1. **No orphan placeholders**: `Grep` the generated SKILL.md for `{{` — must return zero matches. If any placeholder remains, surface its location and offer to fix.
2. **JSON is valid v1**: parse `run_history.json` (mentally or via `python -c "import json; ..."`). Confirm `version == 1`, `fail_counters` is an object, `runs` and `friction_log` are arrays.
3. **Audit phase has correct row count**: count `- Phase` lines in the audit block — must equal the number of domain phases.
4. **Approval gate uses the literal token**: confirm the audit phase contains the exact approval token from Step 3 wrapped in backticks.
5. **Ledger phase is the last phase**: no `## Phase` heading appears after the ledger block.
6. **Phase numbering is contiguous**: 1, 2, ..., N with no gaps. Sub-phases (1.5, 5.5) are allowed but flag for review.

If all six pass, print:

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
/meta-self-learning-skill-gen
```

The skill walks Steps 1–10 with explicit gates. Generation requires the literal `generate` token. The final result is a working `skills/<name>/` folder you can invoke immediately.
