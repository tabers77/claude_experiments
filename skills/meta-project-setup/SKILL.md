---
name: meta-project-setup
description: Analyze any project, audit its Claude Code setup, recommend library artifacts, detect gaps, and generate the complete layered configuration (CLAUDE.md, rules, hooks, child files). Includes auto-improve mode that researches latest best practices and suggests setup upgrades. Use when setting up Claude Code in a new project, onboarding to a repo, auditing an existing setup, generating a full layered config, or upgrading an existing setup.
---

# Skill: project_setup

**Purpose**: Analyze any project, recommend existing library artifacts, detect gaps where new skills/agents/hooks should be created, generate the complete layered Claude Code configuration, and auto-improve existing setups with latest best practices.

**Use when**:
- Starting work on a new project with this plugin active
- Want to know which skills/agents/hooks fit a specific codebase
- Want to discover what new skills the library is missing for this project
- Need a tailored CLAUDE.md and rules generated for a project
- Onboarding to a project and want optimal Claude Code configuration
- Want to generate the full layered Claude Code setup (rules, hooks, child CLAUDE.md)
- Want to upgrade an existing setup with latest best practices

**Tip**: You can pass natural language arguments to focus on specific steps. For example:
```
/meta-project-setup only detect gaps for this project
/meta-project-setup just audit the existing Claude setup
/meta-project-setup generate the full layered setup
/meta-project-setup auto-improve this project's Claude config
```

---

## Process

### Step 1: Accept Target & Detect Mode

Determine the target project:
- If invoked with a path argument, use that path
- If no argument, use the current working directory
- Only confirm the target with the user if the path is ambiguous, multiple repos are detected, or the skill is about to write files outside the current repo. Otherwise, state the inferred target and proceed.

**Mode detection** — after accepting the target, determine which mode to run:

| Condition | Mode | Steps |
|-----------|------|-------|
| User says "generate", "create", "set up", "full setup", "layered setup" | **Generate mode** | Steps 1–10 (full setup with generation) |
| User says "improve", "upgrade", "auto-improve" | **Auto-improve mode** | Step 11 (audit + research + suggest upgrades) |
| No existing setup detected | **Generate mode** (offer) | Offer to run Steps 1–10 |
| Existing setup detected, no keyword | **Auto-improve mode** (offer) | Offer to run Step 11 |
| Default (no keyword, no existing setup context) | **Audit mode** | Steps 1–9 (current behavior: audit + recommend only) |

### Step 2: Fingerprint the Project

Scan the target project across 8 dimensions:

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

- Check for: `CLAUDE.md` (can also be at `.claude/CLAUDE.md`), `.claude/`, `.claude/rules/`, `.claude/skills/`, `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.local.md`
- Check for MCP server configuration: `.mcp.json` or `mcpServers` in settings
- Auto memory state: `~/.claude/CLAUDE.md` present? Auto memory enabled or curated vs default?
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
| **Memory** | Auto memory enabled and curated (recommended for projects with recurring corrections or local learnings) | |
| **Memory** | MCP servers configured for project-specific tools (if applicable) | |
| **Session** | Session management patterns documented (--continue, --resume) | |

**Anti-Pattern Detection** — flag if found:
- Secrets or API keys in CLAUDE.md (should be in CLAUDE.local.md)
- Overly broad rules that conflict with each other
- Skills without clear purpose or duplicate skills
- Missing .gitignore for local config files
- Hooks referencing tools that aren't installed
- Uncurated auto memory growing unbounded (no periodic cleanup)

#### H) Documentation & Knowledge Files

Scan the project for documentation that Claude should know about:
- Search for: `docs/`, `documentation/`, `*.md` in root and key directories, `adr/`, `decisions/`, `wiki/`, `api-spec/`, `openapi.yaml`, `swagger.json`
- Include READMEs in subdirectories, CONTRIBUTING.md, ARCHITECTURE.md, CHANGELOG.md
- Exclude generated/vendored docs (node_modules, .git, build artifacts)

**Present the discovered files to the user and ask:**
> "Which of these docs should Claude **always** have in context (`@path/to/file` import in CLAUDE.md) vs. discover on demand?"

