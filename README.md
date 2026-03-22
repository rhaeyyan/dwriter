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

- 📖 **[Creative Use Cases](documentation/USE_CASES.md)**: 20 creative ways to use dwriter beyond standard task management.
- 🛠️ **[Command Reference](documentation/HEADLESS-README.md)**: Full CLI command reference (Logging, Standups, Todos, Timer, Search, etc.)
- ⚙️ **[Configuration & Development Guide](documentation/DEV-and-CONFIG.md)**: Detailed settings, developer setup, and project info.

## 📋 Table of Contents

- [🎯 Who is this for?](#-who-is-this-for)
- [✨ Key Features](#-key-features)
- [🚀 Quick Start (Installation)](#-quick-start-installation)
  - [🪟 Windows](#-windows)
  - [🐧 Linux (Ubuntu / Mint)](#-linux-ubuntu--mint)
  - [🍎 macOS](#-macos)
  - [🔄 Staying Up to Date](#-staying-up-to-date)
- [🎮 Launching dwriter](#-launching-dwriter)
  - [✅ Your First Command](#-your-first-command)
- [💡 How to Get the Most Out of dwriter](#-how-to-get-the-most-out-of-dwriter)
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
* **🏷️ Smart Organization:** Categorize entries with #tags and &projects or &project:subproject.
* **🔥 Streak Tracking:** Keep your momentum high with a built-in logging streak counter.
* **🔍 Fuzzy Search:** Find past entries and tasks with typo-tolerant fuzzy matching.
* **🎨 Interactive TUI:** Real-time search and todo management with keyboard navigation.
* **⏱️ Timer:** Built-in focus timer that auto-logs completed sessions.
* **✅ Todo Management:** Track pending tasks with priorities and auto-log when completed.

---

## 🚀 Quick Start (Installation)

Getting dwriter running on your computer is quick and easy. We use **uv**, a modern and lightning-fast tool for installing Python applications, which keeps dwriter isolated and tidy on your system.

---

### 🪟 Windows

1.  **Get the Code:**
    *   Click the green **Code** button at the top of this page and select **Download ZIP**, then extract the folder.
    *   *Or*, if you have Git installed, run: `git clone https://github.com/rhaeyyan/dwriter.git`
2.  **Install the Setup Tool (uv):**
    *   Press `Win + X` on your keyboard and select **Terminal** or **PowerShell**.
    *   Copy and paste this command and press Enter:
        ```powershell
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
3.  **Install dwriter:**
    *   Open the `dwriter` folder you downloaded/cloned.
    *   Right-click in any empty space inside the folder and select **Open in Terminal**.
    *   Type `uv tool install .` and press Enter.

---

### 🐧 Linux (Ubuntu / Mint)

1.  **Install the Setup Tool (uv):**
    *   Open your Terminal (`Ctrl + Alt + T`).
    *   Copy and paste this command:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
2.  **Navigate to the folder:**
    *   Use `cd dwriter` to enter the project folder.
3.  **Install dwriter:**
    *   Run: `uv tool install .`

> **Note:** For clipboard support, run: `sudo apt install xclip` or `sudo apt install xsel`

---

### 🍎 macOS

1.  **Install the Setup Tool (uv):**
    *   Open Terminal (Press `Cmd + Space`, type "Terminal", and press Enter).
    *   Copy and paste this command:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
2.  **Navigate to the folder:**
    *   Use `cd dwriter` to enter the project folder.
3.  **Install dwriter:**
    *   Run: `uv tool install .`

---

### 🔄 Staying Up to Date

To get the latest features and fixes, run these commands inside your `dwriter` folder:
```bash
# Get the latest code
git pull

# Update the installation
uv tool upgrade dwriter
```

---

## 🎮 Launching dwriter

Once installed with `uv tool install .`, the `dwriter` command is available from **anywhere** on your computer.

To open the **unified TUI (Terminal User Interface)** and access all features in one place, simply run:

```bash
dwriter
```

This will launch the interactive dashboard where you can:
- **Manage Tasks:** View and complete todos.
- **Track Time:** Use the built-in focus timer.
- **Search:** Fuzzy search through your journal entries.
- **Statistics:** View your contribution calendar and behavioral insights.

### ✅ Your First Command

To see everything dwriter can do, just type:
```bash
dwriter help
```

To start your first journal entry, just type:
```bash
dwriter add "Just finished setting up dwriter! #goals"
```

> **⚠️ Important: Shell Special Characters**
>
> If you are using `#tags` or `&projects` directly in your terminal, your shell (bash, zsh, etc.) might treat them as comments or background commands.
>
> **Always quote your entry** to ensure everything is captured correctly:
> - ✅ **Correct:** `dwriter add "fixed the bug #bug &engine"`
> - ❌ **Incorrect:** `dwriter add fixed the bug #bug &engine` (The shell will ignore everything after `#`)

> **Developer Note:** If you prefer running dwriter locally without installing it globally, you can always use `uv run dwriter` inside the project folder.

---

## 💡 How to Get the Most Out of dwriter

To truly make `dwriter` a seamless part of your daily routine, it helps to adopt a few simple habits and workflows. Here are some pro tips to maximize your experience:

### 1. The "CLI for Capture, TUI for Review" Rule
The magic of `dwriter` is its hybrid design. To stay in your flow state, use the **headless CLI** for all your data entry (`dwriter add`, `dwriter todo`, `dwriter timer`). It takes two seconds and you never leave your prompt. Then, reserve the **interactive TUI** (`dwriter search`, `dwriter stats`, `dwriter edit`) for when you actually need to review your week, plan your sprint, or fix typos. 

### 2. Establish a Tagging Convention Early
Because `dwriter` relies heavily on `#tags` and `&projects` to generate summaries, consistency is key. Pick a handful of standard tags and stick to them. 
* **Good convention:** Use `&projects` for the *context* or *client* (e.g., `&acmecorp`, `&personal`) and `#tags` for the *action* (e.g., `#bugfix`, `#meeting`, `#reading`). 

### 3. Create Subcategories with Colons (`&project:subproject`)
If you have a large project with multiple moving parts, you don't need to invent entirely new project names. You can create clean subcategories by using a colon in your project tag!
* **For Freelancers:** `&client_acme:website` vs. `&client_acme:marketing`
* **For Students:** `&cs_101:homework` vs. `&cs_101:labs`
* **For Makers:** `&desk_build:woodworking` vs. `&desk_build:finishing`
This syntax keeps your root projects organized while giving you granular control over what you are tracking. 

### 4. Let the Timer Do the Logging
If you are sitting down for a focused session, don't just use `dwriter add` afterward. Use `dwriter timer 25 -p my_project`. Not only do you get a visual Pomodoro countdown to keep you accountable, but the TUI will automatically prompt you to log what you accomplished the second the timer finishes. It combines focus tracking and journaling into one step.

### 5. Leverage Natural Language Time-Traveling
Don't stress if you forget to log a massive debugging session on a Friday afternoon. `dwriter` understands natural language. On Monday morning, just run `dwriter add "Fixed the memory leak" --date "last Friday"`. This keeps your timeline pristine for your weekly reviews and contribution calendar.

### 6. Alias it for Ultimate Speed
If you are typing out `dwriter` 20 times a day, save your keystrokes! Add a simple alias to your `.bashrc` or `.zshrc` file:
```bash
alias dw="dwriter"
alias dwt="dwriter todo"
alias dws="dwriter search"
```
Now, logging an idea takes literally three keystrokes: `dw add "New idea!"`. 

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

Launch with `dwriter stats` or access via the first tab in the main TUI.

**Features:**
- 📈 **Unified Pulse Panel** - A high-density 45-day activity heatmap that tracks your logging frequency.
- 💡 **"Two-Cents" Insights** - AI-powered behavioral nudges that warn you about burnout risk, project friction, and context-switching patterns.
- 📅 **History Calendar** - GitHub-style contribution calendar with streak tracking for the past year.
- 📋 **Performance Reports** - Generate a detailed Markdown report of your productivity metrics.

**Keybindings:**

| Key | Action |
| --- | --- |
| `Tab` | Navigate between sections |
| `c` | Copy Performance Report to clipboard |
| `r` | Refresh all data |
| `q` / `Esc` | Quit |

**Visual Elements:**
- **45-day Heatmap** - Shows your activity levels over the last month and a half with color-coded density.
- **Current/Longest Streak** - Displays your logging streaks at the bottom of the calendar.
- **Behavioral Nudges** - Real-time advice like "Watch Your Pace" or "Context Switcher" based on your actual work patterns.

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
