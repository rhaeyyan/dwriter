Here is the revised `README.md`, updated to include comprehensive command lists while maintaining the specific bash formatting style used throughout the document.

# Day Writer 📝

**Day Writer** is a low-friction terminal journaling tool designed for people who live in their command line. It helps you track daily tasks and automatically generate summaries for morning standups or weekly reviews.

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

### Generation and Summaries

Create formatted reports for meetings or documentation.

| Command | Description |
| --- | --- |
| `dwriter standup` | Generate a summary of yesterday's tasks |
| `dwriter review` | Review entries from the last N days |
| `dwriter stats` | Show logging statistics and your current streak |

#### Examples:

```bash
dwriter standup --format slack

```

```bash
dwriter review --days 7 --format markdown

```

### Management and Configuration

Edit your history or customize how the tool behaves.

| Command | Description |
| --- | --- |
| `dwriter edit` | Interactively edit or delete today's entries |
| `dwriter delete --before DATE` | Bulk delete entries older than a specific date |
| `dwriter config show` | View your current settings |
| `dwriter config edit` | Open the configuration file in your editor |
| `dwriter examples` | Display comprehensive usage workflows |

---

## ⚙️ Configuration

Your settings are stored in `~/.day-writer/config.toml`. You can customize default projects, tags, and output formats here.

**Example Config:**

```toml
[defaults]
project = "core-engine"
tags = ["dev"]

[standup]
format = "slack"
copy_to_clipboard = true

```

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

---

## ❓ Troubleshooting

* **Command not found?** Ensure your virtual environment is active.
* **Clipboard issues?** On Linux, make sure you have `xclip` or `xsel` installed.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.