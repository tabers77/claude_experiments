---
name: learning-algo-practice
description: Algorithm and coding interview prep for data scientists. Covers DSA, SQL challenges, pandas/numpy problems, statistics, and ML implementation. Claude presents problems, you solve, Claude corrects.
context: fork
agent: learning-coach
---

# Skill: algo_practice

**Purpose**: Build problem-solving skills through practice — Claude is the interviewer, you are the candidate.

**Use when**:
- Preparing for DS/ML/SWE technical interviews
- Want to sharpen algorithm and data manipulation skills
- Need structured practice with increasing difficulty
- Want to identify weak areas in your technical toolkit

> **vs `/learning-codebase-mastery`**: That skill teaches you specific codebases. This one teaches transferable problem-solving patterns you carry to any interview or project.

---

## Tracks

The user picks a track (or says "random" / "mix"):

### A) Data Structures & Algorithms (classic DSA)
Arrays, hashmaps, trees, graphs, dynamic programming, sorting, searching, sliding window, two pointers, BFS/DFS, greedy.

### B) SQL Challenges
Joins, window functions, CTEs, subqueries, GROUP BY edge cases, NULL handling, query optimization, self-joins, pivot/unpivot.

### C) Pandas & NumPy
Data cleaning, merging/joining, groupby-apply, vectorized operations, reshaping (pivot, melt, stack), time series manipulation, performance (avoiding loops).

### D) Statistics & Probability
Hypothesis testing, confidence intervals, Bayesian reasoning, probability distributions, A/B test design, sample size calculation, p-value interpretation, common traps (Simpson's paradox, multiple comparisons).

### E) ML From Scratch
Implement ML algorithms without libraries: linear regression, logistic regression, decision trees, k-means, KNN, gradient descent, cross-validation, regularization. Understand the math, not just the API.

---

## Process

### 1) Setup

**First**: Check your memory for existing progress (`algo-practice.md`). If found, load the learner's session history, weak areas, and strong patterns. Greet with context: "Welcome back — you've been strong on [X] but could use more practice on [Y]."

Ask the user:
- **Track**: Which track? (A/B/C/D/E/mix)
- **Difficulty**: Easy / Medium / Hard (or "assess me" to auto-calibrate based on memory)
- **Time constraint**: Timed (simulate interview) or untimed (learning mode)
- **Focus**: Any specific topic within the track? (e.g., "dynamic programming", "window functions", or "weak areas from memory")

### 2) Present Problem

Give a clear problem statement:
- Context relevant to data science when possible (e.g., "find the top 3 products by revenue per region" instead of generic "sort arrays")
- Input/output examples
- Constraints (time/space expectations for DSA, dataset size for pandas/SQL)
- Do NOT show the solution or approach

### 3) Let the User Solve

**Critical rules**:
- Do NOT write the solution for the user
- Do NOT reveal the approach unless asked for a hint
- If the user says "hint", give a PROGRESSIVE hint:
  - Hint 1: Which technique/pattern applies here? (e.g., "Think about sliding window")
  - Hint 2: What data structure would help? (e.g., "A hashmap could track frequencies")
  - Hint 3: Pseudocode outline only
  - Never jump to the full solution

### 4) Review the User's Solution

After the user submits their solution:

1. **Correctness**: Does it handle all cases? Test with edge cases
2. **Efficiency**: Time and space complexity analysis
3. **Style**: Is the code clean, readable, idiomatic?
4. **For SQL**: Is the query correct? Could it be simpler? Performance implications?
5. **For pandas**: Are there vectorized alternatives? Memory considerations?
6. **For stats**: Is the reasoning correct? Are assumptions stated?

### 5) Teach the Pattern

After review:
- Name the pattern (e.g., "This is a two-pointer pattern", "This is a window function with PARTITION BY")
- Explain when this pattern applies (what signals to look for)
- Show the optimal solution if the user's was suboptimal — explain the difference
- Give a similar problem to reinforce (don't solve it — let the user practice)

### 6) Track Progress

After each problem, update a mental scorecard:

```
## Session Progress

| # | Track | Topic | Difficulty | Result | Pattern |
|---|-------|-------|------------|--------|---------|
| 1 | SQL | Window functions | Medium | Solved with hint | RANK/ROW_NUMBER |
| 2 | DSA | Two pointers | Easy | Solved clean | Two pointer |
| 3 | Pandas | GroupBy-apply | Medium | Wrong approach | Split-apply-combine |

### Weak areas to practice
- GroupBy patterns in pandas
- Dynamic programming (not attempted yet)

### Strong areas
- SQL window functions
- Array manipulation
```

**After the summary**: Save all progress to memory. Update `algo-practice.md` with the full session history and pattern tracker. Update `MEMORY.md` with a concise session summary.

---

## Output Format

```
## Problem [#N] — [Track]: [Topic]
Difficulty: [Easy/Medium/Hard]

### Problem
[clear problem statement with examples]

### Constraints
[time/space or dataset assumptions]

---
[USER SOLVES]
---

### Review
- Correctness: [pass/fail with explanation]
- Efficiency: O(n) time / O(1) space [or equivalent]
- Style: [feedback]

### Pattern: [Pattern Name]
[When to recognize this pattern, 2-3 sentences]

### Optimal Solution (if different)
[code with explanation]

### Reinforce: Try This Next
[similar problem statement — do NOT solve it]
```

---

## Example Usage

```
# Start a mixed practice session
/learning-algo-practice mix, medium difficulty

# SQL-focused prep
/learning-algo-practice SQL, focus on window functions and CTEs

# Timed interview simulation
/learning-algo-practice DSA, hard, timed 30 minutes

# Auto-calibrate difficulty
/learning-algo-practice pandas, assess me

# ML implementation
/learning-algo-practice ML from scratch, implement logistic regression
```
