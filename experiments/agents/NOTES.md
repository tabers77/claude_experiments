# Agents (Subagents) - Experiment Notes

**Date started**: 2026-02-06
**Status**: Exploring
**Artifact type**: Agent
**Source**: https://code.claude.com/docs/en/sub-agents
**Created**: `.claude/agents/code-reviewer.md`

## What I'm Trying to Learn

How to create specialized subagents for different tasks with isolated context, tool restrictions, and focused system prompts.

## Key Capabilities (from docs)

- Markdown files with YAML frontmatter in `.claude/agents/`
- Tool restriction per agent (read-only, bash-only, etc.)
- Model selection: `haiku`, `sonnet`, `opus`, `inherit`
- Persistent memory across sessions (`user`/`project`/`local`)
- Lifecycle hooks scoped to each agent (`PreToolUse`, `PostToolUse`, `Stop`)
- Foreground or background execution (Ctrl+B to background)
- Preload skills into agent context via `skills` field
- Permission modes: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`
- CLI-defined agents via `--agents` flag for quick testing
- Manage via `/agents` interactive command

## Experiments

### Experiment 1: Basic read-only code reviewer
**Setup**: Created `.claude/agents/code-reviewer.md` with Read, Grep, Glob, Bash tools
**Result**:
**Learned**:

### Experiment 2: Background subagent for parallel research
**Setup**:
**Result**:
**Learned**:

### Experiment 3: Subagent with persistent memory
**Setup**:
**Result**:
**Learned**:

## Key Findings

-

## Decision

- [ ] Add to playbook
- [ ] Keep as-is
- [ ] Not useful for my workflow
