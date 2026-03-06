---
name: commit-ready
description: Update docs, check test gaps, and commit. Git-driven — detects what changed, discovers and updates affected documentation, analyzes test coverage gaps, then commits cleanly. Use when you're ready to commit, wrapping up a session, or before pushing.
---

# Skill: commit-ready

**Purpose**: Ensure documentation is current and test gaps are addressed before every commit.

**Use when**:
- You're ready to commit and want docs + tests checked first
- End of session — wrap up cleanly before switching context
- Before any push — make sure nothing is stale

**Relationship to other skills**:
- `/planning-impl-plan` **opens** a work session (design the plan)
- `/commit-ready` **closes** a work session (sync docs, check tests, commit)

---

## Process

### Step 1: Git Change Detection

```bash
git diff                    # unstaged changes
git diff --staged           # staged changes
git status                  # overall state
git log --oneline -10       # recent commits for context
```

Build a clear picture of what changed — files modified, functions added/removed, modules affected.

### Step 2: Discover Relevant Documentation

Find all documentation that might be affected by the changes:

1. **Glob for `**/*.md`** to find all markdown files in the project
2. **Read each** and determine which ones reference things affected by the changes
3. **Always include** `README.md` and `CLAUDE.md` if they exist at the repo root
4. **Look for plan/implementation files** (e.g., `documentation/IMPLEMENTATION.md`, `IMPLEMENTATION.md`)
5. **If unsure** whether a doc file is affected, **ask the user**
6. **Present the list**: "These docs look affected: [list]. Any others?"

### Step 3: Update Documentation

For each affected doc file, check for stale references caused by the changes:

- **Counts** — test count, endpoint count, skill count, file count, etc.
- **File paths or directory trees** — renamed, added, or removed files
- **Feature descriptions or status items** — completed work, new capabilities
- **Checklist items** — mark `- [x]` for completed items

If a plan/implementation file exists, append a session entry:

```markdown
---

## Session: [YYYY-MM-DD] — [branch name]

### Completed
- [what was done]

### Next Steps
- [ ] [remaining items]
- [ ] [new items discovered]
```

**Skip files where nothing is outdated.**

### Step 4: Test Gap Analysis

Analyze the git diff to identify untested code:

1. **Scan for new functions/classes/methods** that have no corresponding test
2. **Check for modified logic paths** that existing tests don't cover
3. **Look for new modules** with no test file at all

**Categorize findings:**

| Category | Examples | Action |
|----------|----------|--------|
| **Should test** | New public functions, business logic, error handling paths | Flag as gap |
| **Skip** | Config changes, doc-only changes, trivial getters/setters, type-only changes | Ignore |

**Then:**
- If gaps found → present them and ask: "Want me to implement these tests?"
- If confirmed → write the tests following project conventions (detect test framework, directory structure, naming patterns from existing tests)
- If no gaps → report "No test gaps detected" and move on

### Step 5: Commit

1. **Stage files** — only files modified by this skill + the user's changed files. Do NOT use `git add -A` or `git add .`.
2. **Ask the user**: "These files will be committed: [list]. Add or remove any?"
3. **Suggest a commit message** based on the changes
4. **Commit** — one commit with the approved files. Do NOT push unless the user explicitly asks.
5. **Verify** with `git status`

### Step 6: Summary Report

```
## Commit Ready: [branch] — [date]

### Documentation Updated
- [file]: [what changed]
- [file]: no changes needed

### Test Analysis
- [N] gaps found, [N] tests written
- Or: "No test gaps detected"

### Git
- Committed: [commit hash] "[message]"
- Files: [list]
```

---

## Example Usage

```
# Before committing
/commit-ready

# With context about what you worked on
/commit-ready
I was working on the auth module and added two new endpoints

# End of session
/commit-ready
Plan file: documentation/IMPLEMENTATION.md
```
