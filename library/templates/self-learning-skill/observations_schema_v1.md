# `observations.json` schema (v1)

The persistent ledger backing the **observer phase** of a self-learning skill. One file per skill, located at the skill's root (`skills/<skill-name>/observations.json` in plugin form, or `.claude/skills/<skill-name>/observations.json` in project form). Read+written **only by the observer phase**. Manual editing is supported.

This file is **separate from `run_history.json`** by design — different vantage, different lifecycle, different writer. The audit and ledger phases do NOT touch this file.

## Top-level shape

```json
{
  "version": 1,
  "observations": [ ],
  "review_log": [ ]
}
```

## `version` (integer)

Schema version. Bump only on breaking changes. Skills must refuse to write a file whose version they don't recognize — never silently coerce.

## `observations` (array, append-only)

One entry per qualitative signal the observer recorded. Append-only — never overwrite or drop entries on `Write`. Manual deletion is permitted (user housekeeping); observer-driven deletion is not.

```json
{
  "ts": "<iso8601>",
  "run_ref": "<ts of the matching runs[] entry in run_history.json>",
  "target": "<run input>",
  "category": "<slug — see Categories below>",
  "_theme_slug": "<OPTIONAL sub-theme slug — see _theme_slug below>",
  "phase": "<phase number where the signal appeared, or 'cross-phase'>",
  "evidence": "<verbatim quote / observed event — never paraphrased>",
  "interpretation": "<one-line reasoning for why this signal matters>",
  "proposed_audit_tag": "<optional new FAIL tag the audit could track, or null>"
}
```

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO 8601 string | When the observation was recorded (observer-phase wall-clock). |
| `run_ref` | ISO 8601 string | The `ts` of the corresponding `runs[]` entry in `run_history.json`. Lets the observer cross-reference observations with audit outcomes for the same run. |
| `target` | string | Same as the run's `target` field — duplicated here for searchability. |
| `category` | string | Slug from the standard categories table (extend as needed). Stable forever — see "Category naming" below. |
| `_theme_slug` | string \| undefined | OPTIONAL. Underscore-prefixed metadata field consumed by the observer's theme-similarity check. Identifies the underlying sub-theme within a category, since a single category often contains multiple distinct themes (e.g., `user_friction` covering both `gate-token-bypass` and `branch-prefix-override`). See "_theme_slug naming" below. |
| `phase` | string | Phase number (e.g. `"4"`, `"7"`, `"audit"`) or `"cross-phase"` when the signal spans multiple phases. |
| `evidence` | string | Verbatim quote or observed event. NEVER paraphrased. Same rule the audit enforces. |
| `interpretation` | string | Why this signal matters. One line. The observer's reasoning, not the user's. |
| `proposed_audit_tag` | string \| null | Optional. If the observer thinks a new mechanical FAIL tag could cover this signal, name it here (`<phase>-<failure-mode-slug>` convention). Null when the signal is qualitative-only. |

### `_theme_slug` naming

Slug format: short, lowercase-hyphenated. The leading underscore signals "metadata, not strict schema" — readers MUST tolerate its presence or absence on any observation.

The slug identifies the **underlying sub-theme** within the parent `category`. Why it matters: the observer's clustering pass groups observations by category for threshold checks, but a single category often contains multiple distinct themes that should NOT cluster together. Example: `user_friction` could span "gate-token-bypass" (user prefers structured UI over literal tokens) and "branch-prefix-override" (user prefers their own working branch over the skill's default) — both legitimately `user_friction`, but each deserves its own threshold count and its own SKILL.md proposal.

Conventions:
- **Stable forever within a skill.** Once observations reference a `_theme_slug`, never rename it. If the meaning evolves, retire and replace with a different slug — same rule as `fail_counters` tags.
- **Optional but recommended.** Observations without `_theme_slug` are clustered using the parent `category` only. The theme-similarity check in observer-phase.md step 4 falls back to category when sub-themes aren't tagged.
- **Length and shape**: keep slugs short and intent-revealing (e.g. `dev-stack-staleness`, `tracker-closure-drift`, `phase-7-findings-need-severity-and-provenance`).
- **No coordination across skills.** `_theme_slug` is per-skill; the same slug in two skills can mean unrelated things.

### Category naming

Slug format: short, lowercase, snake_case. **Tags are stable forever** — once an observation references a category, never rename it. If the meaning evolves, retire the old slug (stop using it) and introduce a new one.

Standard categories (extend per skill):

