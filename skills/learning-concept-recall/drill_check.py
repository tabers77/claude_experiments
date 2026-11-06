"""Verify Daily Drill cards before they are published, and split them into one
document file per card for the page's `cards` collection.

    python drill_check.py cards.json --out <outbox_dir>

A card is published only if every check passes:
  * the fields the page renders are present (it silently drops a card missing one);
  * kata cards: the `reference` solution passes ALL tests, and the untouched `stub`
    fails at least one (a test suite the stub passes teaches nothing);
  * the theory question stays short (a card is sized for one terminal wait).

The harness mirrors the page's: `t(name, ok, msg)` records a result; prelude,
then the learner's source, then the tests run in one namespace.
Exit code 0 = all cards passed and were written; 1 = nothing was written.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

REQUIRED = ("id", "title", "theory", "answer", "kind", "task", "src", "concepts")
MAX_THEORY_CHARS = 220
PUBLISHED_FIELDS = (
    "id", "title", "concepts", "src", "theory", "answer", "kind", "task",
    "stub", "reveal", "code", "kata", "order", "added_at",
)


def run_kata(prelude: str, source: str, tests: str) -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    def t(name: str, ok: object, msg: str = "") -> None:
        results.append((name, bool(ok), "" if ok else str(msg)))

    ns: dict[str, object] = {"t": t}
    try:
        exec(prelude, ns)  # noqa: S102 - our own card content, run locally to verify it
        exec(source, ns)  # noqa: S102
        exec(tests, ns)  # noqa: S102
    except Exception:
        results.append(("raised", False, traceback.format_exc(limit=1)[-300:]))
    return results


def check(card: dict) -> list[str]:
    problems = [f"missing field `{f}`" for f in REQUIRED if not card.get(f)]
    if card.get("kind") not in ("kata", "predict"):
        problems.append("kind must be 'kata' or 'predict'")
    if len(str(card.get("theory", ""))) > MAX_THEORY_CHARS:
        problems.append(f"theory question longer than {MAX_THEORY_CHARS} chars")
    src = card.get("src") or {}
    if not src.get("sha") or not src.get("file"):
        problems.append("src needs `sha` and `file` (where the answer was verified)")
    if card.get("kind") == "kata":
        kata = card.get("kata") or {}
        if not kata.get("tests") or not card.get("reference") or not card.get("stub"):
            problems.append("kata cards need kata.tests, reference and stub")
        else:
            prelude = kata.get("prelude", "")
            ref = run_kata(prelude, card["reference"], kata["tests"])
            failed = [n for n, ok, _ in ref if not ok]
            if not ref:
                problems.append("tests recorded no results")
            if failed:
                problems.append(f"reference fails: {failed}")
            if all(ok for _, ok, _ in run_kata(prelude, card["stub"], kata["tests"])):
                problems.append("the stub already passes every test")
    elif not card.get("reveal"):
        problems.append("predict cards need a `reveal`")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cards", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    cards = json.loads(args.cards.read_text(encoding="utf-8"))
    bad = 0
    for card in cards:
        problems = check(card)
        print(("FAIL " if problems else "PASS ") + str(card.get("id")))
        for p in problems:
            print("     - " + p)
        bad += bool(problems)
    if bad:
        print(f"{bad} card(s) failed; nothing written.")
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        doc = {k: card[k] for k in PUBLISHED_FIELDS if k in card}
        (args.out / f"{card['id']}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"wrote {len(cards)} card file(s) to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
