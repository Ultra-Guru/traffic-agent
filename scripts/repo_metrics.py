#!/usr/bin/env python3
"""Repository metrics: per-language / per-module line counts.

Usage:
    python3 scripts/repo_metrics.py                    # print stats table
    python3 scripts/repo_metrics.py --write stats.txt  # also write to file
    python3 scripts/repo_metrics.py --gate base.txt    # fail if total < baseline

Counted source roots (production + tests, excluding generated/build dirs):
    native-engine/  (*.h, *.cpp, *.inc)
    core-*/src/     (*.kt)
    app/src/        (*.kt, *.xml)
    python/         (*.py, excluding venv)
    scripts/        (*.py)
    docs/           (*.md)

The gate keeps the repository from regressing below a committed floor,
which protects large feature work from being accidentally deleted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# language -> list of glob suffixes
EXTENSIONS = {
    "cpp": [".h", ".cpp", ".inc"],
    "kotlin": [".kt", ".kts"],
    "xml": [".xml"],
    "python": [".py"],
    "markdown": [".md"],
}

# module -> (display name, roots)
MODULES = [
    ("native-engine", [REPO_ROOT / "native-engine"]),
    ("core-agent", [REPO_ROOT / "core-agent" / "src"]),
    ("core-analysis", [REPO_ROOT / "core-analysis" / "src"]),
    ("core-capture", [REPO_ROOT / "core-capture" / "src"]),
    ("core-exports", [REPO_ROOT / "core-exports" / "src"]),
    ("core-mitm", [REPO_ROOT / "core-mitm" / "src"]),
    ("core-transform", [REPO_ROOT / "core-transform" / "src"]),
    ("app", [REPO_ROOT / "app" / "src"]),
    ("python", [REPO_ROOT / "python"]),
    ("scripts", [REPO_ROOT / "scripts"]),
    ("docs", [REPO_ROOT / "docs"]),
]

EXCLUDED_DIRS = {
    "build", ".gradle", ".git", "__pycache__", "venv", "node_modules",
    ".pytest_cache", "mutants", "htmlcov", ".mutmut-cache",
}


def count_file(path: Path) -> int:
    """Count physical lines (every line incl. blanks) of a text file."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def collect(root: Path) -> dict[str, int]:
    """Walk a root, return {language: lines} skipping excluded dirs."""
    out: dict[str, int] = {}
    if not root.exists():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name == "repo_metrics.py" and path.parent.name == "scripts":
            continue
        lang = next(
            (lg for lg, exts in EXTENSIONS.items() if path.suffix in exts),
            None,
        )
        if lang is None:
            continue
        out[lang] = out.get(lang, 0) + count_file(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="traffic-agent repository metrics")
    ap.add_argument("--write", type=Path, default=None, help="write stats table to this file")
    ap.add_argument("--gate", type=Path, default=None, help="fail when total < baseline in file")
    args = ap.parse_args()

    per_module: list[tuple[str, dict[str, int]]] = []
    grand: dict[str, int] = {}
    for name, roots in MODULES:
        agg: dict[str, int] = {}
        for root in roots:
            for lang, lines in collect(root).items():
                agg[lang] = agg.get(lang, 0) + lines
        per_module.append((name, agg))
        for lang, lines in agg.items():
            grand[lang] = grand.get(lang, 0) + lines

    width = max(len(name) for name, _ in per_module)
    header = f"{'module'.ljust(width)}  cpp    kotlin xml    python markdown  module-total"
    lines = [header, "-" * len(header)]
    for name, agg in per_module:
        cpp = agg.get("cpp", 0)
        kt = agg.get("kotlin", 0)
        xml = agg.get("xml", 0)
        py = agg.get("python", 0)
        md = agg.get("markdown", 0)
        total = cpp + kt + xml + py + md
        lines.append(
            f"{name.ljust(width)}  {str(cpp).ljust(6)} {str(kt).ljust(6)} {str(xml).ljust(6)} "
            f"{str(py).ljust(6)} {str(md).ljust(8)} {total}"
        )
    lines.append("-" * len(header))
    total_all = sum(grand.values())
    lines.append(
        f"{'TOTAL'.ljust(width)}  {str(grand.get('cpp', 0)).ljust(6)} "
        f"{str(grand.get('kotlin', 0)).ljust(6)} {str(grand.get('xml', 0)).ljust(6)} "
        f"{str(grand.get('python', 0)).ljust(6)} {str(grand.get('markdown', 0)).ljust(8)} {total_all}"
    )
    table = "\n".join(lines)
    print(table)

    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(table + "\n", encoding="utf-8")
        print(f"\n[metrics] written to {args.write}")

    if args.gate:
        try:
            baseline = int(args.gate.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            print(f"[metrics] ERROR: cannot read baseline from {args.gate}", file=sys.stderr)
            return 2
        if total_all < baseline:
            print(
                f"[metrics] FAIL: total {total_all} < baseline {baseline} "
                f"(-{baseline - total_all} lines)",
                file=sys.stderr,
            )
            return 1
        print(f"[metrics] gate OK: total {total_all} >= baseline {baseline} (+{total_all - baseline})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
