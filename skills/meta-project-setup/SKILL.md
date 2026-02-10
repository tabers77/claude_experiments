---
name: meta-project-setup
description: Analyze any project, audit its Claude Code setup, recommend existing library artifacts, and detect gaps where new skills should be created. Generates documentation/CLAUDE_SETUP.md with full analysis.
---

# Skill: project_setup

**Purpose**: Analyze any project, recommend existing library artifacts, and detect gaps where new skills/agents/hooks should be created.

**Use when**:
- Starting work on a new project with this plugin active
- Want to know which skills/agents/hooks fit a specific codebase
- Want to discover what new skills the library is missing for this project
- Need a tailored CLAUDE.md and rules generated for a project
- Onboarding to a project and want optimal Claude Code configuration

**Tip**: You can pass natural language arguments to focus on specific steps. For example:
```
/meta-project-setup only detect gaps for this project
/meta-project-setup just audit the existing Claude setup
```

---

## Process

### Step 1: Accept Target

Determine the target project:
- If invoked with a path argument, use that path
- If no argument, use the current working directory
- Confirm the target with the user before proceeding

### Step 2: Fingerprint the Project

Scan the target project across 7 dimensions:

#### A) Language & Framework
- Search for: `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, `Gemfile`, `*.csproj`
- Identify primary language(s) and frameworks (FastAPI, Django, Express, Next.js, etc.)
- Note package manager (pip, npm, cargo, etc.)

#### B) Project Type
- **Service/API**: Has routes, endpoints, server entrypoint
- **Library**: Has setup.py/pyproject.toml with package config, no server
- **CLI**: Has argparse/click/clap, console entrypoint
- **Pipeline**: Has DAGs, schedulers, ETL patterns
- **Monorepo**: Multiple packages/services in subdirectories
- **Frontend**: Has React/Vue/Angular, HTML templates

#### C) Test Infrastructure
- Search for: `tests/`, `test/`, `__tests__/`, `spec/`, `*_test.go`
- Identify framework: pytest, jest, mocha, go test, cargo test
- Check for: fixtures, conftest.py, test utilities, CI test commands
- Estimate coverage: many tests / some / few / none

#### D) CI/CD
- Search for: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `Dockerfile`, `docker-compose.yml`
- Identify: build, test, deploy, lint steps

#### E) Quality Tools
- Search for: ruff, flake8, eslint, prettier, black, mypy, pyright, tsc, clippy
- Check configs: `pyproject.toml [tool.*]`, `.eslintrc`, `tsconfig.json`, `rustfmt.toml`

#### F) Sensitive Areas
- Search for: `auth/`, `middleware/`, `migrations/`, `config/`, `secrets`, `.env`
- Identify: authentication code, database schemas, configuration management

#### G) Existing Claude Setup (Audit)
Perform a full best-practice audit of the project's Claude Code configuration:

- Check for: `CLAUDE.md`, `.claude/`, `.claude/rules/`, `.claude/skills/`, `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.local.md`
- Check for MCP server configuration
- Assess: what's already configured vs what's missing

**Best-Practice Checklist** (check each item):

| Category | Check | Status |
|----------|-------|--------|
| **Memory** | CLAUDE.md exists with project purpose | |
| **Memory** | Run commands documented | |
| **Memory** | Invariants/conventions listed | |
| **Memory** | .claude/rules/ used for topic-specific rules | |
| **Memory** | CLAUDE.local.md for private notes (gitignored) | |
| **Skills** | Skills organized in .claude/skills/ | |
| **Skills** | Each skill has clear goal and process | |
| **Skills** | Dangerous skills have `disable-model-invocation: true` | |
| **Hooks** | Quality gate hooks (lint/format) | |
| **Hooks** | Protection hooks for sensitive paths | |
| **Hooks** | Logging hooks for audit trail (if needed) | |
| **Safety** | .gitignore includes CLAUDE.local.md | |
| **Safety** | No secrets in CLAUDE.md | |

**Anti-Pattern Detection** — flag if found:
- Secrets or API keys in CLAUDE.md (should be in CLAUDE.local.md)
- Overly broad rules that conflict with each other
- Skills without clear purpose or duplicate skills
- Missing .gitignore for local config files
- Hooks referencing tools that aren't installed

### Step 3: Match Fingerprint to Library Artifacts

Use the fingerprint to recommend artifacts from this plugin. Apply these rules:

| Fingerprint Signal | Recommended Artifact | Reasoning |
|--------------------|---------------------|-----------|
| Any project | `/architecture-arch` | Always useful for understanding before changing |
| Has tests | `/safe-changes-refactor-safe` | Can verify invariants via existing tests |
| Has API routes | `/api-development-api-impl` | Consistent endpoint patterns |
| Has API routes | `rules/api.md` | API conventions |
| Complex/large codebase | `/learning-codebase-mastery` | Deep understanding needed |
| Has CI/CD | `/safe-changes-impact-check` | Changes have automated blast radius |
| Has sensitive areas | `/safe-changes-impact-check` | Extra care needed |
| Has sensitive areas | `rules/security.md` | Security conventions |
| Has quality tools | `hooks/quality-gates` | Automate lint/format |
| Has Python | `hooks/quality-gates` (ruff) | Python-specific quality |
| Has TypeScript | `hooks/quality-gates` (eslint) | TS-specific quality |
| Has migrations/DB | `hooks/protection` | Protect schema files |
| Planning phase | `/planning-impl-plan` | Design before coding |
| Vague requirements | `/planning-spec-from-text` | Structure requirements first |
| Tech debt present | `/quality-review` | Assess + prioritize what matters |
| No Claude setup | Step 2G audit covers this | Baseline assessment built-in |
| Any project | `/quality-review` | Quality assessment |
| Any project | `code-reviewer` agent | Automated review after changes |
| Any project | `rules/style.md` | Code style conventions |
| Has tests | `rules/testing.md` | Test conventions |

### Step 4: Detect Library Gaps

Compare the project fingerprint against the full library inventory. For each technology, pattern, or workflow the project uses, check if any existing skill/agent/hook covers it. If not, flag it as a gap.

#### How to detect gaps

For each item found in the fingerprint, ask: **"Does the library have a skill that helps with this?"**

| Project Signal | What the project needs | Check against library |
|---------------|----------------------|---------------------|
| Has DB/migrations (Alembic, Django migrations, Prisma) | Safe schema change workflow, migration review | Only hook protection exists — no active skill |
| Has async workers (Celery, Bull, Sidekiq) | Task queue patterns, retry logic, dead letter handling | No skill covers this |
| Has GraphQL (Apollo, Strawberry, Ariadne) | GraphQL schema design, resolver patterns | `/api-development-api-impl` is REST-only |
| Has WebSockets / real-time | Connection lifecycle, broadcast patterns | No skill covers this |
| Has Docker/K8s/deploy configs | Deployment checklist, container best practices | No skill covers this |
| Has ML/data pipeline (Airflow, dbt, pandas) | Pipeline testing, data validation | No skill covers this |
| Has complex auth (OAuth, JWT, RBAC) | Auth implementation guide, security review | `rules/security.md` is passive — no active skill |
| Has monitoring/observability (Prometheus, Datadog, Sentry) | Observability patterns, alert design | No skill covers this |
| Has caching (Redis, Memcached) | Cache strategy, invalidation patterns | No skill covers this |
| Has microservices / service mesh | Inter-service communication, contract testing | No skill covers this |
| Has scheduled jobs (cron, APScheduler) | Job scheduling patterns, failure handling | No skill covers this |
| Has complex state (Redux, Zustand, MobX) | State management patterns | No skill covers this |
| Has i18n/l10n | Internationalization workflow | No skill covers this |
| Has file uploads / storage (S3, GCS) | File handling patterns, security | No skill covers this |
| No tests found | Test strategy and scaffolding | `rules/testing.md` is passive — no active skill for test design |
| No CI/CD found | CI pipeline setup | No skill covers this |
| Complex debugging needed | Structured debugging workflow | No skill covers this |
| Needs documentation | Doc generation, API docs | No skill covers this |
| Has many dependencies | Dependency audit, upgrade strategy | No skill covers this |

**Important**: Only flag gaps that are **relevant to this specific project**. Don't list every possible gap — only the ones where the project actually uses the technology.

#### For each gap found, provide:

1. **What's missing**: Which project need has no library coverage
2. **Artifact type**: What should be created (Skill / Agent / Hook / Rule)
3. **Suggested name**: Following the `category-name` convention
4. **What it would do**: 2-3 sentence description of the new component
5. **Priority**: High (project uses this daily) / Medium (occasional need) / Low (nice to have)
6. **Could extend**: Whether an existing skill could be expanded instead of creating a new one

### Step 5: Build Tailored Workflows

Group recommendations into 3 workflows with project-specific examples:

#### Onboarding Workflow
"First time working on this project"
1. Run `/architecture-arch` on [specific entrypoint found]
2. Run `/learning-codebase-mastery` on [critical module found]
3. Review with `/quality-review`

#### Development Workflow
"Day-to-day coding"
1. Plan with `/planning-impl-plan` before features
2. Use `/api-development-api-impl` for [specific route pattern found]
3. Check with `/safe-changes-impact-check` before [sensitive areas found]
4. Review with `code-reviewer` agent after changes

#### Quality Workflow
"Before merging / releasing"
1. Run `/quality-review` for overall health + prioritized improvements
3. Run `/safe-changes-refactor-safe` for cleanup work

### Step 6: Present Recommendations

Output the full recommendation report to the console (see Output Format below).
Wait for user confirmation before generating files.

### Step 7: Staged Rollout Advice

Recommend a phased adoption:

**Day 1** (immediate value):
- Copy recommended rules to `.claude/rules/`
- Add CLAUDE.md with project basics
- Start using `/architecture-arch` and `/quality-review`

**Week 1** (daily workflow):
- Enable hooks for quality gates
- Use `/planning-impl-plan` before features
- Use `code-reviewer` agent after changes

**Week 2+** (full integration):
- Add protection hooks for sensitive areas
- Use `/safe-changes-impact-check` before risky changes
- Re-run `/meta-project-setup` periodically to check setup health

### Step 8: Generate `documentation/CLAUDE_SETUP.md`

After presenting recommendations, **always generate a `documentation/CLAUDE_SETUP.md` file** in the `documentation/` directory. This file is the persistent, readable summary of the setup analysis.

The file MUST include:

1. **Project fingerprint table** — the 7-dimension scan results
2. **Setup audit** — best-practice checklist results, anti-patterns detected, features in use vs missing
3. **Recommended artifacts** — skills, agents, rules, hooks with reasons
4. **Library gaps** — project needs not covered by any existing skill, with suggestions for new components to create
5. **Visual workflow diagram** — ASCII flowchart showing how commands connect in practice (see Diagram section below)
6. **Tailored workflows** — onboarding, development, quality with project-specific arguments
7. **Staged rollout** — Day 1 / Week 1 / Week 2+ checklist

### Step 9: (Optional) Generate Additional Files

If the user requests, also generate:
- `CLAUDE.md` for the target project (using appropriate template)
- `.claude/rules/` files (copy recommended rules)

---

## Visual Workflow Diagram

The `documentation/CLAUDE_SETUP.md` MUST contain an ASCII flowchart (inside a code block) that shows the practical decision flow for using commands in the project. Use ASCII art so it renders everywhere — no Mermaid.

Adapt the diagram based on the project fingerprint — only include commands that were recommended.

Use this as a template and customize based on the project:

```
                            +-------------------+
                            |    Start Task     |
                            +--------+----------+
                                     |
                        What are you doing?
                    /          |            \
                   /           |             \
                  v            v              v
        +-------------+  +-----------+  +-----------+
        | ONBOARDING  |  |    DEV    |  |  QUALITY  |
        +------+------+  +-----+-----+  +-----+-----+
               |                |              |
               v                v              v
    /architecture-arch   /planning-impl-plan  /quality-review
    Map the codebase     Design before coding Phase 1: Score
               |                |              Health check
               v                v              |
    /learning-codebase-  Write Code            v
    mastery              |              /quality-review
    Deep-dive modules    v              Phase 2: Prioritize
               |         Sensitive       Triage tech debt
               v         areas?               |
    /quality-review     /      \         Need cleanup?
    Assess health     Yes       No       /          \
                       |        |      Yes          No
               |       v        v       |            |
            [DONE]  /impact-  code-   /refactor-  [DONE]
                    check     reviewer safe
                    Blast     Review   Refactor
                    radius    changes  safely
                      |        |       |
                      v        v       v
                   [DONE]   [DONE]  [DONE]
