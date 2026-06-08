---
name: meta-research-checkpoint
description: A cadence-based, suggestion-only research checkpoint that keeps the self-learning machinery current with the industry. Operates at two levels — Level 1 (the meta generator + the self-learning pattern/templates) and Level 2 (each generated self-learning skill) — by orchestrating the repo's existing research skills and aggregating their findings into per-level improvement suggestions. Never auto-edits any skill. Use when you want to check for industry/Claude Code updates relevant to your skills, revalidate stale self-learning skills, or run a periodic research sweep. Keywords research checkpoint industry updates revalidate stale skills freshness level 1 level 2 meta self-learning orchestrate suggestion-only.
---

# Meta — Research Checkpoint

**Purpose**: periodically check the wider ecosystem (new Claude Code capabilities, library/method shifts, overlap drift) for things the self-learning machinery could adopt, and surface them as **suggestions** — at two levels. Level 1 is the meta layer (the generator + the pattern + the templates). Level 2 is each generated self-learning skill. The checkpoint **orchestrates existing skills** rather than re-implementing research, and **never auto-edits** anything.

**Use when**:
- You want a periodic "is any of this stale vs. the industry?" sweep over your self-learning skills.
- The Phase 0 freshness nudge fired on a skill and you want the *active* counterpart — actually do the research and reset the counter.
- You're maintaining the self-learning pattern and want to know what new Claude Code features it could adopt.

**Not for**:
- Auto-applying changes — this skill is suggestion-only. It writes a report and (optionally) observer `suggestions.md` entries; humans decide.
- Level 3 (normal, non-self-learning skills) — explicitly out of scope. The checkpoint targets only the meta layer (L1) and self-learning skills (L2).
- Editing a skill — open its SKILL.md directly, or run the orchestrated skills' own edit flows.

**Load-bearing principle**: the checkpoint NEVER edits a skill's SKILL.md, frontmatter, or logic. Its only writes are (a) `documentation/RESEARCH_CHECKPOINT.md`, (b) appending a `review_log[]` entry + resetting `runs_since_validation` in a researched L2 skill's `run_history.json`, and (c) optionally appending proposals to an L2 skill's observer `suggestions.md`. Anything beyond those three is out of scope.

## Inputs

| Shape | Example | Mode |
|---|---|---|
| level selector | `--level 1`, `--level 2`, `--level all` | which levels to run (default `all`) |
| force flag | `--all` | for L2: research every self-learning skill, not only those due by freshness gate |
| scope filter | `--skill <name>` | restrict L2 to a single named skill |

If the input is none of the above, default to `--level all` with the freshness gate active (no `--all`).

---

## Process

### Step 1 — Resolve scope

1. Parse the level selector (`--level 1|2|all`, default `all`) and flags (`--all`, `--skill <name>`).
2. **Enumerate L2 candidates**: `Glob skills/*/SKILL.md` (and the project/user scopes if relevant) and select those that are self-learning — detect via frontmatter `metadata.pattern: self-learning` OR a sibling `run_history.json`.
3. **Apply the freshness gate for L2** (unless `--all` or `--skill` is given): a skill is **due** when its `validation_freshness` AND-gate trips — `now - last_validated_at >= thresholds.days` AND `runs_since_validation >= thresholds.runs`. Skills not due are listed as "skipped (fresh)" and not researched. `--all` forces every self-learning skill; `--skill <name>` forces exactly one.
4. Print the resolved plan: which levels run, which L2 skills are due vs. fresh, and that the run is **suggestion-only**.

### Step 2 — Level 1: the meta layer

Run only when `--level` is `1` or `all`. Targets:
- `skills/meta-self-learning-skill-gen/SKILL.md`
- the `library/templates/self-learning-skill/*` template set
- `documentation/SELF_LEARNING_SKILLS.md`

