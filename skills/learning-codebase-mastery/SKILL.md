---
name: learning-codebase-mastery
description: Deep understanding through active learning. Four modes — Deep Dive (structured analysis), Tutor (quiz yourself on code), Recent Changes (quiz on what changed in git), and Pre-Commit (quiz on your uncommitted changes before committing). Use when onboarding, preparing to implement, catching up on changes, or verifying you understand what you're about to commit.
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
- **Before committing** — verify you understand your own changes

> **vs `/architecture-arch`**: Use `/learning-codebase-mastery` when you want to **learn and retain** through quizzes, deep dives, and exercises. Use `/architecture-arch` when you need a quick **reference document** — a structural map you can refer back to.
>
> **vs `/learning-code-review-eye`**: That skill trains you to **spot bugs** in synthetic diffs. This skill's Pre-Commit mode tests whether you **understand** your own changes — what they do, why you made them, and what they affect. Different goal: comprehension vs bug-finding.

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

### D) Pre-Commit Quiz Mode
**Goal**: Verify you understand your own changes before committing — what you changed, why, and what it affects.
- Trigger: include "pre-commit", "before commit", "before committing", or "review my changes" in request
- Claude reads your staged and unstaged changes (`git diff` and `git diff --staged`)
- Generates multiple-choice questions (3 options each) about your own changes
- You pick answers — Claude grades and explains
- Configurable number of questions (default: 3)

**Use this when**: You're about to commit and want to make sure you truly understand every change — not just that it works, but that you can explain it.

> **vs Mode C (Recent Changes)**: Mode C quizzes on **already committed** code (git log). Mode D quizzes on **uncommitted** changes (git diff) — what you're about to commit right now.
>
> **vs `/learning-code-review-eye`**: That trains you to **find bugs** in code. Mode D tests your **comprehension** — do you understand what your change does, not whether it has bugs.

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

## Pre-Commit Quiz Process

1) **Read the changes**:
   - Run `git diff --staged` to see what's staged for commit
   - Run `git diff` to see unstaged changes (mention these to the user — "you also have unstaged changes in X, Y")
   - Run `git status` for an overview
   - If nothing is staged or changed, tell the user: "No changes to quiz on. Stage some changes first."

2) **Analyze the changes**:
   - For each changed file: understand what was added, removed, or modified
   - Identify the **intent** behind the changes (new feature, bug fix, refactor, config change, test)
   - Note which parts of the codebase are affected (which modules, which functions)
   - If needed, read surrounding code for context (the unchanged parts of modified files)

3) **Determine quiz size**:
   - Check if the user specified a number (e.g., "5 questions"). Use that.
   - Default: **3 questions** — enough to verify comprehension without slowing down the workflow
   - For large diffs (10+ files): suggest more questions ("This is a big changeset — want 5 questions instead of 3?")
   - For tiny diffs (1-2 lines): reduce to 2 questions

4) **Build multiple-choice questions**:
   Each question must have **exactly 3 options** (A, B, C). One is correct, two are plausible but wrong.

   **Question types** (mix these based on what the diff contains):

   - **"What does this change do?"** — Tests whether you understand the functional effect
     > Example: "In `scorer.py`, what does the new `normalize` parameter do?"
     > A) Scales all scores to 0-1 range before aggregation
     > B) Removes outlier scores that are more than 2 std devs from the mean
     > C) Converts negative scores to zero

   - **"Why was this change needed?"** — Tests whether you understand the motivation
     > Example: "Why was the `try/except` block added around the API call in `fetch_data()`?"
     > A) To retry failed requests up to 3 times
     > B) To return a default value instead of crashing when the API is unreachable
     > C) To log the error and re-raise it with more context

   - **"What could this affect?"** — Tests awareness of side effects and dependencies
     > Example: "Which other component is most likely affected by renaming `process()` to `process_batch()`?"
     > A) The CLI argument parser in `cli/main.py`
     > B) The pipeline runner that calls `process()` in a loop
     > C) The test fixtures that mock the database connection

   - **"What would happen if...?"** — Tests deeper understanding of the change's behavior
     > Example: "If `max_retries` is set to 0, what happens when the first request fails?"
     > A) It retries once (0 means use default of 1)
     > B) It raises the exception immediately with no retries
     > C) It silently returns None

   - **"What was the previous behavior?"** — Tests whether you know what you replaced
     > Example: "Before this change, how did `calculate_score()` handle missing values?"
     > A) It skipped them and averaged the rest
     > B) It treated them as zero
     > C) It raised a ValueError

   **Rules for writing good questions**:
   - Questions must be answerable from the diff + surrounding context — no trick questions
   - Wrong options must be **plausible** — not obviously absurd
   - Each question should test a different aspect of the changes (don't ask the same thing twice)
   - Reference specific file names and function names from the actual diff
   - Cover the most important changes first — if there are 10 changed files, focus on the ones that matter most

5) **Present all questions at once** using the AskUserQuestion tool:
   - Present each question with its 3 options
   - Use the AskUserQuestion tool so the user can click to select answers
   - This keeps the interaction fast — one round, not back-and-forth

6) **Grade and explain**:
   After the user answers all questions:

   ```
   ## Pre-Commit Quiz Results

   ### Score: [X]/[N] ([emoji based on score])

   ### Q1: [question text]
   **Your answer**: [A/B/C] — [correct/wrong]
   **Correct answer**: [A/B/C] — [brief explanation with reference to the diff]
   [If wrong: "The actual change does X because Y — see line N of file.py"]

   ### Q2: ...

   ### Q3: ...
   ```

7) **Verdict**:
   - **All correct**: "You understand these changes. Safe to commit."
   - **Some wrong**: "You missed [specific aspect]. Review [specific file/section] before committing. Here's what to look at: [pointer]."
   - **Most wrong**: "These changes have more going on than you think. Let me walk you through what each change does before you commit." Then give a brief explanation of each change.

   **Important**: Do NOT block the commit or refuse to let the user proceed. This is a learning tool, not a gate. The user decides whether to commit.

8) **Save progress** to memory:
   - Record: date, number of questions, score, which types of questions were missed
   - Track patterns over time: "You consistently miss 'side effects' questions — try to think about what other code calls the function you changed"

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

# Pre-commit — quick check before committing (default 3 questions)
/learning-codebase-mastery pre-commit

# Pre-commit — more questions for a big changeset
/learning-codebase-mastery before commit, 5 questions

# Pre-commit — focused on specific files
/learning-codebase-mastery review my changes in src/pipeline/
```
