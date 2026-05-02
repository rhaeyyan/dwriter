# dwriter: AI Edition 📝
Experimental: v4.10.1
### *The minimalist journal for those who live in the terminal powered by a Dual-Model AI Pipeline (Gemma 4).*

**dwriter** is a high-signal, low-friction journaling tool designed to capture your work without breaking your flow. It bridges the gap between the raw speed of a command-line interface and the visual clarity of a modern dashboard.

Whether you are a software engineer tracking "deep work," a freelancer logging billable hours, or a student managing assignments, **dwriter** stays out of your way until you need it.

---

## ✨ Core Philosophy: Speed & Clarity

Modern productivity apps are often cluttered with distractions. **dwriter** is designed to prioritize your focus:

*   **⚡ Immediate Capture:** Use the "Headless CLI" to log thoughts, tasks, or focus sessions in seconds without leaving your terminal environment.
*   **🧠 Dual-Model 2nd-Brain:** Reflect on your history with an interactive chat powered by a specialized reasoning pipeline.
*   **🔁 Closed Learning Loop:** The AI now automatically extracts **Facts** (durable preferences, goals, and constraints) from your logs, building a personalized knowledge base that persists across sessions.
*   **🎨 Unified Dashboard:** Launch the Terminal User Interface (TUI) to reflect, search your history, or manage a visual todo board.
*   **🤖 Standup Automation:** Instantly transform your raw logs into formatted summaries for Slack, Jira, or Markdown.
*   **🕸️ Graph Index:** A LadybugDB property-graph index runs alongside SQLite as a derived read layer — powering FTS, graph traversal queries, and the Analytical Engine. Fully local, regenerable with `dw graph rebuild`.
*   **📝 Obsidian Integration:** Seamlessly export AI briefings and periodic reviews directly to your Obsidian vault as clean Markdown notes.
*   **📅 Natural Language:** Talk to your journal like a human. `dwriter add "Fixed the bug" --date "last Friday"` just works.

---

## 🚀 Quick Start

Getting started is as simple as a single command. We use **uv**, the fastest Python package manager, to keep your installation clean and isolated.

### 1. Install uv
If you haven't already, install the **uv** package manager:

*   **Linux / macOS:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
*   **Windows (PowerShell):**
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 2. Clone and Install dwriter
Clone the repository and switch to the **`dwriter-ai`** branch. This branch is required to access the 2nd-Brain AI features.

```bash
git clone https://github.com/rhaeyyan/dwriter.git
cd dwriter
git checkout dwriter-ai
uv tool install .
```

### 3. Keep dwriter Current
To pull the newest features and AI refinements (see **[Update Notes](documentation/update-notes.md)**), navigate to your local directory and run:

```bash
git pull origin dwriter-ai
uv tool install --upgrade .
```

---

## 🎮 How to Use dwriter

### 🧠 The AI 2nd-Brain (Reflection)
To **launch** the interactive chat:

```bash
dwriter
```

**dwriter** features a context-aware "2nd-Brain" designed for deep reflection. It uses a specialized three-tier memory system and a governed **Analytical Engine** to ensure architectural integrity:
- **Fact Memory (New):** Durable user preferences and constraints extracted automatically via the **Closed Learning Loop**.
- **Short-Term Memory:** Seamless access to your last 72 hours of activity, optimized via **Deterministic Compression**.
- **Targeted History:** On-demand retrieval of past entries when you mention specific projects or tags — powered by a **LadybugDB Graph Index**.
- **Governed Security:** All AI-driven insights are filtered through a customizable **Security Mode** (`permission_mode`) such as Read-Only, Append-Only, or Prompt.

### 📊 The Visual Dashboard (TUI)
Navigate between screens using the tab bar:

- **🧠 2nd-Brain:** Query your history and get productivity advice.
- **✅ To-do Board:** Keyboard-driven task board with priorities and overdue tracking.
- **⏱️ Focus Timer:** A full-screen countdown that auto-logs your progress.
- **🔍 Search/Edit:** Live-filtering fuzzy search across all your history with refined indentation.
- **📈 Weekly Pulse:** Behavioral analytics updated every 24 hours.

