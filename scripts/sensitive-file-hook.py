#!/usr/bin/env python3
"""PreToolUse hook: injects additionalContext when editing sensitive files.

Reads JSON from stdin, checks tool_input.file_path against sensitive patterns,
and returns guidance via additionalContext so Claude behaves like a cautious colleague.
"""

import json
import re
import sys

PATTERNS = [
    {
        "regex": r"auth|permission|acl|rbac",
        "guidance": (
            "This file controls authentication or authorization. "
            "Verify no auth bypass is introduced and no permissions are widened unintentionally."
        ),
    },
    {
        "regex": r"config|settings|\.env",
        "guidance": (
            "This may contain configuration or secrets. "
            "Verify nothing sensitive is exposed and no defaults are changed to insecure values."
        ),
    },
    {
        "regex": r"migration|schema|alembic",
        "guidance": (
            "This is a database migration or schema file. "
            "Verify rollback safety, check for data loss, and ensure the migration is idempotent."
        ),
    },
    {
        "regex": r"secret|credential|token|key|password|cert",
        "guidance": (
            "This file may handle secrets or credentials. "
            "Verify no plaintext secrets are introduced and rotation/expiry is preserved."
        ),
    },
    {
        "regex": r"security|crypto|encrypt|decrypt|hash",
        "guidance": (
            "This file handles security-sensitive operations. "
            "Verify cryptographic choices are sound and no security controls are weakened."
        ),
    },
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Normalize path separators for matching
    normalized = file_path.replace("\\", "/").lower()

    matches = []
    for pattern in PATTERNS:
        if re.search(pattern["regex"], normalized):
            matches.append(pattern["guidance"])

    if not matches:
        sys.exit(0)

    context = "SENSITIVE FILE GUIDANCE: " + " | ".join(matches)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
