when I work in big and complex projects using claude code ,  I store findings and documetnaiton in on e foder since I noticed that when starting new sessions claude forgets what we have learned. I have added this to CLAUDE.md so claude alqys read the documentation files but sometimes it skips . INvestigae what are the best practices here, what claude reocmmends , how to approach this , and if there are more innovative solutions 

I’m checking Claude Code guidance and related best practices, then I’ll synthesize a practical setup for large projects, including stronger alternatives to relying on one folder plus CLAUDE.md.

I’ve confirmed two important things from Anthropic’s docs: CLAUDE.md is part of the intended setup, but Claude Code also has newer mechanisms—especially /memory, hooks, subagents, and MCP—that are meant to reduce exactly the “new session forgets project knowledge” problem.

Thought for 36s

What you’re doing is directionally right, but Anthropic’s docs suggest a more structured setup than “one folder + CLAUDE.md”.

The core thing Claude Code recommends is to treat persistent knowledge as several layers, not one big memory dump. Anthropic says every session starts with a fresh context window, and the supported cross-session mechanisms are CLAUDE.md plus auto memory. They also note that CLAUDE.md is loaded as context, not enforcement, so skips can happen if instructions are vague, conflicting, or too long.

Here’s the best-practice model I’d use.

1) Keep CLAUDE.md short, high-signal, and stable

Anthropic explicitly recommends a concise CLAUDE.md with only broad rules that matter in every session: build/test commands, workflow rules, repo etiquette, project-specific architectural decisions, environment quirks, and common gotchas. They specifically warn against bloated files, long tutorials, detailed API docs, or file-by-file descriptions, because once CLAUDE.md gets too large, important rules get lost. They recommend asking of each line: “Would removing this cause Claude to make mistakes?”

So your top-level CLAUDE.md should not be a documentation archive. It should be more like:

canonical commands

must-follow workflow rules

critical architectural constraints

project-wide gotchas

links/imports to other sources

A good heuristic:

CLAUDE.md = operating rules

docs folder = reference material

auto memory = learned quirks

skills/subagents = specialized knowledge/workflows

2) Split memory by scope instead of one big folder

Anthropic recommends multiple scopes for CLAUDE.md: user-wide (~/.claude/CLAUDE.md), project-wide (./CLAUDE.md or ./.claude/CLAUDE.md), parent directories for monorepos, and child-directory CLAUDE.md files that load on demand when Claude works in those directories. More specific locations take precedence.

That means the better pattern for large repos is:

~/.claude/CLAUDE.md → your personal global preferences

repo root CLAUDE.md → shared project rules

services/foo/CLAUDE.md → service-specific constraints

frontend/CLAUDE.md → frontend-specific rules

This is better than a single documentation folder because child CLAUDE.md files are pulled in when Claude actually touches those files, which reduces irrelevant context.

3) Use .claude/rules/ for modular guidance

Anthropic now recommends .claude/rules/ for larger projects. Rules can be split into multiple markdown files, and they can be path-scoped with frontmatter so they only apply when Claude works with matching files. That is a much better fit than stuffing everything into CLAUDE.md.

Example structure:

.claude/
  CLAUDE.md
  rules/
    testing.md
    security.md
    api/
      api-design.md
    frontend/
      react.md

And for path-specific rules:

---
paths:
  - "src/api/**/*.ts"
---

# API Rules
- Validate all inputs
- Use the standard error shape
- Add OpenAPI comments for new endpoints

That gives you “load when relevant” behavior without relying on Claude to remember a giant global document.

4) Use @imports instead of copying everything into CLAUDE.md

Anthropic recommends importing additional files into CLAUDE.md with @path/to/file. Example from their docs: referencing README.md, package.json, git instructions, or personal overrides.

This is important because it lets you keep CLAUDE.md thin while still pointing Claude to the right source of truth.

A strong pattern is:

# Core workflow
- Use pnpm, not npm
- Run targeted tests first, full suite only before final handoff
- NEVER edit generated files manually

# Key references
- Project overview: @README.md
- Available commands: @package.json
- Architecture decisions: @docs/architecture/index.md
- Debugging playbook: @docs/debugging/common-failures.md

That is much better than duplicating all the docs into one memory file.

5) Turn on and curate auto memory

Anthropic’s docs say Claude Code has auto memory, which stores learnings across sessions per working tree, and /memory lets you inspect loaded memory files, enable/disable auto-memory, and audit what was saved. They also note only the first 200 lines are loaded every session for auto memory, so this should be curated, not allowed to grow messy forever.

This is one of the biggest upgrades over the workflow you described.

Use it for things like:

“Redis must be running locally for API tests”

“Service X fails if env var Y is missing”

“Migration scripts live in folder Z and should not be edited manually”

Do not use it for:

long architectural docs

policies that belong in source control

unstable day-to-day notes

Also, Anthropic exposes autoMemoryDirectory in settings, so you can control where this lives from user/local/policy settings.

6) Use /memory to debug “Claude skipped it”

Anthropic directly addresses your exact complaint. If Claude is not following CLAUDE.md, they recommend:

run /memory to verify the file is actually loaded

check the file is in a loadable location

make instructions more specific

look for conflicting rules

use the InstructionsLoaded hook to log what was loaded and why

That is probably the most actionable official answer to “sometimes it skips.”

So when this happens, don’t guess. Check:

Was the file loaded?

Is there a conflicting root/parent/child rule?

Is the instruction too vague?

Is the file too long?

7) Use hooks when you need guarantees

