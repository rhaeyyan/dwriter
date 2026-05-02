# Session History

## [4.10.2] - 2026-05-01
**Session Orchestrator:** Quality Auditor
**Persona:** Core Logic Engineer
**Task:** Fix CLI tag formatting word-wrap bug

*   **Core Logic Engineer:** Investigated the word-wrapping logic for entry tags in `src/dwriter/ui_utils.py` and `src/dwriter/commands/search.py`.
    *   Fixed a bug where rich markup was incorrectly breaking tags with hyphens during `textwrap`. Wrapped tags as plain text first and then replaced the markup tokens in the correct order to maintain exact line length calculation.
    *   Removed an inconsistent leading space from the output of `Project:` in the `dwriter search` command.
*   **Quality Auditor:** Executed `scripts/check_guards.sh`, `pytest`, `ruff`, and `mypy`. All pre-flight tests and checks passed. Bumped project version to `v4.10.2`.
