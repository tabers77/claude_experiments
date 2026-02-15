# Library Rules

When working in this repository:

1. **Plugin-first** - Skills live in `skills/`, agents in `agents/`, hooks in `hooks/`
2. **Skills must be self-contained** - Each skill folder should work when loaded via plugin
3. **Document with examples** - Every skill needs example usage
4. **Sync with playbook** - When updating skills, check if playbook needs updates too
5. **Test in test_project** - Verify skills work before considering them complete
6. **Documentation goes in `documentation/`** - All generated or project-level `.md` files (audits, plans, reports, setup docs) MUST be placed in the `documentation/` directory. Only `CLAUDE.md` and `README.md` stay at the repo root. When a skill generates an `.md` output file, write it to `documentation/`, not the repo root.
7. **Keep docs in sync after every change** - After adding, removing, renaming, or modifying any skill, agent, hook, or structural file, ALWAYS update these files in the same operation:
   - `CLAUDE.md` — update the Available Skills table, directory tree, and any affected sections
   - `README.md` — update the Available Skills table, directory tree, Practical Workflow Guide, and any affected sections
   - `tests/test_skills.py` — update the expected skill count if skills were added or removed
   - Do NOT wait for the user to ask — do it as part of the change itself. If you forget, run `/quality-sync-docs` to catch up.
