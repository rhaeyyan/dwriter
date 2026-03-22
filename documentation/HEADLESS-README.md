# dwriter - Command Reference 🛠️

This document contains the full command-line reference for **dwriter**. For an overview of the tool and installation instructions, please refer to the [Main README](../README.md).

---

## 🛠️ Command Reference

### Logging and Viewing

Use these commands to record your work and view your history.

> **⚠️ Important: Shell Special Characters**
>
> If you are using `#tags` or `&projects` directly in your terminal, your shell (bash, zsh, etc.) might treat them as comments or background commands.
>
> **Always quote your entry** if it contains these markers to ensure everything is captured correctly:
> - ✅ **Correct:** `dwriter add "fixed the bug #bug &engine"`
> - ❌ **Incorrect:** `dwriter add fixed the bug #bug &engine` (The shell will ignore everything after `#`)

| Command | Description |
| --- | --- |
| `dwriter` | Launch the Unified Visual Dashboard |
| `dwriter ui` | Launch the Visual Dashboard (supports deep-linking) |
| `dwriter ui --timer` | Launch dashboard directly to the timer |
| `dwriter ui --todo` | Launch dashboard directly to the todo board |
| `dwriter ui --search` | Launch dashboard directly to search |
| `dwriter add message` | Add a new log entry |
| `dwriter today` | Show all entries logged today |
| `dwriter undo` | Delete the most recent entry |

#### Examples:

```bash
# Multi-word entries work without quotes
dwriter add Fixed the race condition in auth

# But must be quoted if using #tags or &projects
dwriter add "Refactored database layer #refactor &myapp"

# Or quote the markers individually
dwriter add Refactored database layer "#refactor" "&myapp"
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
| `dwriter edit` | List today's entries for ID-based editing |
| `dwriter edit -i ID` | Edit a specific entry by ID |
| `dwriter edit -s QUERY` | Search for an entry to edit (fuzzy match) |
| `dwriter stats` | Show text-based productivity summary |
| `dwriter delete --before DATE` | Bulk delete old entries |
| `dwriter config show` | View your current settings |
| `dwriter config edit` | Open configuration file in editor |
| `dwriter config reset` | Reset configuration to defaults |
| `dwriter config path` | Show configuration file path |
| `dwriter examples` | Display usage workflows |

### Task Management (Todo)

Manage future tasks and to-dos. When a task is marked as done, it automatically generates a daily log entry.

| Command | Description |
| --- | --- |
| `dwriter todo` | List pending tasks (CLI table) |
| `dwriter todo "task"` | Add a new pending task |
| `dwriter todo "task" -t TAG` | Add a task with tags |
| `dwriter todo "task" -p PROJECT` | Add a task with a project |
| `dwriter todo "task" --priority LEVEL` | Set task priority |
| `dwriter todo list` | List pending tasks (CLI table) |
| `dwriter todo list --all` | Show all tasks, including completed ones |
| `dwriter done ID` | Mark a task as complete and log it |
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

Run a timer and log the result when finished.

| Command | Description |
| --- | --- |
| `dwriter timer` | Start a 25-minute timer (CLI progress bar) |
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
| `dwriter search query` | Fuzzy search entries and todos (CLI output) |
| `dwriter search query -p PROJECT` | Filter by project |
| `dwriter search query -t TAG` | Filter by tags |
| `dwriter search query --type TYPE` | Restrict search type |
| `dwriter search query -n LIMIT` | Limit number of results |

> **Tip:** For interactive search with live-filtering, run: `dwriter ui --search`

#### Examples:

```bash
dwriter search

```

```bash
dwriter search auth bug

```

```bash
dwriter search refactor -p my_project

```

```bash
dwriter search cache --type todo

```

```bash
dwriter search meeting -t work -t notes

```

**Match Scores:**
- 🟢 **90%+** (green): Excellent match
- 🟡 **75%+** (yellow): Good match
- ⚪ **60%+** (dim): Partial match

---

[Back to Main README](../README.md)
