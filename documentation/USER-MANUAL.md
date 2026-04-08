# 📖 dwriter: The Cohesive Technical User Manual

Welcome to the comprehensive guide for **dwriter**, the high-signal journaling and productivity tool designed for terminal power users. This manual covers every feature in the **v4.2.0** ecosystem, from rapid headless capture to deep AI-assisted reflection.

---

## 🚀 1. The Core Workflow: Headless-First

**dwriter** is designed with a "Headless-First" philosophy. You should never have to leave your shell to log work, manage tasks, or track time.

### ✍️ Logging Journal Entries (`add`)
Capture thoughts, wins, or notes instantly.
- **Basic:** `dwriter add "Fixed the race condition in auth"`
- **With Tags & Projects:** `dwriter add "Refactored DB layer #backend &core"`
- **Natural Language Dates:** `dwriter add "Met with team" --date "yesterday"`
- **Piping Content:** `git log -1 | dwriter add --stdin "#git-commit"`

### ✅ Task Management (`todo`)
Manage your future actions without a heavy GUI.
- **Add Task:** `dwriter todo "Review PR !high &api @due:friday"`
- **List Tasks:** `dwriter todo list`
- **Complete Task:** `dwriter done <id>` (This automatically logs the task to your journal).
- **Remove Task:** `dwriter todo rm <id>`

### ⏱️ Focus Sessions (`timer`)
Track "Deep Work" sessions directly from the CLI.
- **Start Timer:** `dwriter timer 25` (Starts a 25-minute session).
- **Tagged Timer:** `dwriter timer "50 &feature-x #deepwork"`
- **End of Session:** When the timer finishes, **dwriter** prompts you to log exactly what you achieved.

---

## 🎨 2. The Unified Visual Dashboard (TUI)

Launch the full interactive experience by running `dwriter` without arguments.

### ⌨️ Global Navigation
- **`1-5`**: Switch between screens (2nd-Brain, Logs, To-Do, Timer, Settings).
- **`/`**: Focus the **Omnibox** (Quick-Add bar) from any screen.
- **`Ctrl+P`**: Open the Command Palette for fuzzy-finding actions.
- **`q` or `Esc`**: Quit or go back.

### 🧠 The 2nd-Brain (Landing Screen)
The primary interface for AI interaction.
- **7-Day Pulse:** Every 24 hours, you'll receive a "Pulse" wrap-up (Archetype, Velocity, Big Rock) to help you reflect on your week.
- **Interactive Chat:** Ask questions like *"What did I work on for &project-x last month?"* or *"Summarize my #learning tags."*
- **Context-Aware:** The AI has "Short-Term Memory" (last 72 hours) and "Long-Term Memory" (weekly summaries) to provide accurate answers.

### 📋 The To-Do Board
A keyboard-driven Kanban-style board.
- **`Space`**: Toggle completion.
- **`e`**: Edit task details.
- **`+/-`**: Increase/Decrease priority.
- **`1 / 2 / 3`**: Switch between Pending, Upcoming, and Completed views.

### 🔍 Search & Logs
- **Live Filtering:** Type in the search bar to fuzzy-match entries across your entire history.
- **Quick Edit:** Highlight an entry and press `e` to fix typos or `d` to delete.

---

## ✨ 3. AI-Powered Intelligence

**dwriter** uses local LLMs (via Ollama) to augment your productivity.

### 👻 Omnibox "Ghost Text"
As you type in the TUI Omnibox, the AI analyzes your input semantically.
- **Predictions:** Suggested `#tags` and `&projects` appear in dim gray at the end of your input.
- **`Tab` Acceptance:** Press `Tab` once to accept the first suggested token. Press it again for the next. 
- **`Ctrl+A` Acceptance:** Press `Ctrl+A` to accept all AI suggestions at once.

### 📊 Behavioral Analytics (`stats`)
- **Activity Map:** View your streaks and entry counts over time.
- **Golden Hour:** Discover which time of day you are statistically most productive.
- **Archetypes:** See if you are a "Closer," a "Deep Diver," or a "Sprint Master" based on your 7-day velocity.

---

## 🔄 4. Distributed State & Sync

Keep your data synchronized across your laptop, desktop, and servers.

### ☁️ Background Sync
If `auto_sync = true` is set in your config:
- **Pull on Startup:** The TUI pulls remote changes immediately when launched.
- **Debounced Push:** 10 seconds after you stop typing, **dwriter** pushes your changes to your Git remote.
- **Sync Status:** Watch the footer for status updates: `[✅ Synced]`, `[🧠 Syncing...]`, or `[❌ Sync Failed]`.

### 🔀 Git Integration
- **Auto-Tagging:** Inside a Git repo, `dwriter add` automatically adds `#git-branch` and `&repo-name` to your entries.
- **`.dwriter-ignore`:** Add a file named `.dwriter-ignore` to your repo root with `disable_auto_tag=true` to skip auto-tagging in that specific workspace.

---

## ⚙️ 5. Customization & Advanced Usage

### 🛠 Configuration (`dwriter config edit`)
Customize your experience in `~/.dwriter/config.toml`:
- **Themes:** Choose from `cyberpunk`, `nord`, `dracula`, `catppuccin`, and more.
- **Date Formats:** Set `date_format` to `YYYY-MM-DD`, `MM/DD/YYYY`, or `DD/MM/YYYY`.
- **Permanent Omnibox:** Set `permanent_omnibox = true` to keep the quick-add bar visible at all times.

### 🐚 Shell Integration (Pro Tip)
Add a silent reminder check to your `.zshrc` or `.bashrc`:
```bash
if command -v dwriter >/dev/null 2>&1; then
    dwriter --check-only >/dev/null 2>&1 &
fi
```
This will trigger OS-level desktop notifications for `!urgent` tasks whenever you open a new terminal.

---

## ❓ Troubleshooting

- **Database Locks:** If you see `database is locked`, ensure you don't have multiple TUI instances running. The background sync daemon handles concurrent access safely, but manual edits might conflict.
- **AI Not Responding:** Ensure **Ollama** is running (`ollama serve`) and you have pulled the model (`ollama pull llama3.1`).
- **Sync Errors:** Check `~/.dwriter/logs/sync.log` for detailed Git error messages.

---

[⬅️ Back to README](../README.md) | [⚙️ Config Guide](./DEV-and-CONFIG.md)
