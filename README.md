# Claude Code Library

A production-ready library of Claude Code configurations — skills, hooks, rules, and templates — that you can copy directly into your projects.

## Why This Exists

Setting up Claude Code effectively requires more than just installing it. You need:
- **Skills** that enforce consistent workflows (safe refactoring, architecture mapping, code review)
- **Hooks** that automate quality gates and protect sensitive files
- **Rules** that teach Claude your project's conventions
- **Templates** to bootstrap new projects quickly

This library provides all of these, extracted from real-world usage patterns documented in the [playbook](playbook/How%20I%20Use%20Claude%20Code.md).

---

## Quick Start

### Copy a skill to your project

```bash
# Copy the architecture mapping skill
cp -r library/skills/architecture/arch/ your-project/.claude/skills/

# Use it
/arch focus on the API layer
```

### Copy a template for a new project

```bash
cp library/templates/python-api/CLAUDE.md your-new-project/CLAUDE.md
```

### Add a hook

Copy snippets from `library/hooks/*/README.md` into your `.claude/settings.json`.

---

## Available Skills

| Category | Skill | Purpose |
|----------|-------|---------|
| **Architecture** | `/arch` | Build mental model before touching code |
| **Safe Changes** | `/refactor_safe` | Refactor with explicit invariants and checkpoints |
| **Safe Changes** | `/impact_check` | Understand blast radius before risky changes |
| **Planning** | `/spec_from_text` | Convert vague requirements into testable specs |
| **Planning** | `/impl_plan` | Design implementation before coding |
| **API Development** | `/api_impl` | Implement endpoints with consistent patterns |
| **Quality Review** | `/project_review` | Evidence-based project quality assessment |
| **Quality Review** | `/risk_prioritizer` | Prioritize what matters vs what can wait |
| **Learning** | `/codebase_mastery` | Deep understanding + interactive tutor mode |
| **Meta** | `/audit_setup` | Audit any repo's Claude Code configuration |

---

## Repository Structure

```
claude_experiments/
├── playbook/                    # Source of truth
│   └── How I Use Claude Code.md # Philosophy and patterns
│
├── library/
│   ├── skills/                  # Ready-to-copy skills
│   │   ├── architecture/
│   │   ├── safe-changes/
│   │   ├── planning/
│   │   ├── api-development/
│   │   ├── quality-review/
│   │   ├── learning/
│   │   └── meta/
│   │
│   ├── hooks/                   # Hook configuration examples
│   │   ├── logging/             # Audit trail hooks
│   │   ├── protection/          # Block dangerous actions
│   │   └── quality-gates/       # Lint/format automation
│   │
│   ├── rules/                   # Reusable .claude/rules/ files
│   │   ├── testing.md
│   │   ├── security.md
│   │   ├── api.md
│   │   └── style.md
│   │
│   └── templates/               # CLAUDE.md templates
│       ├── python-api/
│       └── generic/
│
├── test_project/                # Verify skills work here
│
└── audits/                      # Output from /audit_setup
```

---

## Skill Highlights

### `/arch` — Architecture Mapping

Before touching unfamiliar code, map it first:

```
/arch focus on:
- how requests flow from API to database
- where authentication is enforced
- what the main execution paths are
```

**Output**: 10-line overview, component map, execution paths, critical files, risks.

---

### `/refactor_safe` — Safe Refactoring

Refactor like a senior engineer reviewing a junior:

```
/refactor_safe
Goal: extract validation logic into separate module
Constraints:
- keep all existing tests passing
- no API changes
```

**Output**: Current behavior, invariants, step-by-step plan with checkpoints, verification commands.

---

### `/project_review` — Quality Assessment

Get calibrated, evidence-based project assessment:

```
/project_review run tests if possible; focus on test quality and architecture
```

**Output**: Score (0-100) with confidence level, category breakdown, evidence with file paths, top risks, next 3 PR-sized improvements.

---

### `/codebase_mastery` — Learning Mode

Two modes for deep understanding:

```
# Deep dive analysis
/codebase_mastery src/auth/

# Interactive tutor mode (Claude asks YOU questions)
/codebase_mastery tutor src/api/routes.py
```

---

## Hook Examples

### Block edits to protected paths

```json
{
  "hooks": {
    "PreToolCall": [{
      "matcher": "Edit|Write",
      "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -qE '^(migrations/|.env)'; then echo 'BLOCKED' && exit 2; fi"
    }]
  }
}
```

### Auto-format Python files

```json
{
  "hooks": {
    "PostToolCall": [{
      "matcher": "Edit|Write",
      "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q '\\.py$'; then ruff format \"$CLAUDE_FILE_PATH\"; fi"
    }]
  }
}
```

See `library/hooks/*/README.md` for more examples.

---

## The Philosophy

This library is built on a core principle:

> **Claude is a junior engineer + reviewer + tutor — never an autopilot.**

Key patterns:
- **Plan before code**: Use `/impl_plan` and `/refactor_safe` to think first
- **Explicit invariants**: Always state what must not change
- **Small checkpoints**: Verify after each step, not at the end
- **Evidence-based**: Scores without file paths and confidence levels are ignored

Read the full philosophy: [playbook/How I Use Claude Code.md](playbook/How%20I%20Use%20Claude%20Code.md)

---

## Contributing

1. Update the playbook with new patterns
2. Extract into `library/` following existing structure
3. Test in `test_project/`
4. Update this README if adding new skills

---

## License

MIT
