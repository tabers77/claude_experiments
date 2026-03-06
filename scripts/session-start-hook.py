#!/usr/bin/env python3
"""SessionStart hook: validates plugin and shows skill summary on new sessions.

Runs on session startup to verify the plugin is healthy and display
available skills organized by development phase.
"""

import json
import os
import sys
from pathlib import Path


def count_skills(plugin_root: Path) -> tuple[int, list[str]]:
    """Count skills and collect their names."""
    skills_dir = plugin_root / "skills"
    if not skills_dir.exists():
        return 0, []

    names = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            names.append(skill_dir.name)
    return len(names), names


def validate_skills(plugin_root: Path) -> list[str]:
    """Run lightweight validation, return list of issues."""
    issues = []
    skills_dir = plugin_root / "skills"

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            issues.append(f"Missing SKILL.md in {skill_dir.name}")
            continue

        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            issues.append(f"Missing YAML frontmatter in {skill_dir.name}")
        if "_" in skill_dir.name:
            issues.append(f"Underscore in directory name: {skill_dir.name} (use hyphens)")

    return issues


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    source = data.get("source", "startup")

    # Only show full summary on new sessions, not resume/compact
    if source != "startup":
        sys.exit(0)

    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", "")).resolve()
    if not plugin_root.exists():
        plugin_root = Path(__file__).resolve().parent.parent

    count, names = count_skills(plugin_root)
    issues = validate_skills(plugin_root)

    lines = [f"claude-library plugin loaded: {count} skills available."]

    if issues:
        lines.append(f"Validation issues ({len(issues)}):")
        for issue in issues:
            lines.append(f"  - {issue}")

    context = "\n".join(lines)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
