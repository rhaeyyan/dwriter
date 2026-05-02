# Development History & Agentic Engineering Journal

## The Philosophy
`dwriter` was built with a core philosophy: **high-signal, low-friction terminal journaling with a headless-first architecture**. It bridges the gap between the raw speed of a CLI and the visual clarity of a modern dashboard.

A major part of the development process was leveraging **Agentic Engineering**—using specialized AI personas to build, maintain, and refactor the codebase. The goal was intentionality: ensuring the resulting tool is easy to run (resource-wise) and intuitive to use, while keeping the codebase strictly organized and bug-free.

## Agentic Engineering Framework
The repository uses a multi-agent framework to maintain strict domain boundaries. This prevents architectural regression and spaghetti code. Work is delegated to specific "personas," each with a mandate and a bounded domain.

### Global Handoff Protocol & Pre-Flight Checks
To ensure smooth handoffs between AI agents, a strict protocol is enforced:
- **Session-Open Protocol:** The Quality Auditor receives a task, decomposes it, and assigns it to personas in dependency order. A plan is logged in `HISTORY.md` before any code is written.
- **Pre-Flight Checklist:** Before any agent begins work, they must pass a strict checklist:
  - `pytest` passes with 100% success.
  - `ruff` linting reports zero errors.
  - `mypy` type-checking reports zero errors.
  - Custom `scripts/check_guards.sh` passes all architectural guards.
  - The working tree is clean.
- **Architectural Guards:**
  - **UI Isolation:** Frontend components cannot manage database sessions directly.
  - **Security Mode:** AI tool calls must pass through the `PermissionEnforcer`.
  - **Context Budget:** Historical context injections must be strictly compressed to save tokens.
  - **File-Size Ceiling:** Prevents oversized, monolithic modules.

### The Sub-Agents (Personas)
1. **The TUI Architect (Frontend & Visuals)**
   - **Domain:** `src/dwriter/tui/`
   - **Mandate:** Builds theme-aware Textual components while maintaining UI lifecycle integrity. Ensures database isolation via thread-safe data wrappers.
2. **The Core Logic Engineer (Headless Workflow)**
   - **Domain:** `src/dwriter/commands/`, `src/dwriter/date_utils.py`
   - **Mandate:** Maintains the CLI as the "Source of Truth". All data processing is abstracted so both the TUI and CLI consume the same service layer.
3. **The AI & RAG Specialist (Behavioral Scientist)**
   - **Domain:** `src/dwriter/ai/`
   - **Mandate:** Manages the Dual-Model Pipeline and RAG retrieval layer. Orchestrates reasoning models vs. background daemon models.
4. **The Analytics Engineer (Deterministic Intelligence)**
   - **Domain:** `src/dwriter/analytics/`
   - **Mandate:** Owns the deterministic analytics engine (e.g., 7-Day Pulse, task velocity). Completely isolated from AI domains.
5. **The Infrastructure Engineer (Shared Plumbing)**
   - **Domain:** `src/dwriter/sync/`, `src/dwriter/config.py`, shared utilities.
   - **Mandate:** Manages configurations, sync engines (CRDT merge correctness), and shared background daemons.
6. **The QA & Database Lead (Backend Hardening)**
   - **Domain:** `src/dwriter/database.py`, `tests/`
   - **Mandate:** Enforces schema integrity, thread-safe SQLite access, migrations, and test parity across branches.
7. **The Quality Auditor (Session Orchestrator)**
   - **Domain:** Global operational memory.
   - **Mandate:** Gating sessions, bumping versions, running pre-flight checks, and maintaining the `HISTORY.md` audit log.

## Technical Stack Choices
Every dependency in `dwriter` was chosen intentionally to maximize local performance and minimize friction.

### 1. SQLite
**Purpose:** The single source of truth for all entries and to-dos.
**Why:** It is lightweight, requires no background server, and is incredibly fast for local read/write operations. Through thread-safe wrapper queues managed by the QA Lead, SQLite provides the persistence backbone for the application without any overhead.

### 2. LadybugDB
**Purpose:** Graph index and Full-Text Search (FTS).
**Why:** Operating as a CQRS (Command Query Responsibility Segregation) read-side projection, LadybugDB takes the relational data from SQLite and projects it into a graph. This powers advanced topological queries (like "show me all Facts extracted from Entries related to this Project") and blazing-fast Full-Text Search for the AI's Retrieval-Augmented Generation (RAG) pipeline.

### 3. Instructor
**Purpose:** Structured LLM outputs.
**Why:** When dealing with Large Language Models, extracting predictable JSON is notoriously brittle. The `Instructor` library enforces Pydantic schemas on the LLM output, guaranteeing that when `dwriter` asks the AI to extract a "Fact" or "Todo", it returns a strictly typed object that the application can immediately save to the database.

### 4. Ruff
**Purpose:** High-speed Python linting and formatting.
**Why:** `dwriter` enforces strict code quality. Ruff replaces multiple older tools (Flake8, Black, isort) with a single, lightning-fast Rust-based binary, keeping the codebase pristine and formatted consistently across all agent contributions.

### 5. MyPy & Pytest
**Purpose:** Type safety and regression testing.
**Why:** With multiple AI personas concurrently modifying the codebase, maintaining a safety net is paramount. MyPy ensures strict type contracts between different domains (e.g., the UI and the Core Logic), while Pytest provides the behavioral verification required by the Pre-Flight Checklist. No agent is permitted to merge changes if either of these tools report a failure.

## Two Branches, One Soul
`dwriter` ships as two distinct products from one repository:
*   **`main`**: The AI-free edition. Fast, deterministic, and entirely local.
*   **`dwriter-ai`**: The AI edition. Features the full Dual-Model pipeline, 2nd-Brain Command Center, and Graph-based Fact extraction.

The agentic framework allows features developed on the AI branch (like TUI improvements or headless refactors) to be safely ported back to the `main` branch, ensuring both applications evolve together without cross-contamination of AI dependencies.
