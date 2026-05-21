# `run_history.json` schema (v1)

The persistent ledger backing a self-learning skill. One file per skill, located at the skill's root (`skills/<skill-name>/run_history.json` in plugin form, or `.claude/skills/<skill-name>/run_history.json` in project form). Read+written by the skill's audit and ledger phases. Manual editing is supported.

## Top-level shape

```json
{
  "version": 1,
  "fail_counters": { },
  "runs": [ ],
  "friction_log": [ ],
  "improvement_suggestions": [ ],
  "validation_freshness": { }
}
```

The `improvement_suggestions` array is OPTIONAL — it appears only when the skill includes the Mid-run suggestion capture block (see `library/templates/self-learning-skill/suggestion-capture.md`). Skills without that block omit the field entirely; readers must tolerate either shape.

The `validation_freshness` object is OPTIONAL — it appears only when the skill includes the Phase 0 freshness check (see `library/templates/self-learning-skill/freshness-phase.md`). Skills without that phase omit the field entirely; readers must tolerate either shape.

## `version` (integer)

Schema version. Bump only on breaking changes. Skills must refuse to write a file whose version they don't recognize — never silently coerce.

## `fail_counters` (object, keyed by stable tag)

Each entry tracks one categorical failure mode.

| Field | Type | Meaning |
|---|---|---|
| `count` | int | Current consecutive-occurrence count. Reset to 0 on auto-apply. |
| `threshold` | int | Trip threshold. When `count >= threshold`, remediation fires. |
| `phase` | string | Phase identifier where this failure applies (e.g. `"7.5"`, `"audit"`). |
| `description` | string | Human-readable failure mode description. |
| `occurrences` | array | Append-only log of `{ts, target, detail}`. Trim to last 20 to bound size. |
| `remediation_hint` | string | The recommended SKILL.md edit — specific enough that auto-apply locates file + line + before/after. |
| `applied_at` | ISO 8601 string \| null | Last auto-apply timestamp. Null until first trip. |
| `applied_via` | string (optional) | Free-text note of the structural change made when the remediation was last applied. |

### Tag naming convention

`<phase>-<failure-mode-slug>`, lowercase-hyphenated.

Examples (from `shared-bug-gap-fix`):
- `7.5-implicit-skip-no-justification`
- `9-paraphrased-user-input`
- `6-routing-too-coarse-for-trivial-fix`

Tags are **stable forever**. Once a tag has occurrences, never rename it. If the failure mode evolves, retire the old tag (set `applied_at`, leave `count: 0`, stop incrementing) and introduce a new tag with a different slug.

### Threshold tiers

Pick by what the failure defeats:

| Tier | Threshold | Use when... |
|---|---|---|
| **Load-bearing** | **1** | Failure violates the skill's core principle. Examples: audit honesty, no-new-bugs sweep skipped, approval gate bypassed, reproduction check skipped. |
| **Procedural** | **2** | One occurrence may be noise; two is drift. Examples: plan-deviation, scope-too-coarse, attack-order not cleaned, branch-prefix wrong. |
| **Cosmetic** | **5** | Low cost when missed; wait for a clear pattern. Examples: time-estimate accuracy, optional-skim phase missed. |

When in doubt, pick the stricter tier — false trips are recoverable via `git revert`; missed trips compound.

## `runs` (array)

Append-only log, one entry per invocation:

```json
{
  "ts": "2026-05-07T09:00:00Z",
  "target": "<input>",
  "outcome": "closed | paused | aborted | in-progress",
  "phases_failed": ["<tag>", ...],
  "started_at": "<iso8601>",
  "ended_at": "<iso8601>",
  "duration_seconds": 142,
  "phase_durations": {
    "1": 3,
    "2": 14,
    "3": 47,
    "...": "..."
  },
  "quality_derived": "clean | partial | failed | incomplete"
}
```

