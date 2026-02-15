---
name: quality-strategic-advisor
description: Research a project's domain and suggest new features, methods, libraries, and architectural patterns that align with its goals. Goes beyond dependency versions — focuses on what to build next and how to make the project more capable.
---

# Skill: quality-strategic-advisor

**Purpose**: Act as a strategic technical advisor — research the project's domain, understand its goals, and suggest new capabilities, libraries, methods, and architectural patterns that would make it stronger. This is about **what to build next**, not what to upgrade.

**Use when**:
- You want ideas for new features or capabilities aligned with the project's vision
- You want to know what libraries, tools, or techniques exist in the project's domain that you're not using yet
- You're planning the next development cycle and need strategic direction
- You want to validate your roadmap against the current state of the art
- You're exploring a domain (e.g., LLM evaluation, RL training) and want to know what's mature enough to adopt

---

## How This Skill Differs from Similar Skills

This is the most important section. Read this first to know if this is the right skill.

| Skill | What it answers | Scope |
|-------|----------------|-------|
| **`/quality-strategic-advisor`** (this skill) | "What **new capabilities** should this project add? What libraries, methods, or patterns exist in this domain that we're not using yet?" | **Outside-in**: researches the domain, finds what's relevant, suggests what to build |
| `/quality-upgrade-advisor` | "Are my **existing dependencies** up to date? Any security patches or deprecations?" | **Inside-out**: audits what you already have, finds newer versions |
| `/quality-review` | "How **healthy** is my code right now? What's the quality score?" | **Current state**: scores code quality across 8 categories |
| `/architecture-arch` | "How is my codebase **structured**? What are the execution paths?" | **Map**: documents what exists, doesn't suggest additions |
| `/planning-impl-plan` | "**How** should I implement this specific feature?" | **Execution**: plans implementation of a known feature |
| `/meta-discover-claude-features` | "What's new in **Claude Code** that this plugin could adopt?" | **Claude-specific**: only for the Claude Code plugin itself |

**In one sentence**: `upgrade-advisor` tells you to update library X from v1 to v2. `strategic-advisor` tells you that library Y exists and would solve a problem you're facing — or that technique Z from a recent paper could improve your project's core capabilities.

### Example: agent-eval project

| Skill | Would tell you |
|-------|---------------|
| `/quality-upgrade-advisor` | "Bump `trl` from >=0.8 to >=0.12, bump Python to 3.11, drop black for ruff format" |
| **`/quality-strategic-advisor`** | "Consider adding a `ProcessRewardScorer` based on step-level rewards (paper: Let's Verify Step by Step). Look into `LangFuse` for production observability. The `ARES` framework could replace manual RAG evaluation. `Agent Lightning` solves credit assignment — relevant to your multi-agent scoring gap." |

---

## Rules

- **Never implement code** — this skill produces a strategic report only
- **Research before recommending** — use WebSearch + WebFetch to find real libraries, papers, tools, and techniques. Do not hallucinate library names or capabilities
- **Cite every recommendation** — include URLs to repos, docs, papers, or articles. If you cannot verify something online, mark it as "Unverified"
- **Filter ruthlessly by project vision** — only suggest things that align with the project's stated goals. A fascinating library that doesn't fit the project's direction goes in "Watch" at most
- **Assess maturity honestly** — distinguish between production-ready libraries, promising beta tools, and academic papers with no maintained implementation
- **Be specific and actionable** — "consider adding observability" is useless. "Integrate LangFuse (https://langfuse.com/) via their Python SDK to trace evaluation runs in production" is actionable
- **Respect the project's philosophy** — if the project values zero dependencies, don't suggest adding 15 new ones. If it values simplicity, don't suggest over-engineered patterns
- Output goes to `documentation/STRATEGIC_ROADMAP.md`

---

## Process

### Phase 1: Understand the Project Deeply

This phase is critical — bad understanding leads to irrelevant suggestions.

1) **Read project identity files**:
   - README.md — what the project does, its architecture, usage examples
   - CLAUDE.md — goals, constraints, conventions
   - pyproject.toml / package.json / Cargo.toml — dependencies and project metadata
   - Source code structure — scan directories to understand the module layout

2) **Extract the project's domain model**:
   - What is the project's **core abstraction**? (e.g., Episode/Step/Scorer for an evaluation framework)
   - What **problem** does it solve? (e.g., "framework-agnostic agent evaluation with RL support")
   - What **workflows** does it enable? (e.g., "trace → evaluate → reward → train")
   - What **extension points** exist? (e.g., "custom scorers via protocol, custom adapters")
   - What **integrations** does it support? (e.g., "AutoGen, LangGraph, TRL, DSPy")