Classify each doc the user selects into:

| Classification | Mechanism | When to use |
|---------------|-----------|-------------|
| **Always loaded** | `@path/to/file` import in CLAUDE.md | Architecture, conventions, API contracts — relevant every session |
| **On demand** | Claude reads when needed | Large reference docs, changelogs, verbose specs |
| **Ignore** | Not referenced | Generated docs, outdated files, irrelevant to Claude |

**Recommended Documentation Structure** — based on what exists and what's missing, suggest:

| Action | Files | Reason |
|--------|-------|--------|
| **Keep** | [well-organized existing docs] | Already useful as-is |
| **Create** | [missing docs the project needs] | e.g., missing architecture doc, missing runbooks |
| **Split** | [overly large files] | e.g., monolithic README → separate architecture + contributing docs |
| **Merge** | [fragmented small docs] | e.g., scattered notes → consolidated decisions/ |
| **Archive** | [outdated docs] | e.g., old migration guides, superseded specs |

This triage feeds into Step 10g (CLAUDE.md generation) and Step 11a (audit).

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
| Complex codebase with recurring specialist domains | Specialist subagents with `memory: user` | Persistent domain memory avoids re-learning across sessions |
| Has external knowledge bases, wikis, or databases | MCP server config (`.mcp.json`) | Connect Claude to project-specific tools and data sources |

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
4. Document a startup command for quick re-entry (`claude --continue`) or non-interactive CI (`claude -p`)

#### Development Workflow
"Day-to-day coding"
1. Plan with `/planning-impl-plan` before features
2. Use `/api-development-api-impl` for [specific route pattern found]
3. Check with `/safe-changes-impact-check` before [sensitive areas found]
4. Review with `code-reviewer` agent after changes
5. Use `--continue` to resume interrupted work; `--resume` for named sessions on long tasks
6. End with `/commit-ready` to capture session knowledge into docs and commit

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
- Enable and curate auto memory — review via `/memory`

**Week 1** (daily workflow):
- Enable hooks for quality gates
- Use `/planning-impl-plan` before features
- Use `code-reviewer` agent after changes
- Adopt session naming for long tasks: `claude --resume "feature-name"`
- Use `/commit-ready` at session end to capture learnings

**Week 2+** (full integration):
- Add protection hooks for sensitive areas
- Use `/safe-changes-impact-check` before risky changes
- Re-run `/meta-project-setup` periodically to check setup health
- Set up `claude -p` automation for routine maintenance (lint, dep updates, test runs)

### Step 8: Generate `documentation/CLAUDE_SETUP.md`

After presenting recommendations, **always generate a `documentation/CLAUDE_SETUP.md` file** in the `documentation/` directory. This file is the persistent, readable summary of the setup analysis.

The file MUST include:

1. **Project fingerprint table** — the 8-dimension scan results
2. **Setup audit** — best-practice checklist results, anti-patterns detected, features in use vs missing
3. **Recommended artifacts** — skills, agents, rules, hooks with reasons
4. **Library gaps** — project needs not covered by any existing skill, with suggestions for new components to create
5. **Visual workflow diagram** — ASCII flowchart showing how commands connect in practice (see Diagram section below)
6. **Tailored workflows** — onboarding, development, quality with project-specific arguments
7. **Staged rollout** — Day 1 / Week 1 / Week 2+ checklist

### Step 9: (Optional) Generate Additional Files

If the user requests additional files:
- **`CLAUDE.md`**: Delegate to `/meta-claude-md-gen` — it runs an interactive interview to produce a context-rich CLAUDE.md with reading lists, guardrails, and domain conventions. Do NOT generate CLAUDE.md from templates yourself.
- `.claude/rules/` files (copy recommended rules)

### Step 10: Generate Layered Setup (Generate Mode)

This step runs when the user explicitly asks to "generate", "create", or "set up" files, or when the skill detects no existing setup and offers to create one.

#### 10a) Present the generation plan

Show the user what files will be created based on the fingerprint from Step 2:

