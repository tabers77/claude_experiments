# Audit phase template (Phase N-1)

The standardized **pre-action self-audit** that runs immediately before the terminal action (commit, deploy, doc edit, etc.). Drop this into a generated skill as the second-to-last phase.

The audit is **load-bearing**: it cannot be skipped, and the skill cannot mark phases `pass` without satisfying the FAIL detection rules. The whole point is to produce verbatim, falsifiable evidence — never the skill's interpretation of user intent.

## Placeholders to substitute when copying into a SKILL.md

| Placeholder | Meaning | Example |
|---|---|---|
| `{{N}}` | This phase's number | `8` |
| `{{TERMINAL_ACTION}}` | The skill's terminal action (lowercase) | `commit`, `deploy`, `doc-edit` |
| `{{TERMINAL_ACTION_CAPITALIZED}}` | Same, capitalized for sentence start | `Commit`, `Deploy`, `Doc-edit` |
| `{{APPROVAL_TOKEN}}` | Literal user token required to advance | `audit approved`, `proceed` |
| `{{PHASE_AUDIT_ROWS}}` | One row per domain phase, listing evidence shape | see "Authoring notes" below |
| `{{DOMAIN_FAIL_RULES}}` | Skill-specific FAIL detection rules | see worked example below |

---

## Phase {{N}} — Pre-action self-audit (CHECKPOINT, blocking)

The audit runs **before** the {{TERMINAL_ACTION}}. {{TERMINAL_ACTION_CAPITALIZED}} cannot fire until the user explicitly confirms or corrects every audit row. Goal: verbatim, falsifiable evidence — never the skill's interpretation of user intent.

1. **Walk every phase that ran in this session** and emit a structured block. Each verdict MUST cite **objective evidence**: a tool call observed, a command output, a file diff, or a **literal quote** from the user. **Never paraphrase user input.** If the user said "{{APPROVAL_TOKEN}}" with no per-item resolution, record `user said: "{{APPROVAL_TOKEN}}" (no per-item resolution)` — do NOT invent a justification, do NOT summarise intent.

   ```
   Self-audit for run on <input> at <ts>:
   {{PHASE_AUDIT_ROWS}}
   ```

   Each row format: `- Phase X [pass|FAIL] | <evidence>` where `<evidence>` is a literal command, output snippet, file:line reference, or quoted user input.

2. **FAIL detection rules** — these trigger automatically; the skill cannot mark `pass` without satisfying them:

   **Universal FAIL rules** (every self-learning skill inherits these):
   - **`audit-paraphrased-user-input`** (load-bearing, threshold=1): any audit row that paraphrases user intent rather than quoting verbatim.
   - **`audit-no-explicit-approval-wait`** (procedural, threshold=2): skill advanced past a user-gate phase without observing the literal approval token.
   - **`tool-claim-without-call`** (load-bearing, threshold=1): audit row says "ran X" / "invoked Y" but no corresponding tool call observed in this session.

   **Domain FAIL rules** (specific to this skill):

   {{DOMAIN_FAIL_RULES}}

3. **Show the audit and ask the user to confirm OR correct every row.** The audit is NOT approved on silence or partial answer. The skill must wait for the user to:
   - **confirm** each row as written, OR
   - **dictate corrections** (which the skill applies verbatim and re-displays the audit), OR
   - **mark a row FAIL with a tag** (which the skill records).

4. **Approval gate**: the next phase cannot fire until the user explicitly types `{{APPROVAL_TOKEN}}` (case-insensitive). Silence, "looks good", "ok", "proceed", or partial responses are NOT approval.

---

## Authoring notes

### How to write `PHASE_AUDIT_ROWS`

Map 1:1 to the domain phases of the skill. For each phase, write what evidence shape the audit should display. Example for a fictitious 5-phase data-pipeline skill:

```
- Phase 1     [pass]      | input parsed: <mode> <ID>
- Phase 2     [pass]      | source data verified: <table>:<row-count>
- Phase 3     [pass]      | transform applied: <files-changed>
- Phase 4     [pass]      | validation tests: <test-list>; results: <pass/fail-counts>
- Phase 5     [pass|FAIL] | unresolved items: <N> surfaced / <M> resolved-with-explicit-choice
                            user input verbatim: "<literal quote>"
```

The last line of any row that involved user input MUST be a literal quote, not a paraphrase. This is the single most important convention — it's what triggers `audit-paraphrased-user-input`.

### How to write `DOMAIN_FAIL_RULES`

Each rule needs: tag, tier (load-bearing/procedural/cosmetic), threshold, detection condition. Example from `shared-bug-gap-fix`:

```
- **`7.2-plugin-substitution` FAIL** (load-bearing, threshold=1): no `Skill(skill="claude-library:code-diagnosis", ...)` tool call observed in this session, OR the skill emitted a "diagnosis" narration without an actual Skill call.
- **`7.5-implicit-skip-no-justification` FAIL** (load-bearing, threshold=1): `surfaced > resolved-with-explicit-choice`. Count = (surfaced − resolved).
- **`6-routing-too-coarse-for-trivial-fix` FAIL** (procedural, threshold=2): direct-coverage tests existed (≥1) AND change was trivial (no new control-flow keywords) AND broader tier was run anyway AND broader tier surfaced 0 new failures beyond direct AND broader tier wall-clock > 30s.
```

Detection conditions should be **mechanical** — checkable without judgment. If you can't write the condition as a procedure, the rule isn't ready yet; let it accumulate as a friction-log entry first.

### Common mistakes to avoid

- **Don't conflate audit rows with FAIL rules.** Audit rows describe *what to display*; FAIL rules describe *when to mark pass=FAIL automatically*. A skill can have many phases (rows) but only a few FAIL rules.
- **Don't pre-classify severity in audit rows.** That's the user's job in the resolution gate (if the skill has one). The audit just reports.
- **Don't allow soft approval.** "Looks good" / "ok" / "proceed" must NOT advance the skill. Only the literal `{{APPROVAL_TOKEN}}`. This is enforced by `audit-no-explicit-approval-wait`.
