# Day Writer 📝

**Day Writer** is a low-friction terminal journaling tool designed for people who live in their command line. It helps you track daily tasks and automatically generate summaries for morning standups or weekly reviews.

[🛠️ Command Reference](#️-command-reference)                                                                                                                                    │
[⚙️ Configuration](#️-configuration)                                                                                                                                            │
[💻 Developer Commands](#-developer-commands)                                                                                                                                  │
[❓ Troubleshooting](#-troubleshooting)  

---

## ✨ Key Features

* **⚡ Ultra-Fast Logging:** Capture tasks in seconds without leaving your terminal.
* **🤖 Standup Automation:** Instantly format yesterday's work for Slack, Jira, or Markdown.
* **📅 Weekly Reviews:** Generate organized summaries for sprint retrospectives or timesheets.
* **🏷️ Smart Organization:** Categorize entries with #tags and [projects].
* **🔥 Streak Tracking:** Keep your momentum high with a built-in logging streak counter.

---

## 🚀 Quick Start (Installation)

### 1. Prerequisites

Make sure you have **Python 3.8 or higher** and **pip** installed on your system.

### 2. Install from Source

Run these commands in your terminal to set up Day Writer:

```bash
cd dwriter

```

```bash
python3 -m venv .venv

```

```bash
source .venv/bin/activate

```

> On Windows:
> ```bash
> .venv\Scripts\activate
> 
> ```
> 
> 

```bash
pip install -e .

```

---

## 🛠️ Command Reference

### Logging and Viewing

Use these commands to record your work and view your history.

| Command | Description |
| --- | --- |
| `dwriter add "message"` | Add a new log entry |
| `dwriter add "message" -t TAG` | Add an entry with tags (can use multiple `-t`) |
| `dwriter add "message" -p PROJECT` | Add an entry with a project name |
| `dwriter add "message" --date DATE` | Add an entry for a specific date |
| `dwriter today` | Show all entries logged today |
| `dwriter` | Show all entries (default view) |
| `dwriter undo` | Delete the most recent entry |

#### Examples:

```bash
dwriter add "Fixed the race condition in auth"

```

```bash
dwriter add "Refactored database layer" -t refactor -t backend -p myapp

```

```bash
dwriter add "Finished report" --date yesterday

```

```bash
dwriter add "Meeting notes" --date "last Friday"

```

```bash
dwriter add "Completed sprint" --date "3 days ago"

```

**Supported date formats:**
- Relative: `today`, `yesterday`, `tomorrow`
- Days/weeks ago: `3 days ago`, `2 weeks ago`
- Last weekday: `last Monday`, `last Friday`
- Weekday (most recent): `Monday`, `Friday`
- Standard dates: `2024-01-15`, `01/15/2024`, `January 15, 2024`

### Generation and Summaries

Create formatted reports for meetings or documentation.

| Command | Description |
| --- | --- |
| `dwriter standup` | Generate a summary of yesterday's tasks |
| `dwriter standup -f FORMAT` | Generate standup in specific format (bullets, slack, jira, markdown) |
| `dwriter standup --no-copy` | Generate standup without copying to clipboard |
| `dwriter review` | Review entries from the last 5 days (default) |
| `dwriter review --days N` | Review entries from the last N days |
| `dwriter review -f FORMAT` | Review in specific format (markdown, plain, slack) |
| `dwriter stats` | Show logging statistics and your current streak |

#### Examples:

```bash
dwriter standup --format slack

```

```bash
dwriter standup --format jira

```

```bash
dwriter review --days 7 --format markdown

```

### Management and Configuration

Edit your history or customize how the tool behaves.

| Command | Description |
| --- | --- |
| `dwriter edit` | Interactively edit or delete today's entries |
| `dwriter edit -i ID` | Edit a specific entry by ID |
| `dwriter delete --before DATE` | Bulk delete entries older than a specific date (YYYY-MM-DD) |
| `dwriter config show` | View your current settings |
| `dwriter config edit` | Open the configuration file in your editor |
| `dwriter config reset` | Reset configuration to defaults |
| `dwriter config path` | Show configuration file path |
| `dwriter examples` | Display comprehensive usage workflows |

### Task Management (Todo)

Manage future tasks and to-dos. When a task is marked as done, it automatically generates a daily log entry.

| Command | Description |
| --- | --- |
| `dwriter todo add "task"` | Add a new pending task |
| `dwriter todo add "task" -t TAG` | Add a task with tags |
| `dwriter todo add "task" -p PROJECT` | Add a task with a project |
| `dwriter todo add "task" --priority LEVEL` | Set task priority (low, normal, high, urgent) |
| `dwriter todo list` | List all pending tasks |
| `dwriter todo list --all` | Show all tasks, including completed ones |
| `dwriter todo done ID` | Mark a task as complete and log it to today's entries |
| `dwriter todo rm ID` | Delete a task entirely |
| `dwriter todo edit ID` | Edit a task's content interactively |

#### Examples:

```bash
dwriter todo add "Draft new relic ideas" -p Mainframe_Mayhem

```

```bash
dwriter todo add "Fix card draw bug" --priority urgent -t bug

```

```bash
dwriter todo list

```

```bash
dwriter todo done 5

```

### Focus Timer (Pomodoro)

Run a focus timer and log the result when finished.

| Command | Description |
| --- | --- |
| `dwriter focus` | Start a 25-minute focus timer |
| `dwriter focus MINUTES` | Start a custom duration timer |
| `dwriter focus MINUTES -t TAG` | Add tags to the resulting entry |
| `dwriter focus MINUTES -p PROJECT` | Add project to the resulting entry |

#### Examples:

```bash
dwriter focus

```

```bash
dwriter focus 30

```

```bash
dwriter focus 45 -t deepwork -p backend

```

---

## ⚙️ Configuration

Your settings are stored in `~/.day-writer/config.toml`. You can customize default projects, tags, output formats, and display preferences here.

**Example Config:**

```toml
[defaults]
project = "core-engine"
tags = ["dev"]

[standup]
format = "slack"
copy_to_clipboard = true

[review]
default_days = 7
format = "markdown"

[display]
show_confirmation = true
show_id = true
colors = true

```

**Configuration Options:**

| Section | Option | Description | Default |
| --- | --- | --- | --- |
| `[defaults]` | `project` | Default project for new entries | `null` |
| `[defaults]` | `tags` | Default tags for new entries | `[]` |
| `[standup]` | `format` | Default standup format (bullets, slack, jira, markdown) | `"bullets"` |
| `[standup]` | `copy_to_clipboard` | Auto-copy standup to clipboard | `true` |
| `[review]` | `default_days` | Default number of days to review | `5` |
| `[review]` | `format` | Default review format (markdown, plain, slack) | `"markdown"` |
| `[display]` | `show_confirmation` | Show confirmation after adding entries | `true` |
| `[display]` | `show_id` | Show entry IDs in output | `true` |
| `[display]` | `colors` | Enable colored output | `true` |

---

## 💻 Developer Commands

If you want to contribute or run the test suite:

```bash
pip install -e ".[dev]"

```

```bash
pytest

```

```bash
ruff check src/

```

### Shell Completions

Day Writer includes shell completion scripts for Bash and Zsh for faster command entry.

**For Bash:**

```bash
source completions/day.bash

```

Add to your `~/.bashrc` for persistent completions.

**For Zsh:**

```bash
source completions/day.zsh

```

Add to your `~/.zshrc` for persistent completions.

---

## ❓ Troubleshooting

* **Command not found?** Ensure your virtual environment is active.
* **Clipboard issues?** On Linux, make sure you have `xclip` or `xsel` installed.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

[🚀 Quick Start (Installation)](#-quick-start-installation)
