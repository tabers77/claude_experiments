---
name: quality-review
description: Evaluate repository quality and prioritize improvements. Phase 1 scores quality across 8 categories with evidence. Phase 2 prioritizes findings into a Do Now / Plan Soon / Monitor / Accept matrix.
---

# Skill: quality_review

**Purpose**: Evaluate repository quality with calibrated judgment, then prioritize what to fix and in what order.

**Use when**:
- Assessing overall project health
- Planning tech debt work
- Onboarding to understand quality baseline
- Planning refactors or reviewing architecture changes
- Deciding what NOT to fix
- Need to triage tech debt

---

## Rules

- Be evidence-based: cite file paths and brief observations
- If you did not run a check (tests/lint/typecheck), explicitly state that
- Use a provisional 0-100 score with category breakdown and weights
- Provide prioritized improvements with effort/impact analysis
- Always complete both phases — assessment AND prioritization

---

## Process

### Phase 1: Quality Assessment

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

If any category cannot be assessed, mark as "unknown" and reduce confidence.

### Phase 2: Risk Prioritization

Take ALL findings from Phase 1 (risks, improvements, issues) and prioritize them:

5) **For each finding, assess**:
   - **Impact**: What breaks if this goes wrong? (High/Medium/Low)
   - **Likelihood**: How likely is the risk to manifest? (High/Medium/Low)
   - **Effort**: How much work to address? (High/Medium/Low)
   - **Reversibility**: Can we undo if wrong? (Easy/Hard/Impossible)

6) **Categorize into quadrants**:
   - **Do Now**: High impact + High likelihood + Low effort
   - **Plan Soon**: High impact + any likelihood + Medium effort
   - **Monitor**: Medium impact + Low likelihood
   - **Accept/Ignore**: Low impact OR very high effort for low return

7) **Build action sequence** with dependencies

---

## Output Format

```
## Quality Review: [Project Name]

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

### Priority Matrix

#### Do Now (High Priority)
| Item | Impact | Likelihood | Effort | Reasoning |
|------|--------|------------|--------|-----------|
| | | | | |

#### Plan Soon (Medium Priority)
| Item | Impact | Likelihood | Effort | Reasoning |
|------|--------|------------|--------|-----------|
| | | | | |

#### Monitor (Low Priority)
| Item | Impact | Likelihood | Effort | Reasoning |
|------|--------|------------|--------|-----------|
| | | | | |

#### Accept/Ignore
| Item | Reasoning |
|------|-----------|
| | |

### Recommended Sequence
1. [First thing to do]
2. [Second thing to do]
3. [Third thing to do]

### Dependencies
- [Item X] must complete before [Item Y] because [reason]

### What NOT to Do
- [Item]: [why it's not worth it right now]

### Next 3 PR-Sized Actions
1. **[Title]**
   - Files: [paths]
   - Commands: [what to run]
2. ...
```

---

## Example Usage

```
# Full assessment + prioritization
/quality-review run tests if possible; focus on test quality and architecture

# Security-sensitive (no command execution)
/quality-review do not run commands; static review only

# Focused on specific area
/quality-review focus on the API layer only

# With specific items to triage
/quality-review
We found these issues:
- SQL injection in legacy endpoint
- No rate limiting
- Missing input validation
- Outdated dependencies
```
