# Skill: impl_plan

**Purpose**: Design first, code second

**Use when**:
- Before any non-trivial implementation
- Need to prevent "clever but wrong" implementations
- Want human judgment before code is touched

---

## Process

When planning implementation:

1) **Restate goal**
   - What are we building?
   - What problem does it solve?

2) **Define non-goals**
   - What are we explicitly NOT doing?
   - What's out of scope?

3) **Break into steps** (small, ordered)
   - Each step should be completable in isolation
   - Clear dependencies between steps
   - Reversible where possible

4) **Define tests per step**
   - How do we verify each step works?
   - What commands to run?

5) **Provide rollback plan**
   - How to undo each step?
   - What's the point of no return?

---

## Output Format

```
## Implementation Plan: [Feature Name]

### Goal
[Clear statement of what we're building]

### Non-Goals
- [What we're NOT doing]
- [What's out of scope]

### Prerequisites
- [Required before starting]

### Steps

#### Step 1: [Name]
- **What**: [description]
- **Files**: [paths to create/modify]
- **Test**: [command or verification]
- **Rollback**: [how to undo]

#### Step 2: [Name]
- **Depends on**: Step 1
- **What**: [description]
- **Files**: [paths]
- **Test**: [command]
- **Rollback**: [how to undo]

[Continue for all steps...]

### Verification Plan
1. [Full test command]
2. [Integration check]
3. [Manual verification if needed]

### Risks
- [Risk]: [mitigation]
```

---

## Example Usage

```
/impl_plan
Design a Composer module that:
- parses BusinessCaseSpec
- selects agents
- binds MCP tools
- persists workflow
- runs via existing orchestrator
```

Or:

```
/impl_plan
Add authentication to the API:
- JWT-based
- Refresh tokens
- Role-based access
```
