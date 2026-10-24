#!/usr/bin/env python3
"""按任务看板执行 mutmut 变异验证，输出 JSON 摘要与可解析的分数行。

用法::

    python scripts/mutation_score.py --board TB2 --paths traffic_agent/transform --min-score 55

产物：
    - ``mutation-<BOARD>.json``：完整统计（killed/survived/timeout/...）
    - stdout: ``MUTATION_RESULT board=TB2 ... score=0.812`` 供 CI 日志解析

计分口径：mutation_score = (killed + timeout) / (killed + survived + timeout)，
suspicious / skipped / untested 不计入分母，单独报告。
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import subprocess
import sys

CACHE_FILE = ".mutmut-cache"

# mutmut 2.x 缓存中的状态字符串
STATUS_NAMES = {
    "ok_killed": "killed",
    "bad_survived": "survived",
    "bad_timeout": "timeout",
    "ok_suspicious": "suspicious",
    "skipped": "skipped",
    "untested": "untested",
}


def collect_files(spec: str) -> list:
    files = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if os.path.isfile(token):
            files.append(token)
        elif os.path.isdir(token):
            files.extend(sorted(glob.glob(os.path.join(token, "**", "*.py"), recursive=True)))
        else:
            print(f"warning: path not found: {token}")
    seen, unique = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def run_mutmut(files: list, tests_dir: str) -> int:
    cmd = [
        "mutmut", "run",
        "--paths-to-mutate", ",".join(files),
        "--tests-dir", tests_dir,
        "--runner", "python -m pytest -x -q",
        "--no-progress",
        "--simple-output",
    ]
    print("[mutation] running:", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def read_cache(path: str = CACHE_FILE) -> dict:
    if not os.path.exists(path):
        return {}
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT status, COUNT(*) FROM Mutant GROUP BY status").fetchall()
    finally:
        conn.close()
    counts = {}
    for raw_status, count in rows:
        name = STATUS_NAMES.get(raw_status, f"unknown_{raw_status}")
        counts[name] = counts.get(name, 0) + count
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-board mutation verification")
    parser.add_argument("--board", required=True, help="task board id, e.g. TB1")
    parser.add_argument("--paths", required=True, help="comma-separated files/dirs to mutate")
    parser.add_argument("--tests-dir", default="tests")
    parser.add_argument("--min-score", type=float, default=0.0, help="fail if score < min-score (0-1)")
    args = parser.parse_args()

    files = collect_files(args.paths)
    out_path = f"mutation-{args.board}.json"
    if not files:
        print(f"[{args.board}] no mutable targets found (module not yet present?) — skipping")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump({"board": args.board, "skipped": True, "reason": "no target files"}, fh, indent=2)
        return 0

    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    rc = run_mutmut(files, args.tests_dir)
    counts = read_cache()
    killed = counts.get("killed", 0)
    survived = counts.get("survived", 0)
    timeout = counts.get("timeout", 0)
    suspicious = counts.get("suspicious", 0)
    skipped = counts.get("skipped", 0)
    untested = counts.get("untested", 0)
    tested = killed + survived + timeout
    score = (killed + timeout) / tested if tested else 0.0

    summary = {
        "board": args.board,
        "files": files,
        "mutmut_exit_code": rc,
        "counts": counts,
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "suspicious": suspicious,
        "skipped": skipped,
        "untested": untested,
        "tested": tested,
        "mutation_score": round(score, 4),
        "min_score": args.min_score,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print(
        f"MUTATION_RESULT board={args.board} killed={killed} survived={survived} timeout={timeout} "
        f"suspicious={suspicious} skipped={skipped} untested={untested} total={tested} score={score:.3f}"
    )
    print(f"[{args.board}] mutation score: {score * 100:.1f}% (killed {killed}/{tested})")

    if rc not in (0, 2, 4, 8) and not counts:
        print(f"[{args.board}] mutmut failed to run (exit={rc}) — fatal", file=sys.stderr)
        return 1
    if args.min_score and tested and score < args.min_score:
        print(
            f"[{args.board}] FAILED: mutation score {score:.3f} below threshold {args.min_score}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
