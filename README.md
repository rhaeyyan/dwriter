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

To launch the **Unified TUI (Terminal User Interface)**—your primary command center for productivity—simply run:

```bash
dwriter
```

This opens the interactive dashboard where you can manage your entire workflow in one place:
- **✅ Daily Todos:** View, prioritize, and complete tasks.
- **⏱️ Focus Timer:** Run Pomodoro sessions that auto-log your work.
- **🔍 Deep Search:** Fuzzy-find any past entry or task instantly.
- **📊 Pulse Panel:** View your activity heatmap and behavioral insights.

### ✅ Your First Entry

While the TUI is the best way to manage your day, you can always capture a quick thought directly from your terminal:

```bash
dwriter add "Just finished setting up dwriter! #goals"
```

> **⚠️ Pro-Tip: Shell Special Characters**
>
> If you are using `#tags` or `&projects` directly in your terminal, always **quote your entry** to ensure your shell doesn't treat them as comments:
> - ✅ **Correct:** `dwriter add "fixed the bug #bug &engine"`
> - ❌ **Incorrect:** `dwriter add fixed the bug #bug &engine`

---

## 💡 How to Get the Most Out of dwriter

To truly make `dwriter` a seamless part of your daily routine, it helps to adopt a few simple habits and workflows. Here are some pro tips to maximize your experience:

### 1. The TUI is your "Command Center"
The most effective way to use `dwriter` is to keep the **interactive TUI** open in a dedicated terminal tab or window throughout the day. It acts as your dashboard for focus, task management, and reflection. Use the **headless CLI** (`dwriter add`) only for "surgical" data entry when you are in the middle of a coding session and don't want to switch tabs.

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
If you are sitting down for a focused session, don't just use `dwriter add` afterward. Launch the **Timer** in the TUI (`dwriter timer 25 -p my_project`). Not only do you get a visual countdown to keep you accountable, but the TUI will automatically prompt you to log what you accomplished the second the timer finishes. It combines focus tracking and journaling into one step.

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

## 🎨 Visual Dashboard vs. Fast Command-Line

**dwriter** is designed for speed. Most tasks can be done with a single command in your terminal, while the **Unified Dashboard (TUI)** provides a beautiful visual space for deep work and reflection.

To launch the full visual dashboard, simply run:
```bash
dwriter
```

### 🔍 Finding Your Notes

- **Fast Command:** `dwriter search "query"` lists matching notes directly in your terminal.
- **Interactive:** `dwriter ui --search` opens a live search window where you can filter as you type.

### 📋 Task Management

- **Fast Command:** `dwriter todo list` shows your tasks in a simple table. `dwriter todo add "task"` adds a task instantly.
- **Interactive:** `dwriter ui --todo` opens the visual task board for easy management with your keyboard.

### ⏱️ Focus Timer

- **Fast Command:** `dwriter timer 25` runs a simple countdown in your current terminal window.
- **Interactive:** `dwriter ui --timer` launches a large, full-screen timer that helps you stay "in the zone."

### 📊 Productivity Insights

- **Fast Command:** `dwriter stats` prints a quick summary of your streaks and work habits.
- **Interactive:** `dwriter ui` launches the full dashboard with activity maps and helpful suggestions.

> **Designed for Speed:** While the command-line is perfect for quick notes without leaving your work, the Visual Dashboard is your home base for planning and review.

---

## ❓ Troubleshooting

* **Command not found?** Ensure your virtual environment is active.
* **Clipboard issues?** On Linux, make sure you have `xclip` or `xsel` installed.
* **TUI not displaying correctly?** Ensure your terminal supports UTF-8 and has a minimum size of 80x24.
* **TUI appears garbled?** Try resizing your terminal window or using a different terminal emulator.
* **Keyboard input not working in TUI?** Make sure no terminal multiplexer (tmux/screen) is intercepting keys.

---

[🚀 Quick Start (Installation)](#-quick-start-installation)
