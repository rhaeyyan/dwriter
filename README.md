# Day Writer 📝

**Day Writer** is a low-friction terminal journaling tool designed for people who live in their command line. It helps you track daily tasks and automatically generate summaries for morning standups or weekly reviews.

[**⬇️ Jump to Commands Reference**](#-command-reference)

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
