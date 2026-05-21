# Observer phase template (Phase N+1, OPTIONAL)

The standardized **post-ledger observer** that runs as the very last phase of a self-learning skill, *after* the ledger has written and any threshold-tripped audit remediations have been auto-applied. Drop this into a generated skill as the final phase when you want a second vantage on the run that the mechanical audit cannot provide.

The observer is a **suggestion-only** phase. It NEVER edits `SKILL.md` directly. It writes to two new files at the skill's root:

- `observations.json` — append-only ledger of qualitative signals (one entry per signal, schema in `library/templates/self-learning-skill/observations_schema_v1.md`).
- `suggestions.md` — human-readable proposals written when observations cluster (threshold-driven, conservative).

The audit catches *what was told to be tracked*. The observer catches *what wasn't*: user friction, redundant phases, scope drift, signs of audit blind spots. Its main payoff is **cross-run pattern detection** — themes invisible from a single run become visible once `observations.json` accumulates entries.

> **Decoupling note.** This phase is bolted into the host skill for the prototype to keep the change surface small. If the pattern proves valuable, the planned next step is to lift the observer out into a standalone `meta-observer-review` skill (or a Stop hook) that reads any skill's `observations.json` independently. Authors should treat the observer body as movable, not load-bearing in its current location.

## When to include this phase

Include the observer when **any** of these are true:
- The skill has ≥3 domain phases (enough surface for qualitative signals to land somewhere).
- The skill consumes meaningful user input (Phase 7-style resolution gates, audit corrections, mid-run captures).
- The skill is a candidate for cross-run pattern detection (will be invoked many times).

