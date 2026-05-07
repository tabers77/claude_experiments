# Self-Learning Skills — Design Doc

A pattern for Claude Code skills that **improve their own SKILL.md based on real runs**. Each skill keeps a local `run_history.json` ledger of categorical failure modes; when a counter trips its threshold, the skill auto-edits its body per a stored `remediation_hint`. The git diff is the safety net.

This doc captures the pattern, the schema, the invariants, and how to author one manually. A future `meta-self-learning-skill-gen` skill will automate the generation step.

## Why

Most agent self-improvement work either:
- Reflects in freeform prose (Reflexion-style) — drifts, can't be deduplicated.
- Searches over prompt candidates (DSPy/MIPROv2-style) — needs a metric and an eval set.
- Refines via LLM-as-judge offline (MLflow EDD-style) — separates evals from production runs.

This pattern is different on three axes:
1. **Tagged, not freeform.** Every failure mode is a stable categorical tag with a threshold. Tags accumulate occurrences over runs and trip remediation deterministically.
2. **Online, not offline.** Production runs *are* the eval set. The user is the judge.
3. **Self-edits SKILL.md, not weights or external prompts.** The skill is its own artifact; remediation is a text edit; rollback is `git revert`.

The closest published analog is **LangMem's procedural memory refinement** + **Voyager's growing skill library with self-verification**, but neither targets Claude Code's SKILL.md format or uses tag/threshold mechanics.

## The five invariants

These are what make the pattern work. Every self-learning skill must honor them:

1. **Categorical FAIL tags, not freeform reflection.** `<phase>-<failure-mode-slug>`, stable forever. Tags accumulate occurrences correctly across runs; freeform reflections don't.
2. **Threshold tiering by phase severity.** Load-bearing=1, procedural=2, cosmetic=5. This encodes a Bayesian prior on whether a failure deserves a structural change to the SKILL.md.
3. **Verbatim evidence requirement.** The audit phase cannot paraphrase user input or claim a tool ran without observing the call. `audit-paraphrased-user-input` and `tool-claim-without-call` are themselves tracked FAIL tags — the audit polices the audit.
4. **Auto-apply with git as safety net.** No review queue. Remediation edits the SKILL.md immediately; the user catches bad remediations in their normal commit-review loop.
5. **Per-skill local ledger.** No central state to corrupt. Each skill is its own evolving artifact; lessons don't propagate across skills (intentional — keeps blast radius bounded).

## The architecture

A self-learning skill is a regular Claude Code skill folder with two extra ingredients:

```
skills/<name>/
├── SKILL.md              # Domain phases (1..N-2) + standardized audit (N-1) + ledger (N)
└── run_history.json      # Persistent ledger: schema v1
```

The skill's flow:

```
Phase 1..N-2  : Domain work (your custom phases)
Phase N-1     : Pre-action self-audit (verbatim evidence, FAIL detection, approval gate)
Phase N       : Update run-history ledger (append run, increment counters, trip remediation)
```

Phases N-1 and N are **standardized** across all self-learning skills. The domain phases are 1 through N-2.

## The schema

`run_history.json` is the persistent ledger. Full schema documented at:

→ `library/templates/self-learning-skill/run_history_schema_v1.md`

Headline shape:

```json
{
  "version": 1,
  "fail_counters": {
    "<tag>": {
      "count": 0,
      "threshold": 1,
      "phase": "audit",
      "description": "...",
      "occurrences": [{"ts": "...", "target": "...", "detail": "..."}],
      "remediation_hint": "...",
      "applied_at": null
    }
  },
  "runs": [{"ts": "...", "target": "...", "outcome": "closed", "phases_failed": ["<tag>"]}],
  "friction_log": []
}
```

## Universal seed FAIL rules

Every generated self-learning skill ships with these three tags pre-populated (count=0). They apply to any skill that interacts with a user via tool calls:

| Tag | Phase | Threshold | What it catches |
|---|---|---|---|
| `audit-paraphrased-user-input` | audit | 1 (load-bearing) | Audit row paraphrases user intent rather than quoting verbatim. |
| `audit-no-explicit-approval-wait` | audit | 2 (procedural) | Skill advanced past a user-gate without observing the literal approval token. |
| `tool-claim-without-call` | any | 1 (load-bearing) | SKILL.md text claims a tool/skill ran but no corresponding call was observed. |

Domain-specific tags accumulate from real runs. Don't pre-invent tags you can't currently detect mechanically — they'll drift.

## How to author a self-learning skill (manual route)

Until `meta-self-learning-skill-gen` exists, follow this checklist:

### 1. Decide the basics
- **Skill name** (kebab-case, matches folder).
- **Terminal action** — commit / deploy / doc-edit / test-pass.
- **Approval token** — the literal string the user must type to advance past the audit (e.g. `audit approved`, `commit`, `deploy now`).
- **Load-bearing principle** — the one rule the skill must never violate. This is the north star for tier classification.

### 2. Sketch the domain phases
Aim for 5–10 phases. Each needs:
- Trigger (what activates it).
- Exit condition (what evidence proves it ran).
- Evidence shape that maps to an audit row.

