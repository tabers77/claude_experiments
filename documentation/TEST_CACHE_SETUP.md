# Test-cache setup — target repo opt-in

The claude-library plugin ships a pytest plugin (`scripts/pytest_test_cache.py`) that adds a **commit-SHA-keyed test cache** to any project. Once wired, every pytest invocation in the target repo:

- **Deselects** tests that already passed for the current HEAD SHA on a clean working tree.
- **Records** the outcome of every test that ran into `documentation/test-results/<sha>.json`, merging with prior results for the same SHA.

The cache is a property of the **repo + branch**, not of any specific Claude skill — `shared-bug-gap-fix`, `pr-merge-readiness`, `commit-ready`, raw `pytest` from your terminal, and CI all participate. Any of them can run tests; any of them benefits from work the others already did.

## One-time setup (per target repo)

Add a `conftest.py` at the repo root (or merge the snippet into an existing one):

```python
# conftest.py — claude-library SHA-keyed test cache
#
# Reads the CLAUDE_PLUGIN_ROOT env var set by Claude Code when the
# claude-library plugin is loaded. For raw pytest runs outside Claude
# Code (CI, terminal), set CLAUDE_PLUGIN_ROOT yourself or replace the
# fallback path below with a hard-coded plugin path.

import os
import sys

_PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT")
# Optional fallback for when Claude Code isn't the caller — point this at
# the cloned claude-library plugin on disk, or leave empty to disable.
_FALLBACK = ""  # e.g. r"C:\Users\you\Repos\claude_experiments"

_root = _PLUGIN_ROOT or _FALLBACK
pytest_plugins = []
if _root:
    _scripts = os.path.join(_root, "scripts")
    if os.path.isdir(_scripts):
        if _scripts not in sys.path:
            sys.path.insert(0, _scripts)
        pytest_plugins = ["pytest_test_cache"]
```

That's it. No package install, no `pip` dependency. Every subsequent `pytest` invocation in the repo participates.

## Verify it's wired

```
pytest --help | grep -A1 test_cache
```

Should print the `--no-test-cache` option under a `test_cache` group. Then run pytest once; you should see a line like:

```
[test-cache] recorded 12 results -> documentation/test-results/abc12345.json
```

Run pytest again immediately — on the second run you should see:

```
[test-cache] skipped 12 tests already passed for abc12345
```

…and pytest completes in a fraction of the time.

## Commit the cache or gitignore it?

| Choice | Effect |
|---|---|
| **Commit** `documentation/test-results/` (recommended for team workflows) | Teammates pulling the same SHA inherit the cache and skip re-running passed tests. The whole point of "branch-level cache that any skill picks up". |
| **Gitignore** it (recommended for solo projects or large suites) | Cache stays local; no commit noise. You still benefit across sessions on your own machine. |

Either choice is valid. Pick one explicitly and stick with it.

## Per-run opt-out

Disable for one invocation:

```
pytest --no-test-cache
```

The plugin will neither skip nor record on that run. Use this when:

- A test is non-deterministic and you want a fresh sample.
- You suspect the cache is wrong (rare; usually means a `documentation/test-results/<sha>.json` was hand-edited).
- You're debugging a flaky test and want every run to actually execute it.

To always disable: don't add the conftest.py snippet, or set `pytest_plugins = []` unconditionally.

## When the cache is treated as untrustworthy

The plugin **records** results regardless, but it **only deselects** when all of these hold:

- `git rev-parse HEAD` succeeds (we're inside a git repo).
- The working tree is clean (changes inside `documentation/test-results/` are ignored — the plugin's own writes don't self-invalidate).
- `documentation/test-results/<HEAD-sha>.json` exists and its `commit` field matches HEAD.

Otherwise: every test runs and the result is still recorded (so the next clean-tree run benefits).

## Inspecting the cache

The CLI helper at `scripts/test_cache.py` is for ad-hoc inspection:

```
python "$CLAUDE_PLUGIN_ROOT/scripts/test_cache.py" status         # current HEAD
python "$CLAUDE_PLUGIN_ROOT/scripts/test_cache.py" status <sha>   # specific SHA
python "$CLAUDE_PLUGIN_ROOT/scripts/test_cache.py" lookup <sha>   # full JSON dump
```

The plugin uses the helper's functions under the hood (no duplicated state).

## Limitations

- **Per-test outcomes only.** A test that flips from `passed` → `failed` after a code change at the same SHA is impossible (the SHA captures the code), so a dirty tree always invalidates skipping. There's no smarter "only-rerun-affected-tests" mode — that would require per-test source-dependency tracking, which the plugin doesn't do.
- **Junit-style nodeids only.** Parametrized tests work (`test_foo[case-1]` is a distinct nodeid). Tests with non-deterministic IDs (rare) won't match across runs.
- **`pytest-xdist` is untested.** The plugin uses a single in-process state object; in a multi-process xdist run, each worker would try to write the cache concurrently. If you use xdist, treat caching as best-effort or run with `-p no:claude_library_test_cache --no-test-cache` and rely on xdist's own scheduling.
- **Live UI tests should opt out.** They depend on external state (running dev stack, browser) that the SHA doesn't capture. Add `--no-test-cache` to your live UI command.
