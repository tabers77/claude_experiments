---
name: learning-codebase-mastery
description: Deep understanding through active learning. Three modes — Deep Dive (structured analysis), Tutor (quiz yourself on code), and Recent Changes (quiz on what changed in git). Use when onboarding, preparing to implement, or catching up on teammate changes.
---

# Skill: codebase_mastery

**Purpose**: Deep understanding through active learning — understand the code, not just read it.

**Use when**:
- Onboarding to a new codebase
- Understanding a critical file before modifying
- Preparing to implement features yourself
- Need to move from passive reading to active understanding
- Catching up on what changed while you were away
- Reviewing a teammate's recent work to understand their approach

> **vs `/architecture-arch`**: Use `/learning-codebase-mastery` when you want to **learn and retain** through quizzes, deep dives, and exercises. Use `/architecture-arch` when you need a quick **reference document** — a structural map you can refer back to.
>
> **vs `/learning-code-review-eye`**: That skill trains you to **spot bugs** in synthetic diffs. This skill's Recent Changes mode helps you **understand** real changes — what moved, why, and what the impact is.

---

## Modes

### A) Deep Dive Mode (default)
**Goal**: Understand the architecture and internals of a module or file.
- Trigger: default, or include "deep dive", "analyze" in request
- Structured analysis: call graphs, invariants, extension points, data flow
- You read, Claude explains — reference document as output

**Use this when**: You need to understand how code works before touching it.

### B) Tutor Mode
**Goal**: Test and solidify your understanding through interactive quizzes.
- Trigger: include "tutor", "quiz", or "interactive" in request
- Claude asks questions first — you answer — Claude corrects with evidence
- Micro-exercises after each batch
- Increasing difficulty: locate → explain → trace → predict → modify

**Use this when**: You've read the code but want to make sure you actually understand it.

### C) Recent Changes Mode
**Goal**: Understand what changed recently in the codebase and why.
- Trigger: include "recent changes", "what changed", "catch up", or "git log" in request
- Claude reads recent git history (commits, diffs) and quizzes you on the changes
- Tests: what files changed, what the change does, why it was needed, what it could break
- Covers your own commits (do you remember what you did?) and teammates' commits

**Use this when**: You've been away from the project, a teammate pushed changes, or you want to verify you understand recent work.

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

## Recent Changes Process

1) **Determine scope**:
   - Ask the user: how far back? (default: last 5 commits, or "today", "this week", "since Monday", specific commit range)
   - Optionally filter by author, file path, or directory
   - Run `git log --oneline` for the range to get an overview

2) **Read the changes**:
   - For each commit in range: read the diff (`git diff <commit>~1 <commit>`)
   - Understand what changed: new files, modified functions, deleted code, config changes
   - Identify the intent behind each change (bug fix, new feature, refactor, etc.)

3) **Build quiz questions** (6-10 questions, varying types):
   - **"What changed"**: "Which files were modified in commit X?" or "What function was added/removed?"
   - **"Why"**: "What problem was commit X solving?" or "Why was this import added?"
   - **"Impact"**: "What could break if this change has a bug?" or "Which other modules depend on the changed code?"
   - **"Trace"**: "Walk through the new code path for scenario Y"
   - **"Spot the risk"**: "Is there anything in these changes that could cause issues?" (not every change has a risk — sometimes the answer is "looks clean")

4) **Ask 2-3 questions at a time** — wait for user answers

5) **Grade + correct**:
   - For each answer: correct / partially correct / wrong
   - Show the actual diff snippet as evidence
   - Explain what the user missed and why it matters

6) **Summary**:
   ```
   ## Recent Changes Quiz Summary

   ### Commits covered: [range]
   ### Questions: [N]
   ### Score: [X]/[N] ([%])

   ### Changes you understood well
   - [commit/change description]

   ### Changes you need to review again
   - [commit/change description] — [what was missed]

   ### Key takeaways
   - [1-2 things to remember about these changes]
   ```

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
# Deep dive — understand a module's architecture
/learning-codebase-mastery deep dive src/orchestrator/

# Tutor mode — quiz yourself on code you've been reading
/learning-codebase-mastery tutor src/auth/middleware.py

# Focused understanding
/learning-codebase-mastery focus on how requests flow from API to database

# Recent changes — catch up on what happened this week
/learning-codebase-mastery what changed this week

# Recent changes — understand a teammate's work
/learning-codebase-mastery recent changes by @teammate, last 10 commits

# Recent changes — review your own recent commits
/learning-codebase-mastery quiz me on my last 5 commits

# Recent changes — specific directory
/learning-codebase-mastery catch up on changes in src/api/
```
