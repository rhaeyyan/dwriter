#!/usr/bin/env bash
# Architectural Guard Checks
# Run before any session begins. All checks must pass (exit 0) to proceed.

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  [PASS] $name"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $name"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "=== Architectural Guard Checks ==="
echo ""

# UI Isolation Guard: TUI widgets must never open raw SQLAlchemy sessions directly.
check "UI Isolation Guard" \
    '! grep -rn "Session()" src/dwriter/tui/'

# Security Mode Guard: Files in ai/ that make model calls must use PermissionEnforcer.
# Skips vacuously on main (no AI source files). Uses -r flag to prevent xargs firing on empty input.
check "Security Mode Guard" \
    '! grep -rl "import instructor\|import ollama\|import openai" src/dwriter/ai/ --include="*.py" 2>/dev/null | xargs -r grep -L "PermissionEnforcer" 2>/dev/null | grep -q .'

# Context Budget Guard: SummaryCompressor must be present in engine.py alongside history injection.
# Skips vacuously on main where engine.py does not exist.
check "Context Budget Guard" \
    '! [ -f src/dwriter/ai/engine.py ] || grep -q "SummaryCompressor" src/dwriter/ai/engine.py'

# File-Size Ceiling Guard: No .py file outside tui/screens/ may exceed 600 lines.
# TUI screen files are exempt (complex widget composition requires vertical length).
check "File-Size Ceiling Guard" \
    '! find src/dwriter -name "*.py" \
        -not -path "*/tui/screens/*" \
        -not -path "*/__pycache__/*" \
    | while read f; do
        lines=$(wc -l < "$f")
        if [ "$lines" -gt 600 ]; then
            echo "FAIL: $f ($lines lines)"
        fi
      done | grep -q "FAIL"'

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "Guard violations detected. Document each in HISTORY.md with file"
    echo "path and line number, then assign remediation before proceeding."
    exit 1
fi

exit 0