Anthropic is very clear: CLAUDE.md is advisory, but hooks are deterministic. If something must always happen, use a hook instead of an instruction. Examples they give include formatting after edits, blocking edits to protected files, notifications, and re-injecting context.

This is a big mindset shift:

“Please run eslint after edits” → weak, advisory

post-edit hook that runs eslint → strong, enforced

For your use case, good hooks would be:

log which memory/rule files loaded at session start

block edits in generated/migrations folders

run project verification commands after edits

re-inject critical context after compaction

One caveat from Anthropic: hooks are snapshotted at startup in some docs pages, so changes may not affect the current session immediately depending on context.

8) Put specialized knowledge into skills, not into global memory

Anthropic explicitly says that knowledge or workflows that are only sometimes relevant should go into skills, because skills load on demand instead of bloating every conversation.

This is one of the best answers to your problem.

Examples:

.claude/skills/debug-auth/SKILL.md

.claude/skills/release-checklist/SKILL.md

.claude/skills/api-conventions/SKILL.md

Use skills for:

“how we do releases”

“how to troubleshoot auth”

“how to write DB migrations”

“how to investigate performance regressions”

That keeps your persistent base context small and shifts deep procedural knowledge into reusable modules.

9) Use subagents for heavy analysis and persistent specialist memory

Anthropic recommends custom subagents for isolated tasks and says subagents can maintain their own memory. Their docs mention subagent memory locations and that the first 200 lines of a subagent MEMORY.md are included in its prompt; they also recommend asking subagents to consult and then update their memory after finishing work.

That opens a more innovative pattern:

architecture-reviewer subagent with its own memory

bug-investigator subagent with its own memory

security-reviewer subagent with its own memory

This is stronger than a single giant project memory because each specialist keeps a focused knowledge base.

10) Resume sessions instead of always starting fresh

Anthropic also recommends using claude --continue or --resume for long-running tasks, and to name sessions so they’re easier to re-open. They explicitly say conversations are saved locally and can be resumed.

So for big projects:

don’t always start a new session

keep one session per workstream

name them like oauth-migration, billing-bug, schema-refactor

That reduces the amount of memory infrastructure you need in the first place.

11) For monorepos, actively exclude irrelevant memory

Anthropic provides claudeMdExcludes for large monorepos so you can skip top-level or parent CLAUDE.md files that are irrelevant to the current worktree.

That matters because “Claude skipped my instruction” is sometimes really “Claude had too many conflicting instructions.”

12) More innovative solutions

Beyond Anthropic’s basic recommendation, these are the strongest patterns.

A. Retrieval-first project memory

Instead of storing all findings directly in CLAUDE.md, keep a structured docs knowledge base and only import the entry points:

docs/architecture/index.md

docs/runbooks/index.md

docs/decisions/ADR-*.md

docs/incidents/

Then use:

root CLAUDE.md for pointers

rules for path-specific constraints

skills for operational workflows

This follows Anthropic’s “hybrid” context model: some context is loaded upfront via CLAUDE.md, while Claude retrieves other files just-in-time by reading the repo.

B. Deterministic “session bootstrap”

Create a skill or slash-command-like workflow that always does:

read root CLAUDE.md

read relevant docs/index.md

inspect current service/module

summarize active constraints before starting

This is safer than hoping Claude organically reads the right docs.

C. Knowledge capture at task end

Adopt a standard closing prompt:

“Update auto memory with any durable learnings from this task.”

“If any new repo-wide workflow was discovered, propose a CLAUDE.md or rules update.”

“If this is domain-specific, update or create a skill instead.”

That turns learning into a workflow, not an accident.

D. MCP-backed external memory

Anthropic recommends MCP for connecting tools and knowledge sources like Notion, issue trackers, databases, Figma, Slack, etc.

For teams, this can be better than overloading the repo:

architecture decisions in Notion/Confluence

tickets in Jira

incidents in PagerDuty/Sentry

designs in Figma

Then Claude can fetch current context instead of relying only on static local notes.

E. Use non-interactive Claude for memory maintenance

Anthropic recommends claude -p for scripting and CI-style workflows.

You can use that to automate:

nightly summarization of new ADRs into docs/index.md

validation that CLAUDE.md references still exist

generation of rule stubs for new directories

linting of project memory files

What I would recommend for your exact situation

I would change your current setup to this:

~/.claude/
  CLAUDE.md                # your personal preferences
  rules/
    workflows.md

repo/
  CLAUDE.md                # only high-level repo-wide rules
  .claude/
    rules/
      testing.md
      security.md
      api.md
      frontend.md
    skills/
      debug-auth/
        SKILL.md
      release-process/
        SKILL.md
    agents/
      architecture-reviewer.md
      bug-investigator.md
  docs/
    architecture/
      index.md
      adr-001.md
    runbooks/
      index.md
      local-dev.md
    findings/
      2026-03-oauth.md

And I’d use this policy:

CLAUDE.md: under ~100 lines if possible

.claude/rules/: modular, scoped rules

skills: task-specific procedures

docs/: long-form findings and reference material

auto memory: small durable learnings

hooks: things that must always happen

Bottom line

The best practice is not “make Claude always read one big documentation folder.”
The best practice is:

keep CLAUDE.md small and durable

modularize with .claude/rules/

use @imports for key references

enable and curate auto memory

use /memory to verify what loaded

move special workflows into skills

use hooks for guarantees

use subagents and MCP for more advanced persistent knowledge

That is much closer to what Anthropic recommends, and it should be more reliable than your current approach.