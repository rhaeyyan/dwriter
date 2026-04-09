# dwriter Update Notes

## Version 4.3.1 - April 9, 2026

### 🚀 Key Features

#### 1. AI Security & Permissions (Architectural Safety)
- **Granular Security Modes**: Introduced a new `permission_mode` setting (`read-only`, `append-only`, `prompt`, `danger-full-access`) to govern AI tool execution.
- **Surgical Tool Gating**: The 2nd-Brain ReAct loop now intercepts every tool call. If the active mode denies an action (e.g., trying to delete a task in `read-only` mode), the engine returns a standardized "System Error" allowing the LLM to explain the restriction to the user.
- **UI-Independent Logic**: The security mode is built as a pure-Python module, ensuring headless stability.

#### 2. Deterministic Summary Compression
- **High-Signal Context**: Implemented a sophisticated `SummaryCompressor` that optimizes the AI's "Short-Term Memory." It normalizes whitespace, removes duplicate entries, and prioritizes structural headers.
- **Context Budgeting**: Strictly enforces a 1,200-character and 24-line budget on all historical data injected into the LLM. This significantly reduces "Context Bloat" and prevents hallucination caused by redundant information.

### 🛠 Improvements & Fixes
- **Config Schema Evolution**: Added the `permission_mode` key to `AIFeaturesConfig` with backward-compatible defaults.
- **Surgical Integration**: Wired the compression engine into the 2nd-Brain TUI and the AI security mode into the ReAct engine loop.

## Version 4.3.0 - April 9, 2026

### 🚀 Key Features

#### 1. High-Signal Readability (Hanging Indents)
- **Advanced Text Wrapping**: Developed a specialized `wrap_with_hanging_indent` utility in `ui_utils.py`. All journal logs and AI responses now feature perfectly aligned multi-line text, ensuring the second and third lines of a paragraph are indented to match the first word.
- **CLI & TUI Parity**: This formatting is consistently applied across both the headless `today`/`search` commands and the visual 2nd-Brain chat bubbles.

#### 3. Modern "Braille" Spinner
- **Sleek AI Feedback**: Replaced the bulky default loading indicator with a custom, minimalist **Modern Spinner** using elegant Braille characters (`⠋⠙⠹...`).
- **Non-Intrusive UX**: The spinner provides a "Claude-style" modern feel during long Gemma-4 inference times, keeping the interface clean while indicating active reasoning.

### 🛠 Improvements & Fixes
- **AI Verbosity Control**: Refined the 2nd-Brain system prompts to eliminate "Global State" repetition. The AI is now strictly concise, focusing only on the user's immediate request without over-sharing unrelated TODO lists.
- **Visual Cleanup**: Removed high-contrast `[reverse]` highlighting from inline code blocks in AI responses, replacing it with a subtle, theme-integrated blue (`#89b4fa`).
- **Modular Tidiness**: Purged over 15 root-level scratchpad and temporary test scripts, restoring the project's minimalist directory structure.
- **Import & Syntax Hardening**: Resolved a critical `IndentationError` in the AI engine and fixed several `UndefinedName` and line-length (`E501`) violations across the core TUI and UI utility modules.

## Version 4.2.0 - April 8, 2026

### 🚀 Key Features

#### 1. Background Sync Daemon
- **Auto-Sync Automation**: Introduced a non-blocking background sync system. `dwriter` now automatically performs a `pull` on startup and a debounced `push` 10 seconds after any data write (entries or todos).
- **Sync Telemetry**: Added a real-time sync status indicator to the TUI footer (`[✅ Synced]`, `[🧠 Syncing...]`, `[❌ Sync Failed]`).
- **Silent Logging**: All background sync operations now log to `~/.dwriter/logs/sync.log` to prevent UI disruption during network timeouts or conflicts.

#### 2. Omnibox "Ghost Text" & AI Polish
- **Predictive Suggestions**: AI recommendations for projects and tags are now injected as dim gray "ghost text" directly into the Omnibox.
- **Selective Tab-Acceptance**: Users can now use the `Tab` key to selectively accept suggested tokens (e.g., accept the project but skip the tags) without being forced into a bulk `Ctrl+A` application.
- **Greeting Throttling**: The heavy 7-Day Pulse analytics greeting in the 2nd-Brain is now throttled to once per day. Subsequent launches provide a fast, minimalist welcome message.

#### 3. Workspace Awareness & Scoping
- **Git Auto-Tagging Control**: Added a global `git_auto_tag` configuration to toggle environment-aware metadata injection.
- **`.dwriter-ignore` Support**: Repositories can now include a `.dwriter-ignore` file with `disable_auto_tag=true` to prevent project-namespace pollution in monorepos.
- **Visual Hierarchy**: Automatically inherited Git tags are now rendered in a distinct, muted style (`dim #8c92a6`) to distinguish them from user-typed "Intent" tags.