Skip the observer when:
- The skill is a single-phase generator with no execution loop.
- The skill is a one-shot interview where the artifact *is* the output.
- The skill is purely deterministic with no user-judgment branching.

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{N}}` | This phase's number (one higher than the ledger phase) | `10` |
| `{{SKILL_PATH}}` | Skill's root path (where `observations.json` and `suggestions.md` live) | `skills/pr-merge-readiness` |
| `{{CLUSTER_THRESHOLD}}` | Minimum observations sharing a category to trigger a `suggestions.md` write | `3` |

## Two sections to inline (not one)

When retrofitting or generating a skill with the observer pattern, inline **both** of these into the host SKILL.md:

1. The **`Observer file boundary` callout** (see "Companion: Observer file boundary callout" at the bottom of this template) — placed **near the top** of the SKILL.md, between the Mid-run suggestion capture block (or Inputs section if capture is disabled) and the first domain phase. This callout protects the design invariant that domain phases never read observer files.
2. The **`Phase {{N}}` body** (the main section below) — placed as the LAST phase, after the ledger phase.

Both placements are required. Inlining only the Phase body without the boundary callout leaves the door open for the leak the callout prevents.

---

## Phase {{N}} — Post-ledger observer (suggestion-only)

The observer runs **after** the ledger has written `run_history.json` and any audit-tripped remediations have been auto-applied. Its job is to surface qualitative signals the audit's mechanical FAIL detection cannot catch, and — once enough observations accumulate — propose changes for manual review.

The observer NEVER edits `SKILL.md`. It writes only to `observations.json` (per-run notes) and `suggestions.md` (clustered proposals). The user reviews `suggestions.md` and decides whether to integrate any proposal.

1. **Read state**:
   - `{{SKILL_PATH}}/observations.json` — initialize per the schema if missing.
   - `{{SKILL_PATH}}/run_history.json` — for the run that just finished (last entry in `runs[]`) and prior runs (for cross-run context).

2. **Walk the just-finished run from a different vantage than the audit.** The audit reports mechanical FAIL conditions; the observer looks for qualitative signals the audit was never told to look for. Categories to scan for (extend per skill, never invent observations to fill space):

   | Category slug | What to look for | Example signal |
   |---|---|---|
   | `user_friction` | re-asked questions, repeated corrections, "no, I meant", "you missed", visible frustration | user typed three corrections to the same audit row before approving |
   | `redundant_phase` | phase Y's output exactly duplicates phase X's; user explicitly skipped a phase | Phase 4 surfaced findings already listed in Phase 3 |
   | `scope_drift` | the skill ventured outside its frontmatter `description` | a merge-readiness skill started auto-fixing code |
   | `missing_audit_category` | a recurring qualitative concern with no FAIL tag covering it | tracker-file diff anomaly noted by user but not by any audit row |
   | `dev_env_friction` | environmental setup pain that recurs across runs | "stale container missing dep" mentioned in two runs' notes |
   | `output_format_quality` | UX-only signal: format/readability of the skill's output | audit row evidence string too long to scan visually |
   | `cross_phase_redundancy` | two phases share evidence the user only had to provide once | Phase 1 and Phase 3 both quoted the same user input |
   | `boundary_violation` | a domain phase referenced or used content from `observations.json` / `suggestions.md` (which it must not read) | Phase 2's user prompt framing visibly originated in observer-file content; the skill cited a prior observation in-flight to justify a recommendation |
   | `phase_scope_too_broad_for_input` | a phase ran a full-scope routine when the input class would have justified a narrower scope (e.g. lite-mode existed but wasn't taken) | Phase 5 ran the full no-new-bugs sweep on a docs-only diff that Phase 1 had already classified `scope=lite` |
   | `serializable_as_parallel` | two phases ran sequentially that have no data dependency on each other and could parallelize | Phase 3 (pre-commit-check sweep) and Phase 4 (relevant-tests run) ran back-to-back, neither using the other's output |
   | `redundant_work_with_prior_phase` | a phase recomputed something an earlier phase already produced; the second phase's evidence cites the same fact the first one captured | Phase 5's evidence row quotes the same diff path set that Phase 1 already classified |
   | `over_thorough_for_input_class` | a long-running phase fired on a tiny input where its full pass isn't load-bearing; skill lacks input-class dispatch | Phase 4 ran 8 tiers of tests on a single-line README change |
   | `missed_cached_result` | a phase did work whose exact result is already recorded in `runs[]` for the same target / commit / input shape | Phase 2 (clean-merge probe) re-ran `git merge-tree` for a target whose result was identical in the run 30 minutes earlier |

2a. **Efficiency trade-off detector** — runs only when this run has `duration_seconds` and `quality_derived` populated. Skip entirely otherwise (no fabricated signal on pre-instrumentation runs).

   1. Group prior runs in `runs[]` by **input-class similarity** to this run's target. Default grouping: same `outcome` AND same `quality_derived` tier among runs with a similar input shape (skill-specific — e.g. for `pr-merge-readiness`, runs with `scope=lite` cluster together vs `scope=full`). If the skill has no input-class concept, group on `outcome` alone.

   2. Compute the median `duration_seconds` of the matching cohort (need ≥ 3 prior cohort members — otherwise skip; one prior run is not a baseline).

   3. **File an observation** under `phase_scope_too_broad_for_input` (or a more specific category if the evidence points clearly at one) when **both** are true:
      - `this_run.duration_seconds > 1.5 × cohort_median`
      - `this_run.quality_derived` is NOT strictly better than `cohort_median_quality` (i.e. quality didn't improve to justify the time cost). Define the ordering `clean > partial > failed > incomplete`.

   4. **Also file an observation** when **both** are true (the inverse failure mode — fast at the cost of quality):
      - `this_run.duration_seconds < 0.5 × cohort_median`
      - `this_run.quality_derived` is strictly worse than `cohort_median_quality`.

   The trade-off detector exists specifically to prevent "race to fast trash" — every speed delta must be tied to a quality delta before the observer files it. Slow-but-better runs and fast-but-equal runs are NOT observations; they're just variance.

   Each filed observation's `evidence` field MUST include the exact numbers: this run's duration, cohort median, this run's `quality_derived`, cohort median's `quality_derived`, and the cohort size. No paraphrase, no rounding to "much slower."

3. **Append observations** to `observations.json`. Each observation MUST cite verbatim evidence — never paraphrase user input. **Zero observations is a valid output.** Do NOT invent signals to demonstrate the observer is doing work.

   Each observation row:
   ```json
   {
     "ts": "<iso8601-now>",
     "run_ref": "<ts of the matching runs[] entry in run_history.json>",
     "target": "<run input>",
     "category": "<slug from the table above, or new slug if a novel signal>",
     "_theme_slug": "<optional sub-theme slug for the theme-similarity check; lowercase-hyphenated, stable forever>",
     "phase": "<phase number where signal appeared, or 'cross-phase'>",
     "evidence": "<verbatim quote / observed event>",
     "interpretation": "<one-line reasoning for why this signal matters>",
     "proposed_audit_tag": "<optional new FAIL tag the audit could track, or null>"
   }
   ```

4. **Cross-run clustering check** — for each category in `observations.json`:
   - Count entries whose `applied_at` (in any subsequent `review_log` entry) is null.
   - If `count >= {{CLUSTER_THRESHOLD}}`, this category trips a proposal pass.
   - **Convergence rule (overrides threshold)**: if observer recorded ≥1 unaddressed observation in a category AND `run_history.json:improvement_suggestions[]` contains a user-typed entry whose `tag` or `text` matches the same theme, treat the category as cluster-tripped regardless of count. Two independent channels agreeing (observer's qualitative scan + user's explicit suggestion) is stronger evidence than `{{CLUSTER_THRESHOLD}}` same-channel observations. When the convergence rule trips, the proposal in `suggestions.md` MUST cite both the observation `ts` values AND the matching `improvement_suggestions[]` entry verbatim.
   - **Theme-similarity check (before writing a proposal)**: a single category often contains observations describing distinct underlying themes (e.g., `user_friction` covering both "gate-token bypass" and "branch-prefix override"). Before writing a proposal, group the observations within the tripped category by underlying theme — same root-cause, same recommended remediation. Only sub-clusters with count ≥ `{{CLUSTER_THRESHOLD}}` (or convergence) trigger a proposal. Sub-clusters below threshold remain in `observations.json` until they grow. Do NOT lump unrelated themes into one proposal — that produces vague, useless `suggestions.md` entries the user will ignore.

5. **Write proposal to `suggestions.md`** for each tripped category:
   - Append a new section with the clustered theme (one line), the N observations as evidence (verbatim, with `ts` references), the observer's interpretation, and a specific proposed `SKILL.md` edit (or "no specific edit yet — propose new audit tag `<slug>`").
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
     "suggestion_written_to": "{{SKILL_PATH}}/suggestions.md",
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
   - Observer NEVER writes to `run_history.json` **with one narrow exception**: when an observation's category is `dev_env_friction`, the observer MAY append a single corresponding entry to `run_history.json:friction_log[]` (see the schema's `friction_log` section). This is permitted because (a) the schema's `friction_log` field exists exactly for this signal class and tends to sit unused otherwise, and (b) environmental friction has no SKILL.md edit that fixes it — `suggestions.md` is the wrong destination. Observer touches NO other field of `run_history.json`. If multiple `dev_env_friction` observations recur, observer still writes one `friction_log` entry per run (not per observation), with `mitigation_options` derived from prior `friction_log[]` entries when present.
   - Observer DOES NOT block the run from closing. By the time it fires, the ledger has already written and the terminal action is done. If the observer errors, the run is still considered closed.

---

## Authoring notes

### Why post-ledger and not inside the audit

The audit's job is mechanical: predefined FAIL rules with deterministic detection. Co-locating qualitative scanning would either dilute the audit's load-bearing honesty (paraphrase creeps in) or bloat the audit phase. Post-ledger keeps the two vantages cleanly separated: audit = categorical + per-run + auto-apply; observer = qualitative + cross-run + suggestion-only.

It also means observer sees the *post-remediation* state of `SKILL.md` — if the audit just auto-edited a fix in, observer should not duplicate-propose the same fix.

### Why the cluster threshold is conservative

Default `{{CLUSTER_THRESHOLD}} = 3`. A single observation is anecdote; two could be coincidence; three start being a pattern. Lower thresholds produce noisy `suggestions.md` files that erode the user's trust in the proposals. Tune up (not down) for skills with very high run cadence.

### How observer differs from `improvement_suggestions[]` capture

The mid-run suggestion capture (`suggestion-capture.md`) records what the **user** explicitly typed during a run. The observer records what the **skill notices** about the run. They complement each other:

- User says "suggestion: format the audit as a table" → captured in `improvement_suggestions[]`.
- Observer notices "two runs in a row had >5-line evidence strings in audit rows" → recorded in `observations.json` under `output_format_quality`.

When both surface the same theme, that's the strongest signal — observer's clustering pass should specifically check whether any `improvement_suggestions[]` entries align with its own observations and reference them in the proposal.

### Initial state: fresh skill vs. retrofitted skill

For a **freshly-generated** skill that includes the observer phase from day one, initialize `observations.json` empty (per the schema's "Initial state" section) and let it accumulate from real runs. No seed entries.

For a **retrofitted** skill (observer added to an existing skill that already has runs in `run_history.json`), do NOT start `observations.json` empty. Instead:

1. Before the first observer run, do a **paper retrospective** on the existing `runs[]` and `improvement_suggestions[]` of `run_history.json` — identify qualitative themes the audit didn't catch.
2. Pre-populate `observations.json:observations[]` with seed entries derived from that retrospective. Each seed entry MUST:
   - Use a `ts` matching the original `runs[].ts` it describes (back-dated, not the retrofit's wall-clock).
   - Set `run_ref` to the same value as `ts` (matches the original `runs[]` entry).
   - Cite verbatim evidence from `runs[].notes` or `improvement_suggestions[].text` — same no-paraphrase rule as live observations.
   - Tag `category` per the standard table.
3. Do NOT pre-populate `review_log[]` — let the first observer run trigger clustering naturally against the seeded observations. This way cross-run patterns are visible from run 1 of using observer instead of run 4.

This bootstrap is a one-time operation per retrofitted skill. Document it in the skill's commit message ("seeded observations.json with N retrospective entries from runs <ts1>, <ts2>") so the back-dated entries are auditable.

### Tolerate manual edits

`observations.json` and `suggestions.md` are user-editable at any time:
- User flips `Status: unreviewed` to `Status: applied` after manually integrating a proposal.
- User adds `applied_at` / `applied_via` to a `review_log[]` entry to mark resolution.
- User deletes stale entries from `observations.json` if they're no longer relevant.

Never reject either file because the user added a field, changed status, or annotated a record. The observer must tolerate any valid v1 JSON / freeform markdown.

### When the observer should NOT add a proposal

- The audit just auto-applied a remediation that addresses the same theme this run.
- The user already captured the same idea via `improvement_suggestions[]` and applied it.
- The category is `dev_env_friction` and the friction is project-environmental rather than skill-logic (these belong in `friction_log[]` of `run_history.json`, not as a SKILL.md edit proposal — observer can append to `friction_log[]` for these).
- Zero new observations this run AND no clustering tripped. Print summary, exit cleanly.

### Why efficiency proposals stay suggestion-only

`fail_counters` remediations auto-apply on threshold because their failure mode is symmetric: a missed FAIL says "do MORE checking" — worst case is added noise, never a missed bug. Efficiency remediations are the opposite: they say "do LESS work." The failure mode is silent — the skill quietly learns to skip a phase that was load-bearing for an input class it hasn't seen yet, and the user only discovers it when a bad merge lands.

Suggestion-only mode keeps the human in the loop precisely where the asymmetric risk lives. The observer surfaces the evidence; the user decides whether dropping the work is safe.

### Common mistakes to avoid

- **Don't make the observer too eager.** Empty observation rounds are healthy. Eagerness leads to hallucinated patterns and erodes trust.
- **Don't conflate observation with audit FAIL.** If a signal can be mechanically detected, it belongs in the audit's FAIL rules. Observer is for what *can't* be mechanically detected.
- **Don't let observer propose frontmatter edits.** Like the audit, body-only edits are safer. Frontmatter changes can mis-route the skill at trigger time.
- **Don't let observer chain into the audit.** It runs after the ledger; if it sees something the audit missed, the right move is a `proposed_audit_tag` field, not re-firing the audit retroactively.

---

## Companion: Observer file boundary callout (insert near top of SKILL.md)

This is the second section the observer pattern requires (see "Two sections to inline"). Place it near the top of the host SKILL.md — between the Mid-run suggestion capture block (or the Inputs section, if capture is disabled) and the first domain phase. Apply the same `{{N}}` substitution as the Phase body.

```markdown
## Observer file boundary

