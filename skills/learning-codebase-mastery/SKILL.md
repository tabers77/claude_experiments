---
name: learning-codebase-mastery
description: Deep understanding through active learning. Use when onboarding to a new codebase, understanding critical files, or preparing to implement features.
---

# Skill: codebase_mastery

**Purpose**: Deep understanding through active learning

**Use when**:
- Onboarding to a new codebase
- Understanding a critical file before modifying
- Preparing to implement features yourself
- Need to move from passive reading to active understanding

> **vs `/architecture-arch`**: Use `/learning-codebase-mastery` when you want to **learn and retain** through quizzes, deep dives, and exercises. Use `/architecture-arch` when you need a quick **reference document** — a structural map you can refer back to.

---

## Modes

### A) Deep Dive Mode (default)
Structured understanding of code:
- Call graphs
- Invariants
- Extension points
- Data flow

### B) Tutor Mode
Interactive learning where Claude asks YOU questions:
- Trigger: include "tutor", "quiz", or "interactive" in request
- Claude asks questions first
- You answer
- Claude corrects with evidence (paths, snippets, commands)
- You get micro-exercises to implement yourself

---

## Deep Dive Process

1) **Confirm target**:
   - Specific file(s)
   - Goal: understand behavior / prepare for feature work

2) **Analyze and summarize**:
   - Entry points
   - Key functions/classes
   - Data structures
   - Call flow
   - Side effects
   - Invariants

3) **Output structured analysis**

---

## Tutor Mode Process

1) **Confirm target** and goal

2) **Create structured quiz** (8-12 questions, increasing difficulty):
   - "Locate": where is X defined/called?
   - "Explain": what does this function do?
   - "Trace": what is the call sequence for scenario Y?
   - "Predict": what happens if input Z occurs?
   - "Modify safely": where would you add feature A?

3) **Ask 3 questions at a time** (not all at once)

4) **Wait for user answers**

5) **Grade + correct**:
   - For each: Your answer: [checkmark]/[warning]/[x]
   - Correction with file paths and function names
   - Brief "why it matters" note

6) **Give micro-exercise** after each batch:
   - Tiny change to implement
   - Files to edit
   - How to verify

7) **End with "You now understand" checklist**:
   - 5 statements you should be able to say from memory
   - 3 safe feature ideas and where they'd go

---

## Output Format (Deep Dive)

```
## Codebase Analysis: [Target]

### Overview
[Brief description of what this code does]

### Entry Points
- [function/class]: [how it's invoked]

### Key Components
| Component | Responsibility | File |
|-----------|---------------|------|
| | | |

### Call Flow
1. [Entry] → [Step] → [Step] → [Output]

### Data Structures
- [Name]: [purpose and shape]

### Invariants
- [What must always be true]

### Extension Points
- [Where you can safely add functionality]

### Gotchas
- [Non-obvious behavior to watch for]
```

---

## Example Usage

```
# Deep dive
/learning_codebase_mastery src/orchestrator/

# Tutor mode
/learning_codebase_mastery tutor src/auth/middleware.py

# Focused understanding
/learning_codebase_mastery focus on how requests flow from API to database
```
