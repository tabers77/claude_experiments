---
name: {{SKILL_NAME}}
description: {{ONE_LINE_DESCRIPTION}} {{TRIGGER_KEYWORDS}}
metadata:
  pattern: self-learning
  schema-version: 1
---

# {{SKILL_TITLE}}

{{ONE_PARAGRAPH_PURPOSE}}

**Load-bearing principle**: {{LOAD_BEARING_PRINCIPLE}}

## Inputs

The user invokes the skill with one of:

| Shape | Example | Mode |
|---|---|---|
{{INPUT_ROWS}}

If the input is none of the above, {{INPUT_FALLBACK_BEHAVIOR}}.

---

<!--
================================================================================
PHASE 0 — Freshness check (OPTIONAL, non-blocking)
================================================================================
Insert the body of `library/templates/self-learning-skill/freshness-phase.md`
here when the skill opts in (default: opt-in). The phase prints a one-line nudge
when both staleness conditions trip (days_since_validated >= 21 AND
runs_since_validation >= 10) and is silent otherwise. It never blocks Phase 1.

Substitutions:
  - `{{SKILL_NAME}}` → this skill's name
  - `{{SKILL_PATH}}` → e.g. `skills/{{SKILL_NAME}}`

Omit the entire phase block when the skill opts OUT of the freshness check.
In that case, also drop `validation_freshness` from `run_history.json`.
================================================================================
-->

## Phase 0 — Freshness check (non-blocking)

> **Insert here**: the body of `library/templates/self-learning-skill/freshness-phase.md`
> with these substitutions:
>   - `{{SKILL_NAME}}` → this skill's name
>   - `{{SKILL_PATH}}` → this skill's root path (e.g. `skills/{{SKILL_NAME}}`)

<!--
================================================================================
DOMAIN PHASES (1 through N-2)
================================================================================
Replace this section with your skill's domain phases. Each phase should have:
  - A clear trigger (what kind of input or prior-phase output activates it).
  - A clear exit condition (what evidence proves the phase ran correctly).
  - An evidence shape that maps to a Phase N-1 audit row.

Phases that consume user input MUST record the input verbatim — never paraphrase.
Phases that gate progression MUST require a literal approval token (recorded in
the audit phase as the `APPROVAL_TOKEN`).

Number your phases starting at 1. Half-numbered sub-phases (1.5, 5.5, 7.5) are
encouraged for gates and validations that interrupt the main flow — see
`shared-bug-gap-fix` for a worked example.
================================================================================
-->

## Phase 1 — {{PHASE_1_NAME}}

{{PHASE_1_BODY}}

## Phase 2 — {{PHASE_2_NAME}}

{{PHASE_2_BODY}}

<!-- ...add as many domain phases as needed... -->

---

<!--
================================================================================
STANDARDIZED LAST TWO PHASES (do not customize structure)
================================================================================
The audit phase and ledger phase are what make this a SELF-LEARNING skill.
Do not modify their structure. Customize ONLY the placeholders.

To insert their bodies, copy from:
  - library/templates/self-learning-skill/audit-phase.md  (for Phase N-1)
  - library/templates/self-learning-skill/ledger-phase.md (for Phase N)

Substitute the placeholders listed at the top of each template file.
================================================================================
-->

## Phase {{N_MINUS_1}} — Pre-action self-audit (CHECKPOINT, blocking)

> **Insert here**: the body of `library/templates/self-learning-skill/audit-phase.md`
> with these substitutions:
>   - `{{N}}` → `{{N_MINUS_1}}`
>   - `{{TERMINAL_ACTION}}` → `{{TERMINAL_ACTION}}` (e.g. `commit`, `deploy`, `doc-edit`)
>   - `{{TERMINAL_ACTION_CAPITALIZED}}` → capitalized form
>   - `{{APPROVAL_TOKEN}}` → the literal token required to advance (e.g. `audit approved`)
>   - `{{PHASE_AUDIT_ROWS}}` → one audit row per domain phase
>   - `{{DOMAIN_FAIL_RULES}}` → skill-specific FAIL detection rules (start with what you know)

## Phase {{N}} — Update the run-history ledger

> **Insert here**: the body of `library/templates/self-learning-skill/ledger-phase.md`
> with these substitutions:
>   - `{{N}}` → this phase's number
>   - `{{SKILL_PATH}}` → this skill's root path (e.g. `skills/{{SKILL_NAME}}`)
>   - `{{TERMINAL_ACTION}}` → same as above

---

## Edge cases

{{EDGE_CASES}}

## Plugin skills composed by this skill

| Skill | Phase | Trigger |
|---|---|---|
{{COMPOSED_SKILLS}}

## Out of scope

{{OUT_OF_SCOPE}}

## Usage

Tell Claude one of:

```
{{USAGE_EXAMPLES}}
```

The skill walks Phases 1–{{N}} and asks for explicit approval before advancing past every gate. Failure patterns accumulate in `run_history.json`; when a counter trips its threshold, the skill auto-edits its own SKILL.md per the `remediation_hint` and the user reviews the edit in their normal commit-review loop.

---

## Self-learning checklist (before shipping)

Before the first invocation of a generated skill, verify:

- [ ] `run_history.json` exists at the skill's root, initialized with the universal seed FAIL rules from `library/templates/self-learning-skill/run_history_schema_v1.md` ("Initial state" section).
- [ ] The audit phase (`Phase {{N_MINUS_1}}`) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every phase that consumes user input has a row format that records the input **verbatim**, never paraphrased.
- [ ] The terminal action (Phase {{N_MINUS_1}} or earlier) requires the literal `{{APPROVAL_TOKEN}}` — silence, "ok", "looks good" do NOT advance.
- [ ] At least one domain FAIL rule exists OR the rules section explicitly says "no domain rules yet — accumulating from runs."
- [ ] Threshold tiers match phase severity: load-bearing=1, procedural=2, cosmetic=5.
- [ ] The ledger phase (`Phase {{N}}`) is the last phase. No phase fires after it.
- [ ] (Freshness opt-in only) `Phase 0 — Freshness check` is present as the FIRST phase, before Phase 1. It is non-blocking and prints nothing when fresh.
- [ ] (Freshness opt-in only) `run_history.json` contains a `validation_freshness` block initialized to the schema's "Initial state" defaults (thresholds runs=10, days=21).
- [ ] (Freshness opt-in only) The ledger phase contains the `validation_freshness.runs_since_validation` increment step. The skill MUST NOT self-certify freshness — only the user appends `review_log[]` entries.
