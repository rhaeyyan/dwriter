# dwriter - Agent Operating Manual (AGENTS.md)

**Target Version:** v4.10.6+
**Core Philosophy:** High-signal, low-friction terminal journaling with a headless-first architecture and local RAG.

This document serves as the primary instructional context for any AI coding assistant working on the dwriter project.

## 📝 Project Overview

dwriter is a minimalist, high-signal journaling tool bridging a "Fast Command-Line" for capture and a "Visual Dashboard" for reflection.

- **Core Tech Stack:** Python 3.10+, Click (CLI), Textual (TUI), SQLAlchemy (SQLite), Rich (formatting).
- **AI Architecture (dwriter-ai only):** Dual-Model Pipeline (Gemma 4 family).
- **Install:** `uv tool install .`
- **Approved user-facing terms:** "Analytical Engine" and "Security Mode." Internal persona/guard names stay inside `agents/` and never surface in `documentation/`.

## 🌳 Two-Branch Product Model

dwriter ships as two distinct products from one repository:
- **`main`** — AI-free edition. No `src/dwriter/ai/` imports permitted anywhere on this branch.
- **`dwriter-ai`** — AI edition. Full dual-model pipeline, 2nd-Brain, and RAG features.

The Project Maintainer is the only persona authorized to cherry-pick or merge between branches. Every `dwriter-ai` commit that touches non-AI files is classified in `agents/PORTING_MANIFEST.md` as **Portable**, **AI-Only**, or **Pending Review** — see that file for the exact classification rules.

## 🌎 Global Protocol & Workflow Rules

### Session Continuity (Sprint Ledger)
- **Start of session:** Read `SESSION_STATE.md` first.
- **End of session:** Update `SESSION_STATE.md` with (1) what was accomplished, (2) what is unfinished/blocked, (3) explicit next steps.
- **Fail loud on mismatch:** Treat `SESSION_STATE.md` as episodic memory and the repo's actual state as the procedural source of truth. If a ledger entry conflicts with reality, trust the filesystem and flag the discrepancy.
- **Archive Threshold:** If `SESSION_STATE.md` exceeds 150 lines or contains more than 5 historical sessions, move older entries to `ARCHIVED_SESSIONS.md`.

### Handoffs & Limits
- **The 5-File Limit:** No single autonomous task may modify more than 5 files. If a task requires more, split it into smaller sub-tasks.
- **Rejection Loop Cap (Circuit Breaker):** Any autonomous retry loop (like fixing a failing test) has a hard cap of 2 retry cycles. After the second FAIL, stop and escalate.
- **Pre-Flight Checklist:** Before any code is written, ensure: `uv run pytest` passes, `uv run ruff check src/` is clean, `uv run mypy src/ --ignore-missing-imports` passes, and `bash scripts/check_guards.sh` passes.
- **Structured Handoffs:** For complex multi-agent tasks, use the `[SPEC]` / `[COMPLIANCE-REPORT]` / `[COMPLETION-REPORT]` handoff formats, including a "Tipping Point" (the threshold at which a component must be refactored) in the `[SPEC]`. This convention is external to dwriter — the templates live in `Pursuit_AI-Native/AGENTS.md`; inline the relevant template into the handoff rather than assuming the recipient has it memorized.
- **Black-Box TDD:** When adding features, write failing behavioral/integration tests *before* writing the implementation code.
- **Headless-First:** Any feature with both a CLI and TUI surface must land its core logic as a standalone service — no UI imports, no AI imports — before either surface consumes it. If a TUI screen and a CLI command would do the same thing with no shared service function, that's a refactor prerequisite, not a style preference.
- **Feature Intake Gate:** Before starting a new feature, answer in the session entry: (1) which file(s) does this touch, (2) will any exceed the 600-line ceiling after the change, (3) is there an existing abstraction to extend. If (2) is yes, log a refactor plan before writing code.
- **Schema Change Gate:** No new column, table, or index without a one-line schema proposal in the `SESSION_STATE.md` entry first.

