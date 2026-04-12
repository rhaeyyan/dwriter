# dwriter - Instructional Context (AGENTS.md)

This document serves as the primary instructional context for any AI coding assistant working on the dwriter project. It is LLM-agnostic and applies equally to Gemini CLI, Claude Code, Copilot, or any other agent invoked against this codebase.

## 📝 Project Overview
dwriter is a minimalist, high-signal journaling tool bridging a "Fast Command-Line" for capture and a "Visual Dashboard" for reflection.

- **Core Tech Stack:** Python 3.10+, Click (CLI), Textual (TUI), SQLAlchemy (SQLite), Rich (Formatting).
- **AI Architecture:** Dual-Model Pipeline (Gemma 4 family).
- **Security:** Integrated "Security Mode" (Permission Enforcer) gating all AI actions.

## 🛠 Building and Running
- **Installation:** `uv tool install .`
- **Testing:** `uv run pytest`
- **Linting:** `uv run ruff check src/`
- **Type Checking:** `uv run mypy src/`

## 🚀 Analytical Engine Features
- **2nd-Brain:** Action-First Strategic Command Center. Six trigger buttons (`Energy`, `Momentum`, `Golden Hour`, `Stale`, `Focus`, `Pulse`) generate deterministic analytics reports inline. Four AI-powered briefing buttons (`💬 Follow-up`, `Weekly Retro`, `Burnout Check`, `Catch Up`) sit below.
- **Catch Up Briefing:** Compact modal with typed project/tag inputs, recent-value hints, and a `Last 7 Days` / `Custom Range` toggle with collapsible start/end date fields.
- **Security Mode:** User-defined strictness levels for AI data access.
- **Context Compression:** Deterministic normalization of history to prevent reasoning bloat.
- **Local RAG:** Semantic search across historical entries using `nomic-embed-text`.

---

*For session history, see [HISTORY.md](HISTORY.md).*
