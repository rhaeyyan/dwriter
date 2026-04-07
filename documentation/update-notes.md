# dwriter Update Notes

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
- **Security Hardening**: Updated global ignore patterns to strictly exclude internal Gemini CLI context files and local agent workspaces.
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