| Layer | Files | Condition |
|-------|-------|-----------|
| CLAUDE.md | Root CLAUDE.md (via `/meta-claude-md-gen`) | Always |
| Rules | `.claude/rules/style.md` | Always |
| Rules | `.claude/rules/testing.md` | Has tests |
| Rules | `.claude/rules/api.md` | Has API routes |
| Rules | `.claude/rules/security.md` | Has auth/sensitive areas |
| Rules | `.claude/rules/database.md` | Has DB/migrations |
| Rules | `.claude/rules/monorepo.md` | Is monorepo |
| Hooks | `.claude/settings.json` (PostToolUse: lint) | Has quality tools installed |
| Hooks | `.claude/settings.json` (PreToolUse: protect) | Has sensitive areas |
| Child files | `services/*/CLAUDE.md` | Is monorepo |
| Local config | `CLAUDE.local.md` template | Always |
| Gitignore | `.gitignore` update | Always |

#### 10b) Wait for user confirmation before generating anything

#### 10c) Generate rules

Each rule file gets:
- Path-scoping frontmatter (e.g., `paths: ["src/api/**"]`) where applicable
- Content tailored to the detected language/framework from the fingerprint
- Only rules relevant to what the fingerprint found

Example rule file structure:
```markdown
---
description: [Rule purpose]
paths: ["relevant/path/**"]
---

# [Rule Title]

[Concise, actionable rules specific to this project's stack]
```

#### 10d) Generate hooks (`.claude/settings.json`)

Hooks are either **advisory** (inject context, exit 0) or **deterministic** (block/allow, exit 2). Choose deliberately — lint hooks are advisory, protection hooks are deterministic. Frame each generated hook with a comment indicating its guarantee level.

Only generate hooks for tools confirmed installed during fingerprinting:
- **PostToolUse**: lint command matching detected tooling (ruff for Python, eslint for JS/TS, etc.)
- **PreToolUse**: block edits to detected protected paths (migrations/, .env, etc.)
- **PreToolUse**: inject guidance for sensitive file patterns (auth, config, secrets)

**Important**: If `.claude/settings.json` already exists, **merge** new hooks into it — do NOT overwrite existing configuration.

#### 10e) Generate child CLAUDE.md (monorepo only)

For monorepo projects, create minimal CLAUDE.md files per service directory containing:
- Service purpose (derived from README or package.json description)
- Service-specific run/test commands
- Cross-references to related services
- If the monorepo has services with irrelevant cross-service CLAUDE.md, recommend `claudeMdExcludes` in `.claude/settings.local.json` by default (use `.claude/settings.json` only if the team explicitly wants repo-wide exclusions)

#### 10f) Generate local config

- Create a `CLAUDE.local.md` template with sections for private notes, local env quirks, personal preferences
- Include an auto memory curation section in `CLAUDE.local.md` (what to keep, what to prune)
- If project uses external tools/databases, generate a `.mcp.json` stub with commented examples
- Update `.gitignore` to include `CLAUDE.local.md` and `.claude/settings.local.json`

#### 10g) Delegate CLAUDE.md generation

Invoke `/meta-claude-md-gen` to generate the root CLAUDE.md through its interactive interview process. This is the same delegation as Step 9 but now explicitly part of the layered generation flow.

**Pass the doc triage from Step 2H** — for each file the user classified as "always loaded", include it as an `@path/to/file` import in the generated CLAUDE.md (e.g., `@docs/architecture.md`). This ensures important project documentation is deterministically loaded every session rather than left to auto memory.

#### 10h) Output summary

List all files created with brief descriptions:

```
## Generated Files

| File | Purpose |
|------|---------|
| `.claude/rules/style.md` | Code style conventions for [language] |
| `.claude/rules/testing.md` | Test conventions for [framework] |
| `.claude/settings.json` | Hooks: lint with [tool], protect [paths] |
| `CLAUDE.local.md` | Template for private local notes |
| `.gitignore` | Updated with Claude local config entries |
```

### Step 11: Auto-Improve Mode

This step runs when the user explicitly asks to "improve", "upgrade", or "auto-improve", or when the setup already exists and the user re-runs the skill.

#### 11a) Audit current setup