### 🛠 Improvements & Fixes
- **Omnibox Refactor**: Decoupled the Omnibox into a standalone reusable widget with built-in suggestion logic.
- **Config Hardening**: Updated the configuration schema to support `auto_sync` and `last_pulse_greeting` state.

## Version 4.1.0 - April 8, 2026

### 🚀 Key Features

#### 1. Headless Observability (Machine-Readable State)
- **JSON Output Mode**: Introduced the `--json` flag for core data retrieval commands (`stats`, `today`, `todo list`). This enables downstream orchestration and automated tooling by emitting raw, structured JSON instead of human-readable terminal prose.
- **Git Context Awareness**: The `add` command now automatically detects if it is running within a Git repository. It intelligently appends the repository name as a project tag and includes the current branch as a metadata tag (e.g., `#git-main`), ensuring seamless workspace cross-contamination prevention.

#### 2. Proactive AI Intelligence
- **Smart Suggestions**: Implemented a proactive AI notification loop. After logging an entry, the background engine analyzes semantic similarity against past work and suggests relevant projects and tags.
- **Non-Disruptive TUI Toasts**: AI suggestions now appear as non-focus-stealing Textual notifications. Users can globally apply these suggestions with a single `Ctrl+A` keystroke.
- **Graceful Degradation**: Background AI threads are now hardened to handle local LLM timeouts and validation errors silently, ensuring the primary journaling flow remains uninterrupted.

#### 3. Distributed State & Hardening
- **Atomic Sync Writes**: Hardened the synchronization engine to use temporary file swaps (`os.replace`) for JSONL serialization. This eliminates the risk of sync file corruption during unexpected process termination.
- **CRDT Conflict Resolution**: Implemented and verified Lamport clock-based merging for cross-device state synchronization. Higher logical clocks now correctly resolve edit conflicts during `dwriter sync` operations.
- **Background HUD**: Added a persistent status bar to the TUI providing real-time observability. Displays the active Git branch and a spinning processing indicator (`[🧠 Processing...]`) for background AI tasks.

### 🛠 Improvements & Fixes
- **Off-Thread Database Queue**: Refactored the database layer to funnel all write operations through a dedicated background thread. This solves SQLite locking bottlenecks and ensures the Textual event loop remains stutter-free during complex saves.
- **Schema Rollback Safeguards**: Added automated database backups before manual migrations. If a schema upgrade fails, the system now automatically restores from the backup to prevent journal corruption.
- **Syntax & Indentation Guard**: Conducted a comprehensive audit of the TUI's primary application class, resolving structural regressions and ensuring full Python 3.10+ compatibility.

## Version 4.0.0 - April 8, 2026

### 🚀 Key Features

#### 1. 2nd-Brain UI & Chat Refinement
- **Message Bubbles**: Refactored the 2nd-Brain chat into a full-width bubble system. User responses are now strictly **right-aligned**, while AI responses are **left-aligned** with rounded borders.
- **Contextual Formatting**: AI responses now dynamically colorize mentioned dates (`[cyan]`), times (`[$success]`), and priority levels (e.g., `bold red` for Urgent) to match the project's high-signal visual language.
- **Intelligent Onboarding**: The 2nd-Brain now automatically greets the user with a "7-Day Pulse" wrap-up (Archetype, Velocity, Big Rock, and Momentum) upon initialization to provide immediate situational awareness.

#### 2. Local RAG & Vector Memory
- **Embedding Pipeline**: Integrated Ollama's `nomic-embed-text` to vectorize journal entries upon creation.
- **Semantic Search**: Implemented a local RAG (Retrieval-Augmented Generation) pipeline in the `ask` command. The AI now retrieves the top 5 semantically similar historical entries to provide habit-aware insights.
- **Energy Distribution**: Extended the `AnalyticsEngine` to track average energy levels across different life domains (Health, Career, etc.).

#### 3. Standup & Review Evolution
- **Exclusion Filters**: Implemented advanced project and tag filtering for Period Reviews. Users can now provide a comma-separated list of projects/tags to **exclude** from reports and exports.
- **UI Alignment**: Synchronized the Filter button placement with standard dropdowns for a balanced HUD aesthetic.

### 🛠 Improvements & Fixes
- **Omnibox Reliability**: Resolved synchronization issues with the omnibox toggle. Implemented a 0.2s interval and hardened focus management to ensure the omnibox respects "Zen Mode" vs. "Permanent" settings.
- **Global AI Toggle**: Introduced a global kill-switch for 2nd-Brain features. When disabled, the application intelligently swaps the primary landing screen from Chat to the Dashboard analytics.
- **System Hardening**: Added breathing room between the timer progress bar and controls. Refactored timer inputs to automatically strip `&` and `#` flags.
- **Date Sync**: Hardened `format_entry_datetime` to ensure the user's preferred date format (e.g., `MM/DD/YYYY`) is respected across every screen and export format.
- **Code Quality**: Conducted a comprehensive cleanup of the core TUI and configuration logic, resolving over 40 PEP 8 and `ruff` violations.

