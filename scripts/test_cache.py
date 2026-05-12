#!/usr/bin/env python3
"""test_cache: commit-SHA-keyed pytest result cache.

Shared helper for self-learning skills (e.g. pr-merge-readiness) so tests
already passed for the current commit can be skipped when the working tree
is clean.

The script ships in the claude-library plugin and is reached via
${CLAUDE_PLUGIN_ROOT}. It must be invoked with CWD inside the TARGET repo
(the repo that owns the tests); git plumbing runs against that CWD. The
cache lives in the target repo so results travel with the code via git:

    <target-repo-root>/documentation/test-results/<sha>.json

Cache JSON schema (v1):

    {
      "commit": "<sha>",
      "branch": "<branch at time of write>",
      "schema_version": 1,
      "first_recorded_ts": "<iso8601>",
      "last_updated_ts":   "<iso8601>",
      "command_history": [
        {"ts": "...", "command": "pytest -m smoke", "scope": "full",
         "wall_clock_s": 4.2, "tests_recorded": 37}
      ],
      "results": {"<nodeid>": "passed|failed|skipped|error", ...},
      "env": {"python": "3.11.4", "platform": "win32"}
    }

CLI:
    lookup <sha>
    tests-to-run <sha> [--collected FILE]
    record <sha> --report JUNIT_XML --scope full|filter [--command CMD]
                 [--wall-clock-s N]
    status [<sha>]
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


CACHE_SUBDIR = "documentation/test-results"
SCHEMA_VERSION = 1


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()


def repo_root() -> Path:
    return Path(_run(["git", "rev-parse", "--show-toplevel"]))


def head_sha() -> str:
    return _run(["git", "rev-parse", "HEAD"])


def current_branch() -> str:
    try:
        return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    except subprocess.CalledProcessError:
        return "(detached)"


def is_tree_clean(ignore_cache_writes: bool = True) -> bool:
    """True iff the working tree has no uncommitted changes.

    When ``ignore_cache_writes`` is True (default), changes inside
    ``documentation/test-results/`` are ignored. This keeps the helper's
    own writes from self-invalidating the cache: a fresh run can record
    its results and a subsequent skill's lookup will still treat the
    tree as clean. The cache directory is data the helper owns; it
    cannot affect what the tests do.
    """
    out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if ignore_cache_writes:
        lines = [ln for ln in lines if CACHE_SUBDIR not in ln]
    return not lines


def cache_path(sha: str) -> Path:
    return repo_root() / CACHE_SUBDIR / f"{sha}.json"


def load_entry(sha: str) -> dict | None:
    p = cache_path(sha)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_entry(sha: str, entry: dict) -> Path:
    p = cache_path(sha)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------- junit parsing ----------

def _module_path_from_file(file_attr: str) -> str:
    norm = file_attr.replace("\\", "/")
    if norm.endswith(".py"):
        norm = norm[:-3]
    return norm.replace("/", ".")


def junit_to_nodeid(tc: ET.Element) -> str | None:
    """Reconstruct a pytest nodeid from a junit <testcase> element.

    pytest emits classname=<dotted module path>[.ClassName] and name=<test_name>.
    file= is reliable for pytest's junit reporter; we use it when present and
    fall back to deriving the file from classname otherwise.
    """
    name = tc.get("name")
    classname = tc.get("classname") or ""
    file_attr = tc.get("file")
    if not name:
        return None

    if not file_attr:
        parts = classname.split(".")
        while parts and parts[-1][:1].isupper():
            parts.pop()
        file_attr = "/".join(parts) + ".py" if parts else classname

    module = _module_path_from_file(file_attr)
    if classname == module or not classname:
        return f"{file_attr}::{name}"
    if classname.startswith(module + "."):
        class_chain = classname[len(module) + 1 :].split(".")
        return f"{file_attr}::" + "::".join(class_chain + [name])
    return f"{file_attr}::{classname}::{name}"


def parse_junit(report_path: Path) -> dict[str, str]:
    tree = ET.parse(report_path)
    root = tree.getroot()
    suites = root.findall(".//testsuite") if root.tag == "testsuites" else [root]
    out: dict[str, str] = {}
    for suite in suites:
        for tc in suite.findall("testcase"):
            nodeid = junit_to_nodeid(tc)
            if not nodeid:
                continue
            if tc.find("failure") is not None:
                status = "failed"
            elif tc.find("error") is not None:
                status = "error"
            elif tc.find("skipped") is not None:
                status = "skipped"
            else:
                status = "passed"
            out[nodeid] = status
    return out


# ---------- subcommands ----------

def cmd_lookup(args: argparse.Namespace) -> int:
    entry = load_entry(args.sha)
    if entry is None:
        print(f"# no cache entry for {args.sha}", file=sys.stderr)
        return 1
    json.dump(entry, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def _read_collected(args: argparse.Namespace) -> list[str]:
    if args.collected:
        text = Path(args.collected).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]


def cmd_tests_to_run(args: argparse.Namespace) -> int:
    collected = _read_collected(args)
    entry = load_entry(args.sha)
    cur_sha = head_sha()
    clean = is_tree_clean()

    trustworthy = (
        entry is not None
        and entry.get("commit") == args.sha
        and args.sha == cur_sha
        and clean
    )

    if not trustworthy:
        reason = (
            "no cache" if entry is None
            else "sha mismatch" if args.sha != cur_sha
            else "dirty tree" if not clean
            else "stale entry"
        )
        print(f"# cache untrustworthy ({reason}) — returning full set", file=sys.stderr)
        for nid in collected:
            print(nid)
        return 0

    results = entry.get("results", {})
    skipped = 0
    for nid in collected:
        if results.get(nid) == "passed":
            skipped += 1
            continue
        print(nid)
    print(
        f"# cache hit: {skipped}/{len(collected)} already passed for {args.sha[:8]}",
        file=sys.stderr,
    )
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    report = Path(args.report)
    if not report.exists():
        print(f"error: report file not found: {report}", file=sys.stderr)
        return 2

    new_results = parse_junit(report)
    if not new_results:
        print("warning: junit report had no <testcase> elements", file=sys.stderr)

    entry = load_entry(args.sha) or {
        "commit": args.sha,
        "branch": current_branch(),
        "first_recorded_ts": now_iso(),
        "schema_version": SCHEMA_VERSION,
        "command_history": [],
        "results": {},
        "env": {"python": platform.python_version(), "platform": sys.platform},
    }

    entry["last_updated_ts"] = now_iso()
    entry["results"].update(new_results)
    entry["command_history"].append({
        "ts": now_iso(),
        "command": args.command or "(unspecified)",
        "scope": args.scope,
        "wall_clock_s": args.wall_clock_s,
        "tests_recorded": len(new_results),
    })

    out = save_entry(args.sha, entry)
    counts = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
    for s in new_results.values():
        counts[s] = counts.get(s, 0) + 1
    print(
        f"recorded {len(new_results)} results "
        f"(passed={counts['passed']} failed={counts['failed']} "
        f"skipped={counts['skipped']} error={counts['error']}) -> "
        f"{out.relative_to(repo_root())}"
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    sha = args.sha or head_sha()
    entry = load_entry(sha)
    clean = is_tree_clean()
    if entry is None:
        print(f"no cache for {sha[:8]} (working tree: {'clean' if clean else 'dirty'})")
        return 1
    counts = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
    for s in entry.get("results", {}).values():
        counts[s] = counts.get(s, 0) + 1
    print(f"sha={sha[:8]} branch={entry.get('branch')} clean={clean}")
    print(f"first={entry.get('first_recorded_ts')} last={entry.get('last_updated_ts')}")
    print(
        f"results: passed={counts['passed']} failed={counts['failed']} "
        f"skipped={counts['skipped']} error={counts['error']} "
        f"(total={sum(counts.values())})"
    )
    print(f"runs recorded: {len(entry.get('command_history', []))}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="test_cache", description=__doc__.split("\n\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("lookup", help="print cached entry as JSON")
    sp.add_argument("sha")
    sp.set_defaults(func=cmd_lookup)

    sp = sub.add_parser("tests-to-run", help="print nodeids still needing a run")
    sp.add_argument("sha")
    sp.add_argument("--collected", help="path to file with one nodeid per line (default: stdin)")
    sp.set_defaults(func=cmd_tests_to_run)

    sp = sub.add_parser("record", help="merge junit XML results into the cache")
    sp.add_argument("sha")
    sp.add_argument("--report", required=True, help="path to pytest --junit-xml output")
    sp.add_argument("--scope", choices=("full", "filter"), required=True,
                    help="full = whole-suite intent; filter = ran a subset (e.g. -k or specific nodeids)")
    sp.add_argument("--command", help="exact pytest command that ran (for the audit)")
    sp.add_argument("--wall-clock-s", type=float, default=None)
    sp.set_defaults(func=cmd_record)

    sp = sub.add_parser("status", help="human summary of the cache for a SHA")
    sp.add_argument("sha", nargs="?")
    sp.set_defaults(func=cmd_status)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except subprocess.CalledProcessError as e:
        print(f"error: git command failed: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
