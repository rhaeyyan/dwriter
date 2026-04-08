# dwriter 📝
Experimental beta: v4.1.0
### *The minimalist journal for those who live in the terminal powered by llama 3.1:8b.*

**dwriter** is a high-signal, low-friction journaling tool designed to capture your work without breaking your flow. It bridges the gap between the raw speed of a command-line interface and the visual clarity of a modern dashboard.

Whether you are a software engineer tracking "deep work," a freelancer logging billable hours, or a student managing assignments, **dwriter** stays out of your way until you need it.

---

## ✨ Core Philosophy: Speed & Clarity

Modern productivity apps are often cluttered with distractions. **dwriter** is designed to prioritize your focus:

*   **⚡ Immediate Capture:** Use the "Headless CLI" to log thoughts, tasks, or focus sessions in seconds without leaving your terminal environment.
*   **🧠 AI-Powered 2nd-Brain:** Reflect on your history with an interactive chat that understands your long-term goals and recent activity.
*   **🎨 Unified Dashboard:** Launch the Terminal User Interface (TUI) to reflect, search your history, or manage a visual todo board.
*   **🤖 Standup Automation:** Instantly transform your raw logs into formatted summaries for Slack, Jira, or Markdown.
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

**dwriter** features a context-aware "2nd-Brain" designed for deep reflection. It uses a three-tier memory system to help you uncover patterns in your work:
- **Long-Term Memory:** AI-generated weekly retrospectives that identify your biggest wins and friction points.
- **Short-Term Memory:** Seamless access to your last 72 hours of activity.
- **Targeted History:** On-demand retrieval of past entries when you mention specific `&projects` or `#tags`.

### 📊 The Visual Dashboard (TUI)
Navigate between screens using the tab bar:

- **🧠 2nd-Brain:** Query your history and get productivity advice.
- **✅ To-do Board:** Keyboard-driven task board with priorities.
- **⏱️ Focus Timer:** A full-screen countdown that auto-logs your progress.
- **🔍 Search/Edit:** Live-filtering fuzzy search across all your history.
- **📈 Weekly Pulse:** Behavioral analytics updated every 24 hours.

**Observability:** The TUI now features a persistent **Status Bar** that displays your current active Git branch and real-time background task monitoring (`[🧠 Processing...]`).

**dwriter** operates in two modes: the **Fast Command-Line** (for speed) and the **Visual Dashboard** (for depth).

### ✍️ The Fast Command-Line (Headless)
Capture your work the moment it happens. No switching windows, no distractions.

```bash
# Log a quick entry (Always use "quotes" for #tags or &projects)
dwriter add "Refactored the auth layer #backend &project-x"

# Start a 25-minute focus session with shorthand notation
dwriter timer "25 &feature-y #deepwork"

# Add a task to your todo list
dwriter todo "Review the pull request" --priority urgent

# Machine-Readable Output (JSON) for automation
dwriter stats --json
dwriter today --json
```
---

## 💡 Mastering the Workflow

**dwriter** is designed to be your frictionless "brain-to-terminal" bridge. It adapts to your mental state, allowing you to capture everything from high-level project goals to fleeting creative sparks.

### 🏃 Frictionless Capture (The "Keys-Down" Loop)
- **Instant Entry:** `dwriter add "Idea: build a moisture sensor for the garden #someday"`
- **Git Integration:** When running inside a Git repo, `dwriter add` automatically appends the repo name as a project tag and your current branch as a metadata tag.
- **Priority & Deadlines:** Use `!priority` (`!urgent`, `!high`) and `@due:date` (`@due:friday`) directly in your text.
- **Zero Double-Entry:** Use `dwriter done <id>` to complete a task; it's automatically moved to your journal.
- **Instant Signal:** Run `dwriter stats` for a beautiful text-based productivity report.

### 🎨 Creative Organization & Retrieval
- **Total Freedom:** Use `#tags` and `&projects` however you like (e.g., `#draft`, `&home:renovation`).
- **Fuzzy Search:** Don't worry about perfect spelling. Use `/` in the TUI or `dwriter search "query"`.
- **Hierarchical Depth:** Use colons to organize complex structures like `&client:acme:q4-report`.

### 🧠 AI-Augmented Reflection (The 2nd-Brain)
The 2nd-Brain acts as a specialized analytical layer over your logs.

**Proactive Intelligence:** After logging an entry, **dwriter** will semantically analyze your history and suggest relevant `#tags` and `&projects`. Simply press `Ctrl+A` in the TUI to apply them instantly.

### 🧘 Deep Reflection (The Visual Dashboard)
- **The Dashboard:** Run `dwriter` (or `dwriter ui`) to manage your todo board and activity map.
- **Visual History:** Revisit your trip through a chronological log.
- **Easy Correction:** Use the interactive `dwriter edit` to quickly fix typos.

### 🔄 Multi-Device Synchronization
Keep your journal consistent across every machine you use. **dwriter** uses a Git-backed synchronization engine with **CRDT conflict resolution** (Lamport logical clocks) to ensure your data merges flawlessly without corruption.

```bash
# Sync local data with a remote repository
dwriter sync --remote "https://github.com/user/my-journal-sync.git"

# Push or pull manually
dwriter sync --push
dwriter sync --pull
```

---

## 📖 Explore Further

| Document | Description |
| :--- | :--- |
| 📘 **[User Manual](documentation/USER-MANUAL.md)** | **The complete technical guide to every feature.** |
| 🚀 **[Update Notes](documentation/update-notes.md)** | **New in v4.2.0:** Auto-Sync & Ghost Text. |
| 🛠️ **[Command Reference](documentation/HEADLESS-README.md)** | A complete guide to every CLI command and flag. |
| 📖 **[Creative Use Cases](documentation/USE_CASES.md)** | 20 ways to use dwriter for brewing, fitness, travel, and more. |
| ⚙️ **[Dev & Guide](documentation/DEV-and-CONFIG.md)** | Customizing your themes, default projects, and dev setup. |

---

## ❓ Troubleshooting & Tips

*   **Shell Characters:** Always wrap your entries in `"quotes"` if they contain `#tags` or `&projects`.
*   **Clipboard:** On Linux, install `xclip` or `xsel` to enable copy-to-clipboard.
*   **Customization:** Run `dwriter config edit` to tweak your default settings.

---
