# 🛠️ dwriter: The Command Reference

This document serves as the definitive guide for using **dwriter** from your terminal. It covers logging, task management, focus sessions, and automated report generation.

---

## ⚡ Logging & History

Capture your work without leaving the flow.

| Command | Description |
| :--- | :--- |
| `dwriter` | Launch the Unified Visual Dashboard (TUI). |
| `dwriter add "message"` | Log a new journal entry. |
| `dwriter today` | List everything you've accomplished today. |
| `dwriter undo` | Instantly delete the most recent entry. |
| `dwriter edit` | Search or select an entry to correct (interactive). |

### 📅 Time-Traveling with Natural Language
You don't have to log things the moment they happen. **dwriter** understands human dates:

```bash
# Log for yesterday
dwriter add "Finished the report" --date yesterday

# Log for last Friday
dwriter add "Completed the migration" --date "last Friday"

# Log for a specific date
dwriter add "Drafted the proposal" --date 2024-11-20
```

---

## ✅ Task Management (Todos)

Manage your future workload. When you mark a task as "done," it automatically logs a journal entry.

| Command | Description |
| :--- | :--- |
| `dwriter todo list` | View your pending tasks in a clean table. |
| `dwriter todo "task"` | Add a new task to your list. |
| `dwriter done <id>` | Complete a task and automatically log it to your journal. |
| `dwriter todo rm <id>` | Delete a task without logging it. |

### Advanced Task Controls:
```bash
# Set priority (low, normal, high, urgent)
dwriter todo "Fix the auth bug" --priority urgent -p backend

# Add tags or project context
dwriter todo "Write documentation" -t docs -p internal_tools
```

---

## ⏱️ Focus Timer

Run a Pomodoro-style timer in your terminal. When the timer ends, you'll be prompted to log what you accomplished.

| Command | Description |
| :--- | :--- |
| `dwriter timer` | Start a standard 25-minute focus session. |
| `dwriter timer <mins>` | Start a session for a custom number of minutes. |

### Automating the Result:
```bash
# Start a 45-minute deep work session pre-tagged with your project
dwriter timer 45 -p "engine_overhaul" -t "deepwork"
```

---

## 🤖 Summaries & Standups

Stop wasting time trying to remember what you did yesterday for your morning standup.

| Command | Description |
| :--- | :--- |
| `dwriter standup` | Generate a summary of yesterday's tasks. |
| `dwriter review --days 7` | Generate a weekly report of all work. |
| `dwriter stats` | View your streaks, activity counts, and habits. |

### Formats for Every Platform:
```bash
# Markdown for your personal notes
dwriter standup --format markdown

# Slack-friendly bullets
dwriter standup --format slack

# Jira-style formatting
dwriter standup --format jira
```

---

## 🔍 Searching Your History

Fuzzy search through thousands of entries in milliseconds. It handles typos gracefully.

| Command | Description |
| :--- | :--- |
| `dwriter search "query"` | Search all logs and tasks for a specific term. |
| `dwriter search -p <project>` | Filter search results by project. |
| `dwriter search -t <tag>` | Filter search results by tags. |

### Deep-Linking to the UI:
If you prefer a visual search experience:
```bash
dwriter ui --search
```

---

## ⚙️ Configuration

View and edit your settings to match your personal workflow.

| Command | Description |
| :--- | :--- |
| `dwriter config show` | Print your current settings to the terminal. |
| `dwriter config edit` | Open your configuration file in your default editor. |
| `dwriter config path` | Show exactly where your config file is stored. |

---

[⬅️ Back to README](../README.md)
