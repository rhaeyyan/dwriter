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
```

### Configuration Options:

| Section | Option | Description |
| :--- | :--- | :--- |
| `[defaults]` | `project` | The project name automatically applied to new entries. |
| `[standup]` | `format` | Your preferred layout for daily summaries. |
| `[review]` | `format` | The layout used for long-term reports. |
| `[display]` | `colors` | Toggle terminal color support. |

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
