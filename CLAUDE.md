# Claude Code Library (Plugin)

## Purpose

A reusable Claude Code **plugin** that provides skills, agents, hooks, and rules to any project. Connect once, use everywhere — no copying files.

## Quick Start

### One-time use
```bash
claude --plugin-dir /path/to/claude_experiments
```

### Permanent setup (no flag needed)

Create a shell alias so `claude-lib` works from any project. See README.md for full step-by-step guides per OS.

**Windows (PowerShell):** Add to `$PROFILE`:
```powershell
function claude-lib { claude --plugin-dir "C:\path\to\claude_experiments" $args }
```

**macOS/Linux (Bash/Zsh):** Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias claude-lib='claude --plugin-dir /path/to/claude_experiments'
```

Then run `claude-lib` from any project — identical to `claude` but with the plugin pre-loaded.

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
│   ├── session-wrapup/
│   ├── api-development-api-impl/
│   ├── quality-review/
│   ├── quality-strategic-advisor/
│   ├── quality-upgrade-advisor/
│   ├── learning-codebase-mastery/
│   ├── learning-algo-practice/
│   ├── learning-concept-recall/
│   ├── learning-debug-training/
│   ├── learning-code-review-eye/
│   ├── learning-pair-programming/
│   ├── meta-discover-claude-features/
│   ├── meta-experiment-feature/
│   ├── meta-project-setup/
│   ├── meta-skill-audit/
│   └── meta-update-docs/
├── agents/                       # Agent definitions
│   ├── code-reviewer.md
│   └── learning-coach.md
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

Skills are organized by **development phase**. **Essential** = don't skip. *If needed* = use when the situation fits.

| Phase | | Skill | Purpose |
|-------|--|-------|---------|
| **Setup & Onboarding** | **Essential** | `/meta-project-setup` | Audit setup, recommend artifacts |
| | **Essential** | `/architecture-arch` | Map codebase structure |
| | *If needed* | `/quality-review` | Health audit + priority matrix |
| | *If needed* | `/quality-strategic-advisor` | Research domain, suggest new features and capabilities |
| | *If needed* | `/quality-upgrade-advisor` | Upgrade roadmap for stale deps |
| | *If needed* | `/learning-codebase-mastery` | Deep dive + tutor quiz + recent changes quiz |
| **Planning & Design** | **Essential** | `/planning-impl-plan` | Design before coding |
| | *If needed* | `/planning-spec-from-text` | Convert vague input to specs |
| **Building** | *If needed* | `/learning-pair-programming` | Pair program with Claude as guide |
| | *If needed* | `/api-development-api-impl` | Consistent endpoint implementation |
| **Reviewing & Refactoring** | **Essential** | `code-reviewer` agent | Review code after changes |
| | *If needed* | `/code-diagnosis` | Scan for bugs, smells, refactoring opportunities |
| | *If needed* | `/safe-changes-impact-check` | Check blast radius |
| | *If needed* | `/safe-changes-refactor-safe` | Refactor with explicit invariants |
| **Wrapping Up** | **Essential** | `/session-wrapup` | Record progress, sync docs, set next steps |
| **Skill Building** | | `/learning-algo-practice` | Algorithm & interview prep |
| | | `/learning-concept-recall` | Spaced repetition for DS concepts |
| | | `/learning-debug-training` | Systematic debugging training |
| | | `/learning-code-review-eye` | Train code review skills |
| **Library Maintenance** | | `/meta-discover-claude-features` | Scout official docs + community for new features to adopt |
| | | `/meta-experiment-feature` | Experiment with a known feature |
| | | `/meta-skill-audit` | Audit library for overlaps/gaps |
| | | `/meta-update-docs` | Fix stale cross-references |

## Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Expert code review after writing/modifying code |
| `learning-coach` | Persistent learning coach for all learning skills — tracks progress, weak areas, and mastery across sessions via `memory: user` |

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