Used to compute trends ("what fraction of runs aborted?"), correlate FAIL tags across targets, and feed the observer's efficiency-detection logic.

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO 8601 | Wall-clock timestamp when the run was recorded by the ledger. Kept for backward compatibility. Identical to `ended_at` for new runs. |
| `target` | string | Verbatim run input. |
| `outcome` | enum | `closed` (terminal action fired), `paused` (user paused mid-flow), `aborted` (skill stopped on error or user abort), `in-progress` (rare — only when the ledger writes mid-run for crash recovery). |
| `phases_failed` | array | List of FAIL tags tripped during this run. |
| `started_at` | ISO 8601 | OPTIONAL. Timestamp when Phase 0 (or Phase 1 if no Phase 0) first observed input. Absent on pre-instrumentation runs. |
| `ended_at` | ISO 8601 | OPTIONAL. Timestamp when the ledger phase wrote this entry. Absent on pre-instrumentation runs. |
| `duration_seconds` | int | OPTIONAL. `ended_at - started_at` in seconds. Absent on pre-instrumentation runs. |
| `phase_durations` | object | OPTIONAL. Map of phase id (string) → seconds elapsed in that phase. Each phase stamps its own duration as it exits. Absent on pre-instrumentation runs. |
| `quality_derived` | enum | OPTIONAL. Roll-up of `outcome` + `phases_failed` + sentiment-of-this-run's-suggestions. See "Quality derivation" below. Absent on pre-instrumentation runs. |

### Quality derivation

`quality_derived` is computed by the ledger phase from existing signals at run-end. No new user prompt is required:

| Value | Condition |
|---|---|
| `clean` | `outcome == "closed"` AND `phases_failed[]` is empty AND no `improvement_suggestions[]` entry with `sentiment == "negative"` exists whose `target` equals this run's `target` AND whose `ts` falls within `[started_at, ended_at]`. |
| `partial` | `outcome == "closed"` AND (`phases_failed[]` non-empty OR at least one matching negative suggestion exists). |
| `failed` | `outcome == "aborted"`. |
| `incomplete` | `outcome == "paused"` OR `outcome == "in-progress"`. |

The observer phase uses `quality_derived` as the denominator when comparing wall-clock durations across same-shape inputs. Runs lacking `quality_derived` (pre-instrumentation) are excluded from the comparison — never silently treated as `clean`.

### Backward compatibility

All five new fields (`started_at`, `ended_at`, `duration_seconds`, `phase_durations`, `quality_derived`) are OPTIONAL. Readers MUST tolerate their absence on any run. Pre-instrumentation runs simply don't participate in efficiency analysis — they still count for FAIL trends and friction logs.

## `friction_log` (array)

Append-only log of recurring pain points that **aren't** structural failures (environment workarounds, tooling limitations, etc.). Friction items don't auto-apply — they sit in the log until manually resolved:

```json
{
  "ts": "<iso8601>",
  "target": "<input>",
  "phase": "<phase>",
  "detail": "<short description>",
  "mitigation_options": ["<option>", "..."],
  "resolved_at": "<iso8601> | null",
  "resolved_via": "<description> | null"
}
```

When resolved, fill `resolved_at` + `resolved_via` rather than deleting the entry. The historical record is the value — it tells future-you (or another contributor) what workarounds were tried and which one stuck.

## `improvement_suggestions` (array, OPTIONAL)

Present only when the skill includes the Mid-run suggestion capture block (see `library/templates/self-learning-skill/suggestion-capture.md`). Append-only log of user-proposed improvements to the skill itself, captured during runs via trigger prefixes (`suggestion:`, `improvement:`, etc.) plus any final-call entries added during the audit:

```json
{
  "ts": "<iso8601>",
  "target": "<run input>",
  "phase": "<current phase number when the user spoke up, or 'audit' for final-call entries>",
  "tag": "<optional, parsed from [brackets] in the user's message; null if absent>",
  "text": "<verbatim text after the prefix and optional [tag]>",
  "sentiment": "<negative | aspirational | neutral>",
  "applied_at": "<iso8601 | null>",
  "applied_via": "<description of SKILL.md change | null>"
}
```

`sentiment` is OPTIONAL on legacy entries (suggestions captured before sentiment was introduced). When absent, treat as `neutral` — never silently coerce to `negative`. New entries written by skills that include the suggestion-capture block ALWAYS include sentiment. See `library/templates/self-learning-skill/suggestion-capture.md` for the keyword heuristic.

`sentiment` feeds `runs[].quality_derived` (see the "runs" section above): a run is `partial` rather than `clean` when at least one negative-sentiment suggestion was captured during its window. This is the load-bearing link between user-perceived quality and the observer's efficiency-detection logic.

