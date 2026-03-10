---
name: meta-claude-md-gen
description: Generate a context-rich CLAUDE.md through interactive discovery. Interviews you about what Claude should read first, what not to touch, domain conventions, and project rules — then produces a CLAUDE.md that prevents Claude from asking the same questions every session. Use when setting up a new project, when your CLAUDE.md feels too generic, or when Claude keeps misunderstanding your codebase.
---

# Skill: claude_md_gen

**Purpose**: Generate a high-quality CLAUDE.md by interviewing the user about their project. Produces a context-rich file that tells Claude *what to read*, *what matters*, and *what not to touch*.

**Use when**:
- Setting up Claude Code in a new project
- Your existing CLAUDE.md is too generic or missing critical context
- Claude keeps asking questions that a good CLAUDE.md would answer
- You want Claude to understand your project's history, conventions, and sensitive areas

**Not for**: Auditing your Claude Code setup or recommending plugin skills — use `/meta-project-setup` for that.

**Tip**: You can pass arguments to skip the interview or focus on specific sections:
```
/meta-claude-md-gen                           # full interactive interview
/meta-claude-md-gen just the reading list     # only generate the "Always read first" section
/meta-claude-md-gen improve existing          # audit and improve the current CLAUDE.md
```

---

## Philosophy

A great CLAUDE.md is NOT a README. It answers: **"What does Claude need to know to work effectively in this codebase without asking me the same questions every session?"**

The most valuable sections — in order of impact:

1. **What to read first** — pointers to essential context files (saves Claude from guessing)
2. **What NOT to do** — guardrails, expensive operations, regeneration warnings
3. **Domain conventions** — naming formats, data shapes, terminology Claude would get wrong
4. **Commands** — how to run, test, lint (exact copy-paste commands)
5. **Architecture** — just enough to navigate, not a full design doc
6. **Rules and invariants** — things that must stay true across all changes

---

## Process

### Step 1: Detect Starting Point

Check the target project (current working directory or user-specified path):

- Does a `CLAUDE.md` already exist? If yes, read it and switch to **Improve Mode** (Step 1b)
- If no CLAUDE.md exists, proceed to **Discovery Mode** (Step 2)
- Also scan for: `README.md`, `documentation/`, `docs/`, `.claude/` to understand what context already exists

#### Step 1b: Improve Mode

If CLAUDE.md already exists:
1. Read the current CLAUDE.md
2. Score it against the **Quality Checklist** (Step 8)
3. Identify missing high-impact sections
4. Present the gaps to the user: "Your CLAUDE.md is missing X, Y, Z. Want me to interview you about these?"
5. Run only the relevant interview questions from Steps 2-7
6. Merge new content into the existing file, preserving what's already good

### Step 2: Interview — Project Identity

Ask the user these questions (present them all at once, let the user answer in bulk):

```
I need to understand your project to build a great CLAUDE.md. Please answer what you can — skip any that don't apply:

1. What does this project do? (one paragraph — what problem, for whom?)
2. What phase is it in? (early prototype / active development / maintenance / migration)
3. Is there a current status or known limitation? (e.g., "works but accuracy is off")
4. What's the primary language and framework?
```

> **Do NOT scan the codebase to answer these yourself.** The user's mental model is more valuable than file scanning. Scanning fills gaps but should not replace the interview.

### Step 3: Interview — Essential Reading

This is the **highest-value section**. Ask:

```
What files should Claude ALWAYS read before doing anything in this project?

Think about:
- The file that explains what's been done and what's left (roadmap, implementation notes)
- The file that explains WHY things are the way they are (design decisions, findings)
- Any file where you've written context you'd otherwise re-explain every session

Examples:
  "documentation/implementation.md — single source of truth for progress"
  "README.md — project overview and FAQ"
  "docs/findings/ — investigation results that explain data quirks"
```

Then ask:

```
Are there files that are CONDITIONALLY relevant — only needed for specific tasks?

Examples:
  "Only read appendix/dax_measures.md if working on rate computation"
  "Only read docs/api-spec.md if modifying endpoints"
```

### Step 4: Interview — Commands

Ask:

```
What are the essential commands to work with this project?

I need exact commands for:
- Installing dependencies
- Running the project
- Running tests (all, single file, single test)
- Linting / formatting
- Any other common operations (migrations, builds, deploys)

Include flags or variants that are commonly used.
```

### Step 5: Interview — Architecture and Structure

Ask:

