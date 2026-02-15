---
name: meta-discover-claude-features
description: Scout for new Claude Code features and community patterns, then suggest how to adopt them in this plugin. Checks official docs and community repos for what's new and what's relevant.
---

# Skill: discover_claude_features

**Purpose**: Find new Claude Code features and community patterns, then generate actionable suggestions for adopting them in this plugin — filtered by what's actually relevant to our goals.

**Use when**:
- Want to know what's new in Claude Code since you last checked
- Looking for community ideas to improve the plugin
- Planning the next batch of plugin improvements
- Before a library maintenance session — discover what to work on

> **vs `/meta-experiment-feature`**: That skill takes a feature you already know about and sets up an experiment. This skill **finds features you don't know about yet** and tells you which ones matter for this plugin.
>
> **vs `/meta-skill-audit`**: That skill checks for overlaps and gaps within the library. This skill looks **outside** the library — at official docs and community — for new capabilities to bring in.

---

## Sources

### Official Documentation
- Claude Code official docs: `https://docs.anthropic.com/en/docs/claude-code`
- Claude Code changelog / release notes (search for latest)
- Anthropic blog posts about Claude Code updates

### Community Resources
- Community agents & patterns: `https://github.com/undeadlist/claude-code-agents`
- Search for recent Claude Code tips, workflows, and community plugins

The skill should always check **both** official and community sources to get the full picture.

---

## Process

### 1) Understand This Plugin's Objective

Before looking at anything external, read the plugin's own context to understand what we're trying to achieve:

- Read `CLAUDE.md` — understand the plugin's purpose, structure, and available skills
- Read `.claude-plugin/plugin.json` — understand what hooks and configuration exist
- Read `README.md` — understand the skill categories and workflow guide

**Build a mental model of**:
- What this plugin does (reusable skills, agents, hooks, rules for any project)
- What development phases it covers (Setup → Plan → Build → Review → Wrap up → Learn)
- What it's missing (reference the latest `documentation/SKILL_AUDIT.md` if it exists)
- What kind of user it serves (developer who wants Claude as a colleague, not an autopilot)

This context is **critical** — every suggestion must be filtered through "does this actually help THIS plugin and THIS user?"

### 2) Check Official Documentation

Search for and read the latest Claude Code documentation:

- Fetch the official Claude Code docs page
- Search for recent Claude Code release notes, changelogs, or blog posts
- Focus on: new features, new configuration options, new artifact types, deprecated patterns, breaking changes

For each finding, extract:
- **Feature name**: What it's called
- **What it does**: 1-2 sentences
- **Artifact type**: Agent / Skill / Hook / Rule / MCP Server / other
- **Since when**: Version or date if available
- **Source URL**: Where you found it

### 3) Check Community Resources

Fetch and analyze community resources:

- Read `https://github.com/undeadlist/claude-code-agents` — extract agents, patterns, and workflows shared by the community
- Search for other recent Claude Code community patterns, tips, and plugins

For each finding, extract:
- **Pattern/idea name**: What it is
- **What it does**: 1-2 sentences
- **Source**: Where you found it
- **Quality signal**: Is it well-documented? Does it have community traction?

### 4) Filter: What's Relevant to This Plugin?

This is the most important step. **Not everything new is worth adopting.**

For each finding from steps 2-3, evaluate:

| Question | How to assess |
|----------|---------------|
| Does this fill a known gap? | Check against `documentation/SKILL_AUDIT.md` gap list |
| Does this improve an existing skill? | Could it make a current skill more effective? |
| Does this fit the plugin's philosophy? | "Claude as colleague, not autopilot" — does it align? |
| Does this serve the development lifecycle? | Does it fit into Setup/Plan/Build/Review/Wrap up/Learn? |
| Is it mature enough? | Experimental features with no docs = skip for now |
| Is it a pattern or a one-off? | Reusable across projects = high value. Project-specific = low value |

**Discard** anything that:
- Is too project-specific to be a reusable plugin component
- Duplicates what the plugin already does well
- Is experimental/undocumented with no clear use case
- Doesn't align with the "colleague, not autopilot" philosophy

### 5) Generate Suggestions

For each relevant finding, produce a structured suggestion:

```
### [Suggestion Title]

**Source**: [Official docs / Community: repo name]
**Type**: [New skill / Extend existing skill / New agent / New hook / New rule / Config change]
**Priority**: [High / Medium / Low]
**Fills gap**: [Yes — which gap from audit / No — new capability]

**What it is**:
[2-3 sentences explaining the feature/pattern]

**Why it matters for this plugin**:
[1-2 sentences — specific to our goals, not generic]

**How to adopt it**:
- [Concrete step 1]
- [Concrete step 2]
- [Concrete step 3]

**Effort**: [Small (< 1 hour) / Medium (1-3 hours) / Large (half day+)]
```

### 6) Prioritize and Summarize

Group suggestions into:

1. **Adopt now** — High value, low effort, clearly relevant
2. **Plan for next session** — High value but needs more thought or effort
3. **Watch** — Interesting but not mature enough or not urgent
4. **Skip** — Looked at it, doesn't fit (briefly explain why — prevents re-evaluating next time)

### 7) Generate Report

Output the full report to console (see Output Format below).

Then save to `documentation/FEATURE_DISCOVERY.md` — this becomes the reference for what was checked and when, so you don't re-evaluate the same things next time.

---

## Output Format

```
## Feature Discovery Report

**Date**: [date]
**Sources checked**:
- [x] Claude Code official docs
- [x] Claude Code release notes / changelog
- [x] Community: undeadlist/claude-code-agents
- [x] Web search for recent Claude Code patterns

**Plugin context**: [1-2 sentence summary of current state]

---

### Adopt Now

#### [Suggestion 1]
[structured suggestion — see step 5]

#### [Suggestion 2]
...

### Plan for Next Session

#### [Suggestion 3]
...

### Watch

| Feature | Source | Why watching | Check again when |
|---------|--------|-------------|-----------------|
| [name] | [source] | [reason] | [trigger] |

### Skipped

| Feature | Source | Why skipped |
|---------|--------|------------|
| [name] | [source] | [reason] |

---

### Next Steps
1. [ ] [actionable item for "Adopt now" suggestions]
2. [ ] [actionable item]
3. [ ] Use `/meta-experiment-feature` to experiment with [specific feature]
```

---

## Example Usage

```
# Full discovery — check all sources
/meta-discover-claude-features

# Focused on official updates only
/meta-discover-claude-features check official docs only

# Looking for community patterns specifically
/meta-discover-claude-features what's the community doing with Claude Code agents?

# After a Claude Code version update
/meta-discover-claude-features Claude Code just updated — what's new and relevant?
```
