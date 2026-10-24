#!/usr/bin/env python3
"""Source-annotated mutation testing for the native C++ engine.

Lines carrying a trailing `// MUT:<op>` comment are mutated by replacing the
last standalone comparison operator on that line with <op>. Each mutant is
rebuilt incrementally and the test binary is executed; a non-zero exit (or a
timeout / crash) kills the mutant.

Usage:
    python3 scripts/native_mutate.py [--min-score 70] [--src native-engine/src]
                                     [--build-dir native-engine/build] [--list]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OPERATORS = ["==", "!=", "<=", ">=", "<", ">"]
MARKER_RE = re.compile(r"//\s*MUT:(==|!=|<=|>=|<|>)\s*$")
NOT_OP_CHARS = set("<>=!")


def find_mutations(src_dir: Path) -> list[dict]:
    mutations = []
    for cpp in sorted(src_dir.glob("*.cpp")):
        original = cpp.read_text()
        for lineno, line in enumerate(original.splitlines(), start=1):
            match = MARKER_RE.search(line)
            if not match:
                continue
            mutations.append(
                {"file": cpp, "lineno": lineno, "new_op": match.group(1), "line": line}
            )
    return mutations


def last_standalone_operator(code: str) -> tuple[int, int] | None:
    """Returns (start, end) of the last comparison operator that stands alone."""
    best = None
    for op in OPERATORS:
        pos = code.rfind(op)
        while pos != -1:
            before = code[pos - 1] if pos > 0 else ""
            after = code[pos + len(op)] if pos + len(op) < len(code) else ""
            if before not in NOT_OP_CHARS and after not in NOT_OP_CHARS:
                if best is None or pos >= best[0]:
                    best = (pos, pos + len(op))
                break
            pos = code.rfind(op, 0, pos)
    return best


def apply_mutation(source: str, lineno: int, new_op: str) -> str | None:
    lines = source.splitlines(keepends=True)
    if lineno > len(lines):
        return None
    line = lines[lineno - 1]
    match = MARKER_RE.search(line)
    if match is None:
        return None
    code = line[: match.start()]
    span = last_standalone_operator(code)
    if span is None:
        return None
    mutated = code[: span[0]] + new_op + code[span[1]:] + line[match.start():]
    lines[lineno - 1] = mutated
    return "".join(lines)


def run(cmd: list[str], timeout: int = 120, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(cwd), timeout=timeout,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default=str(REPO_ROOT / "native-engine" / "src"))
    parser.add_argument("--build-dir", default=str(REPO_ROOT / "native-engine" / "build"))
    parser.add_argument("--min-score", type=float, default=90.0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    src_dir = Path(args.src)
    build_dir = Path(args.build_dir)
    mutations = find_mutations(src_dir)

    if args.list:
        for m in mutations:
            print(f"{m['file'].name}:{m['lineno']} -> {m['new_op']}")
        print(f"{len(mutations)} mutation site(s)")
        return 0

    if not mutations:
        print("no mutation markers found")
        return 1

    print(f"[baseline] building and running tests")
    if run(["cmake", "-B", str(build_dir), "-S", str(src_dir.parent),
            "-DCMAKE_BUILD_TYPE=Release"]).returncode != 0:
        print("baseline cmake configure failed")
        return 1
    if run(["cmake", "--build", str(build_dir), "-j2"]).returncode != 0:
        print("baseline build failed")
        return 1
    if run(["ctest", "--test-dir", str(build_dir), "--output-on-failure"]).returncode != 0:
        print("baseline tests failed - refusing to mutate a red suite")
        return 1

    killed = 0
    survived = []
    for index, m in enumerate(mutations, start=1):
        cpp: Path = m["file"]
        original = cpp.read_text()
        mutated_source = apply_mutation(original, m["lineno"], m["new_op"])
        if mutated_source is None:
            print(f"[{index}/{len(mutations)}] {cpp.name}:{m['lineno']} SKIP (marker/operator mismatch)")
            continue
        cpp.write_text(mutated_source)
        try:
            build = run(["cmake", "--build", str(build_dir), "-j2"], timeout=120)
            if build.returncode != 0:
                # does not compile -> counts as killed (mutant is not viable)
                outcome_killed = True
            else:
                test = run(["ctest", "--test-dir", str(build_dir)], timeout=args.timeout)
                outcome_killed = test.returncode != 0
        except subprocess.TimeoutExpired:
            outcome_killed = True
        finally:
            cpp.write_text(original)
            # restore baseline binary
            run(["cmake", "--build", str(build_dir), "-j2"], timeout=120)

        label = f"{cpp.name}:{m['lineno']}->{m['new_op']}"
        if outcome_killed:
            killed += 1
            print(f"[{index}/{len(mutations)}] {label} KILLED")
        else:
            survived.append(label)
            print(f"[{index}/{len(mutations)}] {label} SURVIVED")

    total = len(mutations)
    score = 100.0 * killed / total
    print()
    print(f"native mutation score: {score:.1f}% ({killed}/{total} killed)")
    if survived:
        print("survivors:")
        for s in survived:
            print(f"  - {s}")
    if score < args.min_score:
        print(f"FAIL: score below threshold {args.min_score:.1f}%")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
