# Claude Code Library

## Purpose

A reusable library of Claude Code configurations (skills, hooks, rules, templates) that can be copied into other projects.

## Key Commands

```bash
# Test the test_project
cd test_project && pip install -r requirements.txt && pytest

# Run the test API
cd test_project && uvicorn src.main:app --reload
```

## Repo Structure

- `playbook/` - Source of truth: "How I Use Claude Code.md"
- `library/skills/` - Reusable skills organized by use-case
- `library/hooks/` - Hook configuration examples
- `library/rules/` - Reusable .claude/rules/ templates
- `library/templates/` - CLAUDE.md templates for different project types
- `test_project/` - Simple project to verify skills work
- `audits/` - Output from /audit_setup

## How to Use

### Copy a skill to your project
```bash
cp -r library/skills/architecture/arch/ your-project/.claude/skills/
```

### Copy a template for new project
```bash
cp -r library/templates/python-api/* your-new-project/
```

## Invariants

1. **Playbook is source of truth** - All skills derive from `playbook/How I Use Claude Code.md`
2. **Library is copy-paste ready** - Skills should work immediately when copied
3. **Organized by use-case** - Not by feature type

## Available Skills

| Use Case | Skill | Purpose |
|----------|-------|---------|
| Architecture | `/arch` | Build mental model before coding |
| Safe Changes | `/refactor_safe` | Refactor with explicit invariants |
| Safe Changes | `/impact_check` | Understand blast radius |
| Planning | `/spec_from_text` | Convert vague input to specs |
| Planning | `/impl_plan` | Design before coding |
| API Dev | `/api_impl` | Consistent endpoint implementation |
| Quality | `/project_review` | Evidence-based project assessment |
| Quality | `/risk_prioritizer` | Prioritize what matters |
| Learning | `/codebase_mastery` | Deep understanding + tutor mode |
| Meta | `/audit_setup` | Audit any repo's Claude setup |
