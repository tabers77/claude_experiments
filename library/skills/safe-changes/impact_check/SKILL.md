# Skill: impact_check

**Purpose**: Understand blast radius before risky changes

**Use when**:
- Changes to orchestration / agent routing code
- Database schema changes
- Auth/permissions modifications
- Any change with unclear scope

---

## Process

When assessing change impact:

1) **Identify directly affected components**
   - What code will be modified?
   - What functions/classes are touched?

2) **Map indirect dependencies**
   - What calls the modified code?
   - What does the modified code call?
   - Trace 2 levels deep minimum

3) **Assess data/schema impact**
   - Database changes?
   - API contract changes?
   - Config format changes?

4) **Consider runtime/perf impact**
   - New latency paths?
   - Memory/CPU implications?
   - Scaling considerations?

5) **Identify test gaps**
   - What's tested?
   - What's NOT tested?
   - What new tests are needed?

6) **Provide rollback strategy**
   - How to undo if things go wrong?
   - Data migration rollback?
   - Feature flag options?

---

## Output Format

```
## Impact Assessment: [Change Name]

### Directly Affected
- [Component]: [how it changes]

### Indirect Dependencies
- [Component] → [affected by] → [because]

### Data/Schema Impact
- [None / Description of changes]

### Runtime/Performance Impact
- [None / Description of concerns]

### Test Coverage
- Covered: [list]
- Gaps: [list]
- Needed: [list]

### Rollback Strategy
1. [Step]
2. [Step]

### Risk Summary
- High: [items]
- Medium: [items]
- Low: [items]
```

---

## Example Usage

```
/impact_check
Change: Make workflows reusable and persisted
Focus on:
- Orchestrator behavior
- DB schema
- Agent instantiation lifecycle
```