For phases that consume user input, the evidence shape **must** include a verbatim quote slot.

### 3. Pick threshold tiers per phase
For each phase, classify load-bearing / procedural / cosmetic. This determines the threshold for any FAIL tag that lands in that phase.

### 4. Generate the skill folder
Copy `library/templates/self-learning-skill/SKILL.md.tpl` to `skills/<name>/SKILL.md`. Fill in the placeholders. Where the template says "Insert here: the body of audit-phase.md / ledger-phase.md", literally inline the body of those files with placeholder substitutions.

Initialize `skills/<name>/run_history.json` from the "Initial state" snippet in `run_history_schema_v1.md`.

### 5. Validate the structure
Run through this checklist (also embedded at the bottom of `SKILL.md.tpl`):

- [ ] `run_history.json` exists, initialized with the three universal seed tags.
- [ ] Audit phase (Phase N-1) lists one row per domain phase, with concrete evidence shapes.
- [ ] Every user-input phase records input verbatim.
- [ ] Terminal action requires the literal approval token.
- [ ] Threshold tiers match phase severity.
- [ ] Ledger phase is the last phase.

### 6. Smoke run
Invoke the skill on a real task. Verify:
- Audit phase fires before the terminal action.
- Audit lists every phase with evidence.
- Approval gate blocks the terminal action until you type the literal token.
- Ledger phase writes `run_history.json` correctly.

### 7. Iterate from real runs
Don't pre-invent domain FAIL rules. Run the skill on real tasks; when a failure mode emerges, add a new tag with the appropriate threshold. The pattern's whole point is that real runs surface the right rules over time.

## Worked example

`shared-bug-gap-fix` (in the `intelligence-platform` repo) is the reference implementation. Phases 1–7.5 are domain work; Phase 8 is the audit; Phase 10 is the ledger (Phase 9 is the closure commit, sandwiched between audit and ledger because the commit is the terminal action). Its `run_history.json` shows three real remediations applied:

- `8.2.5-no-approval-wait` → restructured Phase 8/9 so commit cannot fire without literal token.
- `9-paraphrased-user-input` → tightened audit to mandate verbatim quotes; added `9-paraphrased-user-input` as a self-tracking FAIL.
- `6-routing-too-coarse-for-trivial-fix` → added Phase 5.5 (test-scope analysis) governing Phase 6.

Each remediation was applied automatically, reviewed in the user's normal commit flow, and reset the counter. The pattern works.

## What's NOT in this design

Decisions deliberately kept simple at v1:

| Out of scope | Why | Future option |
|---|---|---|
| Cross-skill learning | Each skill is its own RL agent. Lessons in one skill don't propagate. | A shared `meta/fail-rules.json` registry could be added later if patterns repeat. |
| Frontmatter / description auto-edits | Wrong keywords could mis-route. Body-only edits are safer and recoverable. | Could be opted in per-skill once we trust the body-edit cycle. |
| Bayesian search over remediation candidates | Adds optimization complexity and a metric requirement. The deterministic threshold-trip is interpretable and good enough. | DSPy-style optimization could be layered on if remediations become combinatorial. |
| Eval set / replay traces | Production runs *are* the eval. The user is the judge. | If quality plateaus, an offline replay harness could be added without disturbing the pattern. |
| Approval queue for remediations | Adds friction, slows iteration. Git diff is the review mechanism. | Could be added per-skill if a skill keeps producing bad remediations. |

## Open questions for v2

- **Ledger pruning.** `occurrences[]` will grow unbounded over years. Recommendation: keep last 20 per tag + rolling stats. Not yet enforced.
- **Tag retirement.** When a remediation is auto-applied, the tag stays in the file with `applied_at` set. Should retired tags be moved to a separate `retired_tags` section after some period?
- **Schema evolution.** When v2 schema lands, what's the migration path? Auto-upgrade on read, or require manual? Currently the schema doc says "skills must refuse to write a file whose version they don't recognize" — that's safe but pushes migration to the user.

These don't block v1. Surface them when they matter.

## References

- Voyager (Wang et al., 2023) — growing skill library with self-verification: https://arxiv.org/abs/2305.16291
- Reflexion (Shinn et al., 2023) — verbal reflection in episodic memory: https://arxiv.org/abs/2303.11366
- Self-Refine (Madaan et al., 2023) — intra-task iterative refinement: https://arxiv.org/abs/2303.17651
- LangMem — procedural memory refinement, productized: https://www.letta.com/blog/agent-memory
- Anthropic — Building Skills for Claude (PDF guide): https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
- DSPy MIPROv2 — Bayesian search over prompt candidates (contrast with deterministic threshold approach): https://dspy.ai/api/optimizers/MIPROv2/

## Templates in this repo

- `library/templates/self-learning-skill/SKILL.md.tpl` — full SKILL.md template
- `library/templates/self-learning-skill/audit-phase.md` — audit boilerplate (Phase N-1)
- `library/templates/self-learning-skill/ledger-phase.md` — ledger boilerplate (Phase N)
- `library/templates/self-learning-skill/run_history_schema_v1.md` — schema reference + bootstrap JSON
