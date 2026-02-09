---
name: safe-changes-refactor-safe
description: Refactor without breaking behavior. Use for multi-file refactors, core logic changes, or when you need explicit invariants and verification.
---

# Skill: refactor_safe

**Purpose**: Refactor without breaking behavior - like a senior reviewing a junior

**Use when**:
- Any refactor that touches multiple files
- Changes to core logic
- Need explicit invariants and verification

---

## Process

1) **Restate the current behavior** + constraints
   - What does this code do today?
   - What are the inputs/outputs?

2) **Identify invariants** (must not change):
   - Input/output schemas
   - Performance constraints
   - API contracts
   - Data integrity rules

3) **Propose a step-by-step plan with checkpoints**:
   - Each checkpoint = code change + test or validation
   - Small, reversible steps

4) **Implement in small diffs**
   - One logical change per step
   - Easy to review and rollback

5) **After each checkpoint**:
   - Run existing tests or propose exact commands
   - If no tests exist, add minimal tests around the invariant

6) **Provide a "review note" section**:
   - What changed
   - Why it's safe
   - What to watch in rollout

---

## Output Format

```
## Current Behavior
[Description of what exists today]

## Invariants (must not change)
1. [Invariant with specific detail]
2. [Invariant with specific detail]

## Refactor Plan

### Checkpoint 1: [Name]
- Change: [what to modify]
- Files: [paths]
- Verify: [command to run]

### Checkpoint 2: [Name]
...

## Review Notes
- Changed: [summary]
- Safe because: [reasoning]
- Watch for: [rollout considerations]
```

---

## Example Usage

```
/safe_changes_refactor_safe
Goal: refactor the feature pipeline to reduce duplicate joins
Constraints:
- keep output schema identical
- add tests
```

Or:

```
/safe_changes_refactor_safe
Goal: Introduce a Composer module
Constraints:
- Existing /chat behavior must remain unchanged
- Existing agent teams must still load correctly
- No tool permissions widened implicitly
```