| Slug | Captures |
|---|---|
| `user_friction` | re-asked questions, repeated corrections, "no, I meant", visible frustration |
| `redundant_phase` | phase Y duplicates phase X's output; user explicitly skipped a phase |
| `scope_drift` | skill ventured outside its frontmatter `description` |
| `missing_audit_category` | a recurring qualitative concern with no FAIL tag covering it |
| `dev_env_friction` | environmental setup pain that recurs across runs |
| `output_format_quality` | UX-only signal: format/readability of the skill's output |
| `cross_phase_redundancy` | two phases share evidence the user only had to provide once |
| `boundary_violation` | a domain phase referenced or used content from `observations.json` / `suggestions.md` (which it must not read) — the post-run capture path for leaks the boundary callout failed to prevent |

## `review_log` (array, append-only)

One entry per **clustering-pass** that wrote (or attempted to write) a proposal to `suggestions.md`. Append-only.

```json
{
  "ts": "<iso8601>",
  "trigger": "threshold | manual",
  "clustered_theme": "<short description>",
  "category": "<the category slug that tripped>",
  "observations_referenced": ["<ts1>", "<ts2>", "<ts3>"],
  "suggestion_written_to": "<path to suggestions.md>",
  "applied_at": "<iso8601 | null>",
  "applied_via": "<description | null>"
}
```

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO 8601 string | When the clustering pass ran. |
| `trigger` | `"threshold"` \| `"manual"` | `threshold` = automatic at `{{CLUSTER_THRESHOLD}}`; `manual` = user invoked an explicit review. |
| `clustered_theme` | string | The theme the observer summarized from the clustered observations. |
| `category` | string | The category slug that hit threshold. |
| `observations_referenced` | array of strings | The `ts` values of the observations clustered into this proposal. Used to mark them as "addressed" so they don't re-cluster on the next run. |
| `suggestion_written_to` | string | Path to the `suggestions.md` file (relative to repo root) where the proposal was appended. |
| `applied_at` | ISO 8601 string \| null | When the user applied the proposal. Null until the user manually fills it in after editing the skill. |
| `applied_via` | string \| null | One-line description of the structural change made when the proposal was applied. Null until applied. |

### How `applied_at` interacts with future clustering

When deciding whether a category has hit threshold for a *new* clustering pass, the observer counts only observations whose `ts` does NOT appear in any prior `review_log[].observations_referenced` entry that has `applied_at != null`. This prevents the same theme from re-clustering after a proposal has been applied.

If a proposal was written but `applied_at` is still null (user hasn't reviewed yet), do NOT trigger a fresh clustering pass for the same category — wait. One unreviewed proposal per category is the limit; otherwise `suggestions.md` becomes noisy.

## Auto-apply behavior

**There is none.** The observer is suggestion-only. `suggestions.md` is the human review queue; the user manually flips `Status: unreviewed` to `Status: applied` and fills in `applied_at` / `applied_via` in `observations.json`.

This is a deliberate asymmetry with `run_history.json`'s Mode B auto-apply:

| Aspect | `run_history.json` audit | `observations.json` observer |
|---|---|---|
| Detection | Mechanical (deterministic FAIL rules) | Qualitative (LLM judgment) |
| Confidence | High (rule fires only when condition holds) | Lower (interpretation can be wrong) |
| Action | Auto-edit `SKILL.md`; git diff is review | Write proposal to `suggestions.md`; user reviews |
| Rollback | `git revert` | Mark `Status: dismissed` |

Auto-apply for observer-derived proposals is deliberately deferred. If the observer becomes consistently right after many runs, a Tier 2 promotion (manually-applied at threshold) or Tier 3 (auto-applied at higher threshold) can be considered — mirroring the path `improvement_suggestions[]` capture takes.

## Manual editing

Hand-editing is supported and expected:
- Mark a `review_log[]` entry as applied (`applied_at`, `applied_via`).
- Delete observations the user disagrees with or considers stale (housekeeping).
- Add new categories to the table by simply using a new slug — observer adapts.
- Annotate `interpretation` retrospectively for context.

The observer must tolerate any valid v1 JSON — never reject the file because the user added a field or annotated a record.

## Initial state

For a freshly-generated skill that includes the observer phase, initialize with:

```json
{
  "version": 1,
  "observations": [],
  "review_log": []
}
```

No seed entries — the observer accumulates from real runs. There is no equivalent of the audit's "universal seed FAIL rules" because qualitative categories are inherently contextual.

## Companion file: `suggestions.md`

When a clustering pass trips, the observer appends a section to `{{SKILL_PATH}}/suggestions.md`. This file is freeform markdown, human-readable, human-editable. Each section follows this shape:

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

The user reviews each section, flips `Status: unreviewed` to `applied` or `dismissed`, and updates `applied_at` / `applied_via` in the matching `review_log[]` entry of `observations.json`.

`suggestions.md` is append-only by the observer; the user may edit any section freely.