Orchestrate the repo's existing research skills (invoke them; cite which one produced each finding). Pass `invocation_mode=composed; parent=meta-research-checkpoint; parent_run_ts=<this run's start>` when invoking any self-learning skill so its freshness/observer phases don't double-fire:
- **`/meta-discover-claude-features`** — new Claude Code capabilities (hook types, skill features, agent/MCP patterns) the self-learning pattern could adopt.
- **`/meta-skill-audit`** — overlap/redundancy across the meta layer and other skills.
- **`/quality-strategic-advisor`** — pattern-level ideas (what the self-learning pattern could *become*).

Only fall back to a raw web search for gaps the orchestrated skills don't cover. Aggregate findings into an **L1 suggestions** list, each tagged with its source skill and a concrete proposed change (file + what to add/alter).

### Step 3 — Level 2: each due self-learning skill

Run only when `--level` is `2` or `all`, for each due (or forced) L2 skill. For each skill, orchestrate (composed invocation, as above):
- **`/meta-discover-claude-features`** scoped to the skill's domain — capabilities relevant to *that* skill.
- **`/quality-upgrade-advisor`** scoped to the skill's domain — stale libraries/methods/patterns in the skill's subject area.
- **`/meta-skill-audit`** — overlap of this skill vs. its peers.

Aggregate per-skill findings into an **L2 suggestions** block tagged with source skill + proposed change.

### Step 4 — Close the freshness loop (L2 only)

For each L2 skill actually researched in Step 3, update its `run_history.json` — this is the **active counterpart** to the passive Phase 0 freshness nudge:
1. Append a `validation_freshness.review_log[]` entry: `{ts, type: "research", summary: "<one line — what was checked, what surfaced>", outcome: "no-change | skill-edited | skill-retired | other"}`. (Outcome is `no-change` unless a human later acts on a suggestion — the checkpoint itself never edits the skill.)
2. Set `last_validated_at` and `last_research_at` to now.
3. Reset `runs_since_validation` to `0`.

These are the ONLY writes the checkpoint makes to a skill's `run_history.json`. Never touch `fail_counters`, `runs[]`, `thresholds`, or any other field. If the skill has no `validation_freshness` block (freshness opted out), skip the reset and note it in the report.

### Step 5 — Write the report

Append a dated section to `documentation/RESEARCH_CHECKPOINT.md` (create it if missing; the file is **append-only** — never rewrite prior sections):

```markdown
## <iso8601-date> — Research checkpoint (levels: <1|2|all>)

### Level 1 — meta layer
- [source: <skill>] <finding> → proposed: <concrete change to file/section>
- ...

### Level 2 — self-learning skills
#### <skill-name> (due: <yes/forced>, freshness reset: <yes/no>)
- [source: <skill>] <finding> → proposed: <concrete change>
- ...

#### <skill-name-2> ...

### Skipped (fresh, not due)
- <skill-name> — last validated <date>, <runs_since_validation> runs since
```

For each L2 skill that has an **observer** (`suggestions.md` present at its root), optionally also append the proposal to that skill's `suggestions.md` queue (status `unreviewed`) so it flows through the existing human-review path. Do this only when the finding maps to a concrete SKILL.md edit; cite the checkpoint run date as the source.

### Step 6 — Summarize and stop

Print a one-block summary: levels run, L1 finding count, per-L2-skill finding counts, which skills had their freshness counter reset, and the report path. Remind the user that **every finding is a suggestion** — nothing was applied.

---

## Cadence

- **Primary: on-demand** — `/meta-research-checkpoint [--level 1|2|all] [--all] [--skill <name>]`.
- **Optional scheduled cadence** via the `schedule` skill (cron). Documented, not baked in — e.g. a monthly `--level all` run. The freshness AND-gate already prevents over-researching fresh skills, so a scheduled run is cheap when nothing is due.

## Edge cases

1. **No self-learning skills exist yet** — L2 is a no-op; run L1 only and say so.
2. **Nothing is due** (and no `--all`/`--skill`) — print "all skills fresh" with the next-due estimate per skill; still allow L1 to run.
3. **An orchestrated skill is unavailable** — note it in the report and continue with the others; never block the whole checkpoint on one missing skill.
4. **A researched skill opted out of freshness** — skip the Step 4 counter reset and note it; the report still records findings.
5. **`RESEARCH_CHECKPOINT.md` was hand-edited** — tolerate it; only ever append a new dated section.

## Out of scope

- **Level 3 (normal skills)** — by design. Only the meta layer (L1) and self-learning skills (L2) are in scope.
- **Auto-applying any suggestion** — humans review and apply.
- **Editing SKILL.md / frontmatter / templates** — the checkpoint researches and reports; it does not change skills.

## Plugin skills composed by this skill

| Skill | Level | Trigger |
|---|---|---|
| `claude-library:meta-discover-claude-features` | L1 + L2 | New Claude Code capabilities relevant to the pattern (L1) or a skill's domain (L2) |
| `claude-library:meta-skill-audit` | L1 + L2 | Overlap/redundancy check |
| `claude-library:quality-strategic-advisor` | L1 | Pattern-level capability ideas |
| `claude-library:quality-upgrade-advisor` | L2 | Stale libraries/methods/patterns in a skill's domain |

## Usage

```
/meta-research-checkpoint                      # all levels; L2 gated by freshness
/meta-research-checkpoint --level 1            # just the meta layer
/meta-research-checkpoint --level 2 --all      # every self-learning skill, ignore freshness gate
/meta-research-checkpoint --skill shared-bug-gap-fix   # one skill, forced
```
