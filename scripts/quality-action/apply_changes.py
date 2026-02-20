"""
Apply auto-mergeable changes from the quality analysis report.

Only applies safe, low-risk changes:
- Dependency version bumps (patch/minor with no breaking changes)
- Trivial code fixes (unused imports, missing __init__.py)

Usage:
    python apply_changes.py --repo-path /path/to/repo --report quality-report.json
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path


def apply_upgrade_finding(repo_path: Path, finding: dict) -> bool:
    """Apply a single upgrade finding (dependency version bump)."""
    cmd = finding.get("upgrade_command")
    if not cmd:
        return False

    # Safety: only allow pip install, npm install, cargo update
    allowed_prefixes = ["pip install", "npm install", "cargo update", "poetry add"]
    if not any(cmd.strip().startswith(p) for p in allowed_prefixes):
        print(f"  Skipping unsafe command: {cmd}")
        return False

    # Strip quotes from arguments — LLMs often wrap specs like 'pytest>=8.0'
    parts = shlex.split(cmd)
    print(f"  Applying: {' '.join(parts)}")
    result = subprocess.run(
        parts, cwd=repo_path, capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        print(f"  Failed: {result.stderr[:500]}")
        return False

    # Update requirements.txt if it's a pip install
    if cmd.startswith("pip install") and (repo_path / "requirements.txt").exists():
        _update_requirements_txt(repo_path, finding)

    return True


def _update_requirements_txt(repo_path: Path, finding: dict):
    """Update requirements.txt with the new version."""
    req_file = repo_path / "requirements.txt"
    content = req_file.read_text(encoding="utf-8")
    dep = finding["dependency"]
    new_ver = finding["recommended_version"]

    # Match patterns: package==1.0.0, package>=1.0.0, package~=1.0.0
    pattern = rf"^({re.escape(dep)})\s*([>=<~!]+)\s*[\d][^\n]*"
    replacement = rf"\1\2{new_ver}"
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if new_content != content:
        req_file.write_text(new_content, encoding="utf-8")
        print(f"  Updated requirements.txt: {dep} -> {new_ver}")


def apply_strategic_finding(repo_path: Path, finding: dict) -> bool:
    """Apply a strategic finding (only trivial code changes)."""
    changes = finding.get("suggested_changes")
    if not changes:
        return False

    category = finding.get("category", "")
    # Only apply truly safe categories
    if category not in ("code_quality",):
        return False

    # For now, only handle "add missing __init__.py"
    if "__init__.py" in changes.lower():
        affected = finding.get("affected_files", [])
        for fpath in affected:
            full = repo_path / fpath
            if not full.exists():
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text("", encoding="utf-8")
                print(f"  Created: {fpath}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Apply auto-mergeable changes")
    parser.add_argument("--repo-path", required=True, help="Path to the repository")
    parser.add_argument(
        "--report", required=True, help="Path to quality-report.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without applying",
    )
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))

    applied = 0
    skipped = 0

    for analysis_type, data in report.items():
        for finding in data.get("findings", []):
            if not finding.get("auto_mergeable"):
                continue

            title = finding.get("title") or finding.get("dependency", "unknown")
            print(f"\n[{analysis_type}] {title}")

            if args.dry_run:
                print("  (dry run — would apply)")
                applied += 1
                continue

            if analysis_type == "upgrade":
                ok = apply_upgrade_finding(repo_path, finding)
            elif analysis_type == "strategic":
                ok = apply_strategic_finding(repo_path, finding)
            else:
                ok = False

            if ok:
                applied += 1
            else:
                skipped += 1

    print(f"\nDone: {applied} applied, {skipped} skipped")

    # Set GitHub Actions outputs
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"changes_applied={applied}\n")

    return 0 if applied > 0 or skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