3) **Extract the project's stated vision and constraints**:
   - Explicit goals (from README, CLAUDE.md, or roadmap files)
   - Design principles (e.g., "zero core dependencies", "protocol-based composition")
   - Known gaps or "Next Steps" sections — things the author already wants but hasn't built
   - Target audience (e.g., "ML engineers building multi-agent systems")

4) **Identify the project's domain keywords**:
   - Extract 5-10 domain-specific terms to use in research searches
   - Example for agent-eval: "LLM evaluation", "agent benchmarking", "reward modeling", "RLHF", "process reward models", "RAG evaluation", "multi-agent credit assignment"

5) **Produce a Project Understanding Card** (output to console before continuing):

```
## Project Understanding: [Name]

**Domain**: [1 sentence]
**Core problem**: [1 sentence]
**Architecture**: [pipeline/library/service/framework — 1 sentence]
**Key abstractions**: [list of 3-5 core concepts]
**Current integrations**: [list]
**Stated vision**: [2-3 bullets]
**Design constraints**: [2-3 bullets]
**Known gaps**: [from README/roadmap — what the author already wants]
**Domain keywords**: [5-10 terms for research]
```

**STOP and confirm with the user** — "Does this accurately capture your project? Anything I'm missing or wrong about?" Adjust before proceeding to research.

---

### Phase 2: Domain Research

Use WebSearch and WebFetch to research the project's domain. This is the core value of the skill.

6) **Search for recent developments in the domain** (use domain keywords from step 4):
   - New libraries and frameworks (search: "[domain keyword] library [current year]")
   - New papers with implementations (search: "[domain keyword] paper implementation github")
   - New techniques or patterns (search: "[domain keyword] best practices [current year]")
   - Industry blog posts and case studies (search: "[project type] architecture [current year]")
   - Conference talks or tutorials (search: "[domain] tutorial [current year]")

7) **For each finding, extract**:
   - **Name**: Library / paper / technique name
   - **What it does**: 2-3 sentences
   - **Maturity**: Production-ready / Beta / Research-only / Unmaintained
   - **Source URL**: GitHub repo, paper, docs page
   - **Stars / adoption signal**: GitHub stars, download count, or "cited by N papers"
   - **Dependencies**: What it requires (does it conflict with the project's constraints?)
   - **Relevance**: Which specific part of the project would this improve?

8) **Search for projects in the same space** (competitors, adjacent tools):
   - What do similar projects do that this one doesn't?
   - Are there common patterns across the ecosystem?
   - What gaps do users of similar tools complain about? (check GitHub issues, discussions)

9) **Search for the project's own ecosystem**:
   - Are there GitHub issues requesting features? (if public repo)
   - Are there forks or extensions that add capabilities?
   - What do users ask about in discussions or related forums?

---

### Phase 3: Filter and Evaluate

10) **For each finding, evaluate fit**:

| Question | How to assess |
|----------|---------------|
| Does it solve a stated gap? | Check against "Known gaps" from Phase 1 |
| Does it extend a core workflow? | Would it add a new node to the project's pipeline? |
| Does it align with design constraints? | Zero-dep project + heavy library = poor fit |
| Is it mature enough to adopt? | Research-only papers with no maintained code = "Watch" |
| Would it serve the target audience? | Does the target user actually need this? |
| Does it avoid scope creep? | Does it stay within the project's domain? |

11) **Discard** findings that:
   - Duplicate what the project already does well
   - Violate stated design constraints
   - Are unmaintained or abandoned (no commits in 12+ months, unresolved critical issues)
   - Are too niche to benefit the target audience
   - Would require fundamental architecture changes for marginal benefit

---

### Phase 4: Strategic Recommendations

12) **Categorize surviving findings into tiers**:

   - **Implement Next** — High value, clearly aligned, mature enough to use, fills a stated gap
   - **Plan for Later** — High value but needs more research, design work, or upstream maturity
   - **Watch** — Interesting but not ready yet. Include a trigger condition ("adopt when X happens")
   - **Skip** — Evaluated and rejected (briefly explain why — prevents re-evaluating later)

13) **For each "Implement Next" and "Plan for Later" recommendation, provide**:

