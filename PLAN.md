# Claude Code Library - Implementation Plan

## Overview

**Purpose**: A reusable library of Claude Code configurations (skills, hooks, rules, templates) that can be copied into other projects. Includes a test project to verify everything works.

**Source of truth**: `playbook/How I Use Claude Code.md` - all skills and patterns derive from this document.

**Core components**:
1. Production-ready skills organized by use-case
2. Reusable hooks for common automation needs
3. CLAUDE.md templates for different project types
4. A simple test project to verify skills work
5. Reference documentation for the audit skill

---

## Repo Structure

```
claude_experiments/
├── CLAUDE.md                           # Meta: rules for this repo
├── PLAN.md                             # This document
│
├── playbook/
│   └── How I Use Claude Code.md        # Source of truth (your philosophy)
│
├── library/
│   ├── skills/                         # Organized by use-case
│   │   ├── architecture/
│   │   │   └── arch/SKILL.md           # /arch - architecture mapping
│   │   │
│   │   ├── safe-changes/
│   │   │   ├── refactor_safe/SKILL.md  # /refactor_safe
│   │   │   └── impact_check/SKILL.md   # /impact_check
│   │   │
│   │   ├── planning/
│   │   │   ├── spec_from_text/SKILL.md # /spec_from_text
│   │   │   └── impl_plan/SKILL.md      # /impl_plan
│   │   │
│   │   ├── api-development/
│   │   │   └── api_impl/SKILL.md       # /api_impl
│   │   │
│   │   ├── quality-review/
│   │   │   ├── project_review/SKILL.md # /project_review
│   │   │   └── risk_prioritizer/SKILL.md # /risk_prioritizer
│   │   │
│   │   ├── learning/
│   │   │   └── codebase_mastery/SKILL.md # /codebase_mastery (tutor mode)
│   │   │
│   │   └── meta/
│   │       └── audit_setup/SKILL.md    # /audit_setup - audit any repo's setup
│   │
│   ├── hooks/                          # Reusable hook configurations
│   │   ├── logging/                    # Observe/notify hooks
│   │   │   └── README.md + settings.json snippets
│   │   ├── protection/                 # Blocking hooks
│   │   │   └── README.md + settings.json snippets
│   │   └── quality-gates/              # Lint/format hooks
│   │       └── README.md + settings.json snippets
│   │
│   ├── rules/                          # Reusable .claude/rules/ templates
│   │   ├── testing.md
│   │   ├── security.md
│   │   ├── api.md
│   │   └── style.md
│   │
│   └── templates/                      # CLAUDE.md templates by project type
│       ├── python-api/
│       │   └── CLAUDE.md
│       └── generic/
│           └── CLAUDE.md
│
├── test_project/                       # Simple project to verify skills work
│   ├── src/
│   │   ├── main.py
│   │   ├── api/routes.py
│   │   └── utils/helpers.py
│   ├── tests/
│   │   └── test_routes.py
│   ├── CLAUDE.md                       # Uses library templates
│   └── requirements.txt
│
├── .claude/                            # This repo's own Claude Code setup
│   ├── settings.local.json
│   ├── rules/
│   │   └── library.md                  # Rules for working in this repo
│   └── docs_reference/
│       └── claude_code_features.md     # Reference for audit skill
│
└── audits/                             # Output from /audit_setup
    └── .gitkeep
```

---

## Skills Library (from Playbook)

### 1. Architecture & Understanding

#### `/arch` - Architecture Mapping
**Source**: Playbook section 2.1
**Purpose**: Build mental model before touching code
**Use when**: Joining large repos, legacy systems, before refactoring

**Key outputs**:
- 10-line overview
- Component map
- Key execution paths (3-5)
- Critical files list
- Risks / tech debt / unknowns

---

### 2. Safe Changes

#### `/refactor_safe` - Safe Refactoring
**Source**: Playbook section 2.2
**Purpose**: Refactor like a senior reviewing a junior
**Use when**: Any refactor that touches multiple files or core logic

**Key outputs**:
- Restate current behavior
- List invariants
- Step-by-step plan with checkpoints
- Verification commands
- Review notes

#### `/impact_check` - Blast Radius Analysis
**Source**: Playbook section 2.3
**Purpose**: Understand what might break before risky changes
**Use when**: Changes to orchestration, auth, data schemas

**Key outputs**:
- Directly affected components
- Indirect dependencies
- Data/schema impact
- Test gaps
- Rollback strategy

---

### 3. Planning & Specs

#### `/spec_from_text` - Text to Spec Conversion
**Source**: Playbook section 2.4
**Purpose**: Turn vague business input into testable specs
**Use when**: Converting PM requirements, business cases to technical specs

