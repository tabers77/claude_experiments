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

### Step 3: Cross-Reference Plan vs Changes (analysis only)

This is the core analysis step. Compare the **plan state** (from Step 1) against the **session delta** (from Step 2). **Do not write any files yet — just gather findings.**

#### 3a: Mark completed plan items
For each planned step/task in the plan file:
- Check if the git changes (commits + diffs) address that item
- If yes → flag it for completion (`- [x]`) and note the evidence (commit hash or changed files)
- If partially done → leave unchecked but prepare a note about progress

#### 3b: Flag plan inaccuracies
- **Steps that are done but not in the plan** — work was done that the plan didn't anticipate. Prepare to add these as new completed items.
- **Steps marked as done previously but code was reverted/changed** — flag as potentially stale.
- **Steps that are no longer relevant** — if the approach changed, flag for user review.

#### 3c: Identify next steps
Combine these sources to build the next steps list:
1. **Remaining unchecked items from the plan** — these are the primary next steps
2. **TODOs in code** — Scan changed files for `TODO`, `FIXME`, `HACK`, `XXX` comments
3. **Partial implementations** — Functions with `pass`, `NotImplementedError`, or stub returns
4. **Failing tests** — If test files were changed, note which tests may need attention
5. **Logical follow-ups** — Based on what was done, what naturally comes next?

**Priority order**: Plan items first, then code TODOs, then inferred follow-ups.

### Step 4: Auto-Fix Stale Docs (write)

Based on the session delta, check if structural changes were made that affect docs:

- **New skill/agent added or removed?** — Check `CLAUDE.md` and `README.md` tables and directory trees
- **Files moved or renamed?** — Check for broken references
- **Skill count changed?** — Check `tests/test_skills.py` expected count

If issues are found:
1. Fix them automatically (update tables, trees, counts)
2. Report what was fixed

If no structural changes were made, skip this step and report "No doc sync needed."

> **Note**: For comprehensive cross-reference checks beyond the session delta, use `/meta-sync-references` directly.

### Step 5: Update the Plan File (write)

**This step writes to the plan file. Everything from this session must be persisted — not just displayed in the terminal.**

#### If the plan file exists:

1. **Update existing checklist items** — mark completed items as `- [x]` based on Step 3a findings
2. **Add any unplanned completed work** — new items from Step 3b, marked as `- [x]`
3. **Append a session entry** at the end of the file:

```markdown
---

## Session: [YYYY-MM-DD] — [branch name]

### Completed This Session
- [bullet list of what was done, from Step 3a + 3b]

### In Progress (uncommitted)
- [any uncommitted work, or "None — all changes committed"]

### Remaining Steps
- [ ] [unchecked plan items, ordered by priority]
- [ ] [new next steps from Step 3c]

### Plan Accuracy Notes
- [any inaccuracies found in Step 3b, or "Plan is accurate"]

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
- [ ] [items from Step 3c]

### Doc Sync
- [auto-fix results]
```

### Step 6: Commit & Push

**All file writes (doc fixes + plan update) are done. Now commit everything in one clean operation.**

1. **Stage all changes** — the user's code changes + updated plan file + any auto-fixed docs
2. **Ask the user** to confirm the commit message (suggest one based on the session summary)
3. **Commit** everything together — one commit, no leftover uncommitted files
4. **Ask the user**: "Push to remote?" — only push if they confirm
5. After push (or skip), verify with `git status` that the working tree is clean

> **Why this order matters**: The plan file and doc fixes are written *before* committing, so everything goes into a single commit. No "branch ahead with uncommitted changes" situation.

### Step 7: Final Report

Output a summary to the console. **This is a summary — the full details are in the plan file.**

```
## Session Wrap-Up: [branch name]

### Completed This Session
- [concise list]

### Plan Status
- [N] items completed (marked in plan)
- [N] items remaining
- [any accuracy notes]

### Next Steps (top 3-5)
- [ ] [highest priority items]

### Docs
- [auto-fixed items or "All in sync"]

### Plan file updated: [path to plan file]
### Git: [committed and pushed / committed only / nothing to commit]
### Status: Ready to switch
```

---

## Output Format (Console)

```
## Session Wrap-Up: feature/auth — 2026-02-12

### Completed This Session
- Implemented user authentication endpoint
- Fixed input validation for registration

### Plan Status
- 3 items completed (marked in IMPLEMENTATION.md)
- 5 items remaining
- 1 unplanned item added (input validation fix)

### Next Steps (from plan)
- [ ] Add unit tests for auth endpoint
- [ ] Implement refresh token logic
- [ ] TODO in src/auth.py:45 — handle token expiry edge case

### Docs
- Updated CLAUDE.md skill table (added new endpoint)
- [or] No structural changes — docs are in sync

### Plan file updated: IMPLEMENTATION.md
### Git: Committed and pushed to origin/feature/auth
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