```markdown
### [Recommendation Title]

**Category**: New feature / New integration / New method / Architecture pattern / Library adoption
**Fills gap**: [Yes — which gap / No — new capability]
**Priority**: High / Medium / Low
**Maturity**: Production-ready / Beta / Research (has code)

**What it is**:
[2-3 sentences explaining the library/technique/pattern]

**Why it matters for this project**:
[2-3 sentences — specific to this project's goals. Not generic benefits.]

**How it would integrate**:
- Where in the architecture: [which module/layer]
- New abstractions needed: [new classes, protocols, or modules]
- Existing code affected: [what changes]
- Dependencies added: [list, or "none"]

**Implementation sketch**:
- [Step 1: concrete action]
- [Step 2: concrete action]
- [Step 3: concrete action]

**Effort**: Small (< 1 day) / Medium (1-3 days) / Large (3+ days)
**Risk**: Low / Medium / High — [what could go wrong]

**Sources**:
- [URL 1 — what it is]
- [URL 2 — relevant docs/paper]
```

14) **Identify synergies between recommendations**:
   - Which recommendations unlock others?
   - Which ones share infrastructure? (e.g., two recommendations both need an event bus)
   - What's the optimal order?

15) **Produce a strategic sequence**:
   - Ordered list of what to tackle first
   - Grouped into themes (e.g., "Evaluation depth", "RL capabilities", "Production readiness")
   - Each theme has a clear goal and 2-4 recommendations

---

### Phase 5: Generate Report

16) **Output the full report to console** (see Output Format below)

17) **Save to `documentation/STRATEGIC_ROADMAP.md`**

---

## Output Format

```markdown
## Strategic Roadmap: [Project Name]

**Generated**: [date]
**Domain**: [1-line domain description]
**Project vision**: [2-3 bullets]

**Sources researched**:
- [x] Domain libraries and frameworks ([N] evaluated)
- [x] Recent papers and techniques ([N] evaluated)
- [x] Similar/adjacent projects ([N] compared)
- [x] Community feedback and requests ([N] sources)

---

### Project Understanding

[Project Understanding Card from Phase 1]

---

### Implement Next

#### 1. [Recommendation Title]
[Full structured recommendation — see step 13]

#### 2. [Recommendation Title]
...

---

### Plan for Later

#### 3. [Recommendation Title]
[Full structured recommendation]

---

### Watch

| # | What | Source | Why watching | Adopt when |
|---|------|--------|-------------|------------|
| 1 | [name] | [URL] | [reason] | [trigger condition] |

---

### Skip

| # | What | Source | Why skipped |
|---|------|--------|------------|
| 1 | [name] | [URL] | [reason — prevents re-evaluating] |

---

### Strategic Sequence

**Theme 1: [name]** — [goal]
1. [Recommendation] (effort, dependencies)
2. [Recommendation] (effort, dependencies)

**Theme 2: [name]** — [goal]
1. [Recommendation]
2. [Recommendation]

---

### Synergies
- [Rec A] + [Rec B]: [shared infrastructure or unlocking relationship]

### Next Steps
1. [ ] [First actionable item from "Implement Next"]
2. [ ] [Second actionable item]
3. [ ] Use `/planning-impl-plan` to design [specific recommendation]
4. [ ] Use `/quality-upgrade-advisor` to check dependency versions before starting
```

---

## Example Usage

```
# Full strategic analysis — research the domain and suggest improvements
/quality-strategic-advisor

# With specific focus areas
/quality-strategic-advisor
Focus on: evaluation techniques and RL integration.
We're planning the next development cycle and want to know what's worth adding.

# With project context
/quality-strategic-advisor
This is an LLM evaluation framework. We want to add:
- Better multi-agent scoring
- Production observability
- Step-level reward models
What libraries and techniques exist for these? What else should we consider?

# Validate an existing roadmap
/quality-strategic-advisor
Here's our planned roadmap: [paste roadmap]
Are we missing anything important? Are there better approaches to any of these?

# Competitive analysis focus
/quality-strategic-advisor
What do similar tools (LangFuse, TruLens, DeepEval, Ragas) do that we don't?
Which of those capabilities would be most valuable to add?
```

---

## Workflow Integration

This skill works best as part of a sequence:

```
1. /architecture-arch              → Understand current codebase structure
2. /quality-review                 → Assess current quality and gaps
3. /quality-strategic-advisor      → Research domain, get strategic suggestions  ← THIS SKILL
4. /quality-upgrade-advisor        → Check dependency versions before building
5. /planning-impl-plan             → Plan implementation of chosen suggestions
6. /learning-pair-programming      → Build it with guidance
```

You don't need to run them all — but if you're doing strategic planning, steps 2-5 give you the full picture: **where you are** (review) → **where you should go** (strategic) → **what to update first** (upgrade) → **how to build it** (plan).
