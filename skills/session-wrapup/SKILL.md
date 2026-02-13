---
name: session-wrapup
description: Close out a coding session cleanly. Git-driven — detects what changed, updates your plan file with completed items and next steps, syncs CLAUDE.md and README.md, then commits and pushes.
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

---

## Three Files — That's It

This skill updates exactly **3 files** based on what changed:

| File | What gets updated |
|---|---|
| **Plan file** (user provides the name) | Completed items marked `[x]`, new next steps added, session entry appended |
| **CLAUDE.md** | Any section affected by the changes (tables, tree, commands, etc.) |
| **README.md** | Any section affected by the changes (tables, tree, workflow guide, etc.) |

**The plan file is the single source of truth** for tracking progress and next steps. Nothing gets written to TODO, ROADMAP, or any other file — only the file the user specifies.

---

## Process

### Step 1: Get the Plan File

If the user provided a plan file path in their message (e.g., `Plan file: IMPLEMENTATION.md`), use it.

If not, **ask the user**: "What is the name of your plan/implementation file?" — they must provide the path. Store it as **plan_file**.

Read the plan file (if it exists) and extract:
- Checklist items (`- [ ]`, `- [x]`)
- Previous session entries
- Overall goals

### Step 2: Git Change Detection

```bash
git log --oneline --since="8 hours ago"   # recent commits (fall back to -10 if empty)
git status                                 # uncommitted changes
git diff                                   # unstaged changes
git diff --staged                          # staged changes
```

### Step 3: Analyze Changes vs Plan (no writes yet)

Compare git changes against the plan file:

1. **Which plan items are done?** — Match commits/diffs to checklist items. Flag them for `- [x]`.
2. **Work done outside the plan?** — Anything implemented that wasn't in the plan. Prepare to add as completed.
3. **What's next?** — Remaining unchecked plan items + TODOs/FIXMEs found in changed files + logical follow-ups. Plan items come first.

### Step 4: Write All Files

**Do all writes before any commit. Nothing gets committed until all 3 files are updated.**

#### 4a: Update the plan file

If the plan file exists:
1. **Verify factual claims** — Scan the plan file for any concrete numbers or facts (test counts, file counts, dependency versions, endpoint counts, etc.). If the git changes affect any of these, update them to match reality. For example, if the plan says "275 tests across 28 files" but you added 23 new tests, update the number.
2. Mark completed items as `- [x]`
3. Add any unplanned completed work as new `- [x]` items
4. Append a session entry:

```markdown
---

## Session: [YYYY-MM-DD] — [branch name]

### Completed
- [what was done]

### Next Steps
- [ ] [remaining plan items]
- [ ] [new items discovered]
```

If the plan file doesn't exist, create it with the session entry above.

#### 4b: Update CLAUDE.md

Read `CLAUDE.md` and check if any section is now outdated based on the git changes:
- Skill/agent tables — add/remove rows if skills or agents changed
- Directory tree — update if files/folders were added, removed, or renamed
- Key commands — update if commands or entry points changed
- Any other section that references something that changed

If nothing is outdated, skip it.

#### 4c: Update README.md

Read `README.md` and check if any section is now outdated based on the git changes:
- Skill tables — add/remove rows if skills changed
- Directory tree — same as CLAUDE.md
- Quick reference — update if skills were added/removed/renamed
- Practical workflow guide — update if workflows changed
- Skill highlights — update if a highlighted skill changed
- Setup instructions — update if dependencies or config changed

If nothing is outdated, skip it.

### Step 5: Commit & Push

All writes are done. Now commit everything cleanly.

1. **Stage only the files this skill modified** — the plan file, CLAUDE.md, and README.md. Do NOT use `git add -A` or `git add .` — only add files by name. Other uncommitted changes in the repo are the user's in-progress work and must not be touched.
2. **Ask the user**: "These are the files I'll commit: [list]. Should I also include any other files from this session?" — let the user decide if session code changes should be in the same commit or separate.
3. **Suggest a commit message** based on what was done this session
4. **Commit** — one commit with the approved files
5. **Ask**: "Push to remote?" — push only if confirmed
6. **Verify** with `git status` — the staged files should be committed; other changes remain unstaged as before

### Step 6: Final Report

```
## Session Wrap-Up: [branch] — [date]

### Completed
- [what was done]

### Next Steps
- [ ] [top items from plan]

### Files Updated
- [plan file]: [N] items marked done, [N] next steps added
- CLAUDE.md: [what changed, or "no changes needed"]
- README.md: [what changed, or "no changes needed"]

### Git: [committed and pushed / committed only]
### Status: Ready to switch
```

---

## Example Usage

```
# Provide the plan file directly
/session-wrapup
Plan file: IMPLEMENTATION.md

# With extra context
/session-wrapup
Plan file: documentation/PLAN.md
I was working on the auth module

# Shorter form
/session-wrapup IMPLEMENTATION.md
```
