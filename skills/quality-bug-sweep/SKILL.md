---
name: quality-bug-sweep
description: Scan the entire project for bugs, vulnerabilities, and improvement opportunities with severity classification. Adapts scanning strategy to project type (web app, data pipeline, library, CLI). Produces a prioritized report with file:line locations. Use when you want a comprehensive bug report across all code, not just one module.
---

# Skill: quality-bug-sweep

**Purpose**: Full-project bug scan with severity classification, adapted to your project type.

**Use when**:
- Before a release — catch what unit tests miss
- After a big refactor — verify nothing subtle broke
- Joining a new project — understand where the risks are
- Periodic health check — find accumulated debt and bugs

> **vs `/code-diagnosis`**: That skill scans a **specific file or module** you point it at. This skill scans the **entire project** systematically.
>
> **vs `/quality-review`**: That skill gives a **numeric quality score** across 8 categories. This skill finds **specific bugs with file:line locations** and severity.
>
> **vs `/commit-ready`**: That skill checks **only changed files** (git diff) for bugs before committing. This skill scans **all existing code** regardless of when it was written.
>
> **vs `code-reviewer` agent**: The agent reviews **recent git changes**. This skill scans the full codebase.

---

## Process

### Step 1: Detect Project Type

Scan for framework markers, entry points, and directory structure. Classify as:

| Type | Markers |
|------|---------|
| Web app | FastAPI/Django/Flask/Express, routes/, endpoints, ASGI/WSGI |
| Data pipeline | Airflow DAGs, Prefect flows, ETL scripts, pandas/spark imports |
| Library | setup.py/pyproject.toml with no app entry point, `src/` layout |
| CLI tool | argparse/click/typer, `__main__.py`, console_scripts |
| Monorepo | Multiple `pyproject.toml` or `package.json`, workspace config |

This determines scan weights:
- **Web app** → security + input validation weighted higher
- **Data pipeline** → correctness + data integrity weighted higher
- **Library** → API surface + type safety weighted higher
- **CLI tool** → error handling + input parsing weighted higher

### Step 2: Build Scan Manifest

1. **Discover all source files** — glob for `**/*.py`, `**/*.js`, `**/*.ts`, etc. based on project languages
2. **Exclude**: vendored code, generated files, `node_modules/`, `__pycache__/`, `.venv/`, test files (test bugs are a separate concern)
3. **Group by module/layer** — organize files by directory or logical component
4. **Estimate scope** — count files and approximate LOC
5. **If >50 source files** → ask the user: "This project has [N] source files. Scan everything, or focus on specific layers?"

### Step 3: Scan Each Module

Read each file and check for issues, classifying by severity:

#### Critical (production-breaking, security, data loss)
- Logic errors that will produce wrong results on common paths
- Unhandled exceptions on likely execution paths
- SQL injection, command injection, XSS vectors
- Authentication/authorization bypasses
- Data corruption or data loss paths
- Race conditions causing data loss
- Hardcoded secrets or credentials

#### High (will cause problems soon, reliability risks)
- Missing input validation on public APIs or user-facing endpoints
- Error handling that swallows important failures silently
- Resource leaks (unclosed files, DB connections, HTTP clients)
- Concurrency issues (shared mutable state, missing locks)
- Missing null/None checks on likely-null values
- Incorrect exception types (catching too broad, wrong type)

#### Medium (code quality, maintainability risks)
- Anti-patterns that make future bugs likely (god functions >50 lines, deep nesting >4 levels)
- Dead code (unreachable branches, unused functions/imports)
- Duplicated logic that should be extracted
- Inconsistent error handling patterns across modules
- Missing type hints on public interfaces (for typed languages)

#### Low (improvements, polish)
- Naming inconsistencies (mixed conventions in same module)
- Minor performance opportunities (unnecessary copies, repeated lookups)
- Missing docstrings on public API functions
- Style inconsistencies within a module

### Step 4: Cross-Cutting Analysis

After scanning individual modules, look for **project-wide patterns**:

- Inconsistent error handling strategies across modules
- Missing or inconsistent logging
- Configuration that differs between environments without clear reason
- Dependency version conflicts or pinning issues
- Circular imports or circular dependencies
- Inconsistent use of async/sync patterns
- Missing or inconsistent input sanitization

### Step 5: Classify and Prioritize

1. **Sort all findings by severity** (Critical → High → Medium → Low)
2. **Within each severity, group by module**
3. **Calculate bug density** per module: `findings / (LOC / 100)` — identifies the most problematic areas
4. **Flag findings NOT covered by existing tests** (if test files exist, cross-reference)

### Step 6: Generate Report

Present findings in console output. If the user requests it, also write to `documentation/BUG_SWEEP.md`.

---

## Output Format

```
## Bug Sweep: [Project Name]

### Project Profile
- Type: [web app / data pipeline / library / CLI / monorepo]
- Source files scanned: [N]
- Lines of code: ~[N]
- Scan focus: [what was weighted based on project type]

### Summary
| Severity | Count | Top Module |
|----------|-------|------------|
| Critical | N     | [module]   |
| High     | N     | [module]   |
| Medium   | N     | [module]   |
| Low      | N     | [module]   |

### Critical Findings
| # | File:Line | Issue | Category | Impact |
|---|-----------|-------|----------|--------|
| 1 | path:42   | [description] | Security | [what goes wrong] |

**Fix**: [specific approach]

### High Findings
[same table format]

### Medium Findings
[same table format]

### Low Findings
[same table format]

### Bug Density by Module
| Module | Files | LOC | Findings | Density |
|--------|-------|-----|----------|---------|

### Cross-Cutting Patterns
- [pattern found across modules]

### What's Clean
- [modules or areas with no findings — balanced reporting]

### Recommended Fix Order
1. [Highest severity, lowest effort first]
2. [Second]
3. [Third]
```

---

## Rules

- **Be specific** — always cite file paths and line numbers, never vague hand-waving
- **Don't invent findings** — if the code is clean, say so. A clean report is a good report
- **Justify severity** — explain why something is Critical vs High. "Could cause data loss" vs "will cause wrong output on edge case"
- **Adapt to project type** — a missing CSRF check is Critical for a web app but irrelevant for a CLI tool
- **Skip generated files** — vendored code, compiled output, and auto-generated files are not your concern
- **Include "What's Clean"** — balanced reporting builds trust and shows which areas are solid
- **Note test coverage** — for each finding, mention whether existing tests cover it or not

---

## Example Usage

```
# Full project scan
/quality-bug-sweep

# Focus on specific concerns
/quality-bug-sweep focus on security and correctness only

# Narrow scope
/quality-bug-sweep skip the frontend, focus on backend Python code

# Save results
/quality-bug-sweep write results to documentation/BUG_SWEEP.md

# Quick scan of a smaller project
/quality-bug-sweep scan test_project/
```