**Observability:** The TUI features a persistent **Status Bar** that displays your current active Git branch and real-time **Background Sync** monitoring (`[✅ Synced]`, `[🧠 Syncing...]`).

### ✍️ The Fast Command-Line (Headless)
Capture your work the moment it happens. No switching windows, no distractions.

```bash
# Log a quick entry (Always use "quotes" for #tags or &projects)
dwriter add "Refactored the auth layer #backend &project-x"

# Start a 25-minute focus session with shorthand notation
dwriter timer "25 &feature-y #deepwork"

# Add a task to your todo list
dwriter todo add "Review the pull request" --priority urgent

# Machine-Readable Output (JSON) for automation
dwriter stats --json
dwriter today --json
```
---

## 💡 Mastering the Workflow

**dwriter** is designed to be your frictionless "brain-to-terminal" bridge. It adapts to your mental state, allowing you to capture everything from high-level project goals to fleeting creative sparks.

### 🏃 Frictionless Capture (The "Keys-Down" Loop)
- **Instant Entry:** `dwriter add "Idea: build a moisture sensor for the garden #someday"`
- **Workspace Awareness:** Inside a Git repo, `dwriter add` automatically appends branch and repository tags.
- **Zero Double-Entry:** Use `dwriter done <id>` to complete a task; it's automatically moved to your journal.
- **Auto-Sync:** Changes are automatically pulled on startup and pushed to your remote 10 seconds after your last edit.

### 🧠 AI-Augmented Reflection (The 2nd-Brain)
The 2nd-Brain acts as a specialized analytical layer over your logs.

**Proactive Intelligence:** After logging an entry, **dwriter** will semantically analyze your history and suggest relevant `#tags` and `&projects`. Simply press `Ctrl+A` in the TUI to apply them instantly.

**Graph-Powered Search:** The AI can execute complex graph queries (Cypher) and Full-Text Search (FTS) against your history to find connections you might have missed.

---

## 🛠️ Tech Stack

**dwriter** is built with a focus on local-first performance and modern terminal aesthetics.

- **Language:** Python 3.10+
- **UI Framework:** [Textual](https://textual.textualize.io/) (TUI) & [Rich](https://rich.readthedocs.io/) (CLI)
- **Database:** SQLite (Write-side) & [LadybugDB](https://github.com/rhaeyyan/ladybug) (Graph Read-side)
- **AI Integration:** [Instructor](https://github.com/jxnl/instructor) (Structured Outputs) & [OpenAI SDK](https://github.com/openai/openai-python)
- **Search:** RapidFuzz (Fuzzy CLI) & FTS5 (Graph Index)
- **Tooling:** [uv](https://github.com/astral-sh/uv) (Package Management), Ruff (Linting), Mypy (Types), Pytest (Testing)

---

## 📖 Explore Further

| Document | Description |
| :--- | :--- |
| 🧠 **[2nd-Brain Guide](documentation/2ND-BRAIN-GUIDE.md)** | **How to get the most out of the AI 2nd-Brain — facts, logging habits, and analytics.** |
| 📘 **[User Manual](documentation/user-manual.md)** | **The complete technical guide to every feature.** |
| 🔄 **[Sync Guide](documentation/sync-guide.md)** | **Simple, step-by-step instructions for non-technical users.** |
| 🚀 **[Update Notes](documentation/update-notes.md)** | **New in v4.10.2:** CLI tag formatting word-wrap bug fix. |
| 🛠️ **[Command Reference](documentation/headless-readme.md)** | A complete guide to every CLI command and flag. |
| 📖 **[Creative Use Cases](documentation/use-cases.md)** | 20 ways to use dwriter for brewing, fitness, travel, and more. |
| ⚙️ **[Dev & Guide](documentation/dev-config.md)** | Customizing your themes, default projects, and dev setup. |

---

## ❓ Troubleshooting & Tips

*   **Shell Characters:** Always wrap your entries in `"quotes"` if they contain `#tags` or `&projects`.
*   **Clipboard:** On Linux, install `xclip` or `xsel` to enable copy-to-clipboard.
*   **Customization:** Run `dwriter config edit` to tweak your default settings.

---
lt settings.

---
