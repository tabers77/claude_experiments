#!/usr/bin/env python3
"""UserPromptSubmit hook: matches user prompts against skill-rules.json
and injects skill suggestions as additionalContext.

Reads JSON from stdin (Claude Code hook input), matches the prompt
against trigger patterns, and outputs JSON with additionalContext
suggesting the matched skill(s).

Exit 0 with no stdout = no suggestion (silent pass-through).
Exit 0 with JSON stdout = additionalContext injected into conversation.
"""

import json
import re
import sys
from pathlib import Path


def load_rules():
    """Load skill-rules.json from the plugin root."""
    script_dir = Path(__file__).resolve().parent
    rules_path = script_dir.parent / "skill-rules.json"
    if not rules_path.exists():
        return []
    with open(rules_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("rules", [])


def match_prompt(prompt, rules):
    """Return list of matching skills for the given prompt."""
    prompt_lower = prompt.lower()
    matches = []
    for rule in rules:
        for trigger in rule["triggers"]:
            if re.search(trigger, prompt_lower):
                matches.append(rule)
                break  # one match per rule is enough
    return matches


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # no input or bad input — pass through silently

    prompt = hook_input.get("prompt", "")
    if not prompt:
        sys.exit(0)

    rules = load_rules()
    if not rules:
        sys.exit(0)

    matches = match_prompt(prompt, rules)
    if not matches:
        sys.exit(0)

    # Build suggestion text — suggest top 2 matches max to avoid noise
    top_matches = matches[:2]
    if len(top_matches) == 1:
        skill = top_matches[0]
        context = (
            f"[Skill suggestion] The skill `/{skill['skill']}` may be relevant here — "
            f"{skill['description']}. "
            f"Mention it to the user if it fits their request."
        )
    else:
        lines = []
        for skill in top_matches:
            lines.append(f"  - `/{skill['skill']}` — {skill['description']}")
        context = (
            "[Skill suggestion] These skills may be relevant:\n"
            + "\n".join(lines)
            + "\nMention the most relevant one to the user if it fits their request."
        )

    # Output JSON with additionalContext
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
