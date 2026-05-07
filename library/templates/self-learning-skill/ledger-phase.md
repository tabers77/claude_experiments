# Ledger phase template (Phase N)

The standardized **run-history ledger update** that runs as the final phase of every self-learning skill. Drop this into a generated skill as the last phase.

This phase is what makes the skill self-improving. Without it, you have a skill with an audit; with it, you have a skill that gets better over time.

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{N}}` | This phase's number (one higher than the audit phase) | `9` |
| `{{SKILL_PATH}}` | Skill's root path (where `run_history.json` lives) | `skills/shared-bug-gap-fix` |
| `{{TERMINAL_ACTION}}` | The skill's terminal action | `commit` |

---

## Phase {{N}} — Update the run-history ledger

Persist the audit so failure patterns become evidence over time.

1. **Read** `{{SKILL_PATH}}/run_history.json`. Initialize if missing per the schema in `library/templates/self-learning-skill/run_history_schema_v1.md`. Use the seed FAIL rules from that schema doc as the starting `fail_counters`.

2. **Append** the run summary to `runs[]`:
   ```json
   {"ts": "<iso8601>", "target": "<input>", "outcome": "<closed|paused|aborted|in-progress>", "phases_failed": ["<tag>", ...]}
   ```

3. **For each FAIL tag** observed in this run:
   - Increment `fail_counters[<tag>].count` by 1.
   - Append to `fail_counters[<tag>].occurrences[]`: `{ts, target, detail}` where `detail` is a one-line description of the specific occurrence (what command ran, what evidence was missing, what user input was paraphrased — be concrete).
   - If the tag is new, create the entry. Pick `threshold` by phase severity:
     - **Load-bearing phase** → threshold = **1** (fix on first occurrence; the failure defeats a core principle).
     - **Procedural phase** → threshold = **2** (one is noise; two is drift).
     - **Cosmetic phase** → threshold = **5** (low cost; wait for a clear pattern).

4. **Write the file** with the `Write` tool. Stage and commit it as part of the {{TERMINAL_ACTION}} commit if that phase already ran; otherwise leave it unstaged for the next closure to pick up.

5. **Threshold check** — for any counter where `count >= threshold`:
   - Print a **fix proposal** block: the failure pattern, the recommended SKILL.md edit (specific file + line + before/after diff drawn from `remediation_hint`), the tag.
   - **Apply automatically** (Mode B): make the SKILL.md edit. The user reviews the change in their normal commit-review loop.
   - After applying: reset the counter to 0; set `applied_at` to the current timestamp; optionally fill `applied_via` with a one-line description of the structural change made.
   - **Conflict handling**: if multiple tags trip in the same run, apply remediations serially (oldest tag first by `occurrences[0].ts`). Surface conflicts to the user — never silently overwrite a remediation that another tag just wrote.

---

## Authoring notes

### Tolerate manual edits

The skill must tolerate any valid v1 JSON in `run_history.json`. The user is allowed to:
- Hand-edit thresholds when tier judgment changes.
- Reset counters after a manual SKILL.md edit so auto-apply doesn't double-fire.
- Annotate `occurrences[].detail` retrospectively.
- Retire stale tags by setting `applied_at` and leaving `count: 0`.

Never reject the file because a count was changed or a field was added. This is the user's escape hatch.

### Tags are stable forever

Once a tag has occurrences, never rename it. If the failure mode evolves, retire the old tag (stop incrementing, leave `applied_at` set) and introduce a new tag with a different slug. Renaming would silently lose accumulated history and break threshold logic.

### Auto-apply is intentionally aggressive

There is no review queue, no staging area, no approval gate on the remediation itself. The git diff is the safety net — the user catches bad remediations in their normal commit flow. If an auto-applied edit was wrong:
1. Revert the SKILL.md change manually (`git checkout -- SKILL.md`).
2. Hand-edit `run_history.json` to clear `applied_at` and reset `count` if you want the counter to start over, OR leave them set so the system doesn't re-trip on the next run.
3. The next run starts clean.

### `friction_log` is out of scope for this phase

Add `friction_log` entries in the originating domain phase where the friction was experienced. The ledger phase just preserves them on write — it doesn't auto-resolve, doesn't increment counters, doesn't trigger remediation.

### Initialization snippet (when `run_history.json` is missing)

Use this exact structure for a fresh ledger; it includes the universal seed FAIL rules:

See `library/templates/self-learning-skill/run_history_schema_v1.md` → "Initial state" section for the full bootstrap JSON. Copy that as-is on first run; do not improvise the seeds.
