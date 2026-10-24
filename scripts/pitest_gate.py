#!/usr/bin/env python3
"""Gate for PIT (pitest) mutation results across Kotlin core modules.

Parses build/reports/pitest/mutations.xml of every core module and computes
an aggregate mutation score: (KILLED + TIMED_OUT) / total mutants.

Usage: python3 scripts/pitest_gate.py --min-score 70
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-score", type=float, default=70.0)
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args()

    counts = {}
    reports = sorted(Path(args.root).glob("core-*/build/reports/pitest/mutations.xml"))
    if not reports:
        print("no pitest reports found - did the pitest task run?")
        return 1

    for report in reports:
        module = report.parts[-4]  # e.g. core-capture
        try:
            tree = ET.parse(report)
        except ET.ParseError as exc:
            print(f"{module}: unreadable report ({exc})")
            return 1
        for mutation in tree.getroot().iter("mutation"):
            status = mutation.get("status", "UNKNOWN")
            counts.setdefault(module, {}).setdefault(status, 0)
            counts[module][status] += 1

    killed_total = 0
    meaningful_total = 0
    print(f"{'module':<18}{'killed':>8}{'timed_out':>11}{'survived':>10}{'no_cov':>8}{'score':>8}")
    for module, by_status in counts.items():
        killed = by_status.get("KILLED", 0)
        timed_out = by_status.get("TIMED_OUT", 0)
        survived = by_status.get("SURVIVED", 0)
        no_coverage = by_status.get("NO_COVERAGE", 0)
        meaningful = killed + timed_out + survived + no_coverage
        killed_total += killed + timed_out
        meaningful_total += meaningful
        score = 100.0 * (killed + timed_out) / meaningful if meaningful else 0.0
        print(f"{module:<18}{killed:>8}{timed_out:>11}{survived:>10}{no_coverage:>8}{score:>7.1f}%")

    if meaningful_total == 0:
        print("no mutants recorded")
        return 1
    aggregate = 100.0 * killed_total / meaningful_total
    print(f"\nkotlin mutation score: {aggregate:.1f}% ({killed_total}/{meaningful_total})")
    if aggregate < args.min_score:
        print(f"FAIL: score below threshold {args.min_score:.1f}%")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