Re-run the Step 2G audit checklist and score each item with specific issues:

| Check | Status | Issue |
|-------|--------|-------|
| CLAUDE.md concise (<200 lines) | Pass/Fail | "Currently 250 lines — extract rules to .claude/rules/ and use @imports" |
| CLAUDE.md uses @imports | Pass/Fail | "No @imports — add for deep context docs" |
| Important docs @imported in CLAUDE.md | Pass/Fail | "Docs exist (docs/, ADRs, etc.) but none are @imported — run Step 2H triage" |
| Rules are modular | Pass/Fail | "All rules in CLAUDE.md — split to .claude/rules/" |
| Rules are path-scoped | Pass/Fail | "Rules apply globally — add paths: frontmatter" |
| Hooks enforce quality gates | Pass/Fail | "No lint hooks — add ruff PostToolUse" |
| Hooks protect sensitive paths | Pass/Fail | "migrations/ unprotected — add PreToolUse block" |
| Child CLAUDE.md (if monorepo) | Pass/Fail/N/A | |
| Local config exists | Pass/Fail | "No CLAUDE.local.md template" |
| .gitignore covers Claude files | Pass/Fail | |
| Auto memory enabled and curated | Pass/Fail/N/A | "Auto memory disabled — consider enabling for projects with recurring corrections or local learnings" |
| Session management documented | Pass/Fail | "No --continue/--resume patterns — add to workflows" |
| claudeMdExcludes for monorepo | Pass/Fail/N/A | "No excludes — add to .claude/settings.local.json to prevent cross-service context noise" |
| Hooks labeled advisory vs deterministic | Pass/Fail | "Hooks lack guarantee framing — add comments" |
| Specialist subagents for complex domains | Pass/Fail | "No persistent subagents — consider for [domain]" |
| Closing workflow captures knowledge | Pass/Fail | "No end-of-task pattern — add /commit-ready" |
| MCP servers configured (if needed) | Pass/Fail/N/A | "External tools exist but no MCP config" |
| Non-interactive automation (claude -p) | Pass/Fail | "No automation patterns — add for routine tasks" |

#### 11b) Research latest best practices

Research current Claude Code best practices (built-in, no dependency on other skills):
- Fetch official Claude Code documentation pages for new config options, hook events, rule features
- Web search for recent Claude Code setup patterns and community best practices
- Extract only findings relevant to project configuration (not skill authoring, not learning)

#### 11c) Generate improvement suggestions

For each audit gap and each research finding, create a suggestion:

```
### Suggestion N: [title]
**Current**: [what exists now]
**Recommended**: [what should change]
**Priority**: High/Medium/Low
**Files affected**: [list]
```

#### 11d) Present suggestions grouped by priority

Present High → Medium → Low. User approves or rejects each suggestion individually.

#### 11e) Apply approved changes

For each approved suggestion:
- Show the diff before writing to existing files
- Create new files directly
- Merge into existing `.claude/settings.json` if it exists

#### 11f) Generate report

Save `documentation/CLAUDE_SETUP_IMPROVEMENTS.md` containing:
- Date and sources checked
- Audit results (before/after scores)
- Changes applied
- Suggestions deferred
- "Run `/meta-project-setup auto-improve` again to check for new best practices"

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
| Documentation | [e.g., docs/architecture/, ADRs present, missing runbooks, root README good] |
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

After displaying the console output, generate the `documentation/CLAUDE_SETUP.md` file containing all of the above PLUS the ASCII workflow diagram.

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

[ASCII flowchart customized for this project]

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
# Analyze current project and generate documentation/CLAUDE_SETUP.md (audit mode)
/meta-project-setup

# Analyze a specific path
/meta-project-setup /path/to/my-project

# Generate the full layered setup (rules, hooks, local config, CLAUDE.md)
/meta-project-setup generate the full layered setup

# Generate complete Claude Code configuration for this project
/meta-project-setup create the complete setup

# Auto-improve an existing setup with latest best practices
/meta-project-setup auto-improve this project's Claude config

# Upgrade existing setup
/meta-project-setup upgrade my Claude setup
```
