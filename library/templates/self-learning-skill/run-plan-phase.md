# Run-plan phase template (Phase 0.5, always-on for greenfield/describe-generated skills)

The standardized **per-run planning phase** that runs immediately before the first domain phase. It is what makes a generated skill *adaptive*: instead of marching the same fixed sequence every run, the skill reads the user's request, starts from the **baseline domain phases fixed at generation time**, and decides per step whether to **reuse / adapt / skip / create**.

This phase is **always-on DNA** for skills produced by greenfield and describe modes — there is no interview toggle, exactly like the timing and composition instrumentation. Convert-mode-retrofitted skills do NOT receive this phase (they stay fixed-sequence by design); their existing phase order is preserved byte-identical.

The run plan is **load-bearing**. Three things are NEVER skippable: this phase (planning), the audit phase, and the ledger phase. They are the machinery, not domain work. Domain (baseline) steps may be skipped, but never silently — every skip is reconciled by the audit (see `audit-phase.md`).

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SKILL_NAME}}` | This skill's name | `shared-bug-gap-fix` |

The literal text "the baseline domain phases" below resolves at run time to whatever Phases 1..N-2 the skill was generated with — the body does NOT hard-code the list, so it stays correct as the SKILL.md evolves.

---

## Phase 0.5 — Understand this run's expectations & build the run plan (non-skippable)

This phase runs **before any domain phase** and **after** the Phase 0 freshness check (when present). It is numbered `0.5` so it sits between the freshness check (Phase 0) and the first domain phase (Phase 1) **without renumbering domain phases** — this keeps every phase-keyed FAIL tag stable.

Do exactly four things, in order:

0. **Stamp `started_at` if it isn't set yet.** When the Phase 0 freshness check is present it stamps `started_at`; when freshness is disabled, Phase 0.5 is the first phase to run, so stamp `started_at = run-start timestamp` here (only if not already set). This keeps the timing instrumentation complete regardless of the freshness toggle.

1. **Capture the request verbatim.** Read the user's invocation input and quote it verbatim into in-memory run state as `run_plan.request`. Never paraphrase — this is the artifact the audit and ledger consume. If the skill was invoked with `invocation_mode=composed`, the "request" is the parent's invocation intent; quote whatever request text the parent passed (or note `composed; no explicit per-run request`).

2. **Start from the baseline — never a blank slate.** The baseline is the set of domain phases this skill was generated with (Phases 1 through N-2, the phases before the audit and ledger). Enumerate them by id. This list is `run_plan.baseline_steps`. You may NOT invent a plan that ignores the baseline; adaptation always starts from it.

3. **Classify every baseline step against this run's request.** For each baseline step, assign exactly one disposition:
   - **reuse** — run the step as written. (→ `run_plan.reused[]`)
   - **adapt** — run the step, modified for this run's intent; record a one-line `how`. (→ `run_plan.adapted[]`)
   - **skip** — do NOT run the step; record a one-line `justification` AND the step's `tier` (load-bearing / procedural / cosmetic). (→ `run_plan.skipped[]`)

   Then add **created** steps ONLY when the run genuinely needs work the baseline doesn't cover; record a one-line `why` and a synthetic id (e.g. `3b`). (→ `run_plan.created[]`)

   **Skip discipline:**
   - A **load-bearing** baseline step may be skipped *only* with an explicit, substantive justification (not "n/a", not empty). Skipping one without justification is an automatic FAIL (`plan-skipped-load-bearing-step-without-justification`, see the audit).
   - **Procedural / cosmetic** steps skip freely — but the skip is still recorded.
   - Every baseline step MUST land in exactly one of reuse / adapt / skip. A baseline step that ends up in none of them is a **silent skip** → automatic FAIL (`plan-silent-skip`, see the audit).

4. **Emit the run plan** to in-memory run state so the audit phase can reconcile it and the ledger can persist it. Print the plan to the user as a short table before proceeding:

   ```
   Run plan for "<verbatim request>":
     baseline: [1, 2, 3, ...]
     reuse:    1
     adapt:    2 — <how>
     skip:     3 — <justification> (tier: procedural)
     create:   3b — <why>
   ```

   This phase does NOT gate on an approval token — it is a planning step, not the terminal action. Proceed to the (non-skipped) domain phases immediately after printing.

**Non-skippable invariant:** Phase 0.5 itself, the audit phase, and the ledger phase are machinery and can never appear in `run_plan.skipped[]`. If a run's request seems to call for skipping the audit or ledger, that is a misread — those always fire.

---

## Authoring notes

### Why `0.5` and not renumbering

The planning phase sits between the freshness check (Phase 0) and domain Phase 1. Numbering it `0.5` keeps domain phases at their original numbers, so every FAIL tag of the form `<phase>-<slug>` (e.g. `7.5-implicit-skip-no-justification`) keeps pointing at the same domain work. Renumbering domain phases to start at 2 would silently shift every phase-keyed tag.

### Reuse vs. adapt vs. create — keep the bar honest

- Prefer **reuse**. Adaptation is for genuine per-run differences in the request, not cosmetic rewording.
- **create** is the rarest disposition. If you find yourself creating steps every run, that's signal the baseline is missing a phase — the observer's `recurring_created_step` category exists to surface exactly that for human review.
- A baseline step skipped on most runs is signal the baseline carries dead weight — the observer's `baseline_step_rarely_used` category surfaces it. Neither the planner nor the observer auto-edits the baseline; promotion/demotion is a human decision.

### Composition

When invoked with `invocation_mode=composed`, Phase 0.5 still fires (unlike the freshness check and observer, which skip when composed). The run plan governs which domain phases execute, and that decision is needed regardless of who invoked the skill. The ledger records the plan in the child's `runs[]` entry exactly as for a standalone run.
