# dwriter - Agent Operating Manual (AGENTS.md)

**Target Version:** v4.6.0+
**Core Philosophy:** High-signal, low-friction terminal journaling with a headless-first architecture and local RAG.

This document serves as the primary instructional context for any AI coding assistant working on the dwriter project.

## 🌎 Global Protocol & Workflow Rules

### Session Continuity (Sprint Ledger)
- **Start of session:** Read `SESSION_STATE.md` first.
- **End of session:** Update `SESSION_STATE.md` with (1) what was accomplished, (2) what is unfinished/blocked, (3) explicit next steps.
- **Fail loud on mismatch:** Treat `SESSION_STATE.md` as episodic memory and the repo's actual state as the procedural source of truth. If a ledger entry conflicts with reality, trust the filesystem and flag the discrepancy.
- **Archive Threshold:** If `SESSION_STATE.md` exceeds 150 lines or contains more than 5 historical sessions, move older entries to `ARCHIVED_SESSIONS.md`.

### Handoffs & Limits
- **The 5-File Limit:** No single autonomous task may modify more than 5 files. If a task requires more, split it into smaller sub-tasks.
- **Rejection Loop Cap (Circuit Breaker):** Any autonomous retry loop (like fixing a failing test) has a hard cap of 2 retry cycles. After the second FAIL, stop and escalate.
- **Pre-Flight Checklist:** Before any code is written, ensure: `uv run pytest` passes, `uv run ruff check src/` is clean, `uv run mypy src/` passes, and `bash scripts/check_guards.sh` passes.
- **Structured Handoffs:** Use `[SPEC]`, `[COMPLIANCE-REPORT]`, and `[COMPLETION-REPORT]` formats for complex multi-agent tasks, explicitly defining a "Tipping Point" for future refactors in the `[SPEC]`.
- **Black-Box TDD:** When adding features, write failing behavioral/integration tests *before* writing the implementation code.

## 🛡️ Automated Architectural Guards
Run `bash scripts/check_guards.sh`.
- **The UI Isolation Guard:** Frontend components must never manage SQLAlchemy sessions directly.
- **The Security Mode Guard:** All AI tool calls must pass through the `PermissionEnforcer`.
- **The Context Budget Guard:** The `SummaryCompressor` must be invoked for all historical context injections.
- **File-Size Ceiling Guard:** No `.py` file outside `tui/screens/` may exceed 600 lines.

## 👥 Sub-Agents (Personas)

To eliminate bureaucratic bloat, `dwriter` operates under a streamlined 3-persona model:

### 1. The Full-Stack Engineer (Core & Frontend)
**Domain:** `src/dwriter/` (excluding `ai/`), `tests/`
**Mandate:** Build end-to-end features on the AI-free `main` branch. Owns TUI visuals, CLI workflow, database schema, and deterministic analytics. Can write full vertical slices but must strictly adhere to UI Isolation rules.

### 2. The AI & RAG Specialist (Behavioral Scientist)
**Domain:** `src/dwriter/ai/`
**Mandate:** Manage the Gemma 4 Dual-Model Pipeline and RAG retrieval layer. Operates entirely isolated from core deterministic logic. Strictly branch-local to `dwriter-ai`.

### 3. The Project Maintainer (Release & Quality)
**Domain:** `agents/`, `documentation/`
**Mandate:** Own the project's operational memory, documentation, and cross-branch integration. Maintains `SESSION_STATE.md`, `agents/PORTING_MANIFEST.md`, and user-facing docs. Authorized to cherry-pick between `dwriter-ai` and `main`.
