# dwriter 📝
### *The minimalist journal for those who live in the terminal.*

**dwriter** is a high-signal, low-friction journaling tool designed to capture your work without breaking your flow. It bridges the gap between the raw speed of a command-line interface and the visual clarity of a modern dashboard.

Whether you are a software engineer tracking "deep work," a freelancer logging billable hours, or a student managing assignments, **dwriter** stays out of your way until you need it.

---

## ✨ Core Philosophy: Speed & Clarity

Modern productivity apps are often cluttered with distractions. **dwriter** is designed to prioritize your focus:

*   **⚡ Immediate Capture:** Use the "Headless CLI" to log thoughts, tasks, or focus sessions in milliseconds without leaving your terminal environment.
*   **🎨 Unified Dashboard:** Launch the Terminal User Interface (TUI) to reflect, search your history, or manage a visual todo board.
*   **🤖 Standup Automation:** Instantly transform your raw logs into formatted summaries for Slack, Jira, or Markdown.
*   **📅 Natural Language:** Talk to your journal like a human. `dwriter add "Fixed the bug" --date "last Friday"` just works.

---

## 🚀 Quick Start

Getting started is as simple as a single command. We use **uv**, the fastest Python package manager, to keep your installation clean and isolated.

### 1. Install the tool (uv)
Choose your operating system and paste the command into your terminal:

*   **Linux / macOS:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
*   **Windows (PowerShell):**
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 2. Clone and Install dwriter
Clone the repository, navigate to the `dwriter` directory, and run:
```bash
git clone https://github.com/rhaeyyan/dwriter.git
cd dwriter
uv tool install .
```

---

## 🎮 How to Use dwriter

**dwriter** operates in two modes: the **Fast Command-Line** (for speed) and the **Visual Dashboard** (for depth).

### ✍️ The Fast Command-Line (Headless)
Capture your work the moment it happens. No switching windows, no distractions.

```bash
# Log a quick entry (use quotes if using #tags or &projects)
dwriter add "Refactored the auth layer #backend &project-x"

# Start a 25-minute focus session with a minimal progress bar
dwriter timer 25 -p feature-y

# Add a task to your todo list
dwriter todo "Review the pull request" --priority urgent
```

### 📊 The Visual Dashboard (TUI)
When you're ready for deep work or reflection, launch the full interactive environment:

```bash
dwriter
```

Inside the dashboard, you can:
- **✅ Manage Todos:** Keyboard-driven task board with priorities.
- **⏱️ Focus Timer:** A full-screen countdown that auto-logs your progress.
- **🔍 Deep Search:** Live-filtering fuzzy search across all your history.
- **📈 Activity Map:** Visualize your productivity streaks and habits.

---

## 📖 Explore Further

| Document | Description |
| :--- | :--- |
| 🛠️ **[Command Reference](documentation/HEADLESS-README.md)** | A complete guide to every CLI command and flag. |
| 📖 **[Creative Use Cases](documentation/USE_CASES.md)** | 20 ways to use dwriter for brewing, fitness, travel, and more. |
| ⚙️ **[Dev & Config Guide](documentation/DEV-and-CONFIG.md)** | Customizing your themes, default projects, and dev setup. |

---

## ❓ Troubleshooting & Tips

*   **Shell Characters:** Always wrap your entries in `"quotes"` if they contain `#tags` or `&projects` to prevent your shell from misinterpreting them.
*   **Clipboard:** On Linux, install `xclip` or `xsel` to enable the "copy-to-clipboard" feature for standup summaries.
*   **Customization:** Run `dwriter config edit` to tweak your default project or change your standup format to `slack` or `jira`.

---
