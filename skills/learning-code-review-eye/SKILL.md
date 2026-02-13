---
name: learning-code-review-eye
description: Train your code review skills for data science. Claude shows you code diffs, you spot issues before Claude reveals them. Tracks which categories of issues you consistently miss.
context: fork
agent: learning-coach
---

# Skill: code_review_eye

**Purpose**: Train YOU to spot bugs, anti-patterns, and issues in code — instead of relying on automated review.

**Use when**:
- Want to become a better code reviewer
- Reviewing PRs feels overwhelming and you miss things
- Preparing for roles that require strong review skills
- Want to develop an instinct for "something is wrong here"

> **vs `code-reviewer` agent**: The agent reviews code FOR you. This skill teaches YOU to review code yourself.

---

## Review Categories (Data Science Focus)

### A) Correctness
- Logic errors, off-by-one, wrong conditions
- Incorrect statistical methods or formulas
- ML pipeline ordering mistakes (e.g., scaling before split)
- SQL producing wrong results

### B) Data Quality
- Missing data validation (no null checks, no schema validation)
- Assumptions about data not verified (uniqueness, ranges, types)
- Silent data loss (inner joins dropping rows, filters too aggressive)
- Hardcoded values that should be parameterized

### C) Performance
- Inefficient pandas (iterrows instead of vectorized, repeated computation)
- N+1 query patterns
- Loading full dataset when only a sample is needed
- Missing caching for expensive computations
- Unnecessary copies of large DataFrames

### D) Security & Safety
- Secrets or credentials in code
- SQL injection in string-formatted queries
- Pickle deserialization of untrusted data
- Missing input validation on user-facing endpoints

### E) Maintainability
- Magic numbers without explanation
- Overly complex one-liners
- No docstrings on public functions
- Dead code, unused imports
- Inconsistent naming conventions
- Copy-pasted code that should be a function

### F) ML-Specific
- Data leakage (preprocessing on full data)
- Target leakage (features correlated with label by construction)
- Reproducibility (missing random seeds, unpinned dependencies)
- Missing experiment tracking (no logging of hyperparameters/metrics)
- Model serving inconsistency (training vs inference preprocessing differs)
- Evaluation on wrong metric for the business problem

### G) Notebook-Specific
- Cell execution order dependencies (cells must run in specific order)
- Global state mutation between cells
- Huge outputs left in committed notebooks
- Missing markdown documentation between code cells
- Credentials or data paths hardcoded in notebooks

---

## Process

### 1) Setup

**First**: Check your memory for existing progress (`code-review-eye.md`). If found, load the learner's blind spot tracker, category hit rates, and weak areas. Greet with context: "Welcome back — your weakest category was [X] at [Y]% hit rate, let's focus there."

Ask the user:
- **Focus**: Which categories to emphasize? (A-G or "all")
- **Difficulty**:
  - Easy: 1 obvious issue per snippet
  - Medium: 2-3 issues, some subtle
  - Hard: Multiple interacting issues, architectural problems
- **Format**:
  - **Code snippet**: Single function or query
  - **PR diff**: Realistic multi-file change
  - **Notebook review**: Jupyter notebook cells
- **Domain**: Generic Python / Data pipeline / ML model / SQL / API

### 2) Present Code for Review

Show a realistic piece of code:

```
A teammate submitted this code for review.
It [brief description of what it does].

Review it and list every issue you find.
Categorize each as: Critical / Warning / Suggestion

[code block — potentially multiple files for PR diff format]
```

**Rules for presenting code**:
- Code should be realistic, not artificially bad
- Mix obvious issues with subtle ones
- Include some things that are actually fine (not everything is wrong)
- For PR diffs: show the diff format with +/- lines

### 3) User Reviews

The user lists their findings.

**Critical rules**:
- Do NOT reveal issues while the user is reviewing
- If the user says "done" or "that's all I see", proceed to evaluation
- If the user asks "any hints?", say how many issues remain: "You found 3 of 6 issues"

### 4) Score the Review

Compare the user's findings against the full issue list:

```
### Review Score

| Issue | Category | Severity | You Found? |
|-------|----------|----------|------------|
| Data leakage in preprocessing | ML-Specific | Critical | Yes |
| No null check on input | Data Quality | Warning | Yes |
| iterrows instead of vectorized | Performance | Warning | No — missed |
| Magic number 0.8 for split | Maintainability | Suggestion | No — missed |
| Unused import | Maintainability | Suggestion | Yes |
| Missing random seed | ML-Specific | Warning | No — missed |

**Found**: 3/6 issues (50%)
**Critical issues caught**: 1/1 (100%)
**Blind spots**: Performance, Reproducibility
```

### 5) Teach What Was Missed

For each issue the user missed:
- **Point it out** in the code (specific line)
- **Explain why it matters** — what would happen in production?
- **Show the fix** — what should the code look like?
- **Pattern to remember** — a one-line rule to internalize (e.g., "Always check: is preprocessing applied before or after the split?")

### 6) Track Blind Spots Over Time

```
## Review Training Progress

### Sessions: [N]

### Blind Spot Tracker
| Category | Times Missed | Times Caught | Hit Rate |
|----------|-------------|-------------|----------|
| Correctness | 1 | 5 | 83% |
| Data Quality | 3 | 4 | 57% |
| Performance | 4 | 2 | 33% — WEAK |
| Security | 0 | 2 | 100% |
| Maintainability | 2 | 6 | 75% |
| ML-Specific | 3 | 3 | 50% — NEEDS WORK |
| Notebook | 1 | 1 | 50% |

### Top 3 Patterns You Miss Most
1. Performance: vectorized alternatives to loops (missed 3x)
2. ML: data leakage patterns (missed 2x)
3. Data Quality: null propagation in joins (missed 2x)

### Recommendation
Focus next session on: Performance + ML-Specific categories
```

**After the summary**: Save all progress to memory. Update `code-review-eye.md` with the full blind spot tracker and category hit rates. Update `MEMORY.md` with a concise session summary.

---

## Output Format

```
## Code Review Training [#N]
Difficulty: [Easy/Medium/Hard]
Format: [Snippet/PR Diff/Notebook]

### Code to Review
[description of what the code does]

[code block]

---
[USER REVIEWS]
---

### Score: [X]/[Y] issues found ([%])

### What You Caught
[list with brief confirmation]

### What You Missed
[for each missed issue: location, explanation, fix, pattern]

### Blind Spot Update
[updated tracker if this is a recurring session]
```

---

## Example Usage

```
# General review practice
/learning-code-review-eye all categories, medium

# Focus on ML-specific issues
/learning-code-review-eye ML-specific, hard, PR diff format

# Quick pandas code review
/learning-code-review-eye performance + data quality, easy, code snippet

# Notebook review practice
/learning-code-review-eye notebook review, medium

# Target weak areas from previous sessions
/learning-code-review-eye focus on my blind spots
```
