---
name: meta-update-docs
description: Detect and fix stale cross-references across the repo. Scans all structural files for broken paths, missing skills, and outdated names, then applies fixes.
---

# Skill: update_docs

**Purpose**: Keep every file in the repo consistent after structural changes (adding/removing/renaming skills, moving files, changing directories).

**Use when**:
- After adding, removing, or renaming a skill or agent
- After moving files between directories
- After any structural change to the repo
- Periodically as a consistency check
- Before committing to ensure nothing is stale

---

## Process

### Step 1: Build the Source of Truth

Scan the actual filesystem to determine what currently exists:

#### A) Skills Inventory
For each directory in `skills/*/`:
- Read `SKILL.md` frontmatter → extract `name`, `description`
- Record: directory name, skill name, description

#### B) Agents Inventory
For each `.md` file in `agents/`:
- Read frontmatter → extract `name`, `description`
- Record: filename, agent name, description

#### C) Documentation Inventory
List all files in `documentation/`:
- Record: filenames

#### D) Directory Structure
Confirm existence of: `skills/`, `agents/`, `hooks/`, `library/`, `documentation/`, `playbook/`, `test_project/`, `experiments/`, `tests/`

Store all of this as the **truth state**.

### Step 2: Scan Reference Files

Read each file that contains cross-references and extract all references. These are the **reference files**:

| File | What to extract |
|------|-----------------|
| `CLAUDE.md` | Skill names in tables, directory tree listing, agent names |
| `README.md` | Skill names in tables, directory tree listing, agent names, command examples |
| `.claude/rules/library.md` | Directory references, documentation rules |
| `test_project/CLAUDE.md` | Skill name references |
| `tests/test_skills.py` | Expected skill count, directory references |
| `documentation/SKILL_AUDIT.md` | Skill/agent/hook/rule inventory (if exists) |
| `documentation/CLAUDE_SETUP.md` | Skill references (if exists) |

For each file, build a list of:
- **Skill names mentioned** (pattern: `/skill-name` or `skill-name/`)
- **Agent names mentioned**
- **Directory paths mentioned**
- **File paths mentioned**
- **Numeric counts** (e.g., "expected >= 13 skills")

### Step 3: Compare Truth vs References

For each reference file, compare extracted references against the truth state:

#### Check 1: Missing Skills
Skills that exist on disk but are NOT listed in a reference file where they should be.
- `CLAUDE.md` Available Skills table should list ALL skills
- `README.md` Available Skills table should list ALL skills
- `CLAUDE.md` directory tree should list ALL skill directories

#### Check 2: Stale Skills
Skill names referenced in files that NO LONGER exist on disk.
- Any `/old-skill-name` that doesn't match a `skills/*/` directory

#### Check 3: Wrong Paths
File or directory paths that don't resolve to actual files.
- `documentation/SOME_FILE.md` referenced but file doesn't exist
- `library/rules/some.md` referenced but file doesn't exist

#### Check 4: Count Mismatches
Numeric assertions that don't match reality.
- `tests/test_skills.py`: expected skill count vs actual
- Any "N skills" or "N agents" claims in documentation

#### Check 5: Documentation Placement
Any `.md` files at the repo root that should be in `documentation/` (except `CLAUDE.md` and `README.md`).

#### Check 6: Naming Convention
Any skill directories or frontmatter names containing underscores instead of hyphens.

### Step 4: Report Findings

Output a report to the console:

```
## Sync Check: claude-library

### Truth State
- Skills: [N] (list names)
- Agents: [N] (list names)
- Documentation files: [N] (list names)

### Issues Found

#### [File: CLAUDE.md]
- MISSING: Skill `/new-skill` not listed in Available Skills table
- STALE: Skill `/old-skill` listed but no longer exists
- COUNT: Directory tree shows 12 skills but 14 exist

#### [File: README.md]
- MISSING: Skill `/new-skill` not in Available Skills table
- STALE: Path `audits/` referenced but directory doesn't exist

#### [File: tests/test_skills.py]
- COUNT: Expected >= 12 but 14 skills exist (should be >= 14)

### No Issues
- .claude/rules/library.md ✓
- test_project/CLAUDE.md ✓

### Summary
- [N] files checked
- [N] issues found
- [N] files clean
```

### Step 5: Apply Fixes

After reporting, fix each issue:

#### For Missing Skills in tables:
- Add a new row to the skill table in `CLAUDE.md` and `README.md` using the skill's frontmatter `name` and `description`

#### For Missing Skills in directory trees:
- Add the skill directory to the tree listing in `CLAUDE.md` and `README.md`

#### For Stale Skills:
- Remove the stale reference from the file

#### For Wrong Paths:
- Update the path to the correct location, or remove if the file no longer exists

#### For Count Mismatches:
- Update the expected count in `tests/test_skills.py`
- Update any numeric claims in documentation

#### For Documentation Placement:
- Move misplaced `.md` files to `documentation/`
- Update any references to the old path

#### For Naming Conventions:
- Rename directories and update frontmatter to use hyphens

### Step 6: Verify Fixes

After applying fixes:
1. Run `python tests/test_skills.py` to confirm all tests pass
2. Re-run Step 2-3 to confirm zero issues remain
3. Report final state

---

## Output Format (Console)

```
## Sync Check: claude-library

### Truth State
- Skills (14): architecture-arch, safe-changes-refactor-safe, ...
- Agents (1): code-reviewer
- Docs (5): PLAN.md, PROBLEM_STATEMENT.md, ...

### Issues Found
[issues by file, or "No issues found — all references are in sync ✓"]

### Fixes Applied
[list of changes made, or "No fixes needed"]

### Verification
- tests/test_skills.py: 7/7 passed ✓
- Re-scan: 0 issues ✓
```

---

## Example Usage

```
# Full sync check + auto-fix
/meta-update-docs

# After adding a new skill
/meta-update-docs just added /my-new-skill

# Dry run — report only, no fixes
/meta-update-docs check only, don't fix
```
