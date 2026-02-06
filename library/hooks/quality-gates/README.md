# Quality Gate Hooks

Hooks that enforce code quality standards.

## Use When
- Ensuring lint passes before edits complete
- Running formatters automatically
- Enforcing type checks

## Configuration Snippets

Add to `.claude/settings.json` or `.claude/settings.local.json`:

### Run Lint After Python Edits

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit|Write",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.py$'; then ruff check \"$CLAUDE_FILE_PATH\" || echo 'Lint issues found'; fi"
      }
    ]
  }
}
```

### Auto-Format on Save

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit|Write",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.py$'; then ruff format \"$CLAUDE_FILE_PATH\"; fi"
      }
    ]
  }
}
```

### TypeScript Lint

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit|Write",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.[tj]sx?$'; then npx eslint \"$CLAUDE_FILE_PATH\" --fix || true; fi"
      }
    ]
  }
}
```

### Run Affected Tests

```json
{
  "hooks": {
    "PostToolCall": [
      {
        "matcher": "Edit",
        "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.py$'; then pytest \"tests/test_$(basename $CLAUDE_FILE_PATH)\" --tb=short 2>/dev/null || true; fi"
      }
    ]
  }
}
```

## Notes

- Quality gates should generally not block (use `|| true`)
- Keep hook execution fast to avoid slowdowns
- Consider running heavier checks only on commit
