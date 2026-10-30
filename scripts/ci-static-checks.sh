#!/usr/bin/env bash
# Repo hygiene gate (CI job 10/10, also runnable locally).
#
# Deterministic, dependency-free checks over the tracked source tree:
#   1. no trailing whitespace on source lines
#   2. no TAB-based indentation in Kotlin/C++/Python/YAML sources
#      (tabs inside string literals are fine; only leading tabs are rejected)
#   3. every text source file ends with a newline
#   4. no leftover merge-conflict markers
#   5. no source file exceeds 1600 lines (push yourself to split)
set -euo pipefail

cd "$(dirname "$0")/.."

status=0
fail() {
    echo "HYGIENE FAIL: $*" >&2
    status=1
}

# File sets. .md is excluded from the whitespace rules on purpose: Markdown
# uses trailing double-space for hard line breaks and Unicode whitespace.
SOURCE_RE='\.(kt|kts|cpp|h|hpp|inc|py|yml|yaml|sh|xml|json|toml|md)$'
STRICT_RE='\.(kt|kts|cpp|h|hpp|inc|py|yml|yaml|sh|xml|json|toml)$'
MAX_LINES=1600

# Generated mutation-testing output (mutmut) is not hand-maintained source.
EXCLUDE_RE='^python/mutants/'

tracked() {
    git ls-files | grep -Ev "$EXCLUDE_RE" || true
}

# --- 1. trailing whitespace -------------------------------------------------
while IFS= read -r f; do
    if grep -nE '[[:blank:]]+$' "$f" >/dev/null 2>&1; then
        count=$(grep -cE '[[:blank:]]+$' "$f")
        fail "trailing whitespace in $f ($count line(s))"
    fi
done < <(tracked | grep -E "$STRICT_RE" || true)

# --- 2. leading TAB indentation ---------------------------------------------
while IFS= read -r f; do
    if grep -nP '^\t' "$f" >/dev/null 2>&1; then
        count=$(grep -cP '^\t' "$f")
        fail "TAB indentation in $f ($count line(s))"
    fi
done < <(tracked | grep -E "$STRICT_RE" || true)

# --- 3. final newline ---------------------------------------------------------
while IFS= read -r f; do
    if [ -s "$f" ]; then
        last=$(tail -c1 "$f" | od -An -tx1 | tr -d ' \n')
        if [ "$last" != "0a" ]; then
            fail "missing final newline: $f"
        fi
    fi
done < <(tracked | grep -E "$SOURCE_RE" || true)

# --- 4. merge conflict markers -------------------------------------------------
while IFS= read -r f; do
    if grep -nE '^(<<<<<<< |>>>>>>> |=======$)' "$f" >/dev/null 2>&1; then
        fail "merge conflict marker in $f"
    fi
done < <(tracked | grep -E "$SOURCE_RE" || true)

# --- 5. file size cap ----------------------------------------------------------
while IFS= read -r f; do
    lines=$(wc -l < "$f")
    if [ "$lines" -gt "$MAX_LINES" ]; then
        fail "$f has $lines lines (max $MAX_LINES)"
    fi
done < <(tracked | grep -E '\.(kt|kts|cpp|h|hpp|py)$' || true)

if [ "$status" -ne 0 ]; then
    echo ""
    echo "Hygiene gate: FAILED"
    exit 1
fi
echo "Hygiene gate: OK ($(tracked | grep -cE "$SOURCE_RE" || true) text files checked)"
