# dwriter - Command Reference 🛠️

This document contains the full command-line reference for **dwriter**. For an overview of the tool and installation instructions, please refer to the [Main README](../README.md).

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
| `dwriter edit` | Launch interactive edit TUI for today's entries |
| `dwriter edit -i ID` | Edit a specific entry by ID |
| `dwriter edit -s QUERY` | Search for an entry to edit (fuzzy match) |
| `dwriter stats` | Launch interactive dashboard TUI |
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
| `dwriter todo` | Launch interactive todo board TUI |
| `dwriter todo "task"` | Add a new pending task |
| `dwriter todo "task" -t TAG` | Add a task with tags |
| `dwriter todo "task" -p PROJECT` | Add a task with a project |
| `dwriter todo "task" --priority LEVEL` | Set task priority (low, normal, high, urgent) |
| `dwriter todo list` | List all pending tasks (static table) |
| `dwriter todo list --all` | Show all tasks, including completed ones |
| `dwriter todo list --tui` | Launch interactive TUI |
| `dwriter done ID` | Mark a task as complete and log it to today's entries |
| `dwriter todo rm ID` | Delete a task entirely |
| `dwriter todo edit ID` | Edit a task's content interactively |

#### Examples:

```bash
dwriter todo

```

```bash
dwriter todo "Draft new relic ideas" -p my_game_project

```

```bash
dwriter todo "Fix card draw bug" --priority urgent -t bug

```

```bash
dwriter todo list

```

```bash
dwriter done 5

```

> **Note:** Options must come **before** the task content:
> ```bash
> dwriter todo --priority urgent -t bug "Fix card draw bug"  # Also works
> ```

### Timer

Run a timer and log the result when finished. Launches an interactive TUI with pause/resume capability.

| Command | Description |
| --- | --- |
| `dwriter timer` | Start a 25-minute timer (interactive TUI) |
| `dwriter timer MINUTES` | Start a custom duration timer |
| `dwriter timer MINUTES -t TAG` | Add tags to the resulting entry |
| `dwriter timer MINUTES -p PROJECT` | Add project to the resulting entry |

#### Examples:

```bash
dwriter timer

```

```bash
dwriter timer 30

```

```bash
dwriter timer 45 -t deepwork -p backend

```

### Search

Fuzzy search your journal entries and to-do tasks. Forgiving of typos and partial matches.

| Command | Description |
| --- | --- |
| `dwriter search` | Launch interactive search TUI |
| `dwriter search "query"` | Fuzzy search entries and todos (static output) |
| `dwriter search "query" -p PROJECT` | Filter by project before searching |
| `dwriter search "query" -t TAG` | Filter by tags before searching (can use multiple `-t`) |
| `dwriter search "query" --type TYPE` | Restrict search to `entry`, `todo`, or `all` |
| `dwriter search "query" -n LIMIT` | Limit number of results per category |

#### Examples:

```bash
dwriter search

```

```bash
dwriter search "auth bug"

```

```bash
dwriter search "refactor" -p my_project

```

```bash
dwriter search "cache" --type todo

```

```bash
dwriter search "meeting" -t work -t notes

```

**Match Scores:**
- 🟢 **90%+** (green): Excellent match
- 🟡 **75%+** (yellow): Good match
- ⚪ **60%+** (dim): Partial match

---

[Back to Main README](../README.md)
