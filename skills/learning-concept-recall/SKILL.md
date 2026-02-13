---
name: learning-concept-recall
description: Spaced repetition for data science and engineering concepts. Quizzes you on what you've learned, adapts to your retention patterns, and reinforces weak areas. Tracks mastery over time.
context: fork
agent: learning-coach
---

# Skill: concept_recall

**Purpose**: Make sure you retain what you learn — not just understand it once and forget.

**Use when**:
- After learning something new (from another skill, a course, or reading)
- Before an interview to refresh key concepts
- When you feel rusty on topics you once knew
- Want to build a personal knowledge base with active recall

> **vs other learning skills**: Other skills teach new things. This one makes sure you **keep** what you learned.

---

## Modes

### A) Quiz Mode (default)
Claude quizzes you on concepts from your topic list. Adapts difficulty based on your answers.

### B) Teach-Back Mode
You explain a concept to Claude. Claude evaluates: is your understanding correct, complete, and precise?

### C) Add Concepts Mode
Register new topics you've been studying. Claude generates recall questions for them.

---

## Concept Categories (Data Science Focus)

### Statistics & Probability
- Hypothesis testing (null/alt, Type I/II errors, power)
- Confidence intervals (interpretation, width factors)
- Probability distributions (normal, binomial, Poisson, exponential — when to use each)
- Bayesian vs frequentist reasoning
- Central limit theorem, law of large numbers
- A/B testing (design, sample size, early stopping, multiple comparisons)
- Correlation vs causation, confounders

### Machine Learning
- Bias-variance tradeoff
- Overfitting / underfitting (detection, prevention)
- Regularization (L1 vs L2, when to use)
- Cross-validation (k-fold, stratified, time-series split)
- Feature engineering (encoding, scaling, selection)
- Model evaluation metrics (precision, recall, F1, AUC-ROC, log loss — when to use which)
- Ensemble methods (bagging vs boosting, random forest vs XGBoost)
- Gradient descent (learning rate, convergence, variants)

### SQL
- JOIN types and when each applies
- Window functions (RANK, LAG, LEAD, running totals)
- GROUP BY vs PARTITION BY
- NULL behavior in aggregations, joins, WHERE clauses
- Query execution order (FROM → WHERE → GROUP → HAVING → SELECT → ORDER)
- Indexing and query optimization basics

### Python / Pandas
- Mutable vs immutable, pass by reference behavior
- List comprehension vs generator vs map/filter
- Pandas: copy vs view, chained indexing trap
- Pandas: merge vs join vs concat
- Vectorized operations vs apply vs iterrows (performance hierarchy)
- Decorators, context managers, generators

### Software Engineering
- Big-O notation (common complexities, how to analyze)
- Data structures (when to use list vs set vs dict vs deque)
- Design patterns (relevant to DS: strategy, factory, observer)
- Git concepts (rebase vs merge, cherry-pick, bisect)

---

## Process

### 1) Start Session

**First**: Check your memory for existing progress (`concept-recall.md`). If found, load the learner's mastery levels, weak areas, and review schedule. Greet with context: "Welcome back — last time you were weak on [X], let's start there."

Ask the user:
- **Mode**: Quiz / Teach-Back / Add Concepts
- **Topics**: Which categories? (or "all", or "weak areas from memory")
- **Duration**: Quick (5 questions) / Standard (15) / Deep (30)

### 2) Quiz Mode Process

For each question:

1. **Ask**: Present a question adapted to difficulty level
   - Easy: definition / recognition ("What does L1 regularization do?")
   - Medium: application ("You have a dataset with 95% class A. Which metric should you NOT use?")
   - Hard: reasoning / traps ("Your A/B test shows p=0.03 but you checked results 5 times during the test. What's wrong?")

2. **User answers**

3. **Evaluate**:
   - Correct → increase difficulty, mark concept as stronger
   - Partially correct → explain what was missing, repeat at same level
   - Wrong → explain clearly with an example, mark for review, decrease difficulty

4. **Reinforce wrong answers**: Come back to missed questions later in the session with a slightly different angle

### 3) Teach-Back Mode Process

1. Claude names a concept: "Explain cross-validation to me"
2. User explains in their own words
3. Claude evaluates:
   - Is it **correct**? (no factual errors)
   - Is it **complete**? (key points covered)
   - Is it **precise**? (no hand-waving, specific language)
4. Claude gives a score: Solid / Needs work / Incorrect
5. If incomplete: Claude asks a follow-up that targets the gap

### 4) Add Concepts Mode

User provides:
- Topic name: "Docker networking"
- What they learned: "Bridge networks, host networks, overlay for swarm..."
- Source: "Docker docs" or "course X"

Claude generates:
- 5-10 recall questions at varying difficulty
- Stores the topic for future quiz sessions

### 5) Session Summary

```
## Recall Session Summary

### Performance
- Questions: 15
- Correct: 10 (67%)
- Partially correct: 3
- Wrong: 2

### Strong (move to longer interval)
- Bias-variance tradeoff
- SQL window functions
- Pandas merge vs join

### Needs Review (shorter interval)
- A/B test multiple comparisons correction
- L1 vs L2 regularization intuition

### New Weak Spots Found
- Bayesian reasoning (first time wrong)

### Suggested Next Session
Focus on: A/B testing methodology, regularization
Recommended in: 3 days (spaced repetition interval)
```

**After the summary**: Save all progress to memory. Update `concept-recall.md` with the full mastery tracker and `MEMORY.md` with a concise session summary.

---

## Output Format

```
## Concept Recall: [Mode] — [Topics]

### Question [N]/[Total]
[question text]

Category: [Statistics / ML / SQL / Python / SWE]
Difficulty: [Easy / Medium / Hard]

---
[USER ANSWERS]
---

### Evaluation
- Result: [Correct / Partially Correct / Wrong]
- [Explanation if wrong or partial]
- [Key insight to remember]

---
[NEXT QUESTION or SESSION SUMMARY]
```

---

## Example Usage

```
# Quick quiz on ML concepts
/learning-concept-recall quiz, ML, quick

# Deep review of weak areas
/learning-concept-recall quiz, weak areas, deep

# Teach-back mode on statistics
/learning-concept-recall teach-back, statistics

# Add new concepts from something I just learned
/learning-concept-recall add concepts: Docker networking, Kubernetes pods

# Pre-interview refresh
/learning-concept-recall quiz, all categories, standard
```