**Lifecycle (Tier 1 — capture only)**:
- Suggestions are recorded verbatim. The current run is NOT altered by capture — the skill continues whatever phase logic dictates.
- `applied_at` and `applied_via` start as `null`; the user fills them in manually after applying a SKILL.md edit inspired by one or more suggestions.
- The array is append-only: never overwrite, never drop entries on `Write`. Manual edits to set `applied_at` are supported and expected.

**Future tiers (deferred)**:
- Tier 2 — when entries with the same `tag` reach a threshold (default 3), surface a fix-proposal block at run end and let the user manually apply.
- Tier 3 — auto-apply at threshold, mirroring `fail_counters` Mode B. Requires a per-suggestion `remediation_hint`, which is friction at the wrong moment; reserved for cases where Tier 2 has proven categorization works.

Skills WITHOUT the suggestion-capture block omit this field entirely. Readers must tolerate either shape (present or absent) — never reject a v1 JSON because `improvement_suggestions` is missing.

## `validation_freshness` (object, OPTIONAL)

Present only when the skill includes the Phase 0 freshness check (see `library/templates/self-learning-skill/freshness-phase.md`). Tracks how long it has been since the skill was last validated — i.e., since the user last ran an improvement-research pass + an overlap-vs-other-skills check — so the skill can nudge the user to revalidate when it has accumulated significant usage without a freshness review.

```json
{
  "created_at": "<iso8601>",
  "last_validated_at": "<iso8601>",
  "last_research_at": "<iso8601> | null",
  "last_overlap_check_at": "<iso8601> | null",
  "runs_since_validation": 0,
  "thresholds": {
    "runs": 10,
    "days": 21
  },
  "review_log": [
    {
      "ts": "<iso8601>",
      "type": "research | overlap | both",
      "summary": "<one line — what was checked, what changed>",
      "outcome": "no-change | skill-edited | skill-retired | other"
    }
  ]
}
```

