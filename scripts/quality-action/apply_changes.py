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


def _get_tracked_files_snapshot(repo_path: Path) -> dict[str, str]:
    """Snapshot all tracked + untracked file contents for change detection."""
    snapshot = {}
    for p in repo_path.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(repo_path))
        # Skip dirs that are not project code
        if any(part in rel for part in [".git", "_quality-action", ".quality-reports", "__pycache__", "node_modules"]):
            continue
        try:
            snapshot[rel] = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    return snapshot


def _files_actually_changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """Return list of files that changed between two snapshots."""
    changed = []
    all_keys = set(before.keys()) | set(after.keys())
    for key in all_keys:
        if before.get(key) != after.get(key):
            changed.append(key)
    return changed


def apply_upgrade_finding(repo_path: Path, finding: dict) -> list[str]:
    """Apply a single upgrade finding. Returns list of files actually modified."""
    cmd = finding.get("upgrade_command")
    if not cmd:
        return []

    # Safety: only allow known package manager install commands
    allowed_prefixes = [
        "pip install", "python -m pip install",
        "npm install", "cargo update", "poetry add",
    ]
    if not any(cmd.strip().startswith(p) for p in allowed_prefixes):
        print(f"  Skipping unsafe command: {cmd}")
        return []

    dep = finding.get("dependency", "")
    new_ver = finding.get("recommended_version", "")

    # Try to update dependency files directly first
    modified = _update_dependency_files(repo_path, dep, new_ver)

    if not modified:
        # Fall back to running the command and checking if files changed
        before = _get_tracked_files_snapshot(repo_path)

        parts = shlex.split(cmd)
        print(f"  Running: {' '.join(parts)}")
        result = subprocess.run(
            parts, cwd=repo_path, capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            print(f"  Failed: {result.stderr[:500]}")
            return []

        after = _get_tracked_files_snapshot(repo_path)
        modified = _files_actually_changed(before, after)

    return modified


def _update_dependency_files(repo_path: Path, dep: str, new_ver: str) -> list[str]:
    """Update dependency version in requirements.txt, pyproject.toml, or setup.cfg.
    Returns list of files that were modified."""
    if not dep or not new_ver:
        return []

    modified = []

    # --- requirements.txt ---
    req_file = repo_path / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        # Match: package==1.0.0, package>=1.0.0, package~=1.0.0, package>=1.0,<2
        pattern = rf"^({re.escape(dep)})\s*([>=<~!]+)\s*[\d][^\n]*"
        replacement = rf"\1\2{new_ver}"
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        if new_content != content:
            req_file.write_text(new_content, encoding="utf-8")
            print(f"  Updated requirements.txt: {dep} -> {new_ver}")
            modified.append("requirements.txt")

    # --- pyproject.toml ---
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        # Match patterns in dependencies lists:
        #   "package>=1.0.0"  "package>=1.0,<2"  "package~=1.0"  "package==1.0"
        pattern = rf'("{re.escape(dep)}\s*[>=<~!]+)\s*[\d][^"]*(")'
        replacement = rf"\g<1>{new_ver}\2"
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            pyproject.write_text(new_content, encoding="utf-8")
            print(f"  Updated pyproject.toml: {dep} -> {new_ver}")
            modified.append("pyproject.toml")

    # --- setup.cfg ---
    setup_cfg = repo_path / "setup.cfg"
    if setup_cfg.exists():
        content = setup_cfg.read_text(encoding="utf-8")
        pattern = rf"^(\s*{re.escape(dep)}\s*[>=<~!]+)\s*[\d][^\n]*"
        replacement = rf"\1{new_ver}"
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        if new_content != content:
            setup_cfg.write_text(new_content, encoding="utf-8")
            print(f"  Updated setup.cfg: {dep} -> {new_ver}")
            modified.append("setup.cfg")

    # --- Also check subdirectory requirements files ---
    for req in repo_path.glob("*/requirements*.txt"):
        rel = str(req.relative_to(repo_path))
        content = req.read_text(encoding="utf-8")
        pattern = rf"^({re.escape(dep)})\s*([>=<~!]+)\s*[\d][^\n]*"
        replacement = rf"\1\2{new_ver}"
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        if new_content != content:
            req.write_text(new_content, encoding="utf-8")
            print(f"  Updated {rel}: {dep} -> {new_ver}")
            modified.append(rel)

    return modified


def apply_strategic_finding(repo_path: Path, finding: dict) -> list[str]:
    """Apply a strategic finding. Returns list of files actually modified."""
    changes = finding.get("suggested_changes")
    if not changes:
        return []

    category = finding.get("category", "")
    # Only apply truly safe categories
    if category not in ("code_quality", "testing"):
        return []

    modified = []

    # Handle "add missing __init__.py"
    if "__init__.py" in changes.lower():
        affected = finding.get("affected_files", [])
        for fpath in affected:
            full = repo_path / fpath
            if not full.exists() and fpath.endswith("__init__.py"):
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text("", encoding="utf-8")
                print(f"  Created: {fpath}")
                modified.append(fpath)

    return modified


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

    all_modified_files = []
    skipped = 0

    for analysis_type, data in report.items():
        for finding in data.get("findings", []):
            if not finding.get("auto_mergeable"):
                continue

            title = finding.get("title") or finding.get("dependency", "unknown")
            print(f"\n[{analysis_type}] {title}")

            if args.dry_run:
                print("  (dry run — would apply)")
                all_modified_files.append("(dry-run)")
                continue

            if analysis_type == "upgrade":
                modified = apply_upgrade_finding(repo_path, finding)
            elif analysis_type == "strategic":
                modified = apply_strategic_finding(repo_path, finding)
            else:
                modified = []

            if modified:
                print(f"  Modified files: {', '.join(modified)}")
                all_modified_files.extend(modified)
            else:
                print("  No files changed — skipping")
                skipped += 1

    # Deduplicate
    unique_files = sorted(set(all_modified_files))
    applied = len(unique_files)

    print(f"\nDone: {applied} file(s) modified, {skipped} skipped")
    if unique_files:
        print(f"Modified files: {', '.join(unique_files)}")

    # Set GitHub Actions outputs — only count as applied if files actually changed
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"changes_applied={applied}\n")

    return 0 if applied > 0 or skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
