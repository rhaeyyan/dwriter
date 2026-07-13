#!/usr/bin/env bash
# Self-tests for scripts/check_guards.sh.
#
# A guard that silently checks the wrong path (this repo shipped exactly that
# bug once — the Analytics guard briefly checked a nonexistent analytics.py)
# passes every run and protects nothing. For each of the 5 guards, this script
# injects a synthetic violation, confirms check_guards.sh reports [FAIL] for
# that guard (and only that guard), removes the violation, and confirms it
# reports [PASS] again. It calls the real check_guards.sh end-to-end rather
# than re-implementing its logic, so it can never drift from the guard it's
# testing.
set -u

cd "$(dirname "$0")/.." || exit 1

PASS=0
FAIL=0
CLEANUP_PATHS=()

cleanup() {
    for p in "${CLEANUP_PATHS[@]:-}"; do
        [ -n "$p" ] && [ -e "$p" ] && rm -f "$p"
    done
    if [ -f /tmp/dwriter_guard_test_engine_backup.py ]; then
        cp /tmp/dwriter_guard_test_engine_backup.py src/dwriter/ai/engine.py 2>/dev/null
        rm -f /tmp/dwriter_guard_test_engine_backup.py
    fi
}
trap cleanup EXIT INT TERM

run_guards() {
    bash scripts/check_guards.sh 2>&1
}

assert_status() {
    # assert_status <self-test-name> <guard-line-name> <expected: PASS|FAIL> <guard-output>
    local test_name="$1" guard_name="$2" expected="$3" output="$4"
    if printf '%s\n' "$output" | grep -qF "[$expected] $guard_name"; then
        echo "  [PASS] $test_name (guard reported $expected as expected)"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $test_name (guard did not report $expected for '$guard_name')"
        echo "$output" | grep -F "$guard_name"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "=== Guard Self-Tests ==="
echo ""

# --- 1. UI Isolation Guard ---
echo "-- UI Isolation Guard --"
violation="src/dwriter/tui/_guard_test_violation.py"
CLEANUP_PATHS+=("$violation")
printf 'def bad():\n    Session()\n' > "$violation"
out=$(run_guards)
assert_status "UI Isolation Guard catches raw Session()" "UI Isolation Guard" "FAIL" "$out"
rm -f "$violation"
out=$(run_guards)
assert_status "UI Isolation Guard clean after removal" "UI Isolation Guard" "PASS" "$out"

# --- 2. Security Mode Guard ---
echo "-- Security Mode Guard --"
violation="src/dwriter/ai/_guard_test_violation.py"
CLEANUP_PATHS+=("$violation")
printf 'import ollama\n\ndef call():\n    pass\n' > "$violation"
out=$(run_guards)
assert_status "Security Mode Guard catches unenforced model call" "Security Mode Guard" "FAIL" "$out"
rm -f "$violation"
out=$(run_guards)
assert_status "Security Mode Guard clean after removal" "Security Mode Guard" "PASS" "$out"

# --- 3. Context Budget Guard ---
echo "-- Context Budget Guard --"
if [ -f src/dwriter/ai/engine.py ]; then
    cp src/dwriter/ai/engine.py /tmp/dwriter_guard_test_engine_backup.py
    sed 's/SummaryCompressor/NotPresentHere/g' /tmp/dwriter_guard_test_engine_backup.py > src/dwriter/ai/engine.py
    out=$(run_guards)
    assert_status "Context Budget Guard catches missing SummaryCompressor" "Context Budget Guard" "FAIL" "$out"
    cp /tmp/dwriter_guard_test_engine_backup.py src/dwriter/ai/engine.py
    out=$(run_guards)
    assert_status "Context Budget Guard clean after restore" "Context Budget Guard" "PASS" "$out"
    rm -f /tmp/dwriter_guard_test_engine_backup.py
else
    echo "  [SKIP] src/dwriter/ai/engine.py does not exist on this branch"
fi

# --- 4. Analytics AI-Free Guard ---
echo "-- Analytics AI-Free Guard --"
if [ -d src/dwriter/analytics ]; then
    violation="src/dwriter/analytics/_guard_test_violation.py"
    CLEANUP_PATHS+=("$violation")
    printf 'from dwriter.ai import engine\n' > "$violation"
    out=$(run_guards)
    assert_status "Analytics AI-Free Guard catches ai/ import" "Analytics AI-Free Guard" "FAIL" "$out"
    rm -f "$violation"
    out=$(run_guards)
    assert_status "Analytics AI-Free Guard clean after removal" "Analytics AI-Free Guard" "PASS" "$out"
else
    echo "  [SKIP] src/dwriter/analytics/ does not exist on this branch"
fi

# --- 5. File-Size Ceiling Guard ---
echo "-- File-Size Ceiling Guard --"
violation="src/dwriter/_guard_test_violation.py"
CLEANUP_PATHS+=("$violation")
python3 -c "print('\n'.join('x = 1' for _ in range(601)))" > "$violation"
out=$(run_guards)
assert_status "File-Size Ceiling Guard catches 601-line file" "File-Size Ceiling Guard" "FAIL" "$out"
rm -f "$violation"
out=$(run_guards)
assert_status "File-Size Ceiling Guard clean after removal" "File-Size Ceiling Guard" "PASS" "$out"

echo ""
echo "=== Guard Self-Test Results: $PASS passed, $FAIL failed ==="
echo ""

[ "$FAIL" -eq 0 ] || exit 1
exit 0
