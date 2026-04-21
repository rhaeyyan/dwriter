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

### 🔍 Headless Observability (JSON Output)
For integration with external tools and scripts, several commands support a `--json` flag to emit raw, machine-readable data:

```bash
# Get today's logs as a JSON array
dwriter today --json

# Get your current productivity metrics and insights
dwriter stats --json

# Get your pending task list as JSON
dwriter todo list --json
```

### 📅 Time-Traveling with Natural Language
You don't have to log things the moment they happen. **dwriter** understands human dates:

```bash
# Log for yesterday (auto-tags with current Git context)
dwriter add "Finished the report" --date yesterday
```

###  Git Integration
If you are working inside a Git repository, `dwriter add` will automatically detect your context:
- **Project:** Sets the project name to the repository's root folder name (if no project is specified).
- **Metadata:** Appends a tag matching your current branch (e.g., `#git-main`).

---

## ✅ Task Management (Todos)

Manage your future workload. When you mark a task as "done," it automatically logs a journal entry.

| Command | Description |
| :--- | :--- |
| `dwriter todo list` | View your pending tasks in a clean table. |
| `dwriter todo "task"` | Add a new task to your list. |
| `dwriter done <id>` | Complete a task and automatically log it to your journal. |
| `dwriter todo rm <id>` | Delete a task without logging it. |

### Advanced Task Controls (Frictionless Shorthand)
The fastest way to manage tasks is to include metadata directly in the content string. **Always use "quotes" for shell safety.**

```bash
# Set priority (low, normal, high, urgent)
dwriter todo "Fix the auth bug !urgent &backend"

# Add tags or project context
dwriter todo "Write documentation #docs &internal_tools"

# Set a due date with @due:date
dwriter todo "Prepare presentation @due:friday #work"
```

---

## ⏱️ Focus Timer

Run a Pomodoro-style timer in your terminal. When the timer ends, you'll be prompted to log what you accomplished.

| Command | Description |
| :--- | :--- |
| `dwriter timer` | Start a standard 25-minute focus session. |
| `dwriter timer "mins"` | Start a session for a custom number of minutes. |

### Automating the Result:
Include your project and tags directly in the timer command string for instant logging.
```bash
# Start a 45-minute deep work session pre-tagged with your project
dwriter timer "45 &engine_overhaul #deepwork"
```

---

## 🤖 AI & Intelligence

Harness your historical data for deeper insights. These features require a local or remote AI backend (like Ollama).

| Command | Description |
| :--- | :--- |
| `dwriter ask "query"` | Ask natural language questions about your history, facts, or productivity. |
| `dwriter compress` | Generate a structured weekly retrospective from your activity logs. |
| `dwriter sync` | Synchronize your journal data across devices via Git. |
| `dwriter graph rebuild` | Rebuild the LadybugDB graph index from SQLite. Run this after install or sync issues. |

### Querying your 2nd-Brain
The `ask` command uses a ReAct loop with access to graph-backed tools and your extracted **Facts**:

```bash
# Query recent wins
dwriter ask "What were my biggest wins this week?"

# Analyze project time (uses graph index)
dwriter ask "How much progress did I make on &project-x?"

# Query durable facts
dwriter ask "What are my current long-term goals according to my logs?"
```

---

## 🤖 Summaries & Standups

Stop wasting time trying to remember what you did yesterday for your morning standup.

| Command | Description |
| :--- | :--- |
| `dwriter standup` | Generate a summary of yesterday's tasks. Supports `--weekly` for a 7-day wrap-up. |
| `dwriter review --days 7` | Generate a weekly report of all work. |
| `dwriter stats` | View your streaks, activity counts, and habits. Supports `--weekly` for high-signal insights. |

### Formats for Every Platform:
```bash
# Markdown for your personal notes
dwriter standup --format markdown

# Include the 7-day Weekly Pulse retrospective
dwriter standup --weekly

# View your weekly productivity summary (headless)
dwriter stats --weekly

# JSON output for custom dashboards
dwriter stats --weekly --json
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