```
Describe the high-level architecture in 2-3 sentences.
Think: "data flows from X through Y to produce Z"

Also: are there different categories of files? For example:
- Pipeline scripts vs exploration scripts
- Source code vs generated output
- Config files vs runtime code
```

If the user's description is thin, THEN scan the codebase to supplement (directory structure, entrypoints, key files). But always prefer the user's framing.

### Step 6: Interview — Guardrails and Conventions

Ask:

```
What should Claude NEVER do or be careful about?

Think about:
- Files or outputs that are expensive to regenerate (require auth, long queries, etc.)
- Operations that could break things (e.g., "never drop the production database")
- Directories that are gitignored but contain important local state

Also: what domain-specific conventions does your project follow?
- Naming formats (e.g., "dates are always YYYY_MM", "IDs are strings not ints")
- Data shapes or terminology Claude might get wrong
- Coding patterns the project follows consistently
```

### Step 7: Interview — Rules and Sync Patterns

Ask:

```
Does your project have any "source of truth" rules?
For example:
- "implementation.md is the roadmap — always update it first, then sync to README"
- "The database schema is the source of truth, not the ORM models"

Also: are there invariants that must NEVER break?
(Things that, if violated, mean something is seriously wrong)
```

### Step 8: Generate CLAUDE.md

Using the interview answers, generate the CLAUDE.md following this structure. **Only include sections where the user provided meaningful content** — skip empty sections rather than filling with placeholders.

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Always read first

- `[file]` -- [why this file matters]
- `[file]` -- [why this file matters]

## Project context and history

Read before [specific task context]:
- `[file/directory]` -- [what it contains and when it's relevant]

Only read if related to the current task:
- `[file]` -- [what it contains]

## [Project-specific section if needed, e.g., "Generated outputs", "Experiment data"]

`[directory/]` contains [what]:
- `[pattern]` -- [description]

[Guardrail about these files, e.g., "Do NOT regenerate unless explicitly asked."]

## Project Overview

[User's description — what it does, current phase, status/limitations]

## Commands

```bash
# [Category]
[exact commands]

# [Category]
[exact commands]
```

## Architecture

```
[High-level flow diagram or description]
```

[Additional architecture notes]

## Project Rules

### [Rule name, e.g., "Documentation Sync Rule"]

[Rule description with numbered steps]

## Important rules

- [Guardrail 1]
- [Guardrail 2]

## Key Conventions

- **[Convention]**: [Description]
- **[Convention]**: [Description]
```

### Generation principles:

1. **Use the user's exact wording** for guardrails and conventions — they know their domain
2. **Reading lists are the most valuable section** — get the "always" vs "conditional" tiers right
3. **Guardrails save more time than structure** — "don't regenerate Outputs/" prevents a 30-minute mistake
4. **Architecture should be navigational** — enough to find things, not a design doc
5. **Commands must be copy-pasteable** — include flags, variants, exact paths
6. **Skip sections with no content** — shorter and accurate beats longer with placeholders
7. **Aim for under 120 lines** — long CLAUDE.md files get skimmed, not read

### Step 9: Quality Checklist

After generating, score the CLAUDE.md and show results:

| Check | Status | Impact |
|-------|--------|--------|
| Has "Always read first" with specific files | | Critical |
| Has conditional reading list (tiered context) | | High |
| Has guardrails / "do NOT" rules | | High |
| Has exact, runnable commands | | High |
| Has domain-specific conventions | | Medium |
| Has architecture overview (navigational) | | Medium |
| Has documentation sync rules | | Medium |
| Has invariants / must-not-break rules | | Medium |
| No placeholder text | | Quality |
| Under 120 lines | | Quality |

Present the score and ask: "Want me to improve any of these areas?"

### Step 10: Write the File

- Show the full generated CLAUDE.md before writing
- If a CLAUDE.md already exists, show a diff preview and ask for confirmation before overwriting
- Write to the project root
- Suggest next steps: "Consider also setting up `.claude/rules/` for topic-specific rules, or run `/meta-project-setup` to get plugin skill recommendations."

---

## Output Format

The skill outputs:
1. **Interview questions** (Steps 2-7) — presented interactively
2. **Generated CLAUDE.md** — shown in full before writing
3. **Quality scorecard** — table showing how the file scores
4. **The file itself** — written to the project root after confirmation

---

## Example Usage

```
# Full interactive generation for current project
/meta-claude-md-gen

# Improve existing CLAUDE.md
/meta-claude-md-gen improve my current CLAUDE.md

# Generate for a specific path
/meta-claude-md-gen for /path/to/my-project

# Focus on a specific section
/meta-claude-md-gen just help me write the reading list
```
