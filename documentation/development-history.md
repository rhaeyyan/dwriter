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

## Core Concepts & Architectural Features
To deliver a high-signal experience, `dwriter` implements several advanced architectural patterns that elevate it from a simple text logger to an intelligent journal.

### 1. The Closed Learning Loop (Fact Extraction)
**What it is:** The AI doesn't just read your logs; it learns from them. The Closed Learning Loop is a background process that automatically parses human text into structured `Fact` objects. It extracts durable user preferences (e.g., *"I prefer working on backend tasks in the morning"*), recurring goals (*"Release the beta by June"*), and persistent constraints (*"I am allergic to Java"*).
**Purpose:** Most AI tools suffer from amnesia or require manual "system prompt" tuning. By storing these facts as dedicated nodes in the LadybugDB graph index (linked via `EXTRACTED_FROM` relationships), the 2nd-Brain agent can query your personal constraints mid-conversation using the `search_facts` tool. This results in highly personalized, context-aware advice without the user ever having to manually configure their preferences.

### 2. The Dual-Model Pipeline
**What it is:** An orchestration pattern that routes different types of AI tasks to specialized models.
- **The Main Brain (Reasoning):** A heavier, reasoning-capable model (like Gemma) handles the interactive 2nd-Brain chat, where context understanding and nuanced responses are critical.
- **The Daemon (Extraction):** A faster, lightweight model runs entirely in the background. It is solely responsible for strictly typed tasks via `Instructor`—like silently parsing a new journal entry to extract tags, projects, and Facts.
**Purpose:** This bifurcation keeps the application highly performant and resource-efficient. The user isn't forced to wait for a heavy reasoning model to boot up just to parse a `#tag` from a CLI command.

### 3. The 7-Day Pulse & Deterministic Analytics
**What it is:** A heavy analytics operation (isolated from the AI domains) that runs once every 24 hours. It calculates actionable metrics like "Momentum" (task completion velocity) and identifies the user's "Big Rock" (the project consuming the majority of their time).
**Purpose:** Users often miss the "forest for the trees" when logging chronologically. The Pulse provides an automated, high-level behavioral archetype (e.g., "The Deep Diver" or "The Firefighter"). By caching this heavy calculation and throttling it to run only once a day, the app provides instant, rich dashboard insights without degrading terminal performance.

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

---

## 🚀 The Evolution: From Headless CLI to Modern TUI
The transition of `dwriter` from a strictly command-line interface to a rich Terminal User Interface (TUI) was a major milestone. 

Initially, `dwriter` focused exclusively on **headless execution** (`dwriter add`, `dwriter search`), favoring speed. However, as the feature set expanded to include complex project graphs and daily analytical pulses, the need for a persistent, dashboard-style view became clear.

By adopting **Textual**, the application gained:
1. **Interactive Event Loops:** Transitioning from simple synchronous Python scripts to an asynchronous, reactive event loop.
2. **Component Architecture:** Building modular UI widgets (like the Omnibox and Standup Modals) that encapsulate their own state and styling.
3. **Thread-Safe Concurrency:** Using Textual worker threads to run heavy analytics and AI RAG queries in the background without freezing the UI. This required enforcing strict SQLite lock patterns in the QA Lead domain.

## 🧠 Skills & Knowledge Acquired
Building and scaling `dwriter` through Agentic Engineering fostered deep expertise across several modern Python domains:

- **Asynchronous UI Development (Textual):** Mastering CSS-like stylesheets in Python, reactive properties, and message-passing event buses.
- **Advanced Concurrency:** Managing race conditions between Textual background workers and local SQLite database sessions.
- **Graph Databases (LadybugDB):** Understanding CQRS (Command Query Responsibility Segregation) by using a relational database (SQLite) for writes and projecting it into a graph index for topological reads and FTS.
- **AI Tool Integration (Instructor & Gemma):** Migrating away from unstructured prompt-engineering to strict, Pydantic-enforced JSON outputs. Implementing an extraction loop where the AI acts as a background daemon parsing human text into structured `Fact` objects.
- **Multi-Agent Orchestration:** Learning how to effectively write "System Prompts" that bind AI to specific architectural domains (e.g. keeping the Analytics Engineer strictly separated from the AI Specialist).
- **Git Branch Parity:** Managing parallel releases from the same repository by strictly guarding module imports and safely backporting UI features from the experimental AI branch to the deterministic main branch.
