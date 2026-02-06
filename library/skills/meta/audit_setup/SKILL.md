# Skill: audit_setup

**Purpose**: Compare any repo's Claude Code setup against best practices

**Use when**:
- Setting up Claude Code in a new project
- Reviewing existing setup for improvements
- Ensuring you're using available features

---

## Process

### 1) Scan Current Setup

Examine the project for Claude Code configuration:

- Read CLAUDE.md (project root)
- Read .claude/CLAUDE.md (if exists)
- Read CLAUDE.local.md (if exists)
- List all skills in .claude/skills/
- List all rules in .claude/rules/
- Check for hooks in .claude/settings.json or .claude/settings.local.json
- Check for MCP configuration

### 2) Compare Against Best Practices

For each feature category, determine:
- Is this feature being used?
- Is it configured correctly?
- Are there improvements to suggest?
- Are there anti-patterns present?

### 3) Generate Report

---

## Output Format

```markdown
# Claude Code Setup Audit

**Date**: [current date]
**Project**: [project path]

## A) Current Setup Summary

| Feature | Status | Notes |
|---------|--------|-------|
| CLAUDE.md | [exists/missing] | [brief assessment] |
| .claude/rules/ | [X files] | [assessment] |
| .claude/skills/ | [X skills] | [assessment] |
| Hooks | [configured/none] | [assessment] |
| MCP | [configured/none] | [assessment] |
| CLAUDE.local.md | [exists/missing] | |

## B) Features In Use

### [Feature Name]
- **Status**: Configured
- **Quality**: [Good / Needs improvement]
- **Notes**: [specific observations]

## C) Features Not In Use

### [Feature Name]
- **Recommendation**: [why you might want this]
- **Priority**: [High/Medium/Low]
- **Example**: [how to add it]

## D) Suggested Improvements

1. **[Improvement]** (Priority: H/M/L)
   - Current: [what exists now]
   - Suggested: [what to change]
   - Why: [benefit]

## E) Anti-Patterns Detected

- **[Pattern]**: [explanation and fix]

## F) Next 3 Actions

1. [Specific actionable task with file paths]
2. [Specific actionable task with file paths]
3. [Specific actionable task with file paths]
```

---

## Feature Checklist

### Memory
- [ ] CLAUDE.md exists with project purpose
- [ ] Run commands documented
- [ ] Invariants/conventions listed
- [ ] .claude/rules/ used for topic-specific rules
- [ ] Path-scoped rules where appropriate
- [ ] CLAUDE.local.md for private notes (gitignored)

### Skills
- [ ] Skills organized in .claude/skills/
- [ ] Each skill has clear goal and process
- [ ] Dangerous skills have `disable-model-invocation: true`

### Hooks
- [ ] Logging hooks for audit trail (if needed)
- [ ] Protection hooks for sensitive paths (if needed)
- [ ] Quality gate hooks (lint/format)

### Safety
- [ ] .gitignore includes CLAUDE.local.md
- [ ] No secrets in CLAUDE.md
- [ ] Stateful skills require explicit invocation

---

## Example Usage

```
# Full audit
/audit_setup

# Save to file
/audit_setup save report to audits/

# Focus on specific area
/audit_setup focus on skills configuration
```
