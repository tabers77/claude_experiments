# Skill: project_review

**Purpose**: Evaluate repository quality with calibrated judgment and evidence

**Use when**:
- Assessing overall project health
- Planning tech debt work
- Onboarding to understand quality baseline
- Need evidence-based scoring, not fake precision

---

## Rules

- Be evidence-based: cite file paths and brief observations
- If you did not run a check (tests/lint/typecheck), explicitly state that
- Use a provisional 0-100 score with category breakdown and weights
- Provide prioritized improvements and next PR-sized actions

---

## Process

1) **Identify project type**: library / service / pipeline / monorepo

2) **Gather evidence**:
   - List key files: README, pyproject/requirements, Dockerfile, CI config
   - Locate tests and test framework
   - Search for lint/type tools
   - Identify entrypoints, dependency injection, config approach

3) **Run checks** (if allowed):
   - Unit tests (pytest)
   - Lint (ruff/flake8)
   - Typecheck (mypy/pyright)

4) **Score categories** (weights in parentheses):
   - A) Build & Run (10)
   - B) Code Organization (10)
   - C) Correctness & Testing (25)
   - D) Maintainability (15)
   - E) Reliability & Observability (10)
   - F) Security & Safety (10)
   - G) Performance (10)
   - H) Design & Architecture (10)

5) **Output format** (see below)

If any category cannot be assessed, mark as "unknown" and reduce confidence.

---

## Output Format

```
## Project Review: [Project Name]

### Summary (10 lines max)
[High-level assessment]

### Score: [X]/100 (Confidence: [High/Medium/Low])

| Category | Score | Weight | Notes |
|----------|-------|--------|-------|
| Build & Run | /10 | 10% | |
| Code Organization | /10 | 10% | |
| Correctness & Testing | /25 | 25% | |
| Maintainability | /15 | 15% | |
| Reliability & Observability | /10 | 10% | |
| Security & Safety | /10 | 10% | |
| Performance | /10 | 10% | |
| Design & Architecture | /10 | 10% | |

### Evidence Highlights
- [path/to/file]: [observation]
- [path/to/file]: [observation]

### Top 5 Risks
1. [Risk]: [impact]
2. ...

### Top 10 Improvements (Prioritized)
1. [Improvement]: [effort] / [impact]
2. ...

### Next 3 PR-Sized Actions
1. **[Title]**
   - Files: [paths]
   - Commands: [what to run]
2. ...
```

---

## Example Usage

```
# Fast review:
/project_review run tests if possible; focus on test quality and architecture boundaries

# Security-sensitive:
/project_review do not run commands; static review only

# Focused review:
/project_review focus on the API layer only
```