**Key outputs**:
- Structured spec (YAML/JSON)
- Assumptions made
- Open questions
- Implied constraints

#### `/impl_plan` - Implementation Planning
**Source**: Playbook section 2.5
**Purpose**: Design first, code second
**Use when**: Before any non-trivial implementation

**Key outputs**:
- Goal + non-goals
- Ordered steps
- Tests per step
- Rollback plan

---

### 4. API Development

#### `/api_impl` - API Implementation
**Source**: Playbook section 2.6
**Purpose**: Implement inference endpoints consistently
**Use when**: Adding new API endpoints

**Key outputs**:
- Handler code
- Request/response models
- Unit tests
- OpenAPI updates
- "How to test locally" commands

---

### 5. Quality & Review

#### `/project_review` - Project Quality Assessment
**Source**: Playbook section 4
**Purpose**: Calibrated judgment with evidence
**Use when**: Assessing overall project health, tech debt

**Key outputs**:
- Provisional score (0-100) with confidence
- Category breakdown (8 categories)
- Evidence highlights (file paths)
- Top 5 risks
- Next 3 PR-sized improvements

#### `/risk_prioritizer` - Decision Support
**Source**: Playbook section 5
**Purpose**: Prioritize what matters vs what can wait
**Use when**: Planning refactors, deciding what NOT to fix

---

### 6. Learning

#### `/codebase_mastery` - Understanding + Tutor Mode
**Source**: Playbook section 3
**Purpose**: Deep understanding through active learning
**Use when**: Onboarding, understanding critical files, preparing to implement

**Two modes**:
- Deep Dive: structured understanding, call graphs, invariants
- Tutor: Claude asks YOU questions, you answer, Claude corrects

---

### 7. Meta

#### `/audit_setup` - Setup Audit
**Purpose**: Compare any repo's Claude Code setup against best practices
**Use when**: Setting up new projects, reviewing existing setups

---

## Hooks Library

### Logging Hooks (observe first)
- Log all file edits with timestamps
- Log tool invocations
- Notify on specific file patterns

### Protection Hooks (block dangerous actions)
- Block edits to `protected/`, `migrations/`, `infra/`
- Block edits to production configs
- Require confirmation for destructive commands

### Quality Gate Hooks
- Run lint on file save
- Run typecheck on edit
- Run tests on specific patterns

---

## Templates Library

### Python API Template ✅
- FastAPI/Flask conventions
- Structured logging
- Error handling patterns
- Test structure

### Generic Template ✅
- Minimal starting point
- Common patterns only

### Future (add as needed)
- Python ML Pipeline Template
- TypeScript API Template

---

## Implementation Status

### Phase 1: Foundation
**Status**: COMPLETE

**Completed**:
- ✅ Repo structure created
- ✅ Playbook moved to `playbook/`
- ✅ CLAUDE.md for repo
- ✅ Library-based organization
- ✅ All 10 skills extracted from playbook
- ✅ test_project with FastAPI app
- ✅ Rules templates (testing, security, api, style)
- ✅ Hook documentation (logging, protection, quality-gates)
- ✅ Templates (python-api, generic)

---

### Phase 2: Verification & Polish
**Status**: NOT STARTED

**Tasks**:
1. ⬜ Test each skill in test_project
2. ⬜ Verify templates work when copied to fresh project
3. ⬜ Add more templates as needed (python-ml-pipeline, typescript-api)

**Deliverables**:
- All skills verified working
- Templates tested
- Library ready for production use

---

## How to Use This Library

### Adding a skill to your project
```bash
# Copy the skill folder to your project
cp -r library/skills/architecture/arch/ your-project/.claude/skills/

# Use it
/arch focus on the API layer
```

### Adding hooks to your project
```bash
# Copy hook config snippet to your .claude/settings.json
# See library/hooks/*/README.md for snippets
```

### Using a template for a new project
```bash
# Copy the template
cp -r library/templates/python-api/* your-new-project/

# Customize CLAUDE.md for your specific project
```

### Auditing any project's setup
```bash
# Run from within the target project
/audit_setup
```

---

## Sync with Playbook

When `playbook/How I Use Claude Code.md` is updated:
1. Identify which skills/patterns changed
2. Update corresponding files in `library/`
3. Test changes in `test_project/`
4. Update this PLAN.md if structure changes

---

## Success Criteria

1. Can copy any skill to a new project and it works immediately
2. Templates provide useful starting points (not just boilerplate)
3. `/audit_setup` gives actionable feedback on any repo
4. Test project validates all skills work correctly
5. Easy to find what you need (organized by use-case)
