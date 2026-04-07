# ⚙️ dwriter: Development & Configuration Guide

This guide covers how to customize **dwriter** to fit your personal workflow and how to contribute to the codebase.

---

## 🛠️ Configuration

Your settings are stored in `~/.dwriter/config.toml`. You can modify this file directly or use the built-in command:
```bash
dwriter config edit
```

### Example Configuration:
```toml
[defaults]
project = "core-engine"
tags = ["dev", "internal"]

[standup]
format = "slack"           # Options: bullets, slack, jira, markdown
copy_to_clipboard = true

[review]
default_days = 7
format = "markdown"

[display]
show_confirmation = true
colors = true
notifications_enabled = false  # Toggle desktop push notifications
```

### Configuration Options:

| Section | Option | Description |
| :--- | :--- | :--- |
| `[defaults]` | `project` | The project name automatically applied to new entries. |
| `[standup]` | `format` | Your preferred layout for daily summaries. |
| `[review]` | `format` | The layout used for long-term reports. |
| `[display]` | `colors` | Toggle terminal color support. |
| `[display]` | `notifications_enabled` | Opt-in to OS-level desktop push notifications for reminders. |

---

## 🧠 Configuring the AI Engine (Ollama)

The **2nd-Brain** and **Weekly Summary** features require a local or remote AI backend. We recommend using [Ollama](https://ollama.com/) for a private, high-speed local experience.

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com/).

### 2. Pull the Recommended Model
We recommend **Llama 3.1** for its strong reasoning and context handling:
```bash
ollama pull llama3.1
```

### 3. Update your dwriter config
Add an `[ai]` section to your `~/.dwriter/config.toml` (or use `dwriter config edit`):

```toml
[ai]
enabled = true
base_url = "http://localhost:11434/v1"  # Default Ollama API endpoint
model = "llama3.1"                      # Or your preferred model
```

---

## 🔔 Reminder System & Shell Integration

The **Reminder System** is "headless-first." It checks for urgent tasks whenever you run a `dwriter` command. For truly hands-off reminders, you can add a silent check to your shell configuration (e.g., `.zshrc` or `.bashrc`).

### 1. The `remind` command
Create a high-priority, time-sensitive task:
```bash
dwriter remind "Submit the report" --at "17:00"
```

### 2. Silent Shell Hook
Add this to your `.zshrc` or `.bashrc` to trigger a reminder check every time you open a terminal or run any command:
```bash
# dwriter silent reminder check
# Only runs if the binary exists, ensures zero impact on shell speed
if command -v dwriter >/dev/null 2>&1; then
    dwriter --check-only >/dev/null 2>&1 &
fi
```
> [!NOTE]
> The `--check-only` flag (implemented via the silent footer logic) ensures that `dwriter` performs its lookup and notification logic without printing any normal output, keeping your terminal clean.

---

## 💻 Developer Setup

**dwriter** is built with Python 3.9+ and follows strict type-safety and linting standards.

### Prerequisite: uv
We use [uv](https://github.com/astral-sh/uv) for all project management. It's significantly faster than standard `pip` and handles virtual environments automatically.

### 1. Clone & Sync
```bash
git clone https://github.com/rhaeyyan/dwriter.git
cd dwriter
uv sync --extra dev
```

### 2. Running the App (Dev Mode)
To run the app directly from the source without installing it:
```bash
uv run dwriter
```

### 3. Code Quality Tools
We maintain high standards using `ruff`, `mypy`, and `pytest`.

*   **Linting:** `uv run ruff check src/`
*   **Type Checking:** `uv run mypy src/`
*   **Testing:** `uv run pytest`

---

## 📊 Project Architecture

**dwriter** is designed with a **Headless-First** architecture:
- **Core Logic:** Decoupled from the UI to ensure the CLI remains fast and scriptable.
- **TUI Layer:** Built with the [Textual](https://textual.textualize.io/) framework for a rich, interactive experience.
- **Storage:** Uses SQLite for local-first, lightning-fast data persistence.

---

## 📄 License
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it as you see fit.

---

[⬅️ Back to README](../README.md)
