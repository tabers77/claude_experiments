# Skill: risk_prioritizer

**Purpose**: Prioritize what matters vs what can wait

**Use when**:
- Planning refactors
- Reviewing architecture changes
- Deciding what NOT to fix
- Need to triage tech debt

---

## Process

1) **Gather context**:
   - What changes/risks are being considered?
   - What's the timeline?
   - What resources are available?

2) **For each item, assess**:
   - **Impact**: What breaks if this goes wrong? (High/Medium/Low)
   - **Likelihood**: How likely is the risk to manifest? (High/Medium/Low)
   - **Effort**: How much work to address? (High/Medium/Low)
   - **Reversibility**: Can we undo if wrong? (Easy/Hard/Impossible)

3) **Categorize into quadrants**:
   - **Do Now**: High impact + High likelihood + Low effort
   - **Plan Soon**: High impact + any likelihood + Medium effort
   - **Monitor**: Medium impact + Low likelihood
   - **Accept/Ignore**: Low impact OR very high effort for low return

4) **Provide reasoning** for each categorization

---

## Output Format

```
## Risk Prioritization: [Context]

### Items Assessed
1. [Item name]
2. [Item name]
...

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
```

---

## Example Usage

```
/risk_prioritizer
Context: Planning Q1 tech debt sprint
Items to consider:
- Upgrade Python from 3.9 to 3.12
- Refactor auth module
- Add structured logging
- Migrate to new ORM
- Fix flaky tests
```

Or:

```
/risk_prioritizer
We found these issues in code review:
- SQL injection in legacy endpoint
- No rate limiting
- Hardcoded secrets in test file
- Missing input validation
- Outdated dependencies
```
