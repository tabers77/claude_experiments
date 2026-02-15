---
name: quality-sync-docs
description: Keep documentation in sync with the actual codebase. Discovers all .md files, builds truth from the filesystem, finds stale references and broken paths, then fixes them. Works in any project.
---

# Skill: quality-sync-docs

**Purpose**: Keep documentation accurate — find and fix references to files, modules, functions, paths, and counts that have gone stale as the codebase evolved.

**Use when**:
- After renaming, moving, adding, or removing files or modules
- After any structural refactor (directory reorganization, module splits/merges)
- Before committing — quick sanity check that docs still match reality
- Periodically as a health check (especially before releases)
- After onboarding setup — verify the README and CLAUDE.md match the actual project

> **vs `/quality-review`**: That skill scores overall code quality across 8 categories. This skill specifically checks whether **documentation references match the filesystem** — broken paths, stale names, wrong counts.
>
> **vs `/session-wrapup`**: That skill records session progress and updates plan files. This skill verifies that ALL documentation files are consistent with the codebase — a deeper structural check.

---

## Rules

- **Never delete documentation content** — only fix references. If something looks wrong but you're not sure, flag it for the user instead of auto-fixing
- **Ask before fixing** — after reporting findings, confirm with the user before applying changes (unless they said "auto-fix")
- **Discover, don't assume** — scan the filesystem to find documentation files. Don't hardcode paths
- **Check ALL `.md` files** — not just README and CLAUDE.md. Implementation plans, audits, setup guides, and changelogs all have references that go stale
- **Be project-agnostic** — this skill must work in any project (Python, Node, Rust, monorepo, etc.)

---

## Process

### Step 1: Discover the Project

Scan the project to understand its structure:

#### A) Find all documentation files
- Glob for `**/*.md` — find every markdown file in the project
- Categorize them:
  - **Root docs**: `README.md`, `CLAUDE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
  - **Docs directory**: `docs/`, `documentation/`, `doc/`
  - **Inline docs**: `.md` files inside source directories
  - **Config docs**: `.claude/`, `.github/`
- List them and note their purpose (from filename or first heading)

#### B) Build the filesystem truth
- **Directories**: What top-level and important subdirectories exist?
- **Source modules**: What packages/modules exist? (scan `src/`, `lib/`, or root for code)
- **Config files**: What config files exist? (`pyproject.toml`, `package.json`, `Cargo.toml`, `Dockerfile`, CI configs)
- **Test files**: Where are tests? What test files exist?
- **Scripts/commands**: Any `Makefile`, `scripts/`, CLI entrypoints?

#### C) Ask the user which docs matter
Present the list of discovered `.md` files and ask:

"I found these documentation files. Which ones should I check for stale references?"

Always include `README.md` and `CLAUDE.md` (if they exist) by default. Let the user add or remove files from the list. Typical candidates:
- `documentation/IMPLEMENTATION.md` — implementation plans reference specific files
- `documentation/SKILL_AUDIT.md` — inventories go stale
- `documentation/UPGRADE_ROADMAP.md` — dependency info changes
- `CHANGELOG.md` — path references
- `docs/architecture.md` — module references
- Any project-specific docs the user points out

### Step 2: Extract References from Each Doc

For each selected documentation file, extract all references:

#### Types of references to find:
| Type | Pattern examples | What could be stale |
|------|-----------------|-------------------|
| **File paths** | `src/auth/middleware.py`, `tests/test_api.py` | File renamed, moved, or deleted |
| **Directory paths** | `src/components/`, `lib/utils/` | Directory restructured |
| **Module/package names** | `import auth_module`, `from pipeline.runner` | Module renamed |
| **Function/class names** | `EvalPipeline`, `calculate_score()` | Renamed or removed |
| **Command examples** | `pytest tests/`, `npm run build` | Paths in commands changed |
| **URL references** | Internal links `[see architecture](docs/arch.md)` | Target file moved |
| **Numeric counts** | "12 modules", "supports 5 frameworks" | Count changed |
| **Directory trees** | ASCII tree listings in README | Structure changed |
| **Config references** | `pyproject.toml [tool.ruff]` section | Config restructured |

For each reference, record:
- **File**: Which doc contains it
- **Line**: Approximate location
- **Type**: File path / directory / function / count / etc.
- **Value**: The actual reference text

### Step 3: Verify Each Reference

For each extracted reference, check if it's still valid:

#### Check 1: File/directory paths
- Does the path exist on the filesystem?
- If not: is there a similar file nearby? (fuzzy match for renames)

#### Check 2: Code references (functions, classes, modules)
- Search the codebase for the referenced name
- If not found: was it renamed? (check git log if available)

#### Check 3: Numeric counts
- Count the actual items and compare
- Common: "N tests", "N modules", "N endpoints", "N skills"

#### Check 4: Directory tree listings
- Compare ASCII trees in docs against actual filesystem
- Check for missing entries, extra entries, or wrong nesting

#### Check 5: Internal markdown links
- For `[text](path)` links: does the target exist?
- For heading references `[text](#heading)`: does the heading exist in the target file?

#### Check 6: Command examples
- Do the paths in command examples (`pytest tests/unit/`, `cd src/api/`) exist?
- Are the tool names available? (optional — just check paths)

### Step 4: Report Findings

Output a structured report:

```
## Doc Sync Check: [Project Name]

### Files Checked
| # | File | References Found | Issues |
|---|------|-----------------|--------|
| 1 | README.md | 24 | 3 |
| 2 | CLAUDE.md | 18 | 1 |
| 3 | documentation/IMPLEMENTATION.md | 12 | 2 |
| ... | | | |

### Issues Found

#### README.md
- LINE ~45: STALE PATH — `src/utils/helpers.py` does not exist. Did you mean `src/common/helpers.py`?
- LINE ~78: WRONG COUNT — Says "12 API endpoints" but found 14 in `src/api/`
- LINE ~120: STALE TREE — Directory tree is missing `src/pipeline/` directory

#### CLAUDE.md
- LINE ~30: STALE REFERENCE — `/old-skill-name` not found. Closest match: `/new-skill-name`

#### documentation/IMPLEMENTATION.md
- LINE ~15: BROKEN LINK — `[see architecture](docs/arch.md)` target does not exist
- LINE ~42: STALE FUNCTION — `process_data()` not found in `src/pipeline.py`. Was it renamed to `process_batch()`?

### Clean Files
- documentation/UPGRADE_ROADMAP.md — no issues found

### Summary
- **Files checked**: [N]
- **References verified**: [N]
- **Issues found**: [N]
- **Files clean**: [N]
```

### Step 5: Fix Issues (with confirmation)

If the user approves fixes (or said "auto-fix"):

#### For stale paths:
- If a likely rename is detected: update to the new path
- If the file was deleted with no replacement: remove the reference or mark it as `[removed]`

#### For wrong counts:
- Update the number to match reality

#### For stale directory trees:
- Regenerate the tree section to match the actual filesystem

#### For broken internal links:
- Update the link target, or flag for manual review if ambiguous

#### For stale code references:
- If a rename is detected (via fuzzy match or git log): update the reference
- If ambiguous: flag for the user with suggestions

### Step 6: Verify

After applying fixes:
1. Re-run the reference scan to confirm zero issues
2. If the project has validation scripts (e.g., `tests/test_skills.py`), run them
3. Report final state

---

## Output Format

```
## Doc Sync Check: [Project Name]

### Truth State
- Source directories: [list]
- Documentation files: [N] ([list])
- Config files: [list]

### Issues Found
[By file, with line numbers and fix suggestions]
[Or: "No issues found — all documentation is in sync"]

### Fixes Applied
[List of changes made]
[Or: "No fixes needed"]

### Verification
- Re-scan: 0 issues
- [test command if applicable]: passed
```

---

## Example Usage

```
# Full sync check — discover all docs, check everything
/quality-sync-docs

# Check specific files only
/quality-sync-docs check README.md and CLAUDE.md only

# Auto-fix without asking
/quality-sync-docs auto-fix

# After a big refactor
/quality-sync-docs I just renamed src/pipeline/ to src/orchestrator/ — fix all references

# Dry run — report only
/quality-sync-docs check only, don't fix

# Focus on a specific doc
/quality-sync-docs check documentation/IMPLEMENTATION.md for stale references
```
