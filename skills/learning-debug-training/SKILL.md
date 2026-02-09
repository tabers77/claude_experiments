---
name: learning-debug-training
description: Systematic debugging training for data scientists. Presents buggy code (Python, SQL, pandas, ML pipelines) and teaches you to find bugs methodically, not by guessing.
---

# Skill: debug_training

**Purpose**: Teach you to debug systematically — reproduce, isolate, hypothesize, verify — instead of randomly changing things.

**Use when**:
- Want to improve your debugging instincts
- Keep finding bugs by accident instead of by method
- Preparing for debugging-focused interviews
- Want to learn common data science pitfalls firsthand

> **vs `/quality-review`**: That skill assesses project health. This one trains YOUR ability to find and fix bugs.

---

## Bug Categories (Data Science Focus)

### A) Data Pipeline Bugs
- Wrong joins (cartesian products, dropped rows from inner join)
- Missing value handling (silent NaN propagation, wrong imputation)
- Data type mismatches (string "1" vs int 1, timezone-naive vs aware)
- Off-by-one in date ranges, slicing
- Duplicate rows from unexpected fan-out

### B) Pandas / NumPy Gotchas
- Chained indexing (`df[condition]['col'] = value` — silent failure)
- Copy vs view confusion
- Incorrect axis in operations (axis=0 vs axis=1)
- GroupBy with NaN keys (silently dropped)
- Merge producing more rows than expected
- `.apply()` returning wrong shape

### C) SQL Bugs
- Wrong GROUP BY (missing columns, unexpected aggregation)
- NULL in WHERE/JOIN conditions (rows silently disappearing)
- Cartesian join from missing join condition
- Window function frame issues (ROWS vs RANGE)
- Incorrect date filtering (inclusive vs exclusive bounds)

### D) ML Pipeline Bugs
- **Data leakage** (fitting scaler on full data before train/test split)
- **Target leakage** (feature that encodes the label)
- Incorrect train/test split (not stratified, time series shuffled)
- Wrong metric for the problem (accuracy on imbalanced data)
- Feature engineering applied inconsistently between train and inference
- Random seed not set (irreproducible results)
- Overfitting to validation set (tuning too many times)

### E) Statistical Errors
- Simpson's paradox (aggregated trend reverses in subgroups)
- Survivorship bias (only analyzing successful cases)
- P-hacking (testing until significance, multiple comparisons)
- Confounding variables mistaken for causation
- Wrong statistical test for the data distribution

### F) Python Logic Bugs
- Mutable default arguments (`def f(x=[])`)
- Late binding closures in loops
- Integer division vs float division
- Shallow copy vs deep copy
- Exception swallowing (bare `except:`)

---

## Process

### 1) Setup

Ask the user:
- **Category**: Which bug category? (A-F or "mix")
- **Difficulty**: Easy (obvious bug) / Medium (subtle) / Hard (multiple interacting bugs)
- **Mode**:
  - **Find the bug**: Claude shows buggy code, you identify the issue
  - **Fix the bug**: Same, but you also write the fix
  - **Explain the failure**: Claude shows code + unexpected output, you explain why

### 2) Present the Bug

Show code that looks reasonable but has a bug:

```
Here is a function/query/pipeline. It is supposed to [expected behavior].
When run, it [actual behavior — wrong output, error, or subtle incorrectness].

[code block]

Your task: Find the bug. Explain what's wrong and why.
```

**Rules for presenting bugs**:
- The code should look plausible — not obviously broken
- Include enough context (imports, sample data) to reason about it
- State the expected vs actual behavior clearly
- For ML bugs: show the pipeline, not just one line

### 3) User Investigates

**Critical rules**:
- Do NOT reveal the bug
- If the user asks "hint", give progressive hints:
  - Hint 1: Which SECTION of the code should you look at? (narrow the scope)
  - Hint 2: What ASSUMPTION does the code make that might be wrong?
  - Hint 3: What would happen if you added a print/assert at line X?
- Encourage the user to state their debugging process, not just the answer

### 4) Evaluate the User's Response

After the user identifies (and optionally fixes) the bug:

1. **Did they find the right bug?** — Yes / Partially / No
2. **Was their process systematic?**
   - Did they reproduce the issue first?
   - Did they isolate the problem area?
   - Did they form a hypothesis before jumping to a fix?
   - Or did they just guess?
3. **Is their fix correct?** — Does it handle edge cases?
4. **Is there a deeper issue?** — Sometimes the visible bug masks a design problem

### 5) Teach the Lesson

After evaluation:
- **Name the bug pattern**: e.g., "This is a data leakage bug", "This is a pandas copy-vs-view issue"
- **Explain WHY it happens**: Root cause, not just what to change
- **Show the correct version**: Side by side with the buggy code
- **Prevention**: How to avoid this in the future (assertions, tests, patterns)
- **Real-world impact**: What would happen in production if this shipped

### 6) Session Summary

```
## Debug Training Summary

### Bugs Attempted: [N]

| # | Category | Bug Pattern | Difficulty | Found? | Process? |
|---|----------|-------------|------------|--------|----------|
| 1 | ML Pipeline | Data leakage | Medium | Yes | Systematic |
| 2 | Pandas | Copy vs view | Easy | Yes | Guessed |
| 3 | SQL | NULL in WHERE | Medium | Hint needed | Improved |

### Debugging Process Score
- Systematic approach: 1/3 (needs work)
- Hypothesis before fix: 2/3 (good)
- Edge case awareness: 1/3 (needs work)

### Patterns to Watch For
- Always check for data leakage when preprocessing before splitting
- Use .copy() explicitly when subsetting DataFrames
- Remember: NULL != NULL in SQL
```

---

## Output Format

```
## Debug Challenge [#N] — [Category]
Difficulty: [Easy/Medium/Hard]

### The Code
[code block with bug]

### Expected Behavior
[what it should do]

### Actual Behavior
[what it actually does — wrong output, error, etc.]

---
[USER INVESTIGATES]
---

### Evaluation
- Found the bug: [Yes/Partially/No]
- Debugging process: [Systematic/Some method/Guessed]
- Fix correct: [Yes/Partial/No]

### The Bug: [Pattern Name]
- **What**: [one line description]
- **Why**: [root cause explanation]
- **Fix**: [corrected code]
- **Prevention**: [how to avoid this in future]
```

---

## Example Usage

```
# Mixed data science bugs
/learning-debug-training mix, medium

# ML pipeline bugs specifically
/learning-debug-training ML pipeline bugs, hard

# Pandas gotchas for quick practice
/learning-debug-training pandas, easy, find the bug

# SQL debugging
/learning-debug-training SQL bugs, explain the failure

# Full session with summary
/learning-debug-training mix, 5 problems, medium-hard
```
