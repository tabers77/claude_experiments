# Protection Hooks

Blocking hooks that prevent dangerous actions.

## Use When
- Protecting production configs
- Preventing accidental migrations
- Enforcing review for sensitive paths

## Configuration Snippets

Add to `.claude/settings.json` or `.claude/settings.local.json`:

### Block Edits to Protected Paths

```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": "Edit|Write",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -qE '^(protected/|migrations/|.env)'; then echo \"BLOCKED: Cannot modify protected path: $CLAUDE_FILE_PATH\" && exit 2; fi"
      }
    ]
  }
}
```

### Block Destructive Git Commands

```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": "Bash",
        "command": "if echo \"$CLAUDE_COMMAND\" | grep -qE 'git (push --force|reset --hard|clean -f)'; then echo \"BLOCKED: Destructive git command requires manual execution\" && exit 2; fi"
      }
    ]
  }
}
```

### Require Confirmation for Specific Files

```json
{
  "hooks": {
    "PreToolCall": [
      {
        "matcher": "Edit",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q 'schema\\|migration'; then echo \"WARNING: Modifying schema/migration file. Review carefully.\"; fi"
      }
    ]
  }
}
```

## Exit Codes

- `exit 0` - Allow action to proceed
- `exit 2` - Block the action
- Other codes - Warning but continue

## Notes

- Start with warnings (`exit 0`) before blocking (`exit 2`)
- Test hooks thoroughly before enabling blocking
- Keep blocked paths list minimal and intentional