| Field | Type | Meaning |
|---|---|---|
| `created_at` | ISO 8601 | Timestamp when this block was first written (typically first run of the freshness phase). |
| `last_validated_at` | ISO 8601 | Timestamp of the most recent completed validation (research + overlap). Bumped when the user appends a `review_log[]` entry. |
| `last_research_at` | ISO 8601 \| null | Timestamp of the most recent improvement-research pass (e.g. `/meta-discover-claude-features` on the skill's domain). Null until first pass. |
| `last_overlap_check_at` | ISO 8601 \| null | Timestamp of the most recent overlap check vs. other skills (e.g. `/meta-skill-audit`). Null until first check. |
| `runs_since_validation` | int | Monotonic counter incremented by the ledger phase every run. Reset to 0 when the user appends a `review_log[]` entry and updates `last_validated_at`. |
| `thresholds.runs` | int | Run count above which (combined with the days threshold) the freshness phase nudges. Default 10. |
| `thresholds.days` | int | Days elapsed above which (combined with the runs threshold) the freshness phase nudges. Default 21 (≈3 weeks). |
| `review_log[]` | array | Append-only audit of validation events. Each entry records what was checked and what changed. |

### Nudge condition

The Phase 0 freshness check prints the nudge only when **BOTH** are true (AND, not OR):
- `now - last_validated_at >= thresholds.days`
- `runs_since_validation >= thresholds.runs`

This avoids nudging cold skills (lots of days but no usage → not load-bearing) and avoids nudging hot-but-recent skills (lots of runs but already validated last week).

### Manual editing

The user is expected to hand-edit this block:
- After running `/meta-discover-claude-features` and `/meta-skill-audit`, append a `review_log[]` entry, set `last_validated_at` (and `last_research_at` / `last_overlap_check_at` as applicable), and reset `runs_since_validation` to 0.
- Adjust `thresholds.runs` / `thresholds.days` per skill cadence — lower for very hot skills, higher for skills with stable surfaces.
- Append a `review_log[]` entry with `outcome: skill-retired` when retiring a skill, so future archaeologists understand why the counter froze.

Skills WITHOUT the freshness phase omit this block entirely. Readers must tolerate either shape — never reject a v1 JSON because `validation_freshness` is missing.

## Auto-apply behavior (Mode B)

When a counter reaches `count >= threshold`:

1. Emit a fix-proposal block: the failure pattern, the recommended edit (file + line + before/after diff drawn from `remediation_hint`), the tag.
2. Apply the edit automatically — the user reviews it in their normal commit-review loop. The git diff is the safety net.
3. Reset `count` to 0; set `applied_at` to the current timestamp; optionally fill `applied_via` with a one-line description of the structural change.

If the same failure recurs after auto-apply, the counter starts climbing again — possibly indicating the remediation missed the root cause. Repeated trips on the same tag are a signal to manually inspect.

### Conflict handling

When multiple tags trip in the same run, apply remediations **serially, oldest tag first** (by `occurrences[0].ts`). Surface conflicts to the user — never silently overwrite a remediation that another tag just wrote in the same run.

## Manual editing

Hand-editing is supported and expected:
- Adjust thresholds when tier judgment changes.
- Reset counters after a manual SKILL.md edit so auto-apply doesn't double-fire.
- Annotate `occurrences[].detail` for retrospective context.
- Retire stale tags by setting `applied_at` and leaving `count: 0`.

The skill must tolerate any valid v1 JSON — never reject the file because the user added a field, changed a count, or annotated a record.

## Initial state

For a freshly-generated skill, initialize with the **universal seed FAIL rules** that apply to any skill consuming user input via tool calls (see `documentation/SELF_LEARNING_SKILLS.md` for the canonical list). Domain-specific tags accumulate from real runs — start the rest empty.

```json
{
  "version": 1,
  "fail_counters": {
    "audit-paraphrased-user-input": {
      "count": 0,
      "threshold": 1,
      "phase": "audit",
      "description": "Audit row paraphrased user intent rather than quoting verbatim. Load-bearing honesty failure.",
      "occurrences": [],
      "remediation_hint": "Tighten the audit phase: 'Each verdict MUST cite objective evidence — a tool call observed, a command output, a file diff, or a literal quote from the user. Never paraphrase user input.' Add explicit FAIL detection for any audit row that paraphrases rather than quotes verbatim.",
      "applied_at": null
    },
    "audit-no-explicit-approval-wait": {
      "count": 0,
      "threshold": 2,
      "phase": "audit",
      "description": "Skill advanced past a user-gate phase without observing the literal approval token.",
      "occurrences": [],
      "remediation_hint": "Add an explicit wait-for-token gate at the audit-to-terminal-action boundary. Silence, 'looks good', 'ok', 'proceed' do NOT count as approval.",
      "applied_at": null
    },
    "tool-claim-without-call": {
      "count": 0,
      "threshold": 1,
      "phase": "any",
      "description": "SKILL.md text claimed a tool/skill ran but no corresponding tool call was observed in the session.",
      "occurrences": [],
      "remediation_hint": "Audit phase MUST verify the actual tool-call trace, not narration. Mark FAIL when the audit row says 'invoked X' but no Skill/Bash/Read call for X exists in the session.",
      "applied_at": null
    }
  },
  "runs": [],
  "friction_log": [],
  "improvement_suggestions": [],
  "validation_freshness": {
    "created_at": "<iso8601 at generation time>",
    "last_validated_at": "<iso8601 at generation time>",
    "last_research_at": null,
    "last_overlap_check_at": null,
    "runs_since_validation": 0,
    "thresholds": {
      "runs": 10,
      "days": 21
    },
    "review_log": []
  }
}
```

Omit the trailing `"improvement_suggestions": []` line when the generated skill opts OUT of the Mid-run suggestion capture block. The default for `meta-self-learning-skill-gen` is to include it; opt-out is reserved for skills that don't fit the pattern (single-phase, pure-interview, one-shot generators).

Omit the trailing `"validation_freshness": { ... }` block when the generated skill opts OUT of the Phase 0 freshness check. The default for `meta-self-learning-skill-gen` is to include it (every skill benefits from periodic revalidation); opt-out is reserved for skills with deliberately frozen surfaces. When both `improvement_suggestions` and `validation_freshness` are omitted, also drop the trailing comma from `friction_log` so the JSON stays valid.
