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

0. **Ownership rule (single source of truth)**: when this skill is invoked with `invocation_mode=composed`, the suggestion still gets captured **only into the deepest active skill's `improvement_suggestions[]`** — i.e. THIS skill's file, not the parent's. The parent's ledger phase looks up child suggestions cross-file at `quality_derived` computation time (see `ledger-phase.md` → "Cross-skill lookup"). Never duplicate a suggestion across two skill files; storage redundancy makes manual edits ambiguous.

   The captured entry records `parent` and `parent_run_ts` (when composed) so the parent can correlate it back to the right parent run. When standalone, both fields are null.

1. **Detect the prefix** at the start of the user's message (any of the five forms above; `[tag]` between the prefix and the text is optional). Anything that does NOT start with one of these prefixes is treated as normal conversation — *not* a suggestion. Mid-run overrides ("don't run X for this branch") still go through the existing user-resolution flow (not this capture path).
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

   `parent` and `parent_run_ts` are populated from the same args the ledger phase parses for `invocation_mode`. Both null on standalone runs. Legacy entries without these fields are treated as standalone.

   **Sentiment classification** — apply this keyword heuristic at capture time (case-insensitive substring match on the suggestion text). The classification is the single best signal we have for "did this run actually achieve its objective?" without prompting the user explicitly:

   | Sentiment | Trigger keywords (any match wins) | What it means |
   |---|---|---|
   | `negative` | `broken`, `wrong`, `incorrect`, `missed`, `failed`, `bug`, `doesn't`, `does not`, `should not`, `shouldn't`, `regression`, `flaw`, `error`, `mistake` | User is flagging a problem with this run — the skill produced a bad outcome. Counts against `quality_derived`. |
   | `aspirational` | `would be nice`, `consider`, `could also`, `enhancement`, `add`, `nice to have`, `idea:`, `it would be cool`, `we should also`, `extend`, `support` | User is suggesting an enhancement — the skill did fine but could grow. Does NOT count against `quality_derived`. |
   | `neutral` | none of the above match, OR matches in both lists | Ambiguous. Default fallback. Does NOT count against `quality_derived`. |

   Resolution rule: if both lists match, classify as `neutral` (cancels out). If neither matches, classify as `neutral` too. **Negative wins only when no aspirational keyword also matches**, so the heuristic stays conservative — better to miss a quality signal than to fabricate one.

   The user may hand-edit `sentiment` in `run_history.json` later if the heuristic misclassified. The classification is recorded once at capture and never re-evaluated by the skill.

3. **Acknowledge** in one line:
   ```
   ✓ suggestion captured (phase X, tag=<tag-or-none>, sentiment=<negative|aspirational|neutral>): "<verbatim text>"
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
