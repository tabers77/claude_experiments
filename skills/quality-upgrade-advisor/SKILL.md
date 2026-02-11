---
name: quality-upgrade-advisor
description: Audit your project's tech stack against its ecosystem — find stale dependencies, deprecated patterns, and new features that align with your vision. Produces documentation/UPGRADE_ROADMAP.md.
---

# Skill: quality-upgrade-advisor

**Purpose**: Check ecosystem currency — audit dependencies against official docs, find deprecated patterns, and produce a prioritized upgrade roadmap aligned with the developer's stated vision.

**Use when**:
- You suspect dependencies are outdated but don't know which matter
- Planning a major version bump or runtime upgrade
- Onboarding to a project and want to know its ecosystem health
- Preparing a tech debt sprint focused on dependencies
- Checking if new library features could simplify existing code

---

## Rules

- **Never execute upgrades** — this skill produces a plan only
- Use **WebSearch + WebFetch** to ground every recommendation in official docs, changelogs, or advisories
- Read the developer's **vision/goals** from CLAUDE.md/README to filter recommendations — skip upgrades that don't align
- Cite sources for every finding (URL, changelog entry, advisory ID)
- If you cannot verify a finding online, mark it as "Unverified" with reduced confidence
- Support multi-ecosystem: Python, Node, Rust, Go, Ruby, .NET
- Limit ecosystem checks to the **top 10-15 key dependencies** — skip transitive/minor ones
- Output goes to `documentation/UPGRADE_ROADMAP.md`

---

## Process

### Phase 1: Project Snapshot

1) **Read project identity files**:
   - CLAUDE.md, README.md (vision, goals, architecture)
   - requirements.txt / package.json / pyproject.toml / Cargo.toml / go.mod / Gemfile / *.csproj
   - Dockerfile, docker-compose.yml (runtime versions)
   - CI configs (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)

2) **Extract tech stack**:
   - Language + runtime version
   - Framework(s) + version
   - Key libraries + versions (top 10-15 by importance)
   - Build tools, linters, test frameworks

3) **Extract developer vision**:
   - What is the project trying to achieve?
   - What constraints are stated? (performance, compatibility, simplicity)
   - What's the target audience / deployment environment?

4) **Produce Project Identity Card**:
   - One-paragraph summary
   - Stack table (component, current version, role)
   - Vision summary (2-3 bullet points)

### Phase 2: Ecosystem Check

5) **For each key dependency, search for**:
   - Latest stable version (WebSearch: "[library] latest version [year]")
   - Deprecation warnings or EOL notices
   - Security advisories (CVEs, GitHub Security Advisories)
   - Breaking changes between current and latest version
   - New features or recommended patterns since current version

6) **For the runtime/language itself**:
   - Current LTS / stable version
   - EOL date for the project's current version
   - Migration guides if a major version jump is needed

7) **For frameworks**:
   - Recommended upgrade path
   - Deprecated APIs the project currently uses (search codebase)
   - New patterns that could replace existing workarounds

8) **Curate findings**:
   - Drop anything irrelevant to this project's vision/stack
   - Merge related findings (e.g., multiple CVEs for one library)
   - Flag "Unverified" items where online sources were inconclusive

### Phase 3: Improvement Roadmap

9) **Categorize each finding into tiers**:
   - **Critical**: Security patches, EOL runtimes, breaking deprecations already emitting warnings
   - **Recommended**: Version bumps with clear benefits, pattern modernization, performance gains
   - **Consider**: New features aligned with project vision, optional improvements
   - **Skip**: Updates with no practical benefit, high migration cost for low return

10) **For each recommendation, provide**:
    - **What**: The specific change
    - **Why**: The benefit (with source link)
    - **From → To**: Current version → target version
    - **Effort**: Low / Medium / High (with explanation)
    - **Risk**: Low / Medium / High (what could break)
    - **Command**: Exact command to execute the upgrade (e.g., `pip install --upgrade fastapi==0.115.0`)
    - **Migration link**: URL to official migration guide or changelog

11) **Identify dependencies between upgrades**:
    - Which upgrades must happen together?
    - Which upgrades unlock others?
    - What's the safest order?

12) **Produce recommended sequence**:
    - Ordered list of upgrade steps
    - Grouped into PR-sized batches
    - Each batch has a verification step

13) **Write `documentation/UPGRADE_ROADMAP.md`**

---

## Output Format

```markdown
## Upgrade Roadmap: [Project Name]
Generated: [date]

### Project Identity Card

**Summary**: [One-paragraph project description]

| Component | Current Version | Role |
|-----------|----------------|------|
| [Python/Node/etc.] | [version] | Runtime |
| [Framework] | [version] | Web framework |
| [Library] | [version] | [role] |
| ... | ... | ... |

**Vision**: [2-3 bullet points from CLAUDE.md/README]

---

### Critical (Act Now)

| # | What | Why | From → To | Effort | Risk | Command |
|---|------|-----|-----------|--------|------|---------|
| 1 | [change] | [reason + source] | v1.0 → v1.5 | Low | Low | `pip install ...` |

**Migration notes**:
- [Item 1]: [link to migration guide]

---

### Recommended (Plan Soon)

| # | What | Why | From → To | Effort | Risk | Command |
|---|------|-----|-----------|--------|------|---------|
| 1 | [change] | [reason + source] | v2.0 → v3.0 | Medium | Medium | `npm install ...` |

**Migration notes**:
- [Item 1]: [link to changelog]

---

### Consider (When Convenient)

| # | What | Why | Aligns With |
|---|------|-----|-------------|
| 1 | [feature/pattern] | [benefit + source] | [vision point] |

---

### Skip (Not Worth It Now)

| # | What | Why Skip |
|---|------|----------|
| 1 | [upgrade] | [reason: high effort, low benefit, etc.] |

---

### Upgrade Sequence

**Batch 1: [theme]** (PR-sized)
1. [step] — `[command]`
2. [step] — `[command]`
3. Verify: `[test command]`

**Batch 2: [theme]** (PR-sized)
1. [step] — `[command]`
2. Verify: `[test command]`

### Dependencies
- [Upgrade X] must happen before [Upgrade Y] because [reason]

### Sources
- [Library name]: [URL to changelog/advisory/docs]
- ...
```

---

## Example Usage

```
# Full ecosystem audit
/quality-upgrade-advisor

# Focus on security-related upgrades only
/quality-upgrade-advisor focus on security patches and CVEs only

# Specific ecosystem
/quality-upgrade-advisor check Python dependencies — we're planning a Python 3.12 migration

# With vision context
/quality-upgrade-advisor
We want to move toward async-first architecture and reduce cold start time.
Only recommend upgrades that help with those goals.

# Minimal check (just Critical tier)
/quality-upgrade-advisor quick — just show me what's critical
```
