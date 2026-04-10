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

## 🔄 Cross-Device Sync

Synchronize your journal across machines using a Git remote as the transport layer. Data is merged conflict-free using Lamport clock-based CRDT logic.

```bash
# Configure your sync remote once
dwriter sync --remote git@github.com:you/dwriter-sync.git

# Push your latest entries
dwriter sync --push

# Pull and merge entries from another machine
dwriter sync --pull
```

Enable automatic background pull on TUI launch:
```toml
# ~/.dwriter/config.toml
[defaults]
auto_sync = true
```

---

## 🏷️ Git Auto-Tagging

When you add an entry inside a Git repository, dwriter can automatically apply the repo name as `&project` and the branch as a `#git-<branch>` tag.

```bash
# Inside a git repo on branch "feature/auth"
dwriter add "Implemented JWT refresh logic"
# → logged as: &my-repo #git-feature/auth

# Disable auto-tagging
dwriter config set git_auto_tag false
```

```toml
[defaults]
git_auto_tag = true   # default: true
```

---

## 🔔 Notification Daemon (Linux)

Install a background systemd daemon that fires desktop notifications for urgent tasks.

```bash
# Install (checks every 5 min by default)
dwriter install-notifications

# Custom interval
dwriter install-notifications --interval 10

# Preview without writing anything
dwriter install-notifications --dry-run

# Remove
dwriter uninstall-notifications
```

Requires `notifications_enabled = true` in your config:
```bash
dwriter config set notifications_enabled true
```

> macOS and Windows: Run `dwriter install-notifications` for platform-specific setup instructions.

---

## 📤 Machine-Readable Output

All key read commands support a `--json` flag for scripting and piping.

```bash
# Today's entries as JSON
dwriter today --json | jq '.[].content'

# Stats as JSON
dwriter stats --json | jq '.streaks'

# Todo list as JSON
dwriter todo list --json | jq '.[] | select(.priority == "urgent")'
```

---

[⬅️ Back to README](../README.md)
