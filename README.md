# Day Writer (dwriter) ✍️

**Version 3.0.1**

A powerful, low-friction terminal journaling and task-tracking application built with Python, Textual, and SQLAlchemy. `dwriter` is designed for developers and power users who want an efficient keyboard-driven interface to manage their daily standups, productivity and break tracking timer sessions, and to-do lists without leaving the terminal.

---

## 🎯 Who is this for?

`dwriter` is for anyone who wants a quiet, distraction-free space to track their time, tasks, and daily progress. You don't need to be a software engineer to use it—you just need to value your focus.

We built this for people who are tired of bloated web apps and endless clicking:

*   **🎨 Freelancers & Creatives**: Writers, designers, and consultants who need to effortlessly log billable hours and pull a summary of what they actually worked on this week.
*   **📚 Students**: Run Pomodoro study sessions, manage assignment to-dos, and track exactly how much time you're dedicating to different subjects.
*   **✍️ Journalers & Reflectors**: Use the standup and review features to easily recall what you did yesterday, making evening journaling or habit tracking a breeze.
*   **🌱 Hobbyists & Makers**: Whether you're tracking the daily growth of your garden, building furniture, or learning a language, log your milestones in seconds without leaving your keyboard.

If you want a minimalist, beautiful productivity suite that gets out of your way, `dwriter` is for you.

---

## 🚀 Quick Installation

### Requirements
- Python 3.9+ (3.11+ recommended)
- Optional: `uv` (for faster package management)

### Setup

#### 1. Install `uv` (Recommended)
`uv` is an extremely fast Python package manager that handles environments automatically.

*   **Windows (PowerShell)**: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
*   **macOS / Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

#### 2. Clone and Enter
```bash
git clone https://github.com/yourusername/dwriter.git && cd dwriter
```

#### 3. Platform-Specific Installation

*   **Windows 11**:
    Open Terminal (PowerShell) and run:
    ```powershell
    uv venv && .\ .venv\Scripts\activate
    uv pip install -e ".[dev]"
    ```
*   **macOS / Linux (Debian/Mint)**:
    Open your terminal and run:
    ```bash
    # (Debian/Mint users: sudo apt install xclip if clipboard fails)
    uv venv && source .venv/bin/activate
    uv pip install -e ".[dev]"
    ```

---

## 🖥️ The Unified TUI: Interactive Experience

The `dwriter` TUI is a comprehensive command center for your daily workflow. It features a responsive, keyboard-optimized interface designed to minimize friction while providing deep insights into your productivity.

### Launching the App
Simply run this command to start the interactive TUI:
```bash
uv run dwriter
```

### 🧩 Core Components

1.  **🏠 Dashboard**: Your productivity nerve center.
    -   **KPI Cards**: Track current streaks, total logs, and task health at a glance.
    -   **Activity Sparklines**: Visualize your logging frequency over the past week.
    -   **Streak Calendar**: A heatmap-style calendar showing your consistency over the last 30 days.
2.  **📓 Logs Screen**: A chronological view of your daily entries. Browse your history, filter by date, or manage previous logs with ease.
3.  **📋 Todo Board**: A kanban-style task manager.
    -   **Multi-step Creation**: Adding a task via the Omnibox triggers a guided workflow for tags, project, priority, and due date.
    -   **Priority Highlighting**: Tasks are color-coded (Red for Urgent, Yellow for High, White for Normal, Dim for Low).
    -   **Smart Filtering**: Quickly see what's pending, overdue, or upcoming.
4.  **⏱️ Productivity & Break Timer**: Stay focused with integrated work and break cycles.
    -   **Session Logging**: Completed sessions are automatically logged with associated tags and projects.
    -   **Visual Feedback**: The navigation tab flashes when the timer is active.

### ⌨️ Navigation & Mastering the Omnibox

