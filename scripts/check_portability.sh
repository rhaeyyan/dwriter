#!/usr/bin/env bash
# Mechanizes the Portability Rules from agents/PORTING_MANIFEST.md for a single
# dwriter-ai commit, to give the Project Maintainer a first-pass classification
# (Portable / AI-Only / Pending Review) before hand-logging a manifest row.
#
# This is a first pass, not a rubber stamp — confirm the suggestion against the
# actual diff before writing it into PORTING_MANIFEST.md.
#
# Usage:
#   scripts/check_portability.sh <sha>                # static checks only (fast)
#   scripts/check_portability.sh <sha> --verify-pytest # + cherry-pick test on main in a
#                                                       #   disposable worktree (slower)
set -u

sha="${1:-}"
verify_pytest=0
[ "${2:-}" = "--verify-pytest" ] && verify_pytest=1

if [ -z "$sha" ]; then
    echo "Usage: $0 <sha> [--verify-pytest]" >&2
    exit 1
fi

cd "$(dirname "$0")/.." || exit 1

if ! git rev-parse --verify "${sha}^{commit}" >/dev/null 2>&1; then
    echo "error: '$sha' is not a valid commit" >&2
    exit 1
fi

changed_files=$(git diff-tree --no-commit-id --name-only -r "$sha")
ai_files=$(printf '%s\n' "$changed_files" | grep -c '^src/dwriter/ai/' || true)
total_files=$(printf '%s\n' "$changed_files" | grep -c '.' || true)
non_ai_files=$((total_files - ai_files))

echo ""
echo "=== Portability Check: $sha ==="
git show -s --format='%h %s' "$sha"
echo ""
echo "Files changed: $total_files (under src/dwriter/ai/: $ai_files, outside: $non_ai_files)"

# Rule 2: no instructor/ollama/openai import ADDED anywhere in the diff.
coupled_imports=$(git diff "${sha}^" "$sha" -- . 2>/dev/null | grep -E '^\+.*\b(import instructor|import ollama|import openai)\b' || true)

# AI-coupling markers outside ai/: catches code that references AI machinery
# without living under src/dwriter/ai/ (the tricky case the manifest rules exist for).
coupled_markers=""
if [ "$non_ai_files" -gt 0 ]; then
    for f in $changed_files; do
        case "$f" in
            src/dwriter/ai/*) continue ;;
        esac
        [ -f "$f" ] || continue
        if git show "$sha:$f" 2>/dev/null | grep -qE 'PermissionEnforcer|SummaryCompressor|import (instructor|ollama|openai)|from \.+ai(\.|\s)|from dwriter\.ai|import dwriter\.ai'; then
            coupled_markers="$coupled_markers$f\n"
        fi
    done
fi

echo ""
if [ "$ai_files" -gt 0 ] && [ "$non_ai_files" -gt 0 ]; then
    verdict="Pending Review"
    reason="mixes $ai_files ai/ file(s) with $non_ai_files non-ai/ file(s) — must be split before any part can be ported"
elif [ "$ai_files" -gt 0 ]; then
    verdict="AI-Only"
    reason="touches only src/dwriter/ai/ files"
elif [ -n "$coupled_imports" ] || [ -n "$coupled_markers" ]; then
    verdict="Pending Review"
    reason="no ai/ files touched, but AI-coupling markers found outside ai/ — needs human judgment"
else
    verdict="Portable (candidate)"
    reason="no ai/ files touched, no AI-coupling markers found"
fi

echo "Suggested classification: $verdict"
echo "Reason: $reason"

if [ -n "$coupled_imports" ]; then
    echo ""
    echo "Added instructor/ollama/openai imports:"
    echo "$coupled_imports"
fi
if [ -n "$coupled_markers" ]; then
    echo ""
    echo "Non-ai/ files referencing AI machinery:"
    printf '%b' "$coupled_markers"
fi

if [ "$verify_pytest" -eq 1 ] && [ "$ai_files" -eq 0 ]; then
    echo ""
    echo "--- Verifying: cherry-pick onto main in a disposable worktree ---"
    wt=$(mktemp -d)
    if git worktree add --detach "$wt" main >/dev/null 2>&1; then
        if git -C "$wt" cherry-pick --no-commit "$sha" >/tmp/portability_cherry_pick.log 2>&1; then
            echo "Cherry-pick applied cleanly. Running uv run pytest in the worktree..."
            if (cd "$wt" && uv run pytest) >/tmp/portability_pytest.log 2>&1; then
                echo "Rule 3: PASS — uv run pytest succeeds on main after cherry-pick."
            else
                echo "Rule 3: FAIL — uv run pytest failed after cherry-pick. See /tmp/portability_pytest.log"
                verdict="Pending Review"
                echo "Downgrading suggested classification to: Pending Review"
            fi
        else
            echo "Rule 3: cherry-pick did not apply cleanly onto main (conflict). See /tmp/portability_cherry_pick.log"
            verdict="Pending Review"
            echo "Downgrading suggested classification to: Pending Review"
        fi
        git -C "$wt" cherry-pick --abort >/dev/null 2>&1
        git worktree remove --force "$wt" >/dev/null 2>&1
    else
        echo "Could not create disposable worktree — skipping Rule 3 verification."
    fi
elif [ "$verify_pytest" -eq 1 ]; then
    echo ""
    echo "--- Skipping cherry-pick verification: commit touches src/dwriter/ai/, out of scope for main ---"
fi

echo ""
echo "Final suggested classification: $verdict"
echo "(Confirm against the diff yourself — this is a first pass, not authoritative.)"
echo ""
