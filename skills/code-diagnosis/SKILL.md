---
name: code-diagnosis
description: Find bugs, anti-patterns, and refactoring opportunities in existing code. Use when you want a targeted scan of a specific module, file, or area — not a full repo audit.
---

# Skill: code_diagnosis

**Purpose**: Targeted scan of existing code to find bugs, smells, and refactoring opportunities

**Use when**:
- You suspect something is wrong but don't know where
- Before refactoring — to know what to fix first
- Reviewing code you didn't write (not a recent diff — use `code-reviewer` agent for that)
- Need a focused diagnosis of a specific module, not a full repo audit

> **vs `/quality-review`**: Use `/quality-review` when you want a **repo-wide health score** with weighted categories and a priority matrix. Use `/code-diagnosis` when you want to **scan a specific area** for concrete issues to fix.
>
> **vs `code-reviewer` agent**: The agent reviews **recent changes** (git diff). This skill scans **existing code** regardless of when it was written.

---

## Process

1) **Confirm the target**:
   - Ask: file(s), module, directory, or "this function"
   - Ask: any specific concerns? (performance, correctness, security, or "everything")

2) **Scan for issues** across these categories:

### A) Bugs & Defects
- Logic errors (wrong conditions, off-by-one, missing edge cases)
- Null/None handling gaps
- Race conditions or state mutation issues
- Incorrect error handling (swallowed exceptions, wrong exception types)
- Type mismatches or implicit conversions

### B) Anti-Patterns & Code Smells
- God classes/functions (doing too much)
- Deep nesting (arrow code)
- Primitive obsession (using strings/dicts where a type would be clearer)
- Feature envy (a function that mostly uses another class's data)
- Shotgun surgery risk (one change requires touching many files)

### C) Refactoring Opportunities
- Duplicated logic that should be extracted
- Dead code (unreachable branches, unused functions/imports)
- Overly complex expressions that could be simplified
- Missing abstractions (repeated patterns without a shared helper)
- Inconsistent patterns within the same module

### D) Security & Safety
- Input validation gaps
- SQL injection, command injection, XSS vectors
- Hardcoded secrets or credentials
- Unsafe deserialization
- Missing access control checks

### E) Performance Concerns
- Unnecessary repeated computation
- N+1 query patterns
- Inefficient data structure choices
- Missing caching for expensive operations
- Blocking calls in async contexts

3) **Classify each finding**:
   - **Bug**: Will cause incorrect behavior — fix now
   - **Smell**: Works but will cause problems as code grows — fix soon
   - **Opportunity**: Could be cleaner/faster — fix when convenient

4) **Suggest concrete fixes** for each finding

---

## Output Format

```
## Code Diagnosis: [Target]

### Summary
[2-3 lines: what this code does, overall impression, biggest concern]

### Findings

#### Bugs (fix now)
| # | Location | Issue | Impact |
|---|----------|-------|--------|
| 1 | file.py:42 | [description] | [what goes wrong] |

**Fix**: [specific code change or approach]

#### Smells (fix soon)
| # | Location | Issue | Category |
|---|----------|-------|----------|
| 1 | file.py:88 | [description] | [anti-pattern name] |

**Fix**: [specific code change or approach]

#### Opportunities (fix when convenient)
| # | Location | Issue | Benefit |
|---|----------|-------|---------|
| 1 | file.py:120 | [description] | [what improves] |

**Fix**: [specific code change or approach]

### Refactoring Roadmap
If the user plans to clean this up, suggest an order:
1. [First fix — highest risk or unblocks others]
2. [Second fix]
3. [Third fix]

### What's Actually Fine
[Call out 1-2 things that look good — not everything is broken]
```

---

## Rules

- **Be specific**: Always cite file paths and line numbers, never vague hand-waving
- **Don't invent issues**: If the code is fine, say so. Not everything needs fixing
- **Distinguish severity clearly**: A bug is not a smell. A smell is not an opportunity
- **Include "What's Actually Fine"**: Balanced feedback builds trust
- **Skip categories with no findings**: Don't pad the report with empty sections

---

## Example Usage

```
# Scan a specific module
/code-diagnosis src/auth/

# Focus on performance only
/code-diagnosis src/data_pipeline.py focus on performance

# Broad scan of a service
/code-diagnosis src/api/ look for bugs, security issues, and refactoring opportunities

# Quick check before refactoring
/code-diagnosis src/utils/validation.py I'm about to refactor this — what should I know?
```
