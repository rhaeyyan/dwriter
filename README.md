# dwriter 📝
v4.8.4
### *The minimalist journal for those who live in the terminal.*

**dwriter** is a high-signal, low-friction journaling tool designed to capture your work without breaking your flow. It bridges the gap between the raw speed of a command-line interface and the visual clarity of a modern dashboard.

Whether you are a software engineer tracking "deep work," a freelancer logging billable hours, or a student managing assignments, **dwriter** stays out of your way until you need it.

---

## ✨ Core Philosophy: Speed & Clarity

Modern productivity apps are often cluttered with distractions. **dwriter** is designed to prioritize your focus:

*   **⚡ Immediate Capture:** Use the "Headless CLI" to log thoughts, tasks, or focus sessions in seconds without leaving your terminal environment.
*   **📈 Weekly Pulse Analytics:** Behavioral analytics engine surfaces archetypes, golden hours, momentum deltas, and project spotlights from your rolling 7-day activity.
*   **🎨 Unified Dashboard:** Launch the Terminal User Interface (TUI) to reflect, search your history, or manage a visual todo board.
*   **📖 High-Signal Readability:** All logs feature **hanging indentation**, ensuring multi-line entries align perfectly for rapid scanning.
*   **🤖 Standup Automation:** Instantly transform your raw logs into formatted summaries for Slack, Jira, or Markdown.
*   **📝 Obsidian Integration:** Seamlessly export briefings and periodic reviews directly to your Obsidian vault as clean Markdown notes.
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
Clone the repository and install from the `main` branch.

```bash
git clone https://github.com/rhaeyyan/dwriter.git
cd dwriter
uv tool install .
```

> Looking for AI features (2nd-Brain, semantic tagging, LLM standup)? Switch to the **`dwriter-ai`** branch.

### 3. Keep dwriter Current
To pull the newest features (see **[Update Notes](documentation/update-notes.md)**), navigate to your local directory and run:

```bash
git pull origin main
uv tool install --upgrade .
```

---

## 🎮 How to Use dwriter

### 📊 The Visual Dashboard (TUI)
Launch the full dashboard:

```bash
dwriter ui
```

Navigate between screens using the tab bar:

- **✅ To-do Board:** Keyboard-driven task board with priorities.
- **⏱️ Focus Timer:** A full-screen countdown that auto-logs your progress.
- **🔍 Search/Edit:** Live-filtering fuzzy search across all your history with refined indentation.
- **📈 Weekly Pulse:** Behavioral analytics updated every 24 hours.

**Observability:** The TUI features a persistent **Status Bar** that displays your current active Git branch and real-time **Background Sync** monitoring (`[✅ Synced]`, `[🧠 Syncing...]`).

**dwriter** operates in two modes: the **Fast Command-Line** (for speed) and the **Visual Dashboard** (for depth).

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
- **Workspace Awareness:** Inside a Git repo, `dwriter add` automatically appends branch and repository tags. Use a `.dwriter-ignore` file to disable this in specific projects.
- **Ghost Text Suggestions:** As you type in the TUI omnibox, token suggestions appear in dim "ghost text." Press `Tab` to selectively accept a `&project` or `#tag` token.
- **Zero Double-Entry:** Use `dwriter done <id>` to complete a task; it's automatically moved to your journal.
- **Auto-Sync:** Changes are automatically pulled on startup and pushed to your remote 10 seconds after your last edit.

### 🎨 Creative Organization & Retrieval
- **Total Freedom:** Use `#tags` and `&projects` however you like (e.g., `#draft`, `&home:renovation`).
- **Fuzzy Search:** Don't worry about perfect spelling. Use `/` in the TUI or `dwriter search "query"`.
- **Hierarchical Depth:** Use colons to organize complex structures like `&client:acme:q4-report`.

### 🧘 Deep Reflection (The Visual Dashboard)
- **The Dashboard:** Run `dwriter ui` to manage your todo board and activity map.
- **Visual History:** Revisit your work through a chronological log.
- **Easy Correction:** Use the interactive `dwriter edit` to quickly fix typos.

### 🔄 Multi-Device Synchronization
Keep your journal consistent across every machine you use. **dwriter** uses a Git-backed synchronization engine to ensure your data merges flawlessly without corruption.

**New to syncing?** Read our **[Step-by-Step Sync Guide](documentation/sync-guide.md)** for a simple, non-technical walkthrough.

```bash
# Connect to your private sync repository
dwriter sync --remote "https://github.com/user/my-journal-sync.git"

# Push or pull manually
dwriter sync --push
dwriter sync --pull
```

---

## 📖 Explore Further

| Document | Description |
| :--- | :--- |
| 📘 **[User Manual](documentation/user-manual.md)** | **The complete technical guide to every feature.** |
| 🔄 **[Sync Guide](documentation/sync-guide.md)** | **Simple, step-by-step instructions for non-technical users.** |
| 🚀 **[Update Notes](documentation/update-notes.md)** | **New in v3.7.0:** Guard 4 compliance & module decomposition. |
| 🛠️ **[Command Reference](documentation/headless-readme.md)** | A complete guide to every CLI command and flag. |
| 📖 **[Creative Use Cases](documentation/use-cases.md)** | 20 ways to use dwriter for brewing, fitness, travel, and more. |
| ⚙️ **[Dev & Guide](documentation/dev-config.md)** | Customizing your themes, default projects, and dev setup. |

---

## ❓ Troubleshooting & Tips

*   **Shell Characters:** Always wrap your entries in `"quotes"` if they contain `#tags` or `&projects`.
*   **Clipboard:** On Linux, install `xclip` or `xsel` to enable copy-to-clipboard.
*   **Customization:** Run `dwriter config edit` to tweak your default settings.

---
