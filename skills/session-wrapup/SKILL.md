---
name: session-wrapup
description: Close out a coding session cleanly. Git-driven — detects what changed, auto-fixes stale docs, updates your implementation plan with completed items and next steps, and checks for uncommitted work.
---

# Skill: session-wrapup

**Purpose**: Close out a coding session before switching projects — record progress, sync docs, define next steps.

**Use when**:
- You're done working on a project and about to switch to another
- You want a clean handoff for your future self (or Claude)
- End of day / end of session wrap-up

**Relationship to other skills**:
- `/planning-impl-plan` **opens** a work session (design the plan)
- `/session-wrapup` **closes** a work session (record progress, sync docs, set next steps)
- Calls `/meta-sync-references` internally for doc-sync (no duplication)

---

## Process

### Step 1: Locate the Implementation Plan

**Ask the user**: "Which file is your implementation/plan file?" and offer common options:
- A path they provide (e.g., `documentation/IMPLEMENTATION_PLAN.md`, `TODO.md`, `PLAN.md`)
- Auto-detect: search for files matching common names (`*PLAN*`, `*TODO*`, `*IMPLEMENTATION*`, `*ROADMAP*`) in `documentation/` and repo root
- Create a new one

If the user provides a file path, use it. If auto-detect finds candidates, present them for selection. Store the chosen path as **plan_file**.

**Read the plan file** (if it exists) and extract:
- **Planned steps** — any checklist items (`- [ ]`, `- [x]`), numbered steps, or task descriptions
- **Previous session entries** — any prior wrap-up sections
- **Overall goals** — the high-level objective described in the plan

Store this as the **plan state** for cross-referencing in later steps.

### Step 2: Git Change Detection

Use git to understand what happened this session — no full repo scan.

Run these commands and capture the output:

```bash
# What's been committed (since last session or on this branch)
git log --oneline --since="8 hours ago"
# If no recent commits, fall back to: git log --oneline -10

# What's currently changed but not committed
git status

# Detailed diff of uncommitted changes
git diff
git diff --staged
```

Store the results as the **session delta**.

### Step 3: Uncommitted Work Check

If `git status` shows uncommitted changes:

1. **List the uncommitted files** with a brief summary of what changed in each
2. **Ask the user**: "You have uncommitted changes. Would you like to commit before wrapping up?"
3. If yes — help them commit (suggest a message based on the diff)
4. If no — note the uncommitted work in the session summary so it's not lost

### Step 4: Cross-Reference Plan vs Changes

This is the core step. Compare the **plan state** (from Step 1) against the **session delta** (from Step 2).

#### 4a: Mark completed plan items
For each planned step/task in the plan file:
- Check if the git changes (commits + diffs) address that item
- If yes → mark it as completed (`- [x]`) and note the evidence (commit hash or changed files)
- If partially done → leave unchecked but add a note about progress

#### 4b: Flag plan inaccuracies
- **Steps that are done but not in the plan** — work was done that the plan didn't anticipate. Add these as new completed items.
- **Steps marked as done previously but code was reverted/changed** — flag as potentially stale.
- **Steps that are no longer relevant** — if the approach changed, flag for user review.

#### 4c: Identify next steps
Combine these sources to build the next steps list:
1. **Remaining unchecked items from the plan** — these are the primary next steps
2. **TODOs in code** — Scan changed files for `TODO`, `FIXME`, `HACK`, `XXX` comments
3. **Partial implementations** — Functions with `pass`, `NotImplementedError`, or stub returns
4. **Failing tests** — If test files were changed, note which tests may need attention
5. **Logical follow-ups** — Based on what was done, what naturally comes next?

**Priority order**: Plan items first, then code TODOs, then inferred follow-ups.

### Step 5: Auto-Fix Stale Docs

Based on the session delta, check if structural changes were made that affect docs:

- **New skill/agent added or removed?** — Check `CLAUDE.md` and `README.md` tables and directory trees
- **Files moved or renamed?** — Check for broken references
- **Skill count changed?** — Check `tests/test_skills.py` expected count

If issues are found:
1. Fix them automatically (update tables, trees, counts)
2. Report what was fixed

If no structural changes were made, skip this step and report "No doc sync needed."

> **Note**: For comprehensive cross-reference checks beyond the session delta, use `/meta-sync-references` directly.

### Step 6: Update the Plan File

**This step writes to the plan file. Everything from this session must be persisted — not just displayed in the terminal.**

#### If the plan file exists:

1. **Update existing checklist items** — mark completed items as `- [x]` based on Step 4a findings
2. **Add any unplanned completed work** — new items from Step 4b, marked as `- [x]`
3. **Append a session entry** at the end of the file:

```markdown
---

## Session: [YYYY-MM-DD] — [branch name]

### Completed This Session
- [bullet list of what was done, from Step 4a + 4b]

### In Progress (uncommitted)
- [any uncommitted work, or "None — all changes committed"]

### Remaining Steps
- [ ] [unchecked plan items, ordered by priority]
- [ ] [new next steps from Step 4c]

### Plan Accuracy Notes
- [any inaccuracies found in Step 4b, or "Plan is accurate"]

### Doc Sync
- [what was auto-fixed, or "No doc sync needed"]
```

#### If the plan file does not exist:

Create it at the chosen path with:

```markdown
# Implementation Plan

> Auto-created by /session-wrapup on [YYYY-MM-DD]

## Session: [YYYY-MM-DD] — [branch name]

### Completed
- [bullet list from this session]

### Next Steps
- [ ] [items from Step 4c]

### Doc Sync
- [auto-fix results]
```

### Step 7: Final Report

Output a summary to the console. **This is a summary — the full details are in the plan file.**

```
## Session Wrap-Up: [branch name]

### Completed This Session
- [concise list]

### Uncommitted Work
- [list or "All committed"]

### Plan Status
- [N] items completed (marked in plan)
- [N] items remaining
- [any accuracy notes]

### Next Steps (top 3-5)
- [ ] [highest priority items]

### Docs
- [auto-fixed items or "All in sync"]

### Plan file updated: [path to plan file]
### Status: Ready to switch
```

---

## Output Format (Console)

```
## Session Wrap-Up: [branch-name] — [YYYY-MM-DD]

### Commits This Session
- abc1234 feat: added user auth endpoint
- def5678 fix: corrected validation logic

### Uncommitted Changes
- src/utils.py — new helper function (not committed)
- [or] All changes committed

### Completed
- Implemented user authentication endpoint
- Fixed input validation for registration

### Next Steps
- [ ] Add unit tests for auth endpoint
- [ ] Implement refresh token logic
- [ ] TODO in src/auth.py:45 — handle token expiry edge case

### Doc Sync
- Updated CLAUDE.md skill table (added session-wrapup)
- Updated README.md directory tree
- [or] No structural changes — docs are in sync

### Implementation plan updated: documentation/IMPLEMENTATION_PLAN.md
### Status: Ready to switch
```

---

## Example Usage

```
# Standard session wrap-up (will ask for your plan file)
/session-wrapup

# Point directly to your plan file
/session-wrapup
Plan file: documentation/IMPLEMENTATION_PLAN.md

# Wrap up with context about what you were working on
/session-wrapup
Plan file: TODO.md
I was working on the auth module — focus the next steps on that area

# Wrap up a specific time range
/session-wrapup
Plan file: documentation/PLAN.md
Only look at commits from the last 2 hours
```