This skill includes an observer phase (Phase {{N}}) that writes to `observations.json` and `suggestions.md`. **All other phases (1 through {{N}}-1) MUST NOT read those files.**

The two files are owned by the observer phase exclusively and exist for cross-run pattern analysis + human review. They are *descriptive* (record what happened across prior runs), not *prescriptive* (do not encode what should happen on this run).

In particular, the agent running domain phases MUST NOT:

- Use `observations.json` content as background context when framing prompts to the user.
- Alter a phase's recommendation, default branching, or option ordering based on prior observations.
- Cite observations to justify a skill behavior in-flight.

The only legitimate path for an observation to change skill behavior is: observer clusters the signal → writes a proposal to `suggestions.md` → human reviews → human edits this `SKILL.md` (or dismisses the proposal). The audit channel and the observer channel remain **isolated by design** — that isolation is what keeps observer's seeded data from silently biasing the skill's defaults.

If you are an LLM/agent running this skill: treat `observations.json` and `suggestions.md` as if they did not exist until you reach Phase {{N}}. Reading them earlier is a load-bearing violation, and there is no FAIL tag for it because the file content is silent — the only safeguard is this rule.
```

### Why this is structurally separate from the Phase body

The Phase body lives at the end of the SKILL.md (it's the last phase). But Claude reads SKILL.md top-to-bottom when invoked, so a prohibition placed only at the bottom does nothing — by the time Claude sees it, it has already read or might already read the observer files. The boundary callout has to live near the top to gate Claude's attention before any domain phase fires. Two distinct insertion points, one shared rule.
