# Claude Code Library (Plugin)

## Purpose

A reusable Claude Code **plugin** that provides skills, agents, hooks, and rules to any project. Connect once, use everywhere — no copying files.

## Quick Start

### Connect to any project
```bash
# Use as a plugin from any project
claude --plugin-dir /path/to/claude_experiments

# Or add to your project's .claude/settings.json:
# { "plugins": ["/path/to/claude_experiments"] }
```

### Plugin skills are namespaced
```bash
/claude-library:architecture-arch    # Build mental model of codebase
/claude-library:meta-project-setup   # Analyze project & get recommendations
```

## Key Commands

```bash
# Test the test_project
cd test_project && pip install -r requirements.txt && pytest

# Run the test API
cd test_project && uvicorn src.main:app --reload
```

## Repo Structure

```
claude_experiments/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/                       # Plugin skills (auto-discovered)
│   ├── architecture-arch/
│   ├── safe-changes-refactor-safe/
│   ├── safe-changes-impact-check/
│   ├── planning-spec-from-text/
│   ├── planning-impl-plan/
│   ├── api-development-api-impl/
│   ├── quality-review/
│   ├── learning-codebase-mastery/
│   ├── meta-experiment-feature/
│   ├── meta-project-setup/
│   ├── meta-skill-audit/
│   ├── meta-sync-references/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   └── learning-code-review-eye/
├── agents/                       # Agent definitions
│   └── code-reviewer.md
├── hooks/                        # Hook configurations
│   └── hooks.json
├── documentation/                # All generated .md docs go here
│   ├── PLAN.md
│   ├── PROBLEM_STATEMENT.md
│   ├── BRAINSTORMING.md
│   ├── SKILL_AUDIT.md
│   └── CLAUDE_SETUP.md
├── library/                      # Reference material
│   ├── hooks/                    # Hook examples by category
│   ├── rules/                    # Reusable rule templates
│   └── templates/                # CLAUDE.md templates
├── playbook/                     # Source of truth
├── test_project/                 # Verification project
└── experiments/                  # Feature experiments
```

## Available Skills

| Use Case | Skill | Purpose |
|----------|-------|---------|
| Architecture | `/architecture-arch` | Build mental model before coding |
| Safe Changes | `/safe-changes-refactor-safe` | Refactor with explicit invariants |
| Safe Changes | `/safe-changes-impact-check` | Understand blast radius |
| Planning | `/planning-spec-from-text` | Convert vague input to specs |
| Planning | `/planning-impl-plan` | Design before coding |
| API Dev | `/api-development-api-impl` | Consistent endpoint implementation |
| Quality | `/quality-review` | Assess quality + prioritize improvements |
| Learning | `/learning-codebase-mastery` | Deep understanding + tutor mode |
| Learning | `/learning-algo-practice` | Algorithm & interview prep for data scientists |
| Learning | `/learning-concept-recall` | Spaced repetition for DS concepts |
| Learning | `/learning-debug-training` | Systematic debugging training |
| Learning | `/learning-code-review-eye` | Train your code review skills |
| Meta | `/meta-experiment-feature` | Set up experiments for new features |
| Meta | `/meta-project-setup` | Audit setup, recommend artifacts, detect library gaps |
| Meta | `/meta-skill-audit` | Audit library for overlaps and gaps |
| Meta | `/meta-sync-references` | Sync cross-references across all files |

## Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Expert code review after writing/modifying code |

## How to Use

### As a plugin (recommended)
```bash
claude --plugin-dir /path/to/claude_experiments
# Then use: /claude-library:meta-project-setup
```

### Copy individual artifacts
```bash
# Copy a rule to your project
cp library/rules/api.md your-project/.claude/rules/

# Copy a template
cp library/templates/python-api/CLAUDE.md your-project/

# Copy hooks config
cp hooks/hooks.json your-project/.claude/hooks.json
```

## Invariants

1. **Playbook is source of truth** - All skills derive from `playbook/How I Use Claude Code.md`
2. **Plugin-first** - Skills live in `skills/` for plugin discovery
3. **Hyphenated names** - Skill names use hyphens only (no underscores) per Claude Code spec
4. **Self-contained** - Each skill works independently when loaded via plugin
5. **Organized by use-case** - Not by feature type
