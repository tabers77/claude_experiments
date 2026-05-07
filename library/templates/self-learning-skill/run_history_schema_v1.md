# `run_history.json` schema (v1)

The persistent ledger backing a self-learning skill. One file per skill, located at the skill's root (`skills/<skill-name>/run_history.json` in plugin form, or `.claude/skills/<skill-name>/run_history.json` in project form). Read+written by the skill's audit and ledger phases. Manual editing is supported.

## Top-level shape

```json
{
  "version": 1,
  "fail_counters": { },
  "runs": [ ],
  "friction_log": [ ]
}
```

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
  "phases_failed": ["<tag>", ...]
}
```

Used to compute trends ("what fraction of runs aborted?") and correlate FAIL tags across targets.

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
  "friction_log": []
}
```
