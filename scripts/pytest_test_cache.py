"""pytest plugin: commit-SHA-keyed test cache.

Once registered, every pytest invocation in the target repo:

  1. At collection, **deselects** tests that already passed for the current
     HEAD SHA when the working tree is clean (ignoring the cache dir itself).
  2. At session end, **records** the outcome of every test that ran into
     ``documentation/test-results/<sha>.json`` (merging with any existing
     entry). Subsequent skills / pytest runs at the same SHA reuse this.

The plugin makes the cache a property of the **repo + branch**, not of any
specific skill: any skill that runs pytest contributes, any skill that runs
pytest benefits — including raw human ``pytest`` runs from the terminal.

Wiring: drop a small ``conftest.py`` snippet into the target repo so this
module is registered as a pytest plugin. See
``documentation/TEST_CACHE_SETUP.md`` in the claude-library plugin.

CLI flags:
  --no-test-cache        Disable for one run (don't skip, don't record).

Telemetry: a terminal summary line reports what happened ("skipped N from
cache", "recorded N results", or the disabled reason).
"""

from __future__ import annotations

import platform
import sys

import pytest

import test_cache  # sibling module; conftest.py puts scripts/ on sys.path


# pytest report.outcome strings ranked by severity — worst wins per nodeid
_OUTCOME_RANK = {"passed": 0, "skipped": 1, "failed": 2, "error": 2}


class TestCachePlugin:
    """Stateful pytest plugin instance.

    State lives on the instance, not on module globals, so pytest_xdist or
    other multi-process runners can be added later without rework.
    """

    def __init__(self) -> None:
        self.sha: str | None = None
        self.disabled_reason: str | None = None
        self.skipped_from_cache: list[str] = []
        # nodeid -> "passed" | "failed" | "skipped" | "error"; set incrementally
        # via pytest_runtest_logreport, worst-status wins.
        self.results: dict[str, str] = {}

    # ----- collection: deselect previously-passed tests -----

    def pytest_collection_modifyitems(self, config, items):
        if config.getoption("--no-test-cache"):
            self.disabled_reason = "--no-test-cache"
            return
        try:
            self.sha = test_cache.head_sha()
        except Exception as e:
            self.disabled_reason = f"no git HEAD ({e.__class__.__name__})"
            return
        if not test_cache.is_tree_clean():
            self.disabled_reason = "dirty tree"
            return  # still record at session end; just don't skip
        entry = test_cache.load_entry(self.sha)
        if entry is None or entry.get("commit") != self.sha:
            # no usable cache yet — fresh run, nothing to skip
            return
        cached = entry.get("results", {})
        keep: list = []
        skip: list = []
        for item in items:
            if cached.get(item.nodeid) == "passed":
                skip.append(item)
            else:
                keep.append(item)
        if skip:
            config.hook.pytest_deselected(items=skip)
            items[:] = keep
            self.skipped_from_cache = [it.nodeid for it in skip]

    # ----- per-test report capture -----

    def pytest_runtest_logreport(self, report):
        # pytest emits a report per phase: setup, call, teardown.
        # We collapse to a single outcome per nodeid, with the worst phase winning.
        nodeid = report.nodeid
        outcome = report.outcome  # "passed" | "failed" | "skipped"

        # A failed setup/teardown is an "error" in junit terms — distinguish it
        # from a regular test failure so cache consumers can decide what to do.
        if outcome == "failed" and report.when in ("setup", "teardown"):
            outcome = "error"

        prev = self.results.get(nodeid)
        if prev is None or _OUTCOME_RANK[outcome] > _OUTCOME_RANK[prev]:
            self.results[nodeid] = outcome

    # ----- session end: persist -----

    def pytest_sessionfinish(self, session, exitstatus):
        if self.disabled_reason == "--no-test-cache":
            return
        if not self.sha or not self.results:
            return
        try:
            entry = test_cache.load_entry(self.sha) or {
                "commit": self.sha,
                "branch": test_cache.current_branch(),
                "first_recorded_ts": test_cache.now_iso(),
                "schema_version": test_cache.SCHEMA_VERSION,
                "command_history": [],
                "results": {},
                "env": {
                    "python": platform.python_version(),
                    "platform": sys.platform,
                },
            }
            entry["last_updated_ts"] = test_cache.now_iso()
            entry["results"].update(self.results)
            entry["command_history"].append({
                "ts": test_cache.now_iso(),
                "command": "pytest (via pytest_test_cache plugin)",
                "scope": "full",
                "tests_recorded": len(self.results),
                "skipped_from_cache": len(self.skipped_from_cache),
                "exit_status": int(exitstatus),
            })
            test_cache.save_entry(self.sha, entry)
            self._saved = True
        except Exception as e:
            self._save_error = repr(e)

    # ----- terminal summary -----

    def pytest_terminal_summary(self, terminalreporter):
        tr = terminalreporter
        if self.disabled_reason:
            tr.write_line(f"[test-cache] disabled: {self.disabled_reason}")
            return
        if self.skipped_from_cache:
            short = (self.sha or "?")[:8]
            tr.write_line(
                f"[test-cache] skipped {len(self.skipped_from_cache)} tests "
                f"already passed for {short}"
            )
        if getattr(self, "_save_error", None):
            tr.write_line(f"[test-cache] failed to record results: {self._save_error}")
        elif getattr(self, "_saved", False):
            short = (self.sha or "?")[:8]
            tr.write_line(
                f"[test-cache] recorded {len(self.results)} results -> "
                f"documentation/test-results/{short}.json"
            )


_plugin = TestCachePlugin()


def pytest_addoption(parser):
    group = parser.getgroup("test_cache", "SHA-keyed pytest result cache")
    group.addoption(
        "--no-test-cache",
        action="store_true",
        default=False,
        help="Disable the SHA-keyed test cache (do not skip, do not record).",
    )


def pytest_configure(config):
    config.pluginmanager.register(_plugin, "claude_library_test_cache")
