# Problem Statement & Initial Request

## The Initial Request

> "Based on the claude notes 'How I Use Claude Code.md' my idea is that this repo could be a repo for testing claude features and experimenting new features. My idea is that based on the official claude code documentation we can always be up to date with new features and better ways to use claude code. I want to put focus on the tutor mode for learning and improving my skills as engineer. In the notes we have best practices and a quick setup so the idea with this repo is that we can test all this in practice. There could also be a mode where you suggest new improvements to the current codebase based on the official claude documentation."

---

## Problems Being Solved

### Problem 1: Gap between theory and practice
**Situation**: You have a comprehensive playbook ("How I Use Claude Code.md") with best practices, skills, and workflows, but no dedicated environment to test and practice these concepts.

**Solution**: Create mock projects and structured exercises to practice each Claude Code feature hands-on.

---

### Problem 2: Staying current with Claude Code features
**Situation**: Claude Code evolves with new features (MCP, custom agents, hooks, etc.). Without a system, it's easy to miss new capabilities or better ways of working.

**Solution**: Create an audit skill (`/meta-project-setup`) that compares your current setup against official documentation and suggests improvements.

**Documentation sources**:
- https://code.claude.com/docs
- https://platform.claude.com/docs

---

### Problem 3: Knowledge gaps in advanced features
**Situation**: Your playbook covers memory and skills well, but has light or no coverage of:
- Hooks (mentioned but not deep)
- Subagents (brief mention)
- MCP (not covered)
- Custom agents (not covered)
- Headless/CI mode (not covered)

**Solution**: Create dedicated learning modules for each feature, ordered foundation-first.

---

### Problem 4: Learning vs doing imbalance
**Situation**: You want Claude to be a "tutor" that helps you learn and improve as an engineer, not just an autopilot that does work for you. Passive consumption of Claude's output doesn't build skills.

**Solution**: Focus on tutor mode with exercises where Claude asks YOU questions, you answer, and Claude corrects with evidence. Include micro-exercises to implement yourself.

---

### Problem 5: Reusability across projects
**Situation**: Once you learn a Claude Code pattern, you want to quickly implement it in other repos and projects.

**Solution**: Structure learning so each module produces reusable artifacts (skill templates, CLAUDE.md templates, hook configurations) that can be copied to other projects.

---

## Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Repo structure | Structured learning path (modules) | Main focus is learning, not ad-hoc exploration |
| Module order | Foundation first | Build solid base before advanced features |
| Playbook integration | Module 0 / Reference | Preserve holistic view, modules extend it |
| Audit skill approach | Hybrid (local ref + update skill) | Balance between speed and staying current |
| Mock projects | Start minimal, add realistic later | Quick start, depth when needed |

---

## Success Criteria

1. **Practical skill**: Can complete a module and confidently use that feature in real projects
2. **Stay current**: `/meta-project-setup` provides actionable suggestions based on latest docs
3. **Quick setup**: Can rapidly configure Claude Code in new repos using learned patterns
4. **Skill growth**: Engineering skills improve through tutor mode and hands-on exercises
5. **No knowledge gaps**: All major Claude Code features covered and practiced

---

## Scope Boundaries

**In scope**:
- Learning Claude Code features (memory, skills, hooks, subagents, MCP, agents)
- Mock projects for practice
- Audit skill for staying current
- Tutor mode for active learning

**Out of scope (for now)**:
- Building production applications
- Claude API/SDK usage (separate from Claude Code CLI)
- Multi-user or team workflows
- Integration with specific IDEs (VS Code, etc.)

---

## Future Considerations

If the current structure doesn't meet needs, consider:
- **More granular modules**: Split large modules into sub-modules
- **Different mock projects**: Add domain-specific examples (ML pipeline, CLI tool, etc.)
- **Spaced repetition**: Track mastery and schedule reviews
- **Community content**: Import skills/patterns from Claude Code community
- **Project templates**: Generate starter configs for different project types
