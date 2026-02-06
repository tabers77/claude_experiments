# Logging Hooks

Observe-first hooks that log actions without blocking.

## Use When
- You want audit trails
- Debugging Claude's behavior
- Understanding what's being modified

## Configuration Snippets

Add to `.claude/settings.json` or `.claude/settings.local.json`:

### Log All File Edits

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit|Write",
        "command": "echo \"[$(date)] Edited: $CLAUDE_FILE_PATH\" >> .claude/edit_log.txt"
      }
    ]
  }
}
```

### Log Tool Invocations

```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": ".*",
        "command": "echo \"[$(date)] Tool: $CLAUDE_TOOL_NAME\" >> .claude/tool_log.txt"
      }
    ]
  }
}
```

### Notify on Specific Patterns

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q 'config\\|secret\\|auth'; then echo \"ALERT: Sensitive file modified: $CLAUDE_FILE_PATH\"; fi"
      }
    ]
  }
}
```

## Notes

- Logging hooks should exit 0 to not block actions
- Keep log paths in `.gitignore` if they contain sensitive info
- Consider log rotation for long-running sessions
