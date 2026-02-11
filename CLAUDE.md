# Claude Code Library (Plugin)

## Purpose

A reusable Claude Code **plugin** that provides skills, agents, hooks, and rules to any project. Connect once, use everywhere — no copying files.

## Quick Start

### Connect to any project
```bash
# One-time use from any project
claude --plugin-dir /path/to/claude_experiments
```

### Permanent setup (no flag needed)

Add to **`~/.claude/settings.json`** (global — all projects) or **`your-project/.claude/settings.json`** (per-project):

```json
{
  "enabledPlugins": {
    "claude-library@local-library": true
  },
  "extraKnownMarketplaces": {
    "local-library": {
      "source": {
        "source": "directory",
        "path": "/path/to/claude_experiments"
      }
    }
  }
}
```

Then just run `claude` — the plugin loads automatically.

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
│   ├── code-diagnosis/
│   ├── safe-changes-refactor-safe/
│   ├── safe-changes-impact-check/
│   ├── planning-spec-from-text/
│   ├── planning-impl-plan/
│   ├── api-development-api-impl/
│   ├── quality-review/
│   ├── learning-codebase-mastery/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   ├── learning-code-review-eye/
│   ├── meta-experiment-feature/
│   ├── meta-project-setup/
│   ├── meta-skill-audit/
│   └── meta-sync-references/
├── agents/                       # Agent definitions
│   └── code-reviewer.md
├── hooks/                        # Hook configurations
│   └── hooks.json
├── documentation/                # All generated .md docs go here
│   ├── PROBLEM_STATEMENT.md
│   └── BRAINSTORMING.md
├── library/                      # Reference material
│   ├── hooks/                    # Hook examples by category
│   ├── rules/                    # Reusable rule templates
│   └── templates/                # CLAUDE.md templates
├── playbook/                     # Source of truth
├── test_project/                 # Verification project
├── tests/                        # Validation scripts
└── experiments/                  # Feature experiments
```

## Available Skills

Skills are organized by workflow phase:

| Phase | Skill | Purpose |
|-------|-------|---------|
| **Understand** | `/architecture-arch` | Build mental model before coding |
| **Understand** | `/learning-codebase-mastery` | Deep understanding + tutor mode |
| **Diagnose** | `/code-diagnosis` | Targeted scan for bugs, smells, refactoring opportunities |
| **Diagnose** | `/quality-review` | Repo-wide health audit + prioritized improvements |
| **Plan** | `/planning-spec-from-text` | Convert vague input to specs |
| **Plan** | `/planning-impl-plan` | Design before coding |
| **Build** | `/api-development-api-impl` | Consistent endpoint implementation |
| **Build** | `/safe-changes-refactor-safe` | Refactor with explicit invariants |
| **Build** | `/safe-changes-impact-check` | Understand blast radius |
| **Learn** | `/learning-algo-practice` | Algorithm & interview prep for data scientists |
| **Learn** | `/learning-concept-recall` | Spaced repetition for DS concepts |
| **Learn** | `/learning-debug-training` | Systematic debugging training |
| **Learn** | `/learning-code-review-eye` | Train your code review skills |
| **Maintain** | `/meta-experiment-feature` | Set up experiments for new features |
| **Maintain** | `/meta-project-setup` | Audit setup, recommend artifacts, detect library gaps |
| **Maintain** | `/meta-skill-audit` | Audit library for overlaps and gaps |
| **Maintain** | `/meta-sync-references` | Sync cross-references across all files |

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
