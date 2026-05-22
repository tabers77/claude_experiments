# Freshness phase template (Phase 0)

The standardized **freshness check** that runs as the FIRST phase of every self-learning skill that opts in. Drop this into a generated skill as Phase 0, before the first domain phase.

This phase is what keeps the skill from rotting. The audit catches mechanical failures in a single run; the freshness check catches **the skill itself falling behind** as Claude Code, the ecosystem, and the skill's neighbors evolve. It is **non-blocking** — it only prints a one-line nudge when the skill is both old and well-used. It never aborts a run.

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SKILL_NAME}}` | The skill's name (used in nudge message) | `pr-merge-readiness` |
| `{{SKILL_PATH}}` | Skill's root path (where `run_history.json` lives) | `skills/pr-merge-readiness` |

---

## Phase 0 — Freshness check (non-blocking)

Before running any domain work, briefly check how stale this skill has gotten. The check is **informational only** — it never blocks a run, and Phase 1 always proceeds after it.

The premise: a skill that gets used heavily but never reviewed against the current state of Claude Code, peer skills, or its own domain will silently rot. The audit + ledger catch mechanical drift inside a run; this phase catches **the skill's own design** falling behind across runs.

0. **Composition check — skip the freshness body entirely when invoked from another skill.** Parse the skill's invocation args for `invocation_mode=composed` (semicolon-separated `key=value` format). When present, **skip steps 1–4 of this phase** and proceed directly to step 5 (proceed to Phase 1). The parent skill's own freshness check is the user-facing nudge; firing a second one here would be noise. Still stamp `started_at` for timing instrumentation — that fires unconditionally regardless of invocation mode.

   Default when the arg is absent or set to anything other than `composed` is `standalone` — all freshness steps below fire.

1. **Read** `{{SKILL_PATH}}/run_history.json` → `validation_freshness`.
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
   - The ledger phase (Phase N) will persist this on first write. Phase 0 itself does NOT write to disk — it only reads. Persistence happens in Phase N to keep all writes to `run_history.json` localized to one phase.

2. **Compute staleness**:
   - `days_since_validated = floor((now - last_validated_at) / 86400)` (in days).
   - `runs_since = validation_freshness.runs_since_validation`.

3. **Nudge condition — both must be true (AND, not OR)**:
   - `days_since_validated >= thresholds.days` (default 21), AND
   - `runs_since >= thresholds.runs` (default 10).

   The AND avoids two failure modes:
   - Cold skills (lots of days, no usage): nothing to revalidate against.
   - Hot recent skills (lots of runs, already validated last week): no value in re-nagging.

4. **When the nudge fires**, print exactly this one-line block at the top of the run (before Phase 1's first output), then continue to Phase 1:

   ```
   ⚠ Freshness: `{{SKILL_NAME}}` last validated <days_since_validated>d ago, <runs_since> runs since.
     Consider running, when you have a moment:
       /meta-discover-claude-features  — research improvements in this skill's domain
       /meta-skill-audit               — overlap check vs. other skills
     Then append a review_log[] entry to {{SKILL_PATH}}/run_history.json → validation_freshness
     and bump last_validated_at + reset runs_since_validation to 0.
   ```

   **When the nudge does NOT fire** (one or both conditions false), print nothing at all. Silence is the success state. Do NOT print "freshness OK" or any other affirmation — chatter erodes the nudge's signal value.

5. **Proceed to Phase 1 unconditionally.** The freshness check is never a hard gate. Even if the user has ignored the nudge for 100 runs, Phase 1 still runs. The user owns the decision to revalidate; this phase only surfaces the signal.

---

## Authoring notes

### Why Phase 0 and not at the end

The nudge has to fire **before** the user gets absorbed in domain work. If it appears at run-end, the user has already moved on mentally and is unlikely to act. Putting it first costs one line of output and lands the signal when attention is highest.

### Why non-blocking

Blocking would be wrong for two reasons:
1. The user may be running the skill in a context where they can't stop to revalidate (mid-incident, deadline pressure). Forcing it would teach them to disable the check entirely.
2. Revalidation is a **review** activity, not an execution activity. It needs deliberate time, not a stolen 30 seconds before the real work fires.

The signal value comes from accumulating staleness pressure, not from forcing a hard stop.

### Why AND-gated (not OR)

A single condition gate — "21 days OR 10 runs" — would nudge low-use skills every 3 weeks regardless of whether anything has changed about how they're used. The AND keeps the nudge tied to **load-bearing skills**: ones the user actually relies on AND has had time to drift away from.

### What "validation" means

When the user appends a `review_log[]` entry, they're certifying that they:
1. Considered whether the skill's design still matches current Claude Code features / community patterns (research).
2. Confirmed the skill is not silently overlapping a peer skill (overlap check).

Either step alone is partial — but partial is fine. The `type` field records which was done (`research`, `overlap`, or `both`). The freshness phase treats any non-empty review as a reset, since even a partial pass is better than none.

### Thresholds are per-skill

Defaults (10 runs, 21 days) work for an average-cadence skill. Hot skills (run multiple times per day) should lower the runs threshold; quiet skills with stable surfaces (used once a month, rarely changed) can raise the days threshold. Tune by editing the JSON directly — there is no UI for this on purpose. Skills should keep their own cadence.

### Initialization is in-memory only

Phase 0 reads. Phase N (ledger) writes. Centralizing writes in the ledger phase preserves the existing invariant that `run_history.json` has exactly one writer per run, which makes concurrent-run scenarios (if they ever exist) safer.

### Why composed runs skip the nudge

When this skill is invoked from another self-learning skill (e.g. `pr-merge-readiness` calling `smart-test-selection`), the user sees one user-facing run, not two. The parent's freshness phase already handles the validation nudge for the composed workflow. Firing a second nudge from the child would surface the same staleness signal twice — and worse, point the user at the wrong skill name.

The skip is body-only: `started_at` still gets stamped for timing. The child's freshness counter (`runs_since_validation`) is still incremented by its own ledger phase regardless of mode, so composed usage accumulates toward the standalone nudge that fires when the user invokes the child directly.

### `friction_log` is out of scope

If a user finds the nudge wording annoying, the ledger phase's `friction_log` is the right place to capture that, not this phase.
