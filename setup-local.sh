#!/usr/bin/env bash
# Setup local skill/agent access for this repo.
# Creates symlinks (Linux/Mac) or junctions (Windows) so that
# .claude/skills/ and .claude/agents/ point to the repo-root
# skills/ and agents/ directories.
#
# Usage: bash setup-local.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$SCRIPT_DIR/.claude"

mkdir -p "$CLAUDE_DIR"

# Remove existing links/dirs if present
if [ -L "$CLAUDE_DIR/skills" ] || [ -d "$CLAUDE_DIR/skills" ]; then
    rm -rf "$CLAUDE_DIR/skills"
fi
if [ -L "$CLAUDE_DIR/agents" ] || [ -d "$CLAUDE_DIR/agents" ]; then
    rm -rf "$CLAUDE_DIR/agents"
fi

# Detect OS and create appropriate links
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows: use directory junctions via PowerShell (no admin required)
    # Note: cmd //c mklink + cygpath is fragile with nested quoting;
    # PowerShell's New-Item -ItemType Junction works reliably from Git Bash.
    SKILLS_WIN=$(cygpath -w "$CLAUDE_DIR/skills")
    SKILLS_TARGET_WIN=$(cygpath -w "$SCRIPT_DIR/skills")
    AGENTS_WIN=$(cygpath -w "$CLAUDE_DIR/agents")
    AGENTS_TARGET_WIN=$(cygpath -w "$SCRIPT_DIR/agents")
    powershell -Command "New-Item -ItemType Junction -Path '$SKILLS_WIN' -Target '$SKILLS_TARGET_WIN'" > /dev/null
    powershell -Command "New-Item -ItemType Junction -Path '$AGENTS_WIN' -Target '$AGENTS_TARGET_WIN'" > /dev/null
else
    # Linux/Mac: use symbolic links (relative paths for portability)
    ln -s ../skills "$CLAUDE_DIR/skills"
    ln -s ../agents "$CLAUDE_DIR/agents"
fi

echo "Done! .claude/skills/ -> skills/ and .claude/agents/ -> agents/"
echo "Skills are now available locally as /skill-name (no plugin needed)."