```

**Customization rules for the diagram:**
- If the project has API routes, add an `/api-development-api-impl` node in the Development flow after PLAN
- If the project has no tests, remove `/safe-changes-refactor-safe` or note "add tests first"
- If the project has vague requirements, add `/planning-spec-from-text` before `/planning-impl-plan`
- Label each node with the actual command AND a short description of what it does for this project
- Use project-specific language (e.g., "Touching auth/ or migrations?" instead of generic "sensitive areas")

---

## Output Format (Console)

```
## Project Setup: [Project Name]

### Project Fingerprint

| Dimension | Finding |
|-----------|---------|
| Language | [e.g., Python 3.11] |
| Framework | [e.g., FastAPI] |
| Type | [e.g., API Service] |
| Tests | [e.g., pytest, 45 test files, good coverage] |
| CI/CD | [e.g., GitHub Actions - build, test, deploy] |
| Quality Tools | [e.g., ruff, mypy] |
| Sensitive Areas | [e.g., src/auth/, migrations/] |
| Existing Claude Setup | [e.g., None / Partial / Complete] |

### Recommended Plugin Artifacts

#### Skills (slash commands)
| Skill | Why | Example Usage |
|-------|-----|---------------|
| `/architecture-arch` | [reason] | `/architecture-arch map the [specific module]` |
| ... | | |

