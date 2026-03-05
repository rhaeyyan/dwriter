# dwriter 📝

**dwriter** is a low-friction terminal journaling tool designed for people who live in their command line. It helps you track daily tasks and automatically generate summaries for morning standups or weekly reviews.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🚀 Quick Start (Installation)](#-quick-start-installation)
  - [🪟 Windows 11](#-windows-11)
  - [🐧 Linux (Ubuntu / Mint)](#-linux-ubuntu--mint)
  - [🍎 macOS (MacBook)](#-macos-macbook)
  - [✅ Verify Installation](#-verify-installation)
- [🛠️ Command Reference](#️-command-reference)
  - [Logging and Viewing](#logging-and-viewing)
  - [Generation and Summaries](#generation-and-summaries)
  - [Management and Configuration](#management-and-configuration)
  - [Task Management (Todo)](#task-management-todo)
  - [Focus Timer (Pomodoro)](#focus-timer-pomodoro)
  - [Search](#search)
- [🎨 Interactive TUI](#-interactive-tui)
  - [🔍 Interactive Search](#-interactive-search-dwriter-search)
  - [📋 Interactive Todo Board](#-interactive-todo-board-dwriter-todo)
  - [✏️ Edit Entries](#️-edit-entries-dwriter-edit)
  - [⏱️ Focus Timer](#️-focus-timer-dwriter-focus)
  - [📊 Dashboard](#-dashboard-dwriter-stats)
- [⚙️ Configuration](#️-configuration)
- [💻 Developer Commands](#-developer-commands)
  - [Shell Completions](#shell-completions)
- [🛠️ For Contributors & Developers](#️-for-contributors--developers)
  - [Creating New Projects](#creating-new-projects)
- [❓ Troubleshooting](#-troubleshooting)
- [📄 License](#-license)

---

## ✨ Key Features

* **⚡ Ultra-Fast Logging:** Capture tasks in seconds without leaving your terminal.
* **🤖 Standup Automation:** Instantly format yesterday's work for Slack, Jira, or Markdown.
* **📅 Weekly Reviews:** Generate organized summaries for sprint retrospectives or timesheets.
* **🏷️ Smart Organization:** Categorize entries with #tags and [projects].
* **🔥 Streak Tracking:** Keep your momentum high with a built-in logging streak counter.
* **🔍 Fuzzy Search:** Find past entries and tasks with typo-tolerant fuzzy matching.
* **🎨 Interactive TUI:** Real-time search and todo management with keyboard navigation.
* **⏱️ Focus Timer:** Built-in Pomodoro timer that auto-logs completed sessions.
* **✅ Todo Management:** Track pending tasks with priorities and auto-log when completed.

---

## 🚀 Quick Start (Installation)

Follow the steps below for your operating system.

---

### 🪟 Windows 11

#### Option 1: Using uv (Recommended - Faster & Modern)

**Step 1: Open PowerShell**
- Press `Win + X` and select **Terminal** or **PowerShell**

**Step 2: Install uv** (if not already installed)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 3: Navigate to the dwriter folder**
```powershell
cd dwriter
```

**Step 4: Install with uv**
```powershell
uv sync --extra dev
```

**Step 5: Run dwriter**
```powershell
uv run dwriter --help
```

#### Option 2: Using pip (Traditional)

**Step 1: Open PowerShell**
- Press `Win + X` and select **Terminal** or **PowerShell**

**Step 2: Navigate to the dwriter folder**
```powershell
cd dwriter
```

**Step 3: Create a virtual environment**
```powershell
python -m venv .venv
```

**Step 4: Activate the virtual environment**
```powershell
.venv\Scripts\Activate
```

**Step 5: Install dwriter**
```powershell
pip install -e ".[dev]"
```

**Done!** You can now use dwriter by typing `dwriter` in your terminal.

---

### 🐧 Linux (Ubuntu / Mint)

#### Option 1: Using uv (Recommended - Faster & Modern)

**Step 1: Open Terminal**
- Press `Ctrl + Alt + T` or search for "Terminal" in your applications

**Step 2: Install uv** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 3: Navigate to the dwriter folder**
```bash
cd dwriter
```

**Step 4: Install with uv**
```bash
uv sync --extra dev
```

**Step 5: Run dwriter**
```bash
uv run dwriter --help
```

#### Option 2: Using pip (Traditional)

**Step 1: Open Terminal**
- Press `Ctrl + Alt + T` or search for "Terminal" in your applications

**Step 2: Navigate to the dwriter folder**
```bash
cd dwriter
```

**Step 3: Create a virtual environment**
```bash
python3 -m venv .venv
```

**Step 4: Activate the virtual environment**
```bash
source .venv/bin/activate
```

**Step 5: Install dwriter**
```bash
pip install -e ".[dev]"
```

**Done!** You can now use dwriter by typing `dwriter` in your terminal.

> **Note:** On Linux, you may need `xclip` or `xsel` for clipboard features:
> ```bash
> sudo apt install xclip
> ```

---

### 🍎 macOS (MacBook)

#### Option 1: Using uv (Recommended - Faster & Modern)

**Step 1: Open Terminal**
- Press `Cmd + Space`, type "Terminal", and press `Enter`

**Step 2: Install uv** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 3: Navigate to the dwriter folder**
```bash
cd dwriter
```

**Step 4: Install with uv**
```bash
uv sync --extra dev
```

**Step 5: Run dwriter**
```bash
uv run dwriter --help
```

#### Option 2: Using pip (Traditional)

**Step 1: Open Terminal**
- Press `Cmd + Space`, type "Terminal", and press `Enter`

**Step 2: Navigate to the dwriter folder**
```bash
cd dwriter
```

**Step 3: Create a virtual environment**
```bash
python3 -m venv .venv
```

**Step 4: Activate the virtual environment**
```bash
source .venv/bin/activate
```

**Step 5: Install dwriter**
```bash
pip install -e ".[dev]"
```

**Done!** You can now use dwriter by typing `dwriter` in your terminal.

---

### ✅ Verify Installation

After installation, verify dwriter is working:

```bash
dwriter --help
```

You should see a list of available commands.

> **⚠️ Troubleshooting: "ModuleNotFoundError" or missing dependencies?**
>
> If you see an error like `ModuleNotFoundError: No module named 'rapidfuzz'` (or any other module), it means the global installation is missing some dependencies. This can happen if you installed dwriter before certain dependencies were added.
>
> **Quick Fix:** Use `uv run` to ensure all dependencies are available:
>
> ```bash
> uv run dwriter --help
> ```
>
> This runs dwriter inside the project's virtual environment where all dependencies are properly installed.
>
> **Permanent Fix:** Reinstall dwriter with all dependencies:
>
> ```bash
> pip install --upgrade -e ".[dev]"
> ```
>
> After reinstalling, `dwriter --help` should work directly.

---

**💡 Recommended Usage:**

For the most reliable experience, we recommend always using `uv run dwriter` instead of installing globally. This ensures:
- ✅ All dependencies are available
- ✅ No conflicts with other Python packages
- ✅ Easy to update or remove later

Example:
```bash
uv run dwriter add "my task"
uv run dwriter standup
uv run dwriter search
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
dwriter todo "Draft new relic ideas" -p my_project

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

### Focus Timer (Pomodoro)

Run a focus timer and log the result when finished. Launches an interactive TUI with pause/resume capability.

| Command | Description |
| --- | --- |
| `dwriter focus` | Start a 25-minute focus timer (interactive TUI) |
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

## 🎨 Interactive TUI

dwriter now includes interactive TUI (Text User Interface) modes for enhanced workflow. These modes provide real-time, keyboard-driven interfaces for common tasks.

### 🔍 Interactive Search (`dwriter search`)

Launch with `dwriter search` (no arguments).

**Features:**
- Real-time fuzzy filtering as you type
- Color-coded match scores
- Browse entries and todos in separate sections
- Matching tag/project colors across entries and todos

**Keybindings:**

| Key | Action |
| --- | --- |
| `j` / `k` | Navigate down / up |
| `Enter` | Select item (copy content to clipboard) |
| `/` | Focus search input |
| `Ctrl+N` | Toggle search type (All / Entries / Todos) |
| `q` / `Esc` | Quit

**Visual Features:**
- 📝 **Entries section** - Journal entries with date/time stamps
- ✅ **Todos section** - Tasks with priority labels
- 🏷️ **Consistent colors** - Yellow tags (#tag) and purple projects across both sections

### 📋 Interactive Todo Board (`dwriter todo`)

Launch with `dwriter todo` (no arguments) or `dwriter todo list --tui`.

**Features:**
- View all pending tasks with priority colors
- Mark tasks complete with automatic journal logging
- Edit and delete tasks inline
- Toast notifications for actions

**Keybindings:**

| Key | Action |
| --- | --- |
| `j` / `k` | Navigate down / up |
| `Space` / `Enter` | Mark task complete (auto-logs to journal) |
| `e` | Edit task content |
| `d` | Delete task (with confirmation) |
| `+` | Increase priority (e.g., normal → high) |
| `-` | Decrease priority (e.g., high → normal) |
| `t` | Edit tags (comma-separated) |
| `p` | Edit project name |
| `r` | Refresh list |
| `q` / `Esc` | Quit |

**Priority Colors:**
- 🔴 **URGENT** (red)
- 🟡 **HIGH** (yellow)
- ⚪ **NORMAL** (white)
- ⚫ **LOW** (dim)

### ✏️ Edit Entries (`dwriter edit`)

Launch with `dwriter edit` (no arguments).

**Features:**
- Edit today's entries in a clean table view
- Modify content, tags, and project separately
- Delete entries with confirmation
- No more fragile pipe-delimited syntax

**Keybindings:**

| Key | Action |
| --- | --- |
| `j` / `k` | Navigate down / up |
| `e` / `Enter` | Edit entry content |
| `t` | Edit tags (comma-separated) |
| `p` | Edit project name |
| `d` | Delete entry (with confirmation) |
| `r` | Refresh list |
| `q` / `Esc` | Quit |

### ⏱️ Focus Timer (`dwriter focus`)

Launch with `dwriter focus [MINUTES]`.

**Features:**
- Large digital countdown timer
- Pause/resume with Space key
- Adjust time on the fly with +/-
- Progress bar visualization
- Auto-prompt to log session on completion

**Keybindings:**

| Key | Action |
| --- | --- |
| `Space` | Pause/Resume timer |
| `+` | Add 5 minutes |
| `-` | Subtract 5 minutes |
| `Enter` | Finish session early |
| `q` / `Esc` | Quit (with confirmation) |

> **Hybrid CLI/TUI Design:** Quick operations remain CLI-based (`dwriter add`, `dwriter todo "task"`) for frictionless use. TUI modes launch only when needed for interactive workflows.

### 📊 Dashboard (`dwriter stats`)

Launch with `dwriter stats`.

**Features:**
- 📅 GitHub-style contribution calendar with streak tracking
- 📊 Weekly activity bar chart
- 📈 Statistics summary (total entries, tasks, tags, projects)
- 🏷️ Top tags with usage bars

**Keybindings:**

| Key | Action |
| --- | --- |
| `r` | Refresh all data |
| `Tab` | Navigate between sections |
| `q` / `Esc` | Quit |

**Visual Elements:**
- **Contribution Calendar** - Shows your logging activity over the past year with color-coded squares (darker = more entries)
- **Current/Longest Streak** - Displays your logging streaks at the top of the calendar
- **Weekly Chart** - Bar chart showing entries per week for the last 8 weeks
- **Stats Summary** - Total entries, completed tasks, unique tags, projects, and date range
- **Top Tags** - Your 10 most-used tags with visual usage bars

> **Hybrid CLI/TUI Design:** Quick operations remain CLI-based (`dwriter add`, `dwriter todo "task"`) for frictionless use. TUI modes launch only when needed for interactive workflows.

---

## ⚙️ Configuration

Your settings are stored in `~/.dwriter/config.toml`. You can customize default projects, tags, output formats, and display preferences here.

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

dwriter maintains **strict type safety** and **clean code standards** via mypy and ruff. All CI checks must pass before merging.

### Code Quality Status

| Tool | Status | Coverage |
|------|--------|----------|
| **mypy** | ✅ Strict mode | 27 source files, 0 errors |
| **ruff** | ✅ All checks | 0 errors |
| **pytest** | ✅ Test suite | All tests passing |

### Quick Start for Development

#### Using uv (Recommended)

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/ tests/

# Run the application
uv run dwriter --help
```

#### Using pip

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Run linting
ruff check src/ tests/

# Run the application
dwriter --help
```

### Development Workflow

**1. Making Changes**

```bash
# Edit your code
# ...

# Run type checking
uv run mypy src/

# Run linting (auto-fix when possible)
uv run ruff check src/ tests/ --fix

# Run tests
uv run pytest
```

**2. Before Committing**

```bash
# Ensure all checks pass
uv run mypy src/ && uv run ruff check src/ tests/ && uv run pytest
```

### Tool Configuration

All tooling is configured in [`pyproject.toml`](pyproject.toml):

- **mypy**: Strict mode with Python 3.9+ compatibility
- **ruff**: PEP-8, pydocstyle (Google convention), bugbear, pyupgrade
- **pytest**: Coverage enabled with `-v --cov=dwriter`

---

## 🛠️ For Contributors & Developers

### Creating New Projects

dwriter includes a bootstrap script for creating Python projects with the same modern tooling setup:

```bash
# Create a new project with uv, hatchling, ruff, mypy, and pytest pre-configured
./create-python-project.sh my_new_project
```

This is useful for:
- **Creating dwriter plugins or extensions**
- **Starting new Python projects** with best-practice configuration
- **Learning modern Python project structure** (uv, hatchling, strict typing)

The script creates a project with:
- ✅ `uv` package manager with `hatchling` build backend
- ✅ Python 3.12 target
- ✅ `ruff` with comprehensive linting rules
- ✅ `mypy` in strict mode
- ✅ `pytest` configuration
- ✅ `src/` layout structure

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Type Coverage** | 100% (mypy strict) |
| **Lint Errors** | 0 |
| **Test Coverage** | Enabled via pytest-cov |
| **Python Versions** | 3.8 - 3.12 |
| **Dependencies** | 9 (click, tomlkit, pyperclip, sqlalchemy, rich, rapidfuzz, textual) |
| **Dev Dependencies** | 7 (pytest, pytest-cov, black, ruff, mypy, types-pyperclip, tomli) |

---

### 🐚 Shell Completions

dwriter includes shell completion scripts for Bash and Zsh for faster command entry.

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
* **TUI not displaying correctly?** Ensure your terminal supports UTF-8 and has a minimum size of 80x24.
* **TUI appears garbled?** Try resizing your terminal window or using a different terminal emulator.
* **Keyboard input not working in TUI?** Make sure no terminal multiplexer (tmux/screen) is intercepting keys.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

[🚀 Quick Start (Installation)](#-quick-start-installation)