## 🛡️ Automated Architectural Guards
Run `bash scripts/check_guards.sh`.
- **The UI Isolation Guard:** Frontend components must never manage SQLAlchemy sessions directly.
- **The Security Mode Guard:** All AI tool calls must pass through the `PermissionEnforcer`, gated by user-defined strictness (`read-only`, `append-only`, `prompt`, `danger-full-access`).
- **The Context Budget Guard:** The `SummaryCompressor` must be invoked for all historical context injections (target: 1,200 chars / 24 lines).
- **The Analytics AI-Free Guard:** `src/dwriter/analytics/` must never import from `src/dwriter/ai/`, on either branch. Output must be identical across branches for identical input — divergence is a bug, not a feature difference.
- **File-Size Ceiling Guard:** No `.py` file outside `tui/screens/` may exceed 600 lines.

## 👥 Sub-Agents (Personas)

To eliminate bureaucratic bloat, `dwriter` operates under a streamlined 3-persona model:

### 1. The Full-Stack Engineer (Core & Frontend)
**Domain:** `src/dwriter/` (excluding `ai/`), `tests/`
**Mandate:** Build end-to-end features on the AI-free `main` branch. Owns TUI visuals, CLI workflow, database schema, and deterministic analytics. Can write full vertical slices but must strictly adhere to UI Isolation rules and the Analytics AI-Free Guard.

### 2. The AI & RAG Specialist (Behavioral Scientist)
**Domain:** `src/dwriter/ai/`
**Mandate:** Manage the Gemma 4 Dual-Model Pipeline and RAG retrieval layer. Operates entirely isolated from core deterministic logic. Strictly branch-local to `dwriter-ai`.

### 3. The Project Maintainer (Release & Quality)
**Domain:** `agents/`, `documentation/`, and the session ledger (`SESSION_STATE.md`, `ARCHIVED_SESSIONS.md` at repo root).
**Mandate:** Own the project's operational memory, documentation, and cross-branch integration. Maintains `SESSION_STATE.md`, `agents/PORTING_MANIFEST.md`, and user-facing docs. Authorized to cherry-pick between `dwriter-ai` and `main` — see Two-Branch Product Model above.

## 🧰 Local Claude Code Tooling

The 3 personas and several gates above are also formalized as machine-local Claude Code
config under `.claude/` (gitignored — not tracked in git, so this describes tooling that
exists on a given contributor's machine, not shared repo state; a fresh clone has none of it
until set up). It complements the rules above, it doesn't replace them:
- **`.claude/agents/*.md`** — the 3 personas as dispatchable subagents (`full-stack-engineer`,
  `ai-rag-specialist`, `project-maintainer`), each carrying a domain self-check, since Claude
  Code's `tools:` frontmatter restricts tool categories, not file paths.
- **`.claude/hooks/pre-flight-check.sh`** — a Stop hook that runs the Pre-Flight Checklist
  (pytest/ruff/mypy/guards) automatically, but only when uncommitted `.py` changes exist at
  session end — doc-only or already-clean sessions skip it.
- **`.claude/hooks/block-ai-on-main.sh`** — a PostToolUse hook that mechanically rejects any
  write under `src/dwriter/ai/` while `main` is checked out, backstopping the Two-Branch
  Product Model rule above with something sturdier than reviewer discipline.
- **`.claude/skills/handoff/`** — inlines the `[SPEC]`/`[COMPLIANCE-REPORT]`/`[COMPLETION-REPORT]`
  templates referenced under Handoffs & Limits, so they don't have to be recalled from
  `Pursuit_AI-Native/AGENTS.md` by memory.
- **`scripts/test_guards.sh`** — self-tests each guard in `check_guards.sh` by injecting a
  synthetic violation and confirming it's caught, then confirming a clean pass afterward. Exists
  because this repo has already shipped one guard that silently checked the wrong path.
- **`scripts/check_portability.sh <sha>`** — mechanizes the Portability Rules in
  `agents/PORTING_MANIFEST.md` for a first-pass Portable/AI-Only/Pending-Review suggestion; the
  Project Maintainer still confirms it against the diff before logging a manifest row.
