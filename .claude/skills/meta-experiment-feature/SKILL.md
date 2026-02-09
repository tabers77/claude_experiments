---
name: meta-experiment-feature
description: Quickly set up and experiment with a new Claude Code feature. Use when discovering new features like agents, MCP servers, or hook types.
---

# Skill: experiment_feature

**Purpose**: Quickly set up and experiment with a new Claude Code feature

**Use when**:
- You discover a new Claude Code feature (agents, MCP servers, new hook types, etc.)
- You want to test a feature before adding it to real projects
- You need a structured way to document what you learn

---

## Process

### 1) Gather Input

The user provides ONE of:
- **A source URL** (preferred) -- docs page, release notes, blog post
- **A feature name** -- e.g. "agents", "mcp-sqlite", "hooks"
- **Both** -- a name + URL

### 2) Research the Feature

If a URL was provided:
- Fetch and read the source URL
- Extract: feature name, what it does, key capabilities, configuration, examples

If only a name was provided:
- Search the web for official Claude Code / Anthropic documentation on the feature
- Read the most relevant result

From the research, determine:
- **Feature name**: Short identifier (e.g. `agents`, `mcp_servers`, `hooks`)
- **Artifact type**: What kind of Claude Code configuration is this? (see Artifact Types below)
- **Use case**: What problem does this feature solve? (1-2 sentences)
- **Key capabilities**: What can it do? (3-5 bullets)

### 3) Determine Artifact Type

**CRITICAL**: Different Claude Code features live in different places. Based on the research, identify the correct artifact type and location:

| Artifact Type | Where it lives | When to use |
|---------------|---------------|-------------|
| **Agent** | `.claude/agents/[name].md` | Subagents, specialized AI assistants with isolated context |
| **Skill** | `.claude/skills/[category]_[name]/SKILL.md` | Reusable prompt workflows invoked with `/slash-commands` |
| **Hook** | `.claude/settings.json` (hooks section) | Shell commands triggered by lifecycle events (PreToolUse, PostToolUse, etc.) |
| **Rule** | `.claude/rules/[name].md` | Always-loaded instructions that guide Claude's behavior |
| **MCP Server** | `.claude/settings.json` (mcpServers section) | External tool servers that extend Claude's capabilities |
| **Template** | `library/templates/[name]/` | CLAUDE.md and config templates for new projects |

**Do NOT always default to creating a skill.** Match the artifact to the feature.

### 4) Present Findings for Confirmation

Present your research to the user and ask them to confirm or correct:

```
Based on [source], here's what I found:

> **Feature**: [name]
> **Artifact type**: [Agent / Skill / Hook / Rule / MCP Server / Template]
> **Use case**: [1-2 sentence summary]
> **Key capabilities**:
> - [capability 1]
> - [capability 2]
> - [capability 3]
>
> **Will create**:
> - [exact file path(s) that will be created]
> - `experiments/[feature_name]/NOTES.md` (experiment tracking)

Does this look right, or would you like to adjust anything?
```

Wait for user confirmation before proceeding.

### 5) Create the Artifact

After confirmation, create the **correct artifact type** plus a NOTES.md for experiment tracking.

#### If Artifact Type = Agent

Create the agent file directly in `.claude/agents/`:

```markdown
---
name: [agent-name]
description: [what this agent does and when to delegate to it]
tools: [comma-separated tool list, or omit to inherit all]
model: [sonnet/opus/haiku/inherit]
---

[System prompt for the agent based on research findings]
```

Plus experiment notes at `experiments/[feature_name]/NOTES.md`.

#### If Artifact Type = Skill

Create in `.claude/skills/[category]_[name]/`:

```markdown
---
name: [category]_[feature_name]
description: [use case from research]. Status: EXPERIMENTAL.
---

[Skill content based on research]
```

Plus experiment notes at `experiments/[feature_name]/NOTES.md`.

#### If Artifact Type = Hook

Create a reference file at `experiments/[feature_name]/HOOK_CONFIG.json` showing the exact JSON to add to `.claude/settings.json`, plus NOTES.md.

Do NOT modify `.claude/settings.json` directly -- show the config and let the user decide when to activate it.

#### If Artifact Type = Rule

Create the rule file in `.claude/rules/[name].md` plus NOTES.md.

#### If Artifact Type = MCP Server

Create a reference file at `experiments/[feature_name]/MCP_CONFIG.json` showing the exact JSON to add to MCP config, plus NOTES.md.

### 6) Create Experiment Notes

Always create `experiments/[feature_name]/NOTES.md`:

```markdown
# [Feature Name] - Experiment Notes

**Date started**: [date]
**Status**: Exploring
**Artifact type**: [type]
**Source**: [URL]
**Created**: [list of files created]

## What I'm Trying to Learn

[use case]

## Key Capabilities (from docs)

- [capability 1]
- [capability 2]
- [capability 3]

## Experiments

### Experiment 1: [description]
**Setup**:
**Result**:
**Learned**:

## Key Findings

-

## Decision

- [ ] Add to playbook
- [ ] Keep as-is
- [ ] Not useful for my workflow
```

### 7) Suggest Test Plan

Based on the artifact type, suggest specific tests:

- **Agents**: Create agent, invoke it by asking Claude to delegate, verify output and tool restrictions
- **Skills**: Invoke with `/skill_name`, verify output format
- **Hooks**: Add config to settings.json, trigger the event, verify hook runs
- **Rules**: Start new conversation, verify Claude follows the rule
- **MCP**: Start MCP server, verify tools appear, test tool calls

### 8) Provide Next Steps

Output a checklist tailored to the artifact type.

---

## Output Format

```
## New Feature Experiment: [Feature Name]

### Artifact Type
[Agent / Skill / Hook / Rule / MCP Server]

### Created
- [list of files created with paths]

### Use Case
[what problem it solves]

### Test Plan
1. [specific step to test]
2. [specific step to test]
3. [specific step to test]

### Next Steps
1. [ ] Read official docs: [URL]
2. [ ] Run experiments
3. [ ] Document findings in NOTES.md
4. [ ] Decide: keep / expand / abandon
```

---

## Example Usage

```
# Agents -- creates .claude/agents/code-reviewer.md
/meta_experiment_feature agents

# MCP -- creates experiments/mcp_sqlite/MCP_CONFIG.json + NOTES.md
/meta_experiment_feature mcp-sqlite https://modelcontextprotocol.io/servers

# Hooks -- creates experiments/pre_commit_hooks/HOOK_CONFIG.json + NOTES.md
/meta_experiment_feature https://code.claude.com/docs/en/hooks

# Skills -- creates .claude/skills/category_name/SKILL.md
/meta_experiment_feature custom slash commands for code generation
```
