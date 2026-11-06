---
name: learning-concept-recall
description: Spaced repetition for data science and engineering concepts. Quizzes you on what you've learned, adapts to your retention patterns, and reinforces weak areas. Tracks mastery over time. RECENT mode turns the code you merged lately into verified Daily Drill cards (one-line theory question + a runnable kata or a predict-the-result exercise) and folds your drill results back into the mastery tracker. Use when you want to review concepts, test your knowledge, do a quick quiz session, or "make drill cards from what we shipped", "refresh the drill", "learn from recent merges".
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

### D) Recent Work Mode (`recent`)
Turns what was merged lately in the current repo into **Daily Drill cards**: a page the learner opens during dead time (waiting on terminals). Each card is one short theory question about how a concept behaves in practice, then either a **kata** (write ~10 lines, tests run in the page) or a **predict** exercise (real code + tiny inputs, say what comes out). The learner rates each card got it / shaky / missed, and the page schedules it again. This mode also folds those results back into `concept-recall.md`, so there is one progress record, not two. See section 4b.

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
- **Mode**: Quiz / Teach-Back / Add Concepts / Recent (skip all three questions when the user already said `recent`; go straight to 4b)
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

### 4b) Recent Work Mode Process

State lives in your memory under `drill/`:
- `drill/config.json`: the Daily Drill page URL, the Obsidian concepts folder, per repo `{branch, last_refresh, last_sha}`, `results_folded_until`, and every published card `{id, concepts, sha, added_at}`.
- `drill/inbox/attempts/`: the learner's results, exported by the main session at the end of the previous refresh. One JSON per attempt: `card, rating, theory_answer, practice_answer, code, tests_passed, tests_total, looked_before_answering, at`.
- `drill/outbox/<date>/`: the cards you write.

**You cannot reach the page yourself** (no ArtifactData tool in this agent). You prepare files. The main session publishes them and exports results, following the hand-back block in step 6. If `config.json` is missing, stop and say: "No Daily Drill page is configured. Ask the main session to create one and write `drill/config.json`."

Inputs (all optional): repo (default: the current one), `since` (default: that repo's `last_refresh`, else 21 days), count (default 5, max 8).

1. **Fold in results first.** Read the attempts in `drill/inbox/attempts/` newer than `results_folded_until`. For each one, grade the typed `theory_answer` against the card's answer yourself (Correct / Partial / Wrong), independently of the learner's self-rating. In `concept-recall.md`:
   - update mastery for the card's concepts;
   - record any **calibration gap**: a "got it" whose typed answer was wrong, or `looked_before_answering: true`. This is the most useful signal the drill produces;
   - for missed or shaky cards, add a **variant** to this run's candidates: same concept, a new angle or new numbers, never the same question.

   Set `results_folded_until` to the newest attempt's `at`. With no inbox files, say "no results to fold in yet" and continue.

2. **Pick commits.** Run `git log --first-parent <branch> --since=<since> --pretty='%h %ad %s' --date=short`.
   - Keep `feat`/`fix` commits that implement a mechanism.
   - Skip merges, chores, docs, tracker/record edits, coordination tooling, and pure UI copy.
   - Rank **transferable** concepts first: statistics and experimentation, retrieval, caching and invalidation, auth, concurrency, SQL, evaluation and LLM judging. Platform-specific plumbing comes last.
   - Skip a concept already in `config.cards`, unless it is a variant from step 1.
   - Prefer concepts that match a file name in the Obsidian concepts folder, and use those names in `concepts`, so the cards link to the learner's theory notes.

3. **Write one card per commit**, after reading its diff (`git show <sha> --stat`, then the touched code at HEAD). Card fields:
   `id` (kebab-case, unique), `title`, `concepts` (short, `·`-separated), `src {stream, sha, file}`, `theory`, `answer` (HTML), `kind` (`kata`|`predict`), `task` (HTML), `reveal` (HTML), `code` (the real code, trimmed, or null), `order` (`YYYYMMDD` × 10 + n), `added_at`. Kata cards also need `stub`, `reference`, and `kata {prelude, tests}`.
   - **Theory:** one sentence, ≤ 220 characters, asking how the concept changes behaviour in practice, never a definition. The answer is ≤ 120 words, in plain words, and names the real constants (for example "435 per arm", "−0.35").
   - **Kata** (about half the cards): the reference solution is ≤ ~12 lines; the prelude supplies helpers and constants. Tests are 4–6 calls to `t("plain-words name", ok, msg)`. **At least one test must encode the concept's trap**, the mistake a person who only half understands would make. Example: one hash for both exposure and arm puts every exposed unit in control.
   - **Predict** (the rest): a real snippet of ≤ 10 lines, plus 2–4 scenarios or a tiny-number table. The reveal answers each scenario with its reason.
   - Use tiny concrete numbers wherever the concept is quantitative; the learner profile says they help reconstruction.
   - **Never teach what the code doesn't do.** Every claim in `answer` and `reveal` must be traceable to the code at `src.sha`. If it isn't, cut it.

4. **Verify.** Write the cards as a JSON list to `drill/outbox/<date>/cards.json`, then run the checker in this skill's base directory:
   `python <skill base dir>/drill_check.py drill/outbox/<date>/cards.json --out drill/outbox/<date>/docs`
   It requires every reference to pass all its tests and every stub to fail at least one. Fix and re-run until every card prints PASS. **Never hand back a failing card**, and never weaken a test to make it pass.

5. **Update memory.** Append the new cards to `config.cards`, set the repo's `last_refresh` and `last_sha`, and add the new concepts to `concept-recall.md` with status `new (drill)`.

6. **Hand back** with a short table (card · concept · kata/predict · source commit), plus the results you folded in: N attempts, calibration gaps by name. End with this block, filled in, for the main session to run:

```
MAIN SESSION — publish the drill (2 calls):
1. ArtifactData batch, url <artifact_url>: one {op:"set", collection:"cards", doc_id:<id>, file_path:"<abs path>/docs/<id>.json"} per card
2. ArtifactData list, url <artifact_url>, collection "attempts", query {limit:1000}, out_dir "<abs path to drill/inbox>"
```

The page reads `cards` live, so no republish is needed. Call 2 exports this round's results for the next refresh to fold in.

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

# Daily Drill: cards from what was merged since the last refresh, and fold in my results
/learning-concept-recall recent

# Same, a wider window and more cards
/learning-concept-recall recent, since 2026-10-01, 8 cards
```