#### Agents
| Agent | Why | When to Use |
|-------|-----|-------------|
| `code-reviewer` | [reason] | After modifying [specific areas] |

#### Rules (copy to .claude/rules/)
| Rule | Why |
|------|-----|
| `api.md` | [reason] |
| ... | |

#### Hooks (add to .claude/settings.json)
| Hook | Why |
|------|-----|
| Quality gate: ruff | [reason] |
| Protection: migrations | [reason] |
| ... | |

### Library Gaps (New Components to Create)

| Gap | Type | Suggested Name | What It Would Do | Priority |
|-----|------|---------------|-----------------|----------|
| [project need not covered] | [Skill/Agent/Hook/Rule] | `[category-name]` | [2-3 sentence description] | [H/M/L] |
| ... | | | | |

> To create a suggested skill, run: `/meta-experiment-feature [suggested-name]`

### Tailored Workflows

#### Onboarding
1. [step with project-specific arguments]
2. [step]
3. [step]

#### Development
1. [step with project-specific arguments]
2. [step]
3. [step]

#### Quality
1. [step with project-specific arguments]
2. [step]
3. [step]

### Staged Rollout

#### Day 1
- [ ] [specific action]
- [ ] [specific action]

#### Week 1
- [ ] [specific action]
- [ ] [specific action]

#### Week 2+
- [ ] [specific action]
- [ ] [specific action]
```

After displaying the console output, generate the `documentation/CLAUDE_SETUP.md` file containing all of the above PLUS the Mermaid workflow diagram.

---

## `documentation/CLAUDE_SETUP.md` File Template

The generated file should follow this structure:

```markdown
# Claude Code Setup: [Project Name]

> Generated by `/meta-project-setup` on [date]

## Project Fingerprint

[fingerprint table]

## Recommended Skills & Tools

[artifacts tables]

## Library Gaps — Suggested New Components

[gaps table with suggested names, types, descriptions, priorities]

## How to Use — Visual Workflow

[Mermaid diagram customized for this project]

## Workflows

### Onboarding
[steps]

### Development
[steps]

### Quality
[steps]

## Staged Rollout

### Day 1
[checklist]

### Week 1
[checklist]

### Week 2+
[checklist]
```

---

## Example Usage

```
# Analyze current project and generate documentation/CLAUDE_SETUP.md
/meta-project-setup

# Analyze a specific path
/meta-project-setup /path/to/my-project

# Analyze and also generate CLAUDE.md + rules
/meta-project-setup generate configs for this project
```
