# Mid-run suggestion capture template

A standardized block that lets the user propose improvements to a self-learning skill **at any point during a run**, not only at the audit. The skill recognizes specific trigger prefixes; any user message starting with one is captured verbatim into `improvement_suggestions[]` in `run_history.json`, then the run continues exactly where it was.

This block lives in the SKILL.md right after the Project config section (or, for skills without a config block, right after the Inputs section) — before the first domain phase. The protocol is global: every phase inherits it without per-phase wiring.

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SKILL_NAME}}` | This skill's name (kebab-case) | `pr-merge-readiness` |
| `{{SKILL_PATH}}` | Path to the skill folder where `run_history.json` lives | `skills/pr-merge-readiness` |

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
improvement: [6-detection-tightening] add internal token regex
```

**Capture protocol** (the skill follows this exactly):

1. **Detect the prefix** at the start of the user's message (any of the five forms above; `[tag]` between the prefix and the text is optional). Anything that does NOT start with one of these prefixes is treated as normal conversation — *not* a suggestion. Mid-run overrides ("don't run X for this branch") still go through the existing user-resolution flow (not this capture path).
2. **Record verbatim** into `improvement_suggestions[]`:
   ```json
   {
     "ts": "<iso8601-now>",
     "target": "<run input>",
     "phase": "<current phase number when the user spoke up>",
     "tag": "<optional, parsed from [brackets]>",
     "text": "<everything after the prefix and optional tag>",
     "applied_at": null,
     "applied_via": null
   }
   ```
3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase X, tag=<tag-or-none>): "<verbatim text>"
   ```
4. **Resume** the current phase from where it was. The capture does NOT alter the current run — it only records the suggestion for future review at the audit and threshold-based aggregation later.

**What this is NOT**:

- **NOT a phase override.** Mid-run logic objections without a trigger prefix go through the user-resolution flow. With a trigger prefix → captured as a long-term improvement idea but the current run still does whatever its phase logic says.
- **NOT auto-applied.** Captured suggestions live in `{{SKILL_PATH}}/run_history.json` for later review. Tier 1 (default): the user manually applies whichever resonate. Future tiers may add tag-based aggregation and threshold-driven proposals; auto-apply is deliberately deferred.
- **NOT a substitute for FAIL counters.** FAIL counters track *what went wrong* (mechanically detected). Suggestions track *what could be better* (user-perceived). They live in different fields and have different lifecycles.

---

## Authoring notes

### Why anywhere-in-run instead of audit-only

In-the-moment capture catches insights that fade by audit time, AND attaches the right phase context automatically (the user is observing phase N when they have the thought, so `phase: N` in the JSON record is mechanically correct rather than recalled).

The trigger-prefix requirement keeps the protocol scoped — if the user types "we should run X" without a prefix, that's a phase-override request (different intent, different handling) rather than a long-term suggestion.

### Why no auto-apply at threshold (yet)

A FAIL has a known mechanical fix ("add this verbatim-quote sentence"). A free-text suggestion has no canonical SKILL.md edit — *how* exactly do we wire "run targeted unit tests" into the test-routing phase? Auto-apply would need a remediation_hint per suggestion, and asking the user for that at suggestion time adds friction at exactly the wrong moment.

Capture-only (Tier 1) is the right ceiling until you have ~10–20 entries showing whether suggestions cluster naturally into tags. Promote to threshold-based proposals (Tier 2) once the data justifies it; reserve auto-apply (Tier 3) for cases where Tier 2 has proven the categorization works reliably.

### When to opt out of this block

Skills where suggestion capture doesn't fit:
- Pure interview / Q&A skills with no execution loop (the user is co-authoring the artifact, not observing a run).
- Skills with a single domain phase (no in-run context to capture).
- One-shot generators where the artifact is the entire output (no audit-style review window).

For all other self-learning skills, default to including this block.
