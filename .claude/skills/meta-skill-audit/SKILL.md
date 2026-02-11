---
name: meta-skill-audit
description: Audit all skills, agents, hooks, and rules for overlaps and gaps. Detects redundant components and missing coverage. Generates a documentation/SKILL_AUDIT.md with merge suggestions.
---

# Skill: skill_audit

**Purpose**: Keep the library lean — one component per purpose, no confusion about which to use.

**Use when**:
- After adding new skills or agents
- Periodically to keep the library clean
- Before onboarding someone to the plugin
- When unsure if a new skill overlaps with an existing one

---

## Process

### Step 1: Inventory All Components

Scan the repo and build a complete inventory:

#### A) Skills
For each directory in `skills/*/SKILL.md`:
- Read the YAML frontmatter (`name`, `description`)
- Read the first section to extract the **Purpose** line and **Use when** bullets
- Categorize by use-case prefix (e.g., `safe-changes-*`, `planning-*`, `meta-*`, `quality-review-*`)

#### B) Agents
For each file in `agents/*.md`:
- Read frontmatter (`name`, `description`, `tools`, `model`)
- Extract what it does and when it's used

#### C) Hooks
Read `.claude-plugin/plugin.json` hooks section (or `hooks/hooks.json`):
- List each hook event + matcher + what it does

#### D) Rules
For each file in `library/rules/*.md`:
- Extract the topic and key conventions it enforces

### Step 2: Build Comparison Matrix

Create a matrix of all components with these columns:

| Component | Type | Purpose (1 line) | Triggers / Use When | Outputs |
|-----------|------|-------------------|---------------------|---------|

### Step 3: Detect Overlaps

Compare every pair of components. Flag overlap when ANY of these are true:

1. **Purpose overlap**: Two components solve the same problem or answer the same question
   - Example: a skill that "reviews code quality" and an agent that "reviews code for quality" → overlap
2. **Trigger overlap**: Two components are used in the same scenario
   - Example: both are used "before risky changes" or "when refactoring"
3. **Output overlap**: Two components produce similar deliverables
   - Example: both produce a "risk assessment" or "prioritized list"

**Overlap severity levels:**
- **High**: Components are nearly identical in purpose — one should be removed or merged
- **Medium**: Components overlap partially — consider merging the overlapping parts
- **Low**: Components share a scenario but serve different angles — document when to use which

For each overlap found, provide:
- The two components involved
- What specifically overlaps (purpose, trigger, or output)
- Severity (High / Medium / Low)
- Recommendation: merge, differentiate, or keep with clarification

### Step 4: Detect Gaps

Check for common software engineering workflows that have NO component coverage:

| Area | Expected Coverage | Check |
|------|-------------------|-------|
| **Database/migrations** | Safe schema changes, migration review | Any skill mentions DB/schema/migration? |
| **Security review** | Vulnerability scanning, auth review | Beyond rules — any skill does active security analysis? |
| **Deployment/release** | Deploy checklist, release notes | Any skill covers deploy workflow? |
| **Debugging/troubleshooting** | Systematic debugging, log analysis | Any skill for structured debugging? |
| **Documentation** | Generate/update docs, API docs | Any skill for doc generation? |
| **Dependency management** | Upgrade deps, audit vulnerabilities | Any skill for dependency review? |
| **Performance** | Profiling, optimization workflow | Any skill for performance analysis? |
| **Onboarding** | New team member setup | Beyond codebase-mastery — project-specific onboarding? |
| **Testing strategy** | Test plan design, coverage analysis | Beyond rules — any skill designs test strategies? |
| **Code generation** | Scaffolding, boilerplate generation | Any skill for generating code patterns? |

For each gap found, assess:
- **Priority**: High (common need) / Medium (occasional) / Low (nice-to-have)
- **Suggestion**: What a new skill covering this would look like (1-2 sentences)
- **Could extend**: Whether an existing skill could be expanded to cover it instead

### Step 5: Generate Report

Output the full audit to the console (see Output Format below).

### Step 6: Generate `documentation/SKILL_AUDIT.md`

**Always generate a `documentation/SKILL_AUDIT.md` file** in the `documentation/` directory. This is the actionable artifact the user reviews before approving changes.

The file MUST include:

1. **Component inventory table** — every skill, agent, hook, rule with its purpose
2. **Overlap report** — each overlap with severity and merge recommendation
3. **Gap report** — each gap with priority and suggestion
4. **Merge proposals** — for each High/Medium overlap, a concrete description of what the merged component would look like:
   - Proposed name
   - Proposed description
   - What to keep from each component
   - What to drop
   - Which file(s) to delete after merge
5. **Next steps checklist** — actionable items the user can approve or reject

---

## Output Format (Console)

```
## Skill Audit: claude-library

### Component Inventory

| # | Component | Type | Purpose |
|---|-----------|------|---------|
| 1 | architecture-arch | Skill | Build mental model before coding |
| 2 | code-reviewer | Agent | Review code for quality/security |
| ... | | | |

### Overlaps Detected

#### [Severity] Overlap: [Component A] vs [Component B]
- **What overlaps**: [purpose / trigger / output]
- **Severity**: [High / Medium / Low]
- **Recommendation**: [merge / differentiate / keep with docs]
- **Merge proposal**: [if applicable — what the merged version looks like]

### Gaps Detected

| Area | Priority | Suggestion | Could Extend |
|------|----------|------------|--------------|
| [area] | [H/M/L] | [what a skill for this would do] | [existing skill or "new"] |

### Next Steps
1. [ ] [actionable item]
2. [ ] [actionable item]
```

After console output, generate `documentation/SKILL_AUDIT.md` with the full report plus detailed merge proposals.

---

## `documentation/SKILL_AUDIT.md` Template

```markdown
# Skill Audit: claude-library

> Generated by `/meta-skill-audit` on [date]

## Component Inventory

[full table of all components]

## Overlap Analysis

### [Overlap 1 title]
- **Components**: [A] vs [B]
- **Severity**: [High/Medium/Low]
- **What overlaps**: [details]
- **Recommendation**: [action]

#### Merge Proposal (if applicable)
- **New name**: [proposed-name]
- **New description**: [combined description]
- **Keep from [A]**: [what to preserve]
- **Keep from [B]**: [what to preserve]
- **Drop**: [what's redundant]
- **Files to delete after merge**: [paths]

### [Overlap 2 title]
...

## Gap Analysis

| Area | Priority | Current Coverage | Suggestion |
|------|----------|-----------------|------------|
| [area] | [H/M/L] | [none / partial via X] | [recommendation] |

## Next Steps

### Merges to approve
- [ ] Merge [A] + [B] into [new name] (see proposal above)

### Gaps to fill
- [ ] Create skill for [area] (Priority: [H/M/L])

### No action needed
- [Component X] and [Component Y]: Low overlap, keep separate (different angles)
```

---

## Example Usage

```
# Full audit of all components
/meta-skill-audit

# After adding a new skill, check for overlaps
/meta-skill-audit just added /my-new-skill, check if it overlaps
```
