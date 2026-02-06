# Claude Code Features Reference

**Last updated**: 2025-02-06
**Source**: Official Claude Code documentation

This file serves as a local reference for the `/audit_setup` skill to compare against.

---

## 1. Memory System

### CLAUDE.md Files
- **Project root CLAUDE.md**: Loaded automatically, shared with team via git
- **.claude/CLAUDE.md**: Alternative location, same behavior
- **CLAUDE.local.md**: Personal notes, add to .gitignore

### .claude/rules/ Directory
- Markdown files loaded based on path matching
- Use `paths:` frontmatter for path-scoped rules
- Example: `api.md` with `paths: ["src/api/**"]`

### Memory Hierarchy
1. Managed policies (enterprise)
2. User settings (~/.claude/)
3. Project settings (.claude/, CLAUDE.md)

---

## 2. Skills

### Structure
```
.claude/skills/
└── skill_name/
    └── SKILL.md
```

### Invocation
- User types `/skill_name` or `/skill_name args`
- Claude can invoke if not restricted

### Safety Controls
- `disable-model-invocation: true` in frontmatter prevents auto-invocation
- Useful for destructive or dangerous skills

### Best Practices
- Clear goal statement
- Structured output format
- Step-by-step process

---

## 3. Hooks

### Events
- `PreToolCall` - Before a tool executes
- `PostToolCall` - After a tool executes
- `Notification` - For notifications
- `Stop` - When Claude stops

### Configuration
In `.claude/settings.json` or `.claude/settings.local.json`:
```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": "Edit",
        "command": "echo 'File being edited: $CLAUDE_FILE_PATH'"
      }
    ]
  }
}
```

### Hook Behavior
- Exit 0: Continue
- Exit 2: Block the action
- Other exit codes: Warning but continue

### Environment Variables
- `CLAUDE_TOOL_NAME` - Name of the tool
- `CLAUDE_FILE_PATH` - File being operated on
- Tool-specific variables available

---

## 4. Subagents (Task Tool)

### When to Use
- Parallel independent tasks
- Isolated context (prevent pollution)
- Noisy operations (repo-wide scans)

### Configuration
- `allow`: List of allowed tools
- `deny`: List of denied tools
- Both: allow takes precedence

### Agent Types
- `Explore` - Codebase exploration
- `Plan` - Implementation planning
- `Bash` - Command execution
- `general-purpose` - Multi-step tasks

---

## 5. MCP (Model Context Protocol)

### Purpose
Connect Claude to external tools and data sources

### Configuration
In `.claude/settings.json`:
```json
{
  "mcpServers": {
    "server_name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

### Common Servers
- Filesystem access
- Database connections
- API integrations

---

## 6. Custom Agents (SDK)

### Purpose
Build specialized agents with custom behaviors

### Key Concepts
- Agent definition
- Tool binding
- Orchestration patterns

---

## Feature Checklist for Audits

- [ ] CLAUDE.md exists with run commands
- [ ] Invariants documented
- [ ] Path-scoped rules used where appropriate
- [ ] Skills organized in .claude/skills/
- [ ] Dangerous skills have disable-model-invocation
- [ ] Hooks for automation/safety
- [ ] MCP configured for external integrations
- [ ] CLAUDE.local.md for personal notes (gitignored)
