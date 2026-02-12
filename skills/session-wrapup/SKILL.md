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

### Step 1: Git Change Detection

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

### Step 2: Uncommitted Work Check

If `git status` shows uncommitted changes:

1. **List the uncommitted files** with a brief summary of what changed in each
2. **Ask the user**: "You have uncommitted changes. Would you like to commit before wrapping up?"
3. If yes — help them commit (suggest a message based on the diff)
4. If no — note the uncommitted work in the session summary so it's not lost

### Step 3: Summarize What Was Completed

From the git log and diffs, extract:

- **What was implemented** — list each meaningful change (not every file, but each logical unit of work)
- **What was modified** — existing code that was updated
- **What was fixed** — bugs or issues resolved

Write this as a concise bullet list. Use commit messages as the primary source, supplemented by diff analysis for uncommitted work.

### Step 4: Identify Next Steps

Analyze the session delta to infer what's pending:

1. **TODOs in code** — Scan changed files for `TODO`, `FIXME`, `HACK`, `XXX` comments
2. **Partial implementations** — Functions with `pass`, `NotImplementedError`, or stub returns
3. **Failing tests** — If test files were changed, note which tests may need attention
4. **Logical follow-ups** — Based on what was done, what naturally comes next?

Present these as actionable next steps, not vague suggestions.

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

### Step 6: Update Implementation Plan

Write or append to the project's implementation tracking document (typically `documentation/IMPLEMENTATION_PLAN.md` or whichever planning doc exists).

#### If the planning doc exists:

Append a new session entry:

```markdown
---

## Session: [YYYY-MM-DD] — [branch name]

### Completed
- [bullet list from Step 3]

### In Progress (uncommitted)
- [any uncommitted work, or "None — all changes committed"]

### Next Steps
- [ ] [actionable item from Step 4]
- [ ] [actionable item from Step 4]
- [ ] ...

### Doc Sync
- [what was auto-fixed, or "No doc sync needed"]
```

#### If no planning doc exists:

Create `documentation/IMPLEMENTATION_PLAN.md` with:

```markdown
# Implementation Plan

## Session: [YYYY-MM-DD] — [branch name]

### Completed
- [bullet list]

### Next Steps
- [ ] [items]

### Doc Sync
- [auto-fix results]
```

### Step 7: Final Report

Output a summary to the console:

```
## Session Wrap-Up: [branch name]

### Completed This Session
- [concise list]

### Uncommitted Work
- [list or "All committed"]

### Next Steps
- [ ] [actionable items]

### Docs
- [auto-fixed items or "All in sync"]

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
# Standard session wrap-up
/session-wrapup

# Wrap up with context about what you were working on
/session-wrapup
I was working on the auth module — focus the next steps on that area

# Wrap up a specific time range
/session-wrapup
Only look at commits from the last 2 hours
```