*   **Global Omnibox (`/`)**: The green bar at the top is the "Omnibox". Use it to log anything instantly without switching screens.
    -   *Journaling*: `Fixed the race condition #bug &auth`
    -   *Backdating*: `Wrote documentation 2024-03-10 #docs`
    -   *Timer*: `#dev &website 25` (Starts a 25-minute timer session)
*   **Command Palette (`Ctrl+P`)**: Search for any command or switch screens by name.
*   **Quick Switch (`1` - `4`)**: Jump between Dashboard, Logs, To-Do, and Timer instantly.
*   **Search (`Ctrl+S`)**: Fuzzy search through all your entries and tasks.

---

## ⌨️ Headless Mode: Power of the CLI

`dwriter` is fully functional from the command line, allowing you to integrate it into your scripts, aliases, or simply use it for quick "fire-and-forget" logging without launching the full interface.

### 🪵 Quick Logging
Log entries directly with tags and projects:
```bash
uv run dwriter add "Implemented user authentication" -t security -p myapp
uv run dwriter today  # List today's entries
```

### 📋 Task Management
Manage your todos without leaving your shell:
```bash
uv run dwriter todo add "Write unit tests" --priority high --due tomorrow
uv run dwriter todo list            # Show pending tasks in a formatted table
uv run dwriter done 42              # Mark task ID 42 as complete (logs it automatically!)
uv run dwriter done "fix bug" -s    # Fuzzy search for a task and mark as done
```

### 📊 Reports & Insights
Generate standup summaries or view stats instantly:
```bash
uv run dwriter standup --format slack --with-todos  # Copies a formatted summary to clipboard
uv run dwriter review --days 7                      # Review everything from the last week
uv run dwriter stats                                # View quick productivity metrics
```

### ⏱️ Timers
Start a timer session that logs to your database when finished:
```bash
uv run dwriter timer 25 -t deep-work -p project-x
```

---

## ⚙️ Configuration

`dwriter` creates a `config.toml` file on first run. You can customize themes, default tags, timer durations, and more.

*   **Linux/macOS**: `~/.config/dwriter/config.toml`
*   **Windows**: `%APPDATA%\dwriter\config.toml`

**Key Settings:**
- `theme`: `cyberpunk`, `dracula`, `catppuccin`, `nord`, `gruvbox`.
- `ergonomic_mode`: Adds extra padding and simplifies borders for a cleaner look.
- `standup`: Configure default formats and clipboard behavior.

---

## 🛠️ For Contributing Developers

### Project Architecture
- `src/dwriter/cli.py`: Entry point using Click for subcommands.
- `src/dwriter/tui/app.py`: Main Textual application logic.
- `src/dwriter/tui/screens/`: Individual TUI modules (Dashboard, Todo, Timer, etc.).
- `src/dwriter/database.py`: SQLAlchemy ORM and SQLite data management.

### Development Standards
We use **Ruff** for linting/formatting and **Mypy** for type safety.
```bash
pytest          # Run the test suite
ruff check .    # Check for linting errors
ruff format .   # Auto-format the codebase
mypy .          # Run static type checking
```

To contribute, please ensure your code passes all checks and includes relevant tests in the `tests/` directory.

---

## ❓ Troubleshooting

- **Terminal Size**: The TUI is optimized for **88x42** characters. If the UI looks cramped, try enlarging your terminal window. The app will attempt to auto-resize on supported terminals.
- **Database Location**: Data is stored in `~/.local/share/dwriter/` (Linux) or platform equivalents. If you experience database locks, ensure no other instance of `dwriter` is running.
- **Dependencies**: If `pyperclip` fails to copy to clipboard (common on Linux), ensure you have `xclip` or `xsel` installed: `sudo apt install xclip`.
- **Colors & Themes**: If colors look weird, ensure your terminal supports **True Color (24-bit)**. Set `export COLORTERM=truecolor` in your shell profile if necessary.

---

## 📜 License
This project is licensed under the MIT License.
