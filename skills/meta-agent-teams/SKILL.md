---
name: meta-agent-teams
description: Decompose tasks into multi-agent orchestration plans. Analyzes your task, recommends team composition, scope boundaries, and coordination strategy. Use when a task is too large for one agent, when you want to parallelize work, or when planning agent teams.
---

# Agent Teams Orchestration Planner

## Purpose

Decompose complex tasks into coordinated multi-agent work using Claude Code's Agent Teams feature. Produces actionable orchestration plans — not theory, not quizzes.

## Use When

- Task is too large or slow for a single agent
- You want to parallelize independent workstreams
- You need to plan agent team composition and scope boundaries
- Working on cross-cutting changes that touch multiple modules/layers

## vs Other Skills

- **vs `/planning-impl-plan`**: Plans implementation steps for *one agent*. This skill plans how to *split work across multiple agents*.
- **vs `/meta-experiment-feature`**: Experiments with new Claude Code features. This is a *production workflow tool* for Agent Teams orchestration.

---

## Process

### Step 1: Gather Input

Ask the user to describe the task (or point to an issue/spec). Understand:
- What needs to change
- How many files/modules are involved
- Dependencies between changes
- Current branch state and any constraints

If the user already provided a task description, proceed directly.

### Step 2: Assess — Is Agent Teams the Right Call?

Not every task benefits from multi-agent work. **Recommend Agent Teams only when:**
- 3+ independent workstreams exist
- Changes touch different modules/layers with minimal overlap
- Task would take >30 min single-threaded

**Reject Agent Teams if:**
- Changes are tightly coupled (agents would constantly conflict)
- Task is inherently sequential (each step depends on the last)
- Files overlap heavily (merge conflicts likely)
- Task is small enough for one agent (<15 min)

If Agent Teams is not the right call, say so clearly and suggest single-agent approach instead.

### Step 3: Decompose into Agents

For each agent, define:
- **Name/role** — descriptive (e.g., "test-writer", "api-impl", "docs-updater")
- **Scope** — exact files/directories it owns (no overlap between agents)
- **Task** — what it does (1-2 sentences)
- **Tools needed** — which tools it requires (Read, Edit, Write, Bash, Grep, Glob, etc.)
- **Dependencies** — what must complete before it starts (if any)

**Critical rule**: No two agents should edit the same file. If they must, make one sequential after the other.

### Step 4: Design Coordination Strategy

- **Parallel vs sequential** — which agents can run simultaneously
- **Merge strategy** — how to combine results (separate worktrees? sequential commits? single branch?)
- **Conflict prevention** — file ownership boundaries, shared interfaces defined upfront
- **Verification** — how to check combined output works after all agents complete

### Step 5: Cost & Risk Assessment

- **Token budget** — estimated per-agent (small: <50k tokens, medium: 50-150k, large: 150k+)
- **Blast radius** — what breaks if an agent goes wrong
- **Rollback** — how to undo each agent's work independently
- **Cost comparison** — Agent Teams cost vs single-agent time trade-off (more agents = more tokens but faster wall-clock)

### Step 6: Present Plan for Confirmation

Present the structured plan (see Output Format below). **Wait for user approval** before suggesting execution.

### Step 7: Suggest Execution

After approval, provide the exact workflow to launch agents:
- Agent tool invocations with `subagent_type`, prompts, and `isolation: "worktree"` if needed
- Whether to run in foreground or background
- Which agents to launch in parallel vs sequentially
- Verification steps after all agents complete

---

## Output Format

```
## Agent Teams Plan: [Task Name]

### Assessment
- **Recommended**: Yes/No — [reason]
- **Agents**: [count]
- **Estimated complexity**: [Low/Medium/High]

### Team Composition

#### Agent 1: [Role Name]
- **Task**: [what it does]
- **Scope**: [files/directories]
- **Tools**: [tool list]
- **Depends on**: [none / Agent N]

#### Agent 2: [Role Name]
- **Task**: [what it does]
- **Scope**: [files/directories]
- **Tools**: [tool list]
- **Depends on**: [none / Agent N]

[... repeat for each agent]

### Coordination
- **Execution order**: [diagram or sequence]
- **Parallel groups**: [which agents run together]
- **File boundaries**: [ownership map]
- **Merge strategy**: [how results combine]

### Cost & Risk
- **Token estimate**: [per agent + total]
- **Key risk**: [biggest concern + mitigation]
- **Rollback**: [how to undo]

### Verification
1. [check after all agents complete]
2. [integration test]
3. [manual review points]
```

---

## Example Usage

```
# Plan agent teams for a large refactor
/meta-agent-teams Refactor auth module: extract middleware, update routes, add tests, update docs

# Assess if a task needs agent teams
/meta-agent-teams Should I use agent teams for adding pagination to all API endpoints?

# Plan teams for cross-cutting change
/meta-agent-teams Add logging to all services: API layer, data pipeline, background workers

# Plan a full project health check (docs + tests + bugs in parallel)
/meta-agent-teams Project health check: Agent 1 syncs docs (quality-sync-docs workflow), Agent 2 validates test coverage (commit-ready test gap analysis), Agent 3 does full bug sweep (quality-bug-sweep workflow)
```