## Version 3.9.0 - April 7, 2026

### 🚀 Key Features

#### 1. Strategic AI Hardening (Analytical Mandate)
- **Execution Safeguards**: Strictly enforced a "no-action" mandate across the AI engine. The 2nd-Brain is now a dedicated analytical companion for reflection and data retrieval, with all direct write access (task/log creation) removed to ensure data integrity and user intent alignment.
- **Improved Context Routing**: Refined the routing architecture to prioritize history retrieval, context restoration, and productivity analytics.
- **Fallthrough Protection**: Implemented strict early-return logic and conversational fallback handlers to prevent the AI from hallucinating successful database modifications.

#### 2. Professional Documentation Refactor
- **Unified Standard**: Conducted a project-wide revision of all Markdown documentation and internal code comments. 
- **Google-Style Compliance**: All core modules now feature standardized Google-style docstrings, improving maintainability and developer onboarding.
- **Narrative Neutrality**: Removed marketing-style fluff and "AI-assistant" conversational filler from all technical guides and UI help strings.

### 🛠 Improvements & Fixes
- **Docstring Stabilization**: Fixed inconsistent parameter documentation in the TUI screen modules.

## Version 3.8.0 - April 6, 2026

### 🚀 Key Features

#### 1. AI-Augmented "2nd-Brain" Architecture
- **Intent Routing Intelligence**: Re-engineered the natural language engine with a multi-stage routing architecture. Requests are now categorized into specialized functional domains (Reflection, Analytics, Context Restoration) before detailed extraction.
- **Interactive 2nd-Brain TUI**: Introduced a dedicated chat interface as the primary TUI landing screen. Features a context-aware "Memory" system that provides the AI with immediate access to recent tasks and journal entries for highly relevant assistance.
- **Project Decomposition Engine**: Implemented advanced logic to break down complex natural language project requests into structured, estimated sub-task lists.

#### 2. Background Intelligence & Analytics
- **Context-Aware Analytics**: The 2nd-Brain now uncovers non-obvious productivity correlations, such as peak performance windows and project-specific bottlenecks, by analyzing 30-day historical data.
- **Narrative Productivity Wrapped**: Added AI-powered analytical summaries to the `stats` command, providing a conversational "Wrapped" style overview of wins, struggles, and focus areas.

### 🛠 Improvements & Fixes
- **AI Engine Robustness**: Transitioned to `MD_JSON` mode for structured extraction to eliminate schema-leak errors and improve reliability with local models like Llama 3.1.
- **Unified Omnibox Identity**: Synchronized placeholder behavior and visual cues across the 2nd-Brain, Logs, and To-Do screens.
- **Responsive TUI Layout**: Refactored the screen management system for pixel-perfect text wrapping and interactive chat log population.

### ⚠️ Known Issues
- **Action Execution**: The AI 2nd-Brain is currently configured for **reflection and analysis only**. It cannot directly modify the database (e.g., adding tasks or logs). Use the standard CLI or TUI boards for execution.

## Version 3.7.0 - April 6, 2026

### 🚀 Key Features

#### 1. 7-Day "Weekly Pulse" Wrap-up
- **Dynamic Metrics Engine**: Integrated advanced behavioral analytics into the core engine. Users are now categorized by **Archetypes** (e.g., "The Deep Diver", "The Closer") based on their rolling 7-day activity.
- **Peak Performance Visualization**: Automated identification of the user's **Golden Hour**, the time window of highest focus and task completion.
- **Momentum & Velocity**: Real-time tracking of task clearing rates compared to the previous week, providing a clear "Momentum Delta."
- **Project Spotlight**: Automated "Big Rock" detection that highlights which project consumed the majority of your bandwidth this week.

#### 2. Headless-First Weekly Summaries
- **`dwriter stats --weekly`**: A new high-signal terminal command that renders the Weekly Pulse wrap-up without launching the TUI.
- **`dwriter standup --weekly`**: Integrated weekly retrospective summaries into the standup generator, supporting multi-format export for Slack, Jira, and Markdown.

### 🛠 Improvements & Fixes
- **Dashboard Refinement**: Replaced the static "Two-Cents" insight box with the dynamic "7-Day Pulse" retrospective.
- **TUI Selector Hardening**: Implemented high-specificity CSS overrides for custom HUD elements to ensure visual consistency across different terminal themes.
- **Styling Harmonization**: Unified the "Quick Add" visual indicators across both the Logs and To-Do screens.

### ⚠️ Known Issues
- **Quick Add Vibrancy**: The `[+]` tab in the To-Do board may exhibit a slight color intensity mismatch compared to the Logs screen button in certain high-contrast themes due to internal Textual rendering logic.
