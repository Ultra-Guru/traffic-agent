#!/usr/bin/env python3
"""Gate for mutmut 3.x results.

Parses mutants/**/*.meta files written by mutmut 3 and computes the mutation
score from the recorded exit codes:
    1 / 3            -> killed
    24/-24/36/152... -> timeout (counted as killed)
    0                -> survived
    33 / 34 / None   -> no tests / skipped / not checked (excluded)

Usage: python3 scripts/mutmut_gate.py --min-score 70 [--mutants python/mutants]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

KILLED_CODES = {1, 3}
TIMEOUT_CODES = {24, -24, 36, 152, 255, -11, -9}
SURVIVED_CODES = {0}
EXCLUDED_CODES = {33, 34, None}  # no tests / skipped / not checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-score", type=float, default=70.0)
    parser.add_argument("--mutants", default=str(REPO_ROOT / "python" / "mutants"))
    args = parser.parse_args()

    mutants_dir = Path(args.mutants)
    if not mutants_dir.exists():
        print(f"no mutants directory at {mutants_dir} - did mutmut run?")
        return 1

    counts = {"killed": 0, "timeout": 0, "survived": 0, "excluded": 0}
    for meta_path in mutants_dir.rglob("*.meta"):
        data = json.loads(meta_path.read_text())
        for _key, code in data.get("exit_code_by_key", {}).items():
            if code in KILLED_CODES:
                counts["killed"] += 1
            elif code in TIMEOUT_CODES:
                counts["timeout"] += 1
            elif code in SURVIVED_CODES:
                counts["survived"] += 1
            else:
                counts["excluded"] += 1

    meaningful = counts["killed"] + counts["timeout"] + counts["survived"]
    if meaningful == 0:
        print("no mutation results recorded - did mutmut run?")
        return 1

    score = 100.0 * (counts["killed"] + counts["timeout"]) / meaningful
    print(f"python mutation score: {score:.1f}%")
    print(
        f"  killed={counts['killed']} timeout={counts['timeout']} "
        f"survived={counts['survived']} excluded={counts['excluded']}"
    )
    if score < args.min_score:
        print(f"FAIL: score below threshold {args.min_score:.1f}%")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
