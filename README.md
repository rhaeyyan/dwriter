# dwriter 📝

**dwriter** is a low-friction terminal journaling tool designed for people who live in their command line. It helps you track daily tasks and automatically generate summaries for morning standups or weekly reviews.

## 🎯 Who is this for?
dwriter is for anyone who wants a quiet, distraction-free space to track their time, tasks, and daily progress. You don't need to be a software engineer to use it—you just need to value your focus.

dwriter was built for people who are tired of bloated web apps and endless clicking:

- 🎨 Freelancers & Creatives: Writers, designers, and consultants who need to effortlessly log billable hours and pull a summary of what they actually worked on this week.
- 📚 Students: Run focus timer study sessions, manage assignment to-dos, and track exactly how much time you're dedicating to different subjects.
- ✍️ Journalers & Reflectors: Use the standup and review features to easily recall what you did yesterday, making evening journaling or habit tracking a breeze.
- 🌱 Hobbyists & Makers: Whether you're tracking the daily growth of your garden, building furniture, or learning a language, log your milestones in seconds without leaving your keyboard.

If you want a minimalist, beautiful productivity suite that gets out of your way, dwriter is for you.

---

## 📚 Documentation

Detailed documentation for advanced usage and development:

- 🛠️ **[Command Reference](HEADLESS-README.md)**: Full CLI command reference (Logging, Standups, Todos, Timer, Search, etc.)
- ⚙️ **[Configuration & Development Guide](DEV-and-CONFIG.md)**: Detailed settings, developer setup, and project info.
## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🚀 Quick Start (Installation)](#-quick-start-installation)
  - [🪟 Windows 11](#-windows-11)
  - [🐧 Linux (Ubuntu / Mint)](#-linux-ubuntu--mint)
  - [🍎 macOS (MacBook)](#-macos-macbook)
  - [✅ Verify Installation & Launch](#-verify-installation--launch)
  - [🔄 Staying Up to Date](#-staying-up-to-date)
- [🎨 Interactive TUI](#-interactive-tui)
  - [🔍 Interactive Search](#-interactive-search-dwriter-search)
  - [📋 Interactive Todo Board](#-interactive-todo-board-dwriter-todo)
  - [✏️ Edit Entries](#-edit-entries-dwriter-edit)
  - [⏱️ Timer](#-timer-dwriter-timer)
  - [📊 Dashboard](#-dashboard-dwriter-stats)
- [📚 Documentation](#-documentation)
- [❓ Troubleshooting](#-troubleshooting)

---

## ✨ Key Features

* **⚡ Ultra-Fast Logging:** Capture tasks in seconds without leaving your terminal.
* **🤖 Standup Automation:** Instantly format yesterday's work for Slack, Jira, or Markdown.
* **📅 Weekly Reviews:** Generate organized summaries for sprint retrospectives or timesheets.
* **🏷️ Smart Organization:** Categorize entries with #tags and [projects].
* **🔥 Streak Tracking:** Keep your momentum high with a built-in logging streak counter.
* **🔍 Fuzzy Search:** Find past entries and tasks with typo-tolerant fuzzy matching.
* **🎨 Interactive TUI:** Real-time search and todo management with keyboard navigation.
* **⏱️ Timer:** Built-in focus timer that auto-logs completed sessions.
* **✅ Todo Management:** Track pending tasks with priorities and auto-log when completed.

---

## 🚀 Quick Start (Installation)

Follow the steps below for your operating system.

---

### 🪟 Windows 11

#### Option 1: Using uv (Recommended - Faster & Modern)

**Step 1: Clone Repo**
- Press `Win + X` and select **Terminal** or **PowerShell**
- Run: `gh repo clone rhaeyyan/dwriter` (clone repo to a location and remember the file location)
  
**Step 2: Install uv** (if not already installed)
- Open new Terminal window: Press `Win + X` and select **Terminal** or **PowerShell**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 3: Navigate to the dwriter folder**
- Inside the dwriter folder and right click and select  `Open in Terminal` 

**Step 4: Install with uv**
```powershell
uv sync --extra dev
```

**Step 5: Run dwriter**
```powershell
uv run dwriter
```
> ```bash
> uv run dwriter help
> ```

#### Option 2: Using pip (Traditional - Not Recommended)

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
uv run dwriter
```
> Use `help` command to see all commands and features
> ```bash
> uv run dwriter help
> ```

#### Option 2: Using pip (Traditional - Not Recommended)

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
uv run dwriter
```
> Use `help` command to see all commands and features
> ```bash
> uv run dwriter help
> ```

#### Option 2: Using pip (Traditional - Not Recommended)

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

### ✅ Verify Installation & Launch

After installation, you can launch dwriter by entering:

```bash
uv run dwriter
```
> Use `help` command to see all commands and features
> ```bash
> uv run dwriter help
> ```

You should see a list of available commands.

---

### 🔄 Staying Up to Date

To ensure you have the latest features and bug fixes, regularly update your local copy of dwriter:

```bash
# Pull the latest changes from the repository
git pull origin experimental-tui

# Update dependencies
uv sync --extra dev
```

You can check your current version by running:
```bash
uv run dwriter --version
```

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

### ⏱️ Timer (`dwriter timer`)

Launch with `dwriter timer [MINUTES]`.

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

## ❓ Troubleshooting

* **Command not found?** Ensure your virtual environment is active.
* **Clipboard issues?** On Linux, make sure you have `xclip` or `xsel` installed.
* **TUI not displaying correctly?** Ensure your terminal supports UTF-8 and has a minimum size of 80x24.
* **TUI appears garbled?** Try resizing your terminal window or using a different terminal emulator.
* **Keyboard input not working in TUI?** Make sure no terminal multiplexer (tmux/screen) is intercepting keys.

---

[🚀 Quick Start (Installation)](#-quick-start-installation)
