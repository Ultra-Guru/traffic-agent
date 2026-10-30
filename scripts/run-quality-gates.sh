#!/usr/bin/env bash
# Local replica of the ten CI quality gates (jobs 1-10 of .github/workflows/ci.yml).
#
# Usage:
#   bash scripts/run-quality-gates.sh            # everything
#   bash scripts/run-quality-gates.sh fast       # skip mutation gates (1,3,5,7,8,9,10 only)
#   bash scripts/run-quality-gates.sh <n> [...]  # run selected gates by number
#
# The Android gates (7/8/9) require a local SDK; export ANDROID_HOME or have
# local.properties point at one. On constrained machines run one gate at a
# time — each Gradle invocation is memory-hungry.
set -euo pipefail

cd "$(dirname "$0")/.."

MODE="${1:-all}"
SELECTED=()
if [[ "$MODE" != "all" && "$MODE" != "fast" ]]; then
    SELECTED=("$@")
fi

want() {
    local n="$1"
    if [ "${#SELECTED[@]}" -gt 0 ]; then
        local found=0
        for s in "${SELECTED[@]}"; do [[ "$s" == "$n" ]] && found=1; done
        [[ "$found" == "1" ]]
    elif [ "$MODE" == "fast" ]; then
        # fast mode: everything except the mutation gates (2, 4, 6)
        [[ "$n" != "2" && "$n" != "4" && "$n" != "6" ]]
    else
        true
    fi
}

step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }

if want 1; then
    step "1/10 native: C++ unit tests"
    cmake -S native-engine -B native-engine/build -DCMAKE_BUILD_TYPE=Release >/dev/null
    cmake --build native-engine/build -j"$(nproc)" >/dev/null
    ctest --test-dir native-engine/build --output-on-failure
fi

if want 2; then
    step "2/10 native: mutation gate"
    python3 -u scripts/native_mutate.py --min-score 90
fi

if want 3; then
    step "3/10 python: unit tests"
    (cd python && python -m pytest tests -q)
fi

if want 4; then
    step "4/10 python: mutation gate"
    (cd python && mutmut run)
    python3 scripts/mutmut_gate.py --min-score 70
fi

if want 5; then
    step "5/10 kotlin: core unit tests"
    ./gradlew -Pta.skipAndroid allUnitTests
fi

if want 6; then
    step "6/10 kotlin: PIT mutation gate"
    ./gradlew -Pta.skipAndroid allPitest
    python3 scripts/pitest_gate.py --min-score 65
fi

if want 7; then
    step "7/10 android: app unit tests"
    ./gradlew :app:testDebugUnitTest
fi

if want 8; then
    step "8/10 android: lint"
    ./gradlew :app:lintDebug
fi

if want 9; then
    step "9/10 android: assemble debug APK"
    ./gradlew :app:assembleDebug
fi

if want 10; then
    step "10/10 repo: hygiene checks"
    bash scripts/ci-static-checks.sh
fi

step "quality gates: OK"
