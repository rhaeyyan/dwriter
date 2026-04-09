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
git_auto_tag = true        # Automatically apply git branch/repo tags
auto_sync = true           # Enable background sync via Git

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
| `[defaults]` | `git_auto_tag` | Toggle automatic Git branch and repository tagging. |
| `[defaults]` | `auto_sync` | Enable/disable non-blocking background synchronization. |
| `[standup]` | `format` | Your preferred layout for daily summaries. |
| `[review]` | `format` | The layout used for long-term reports. |
| `[display]` | `colors` | Toggle terminal color support. |
| `[display]` | `notifications_enabled` | Opt-in to OS-level desktop push notifications for reminders. |
| `[display]` | `permanent_omnibox` | Whether to keep the omnibox visible at all times. |
| `[ai.features]` | `permission_mode` | AI security level (`read-only`, `append-only`, `prompt`, `danger-full-access`). |
| `[ai.features]` | `auto_tagging` | Toggle background AI semantic analysis for entries. |
| `[ai.features]` | `reflection_prompts` | Enable AI reflection prompts in the TUI. |
| `[ai.features]` | `burnout_detection` | Enable weekly burnout detection analytics. |

---

## 🛡️ AI Multi-Agent Framework

**dwriter** development and AI-driven insights are governed by a **Multi-Agent Framework**. This system ensures that every contribution and AI response adheres to the project's foundational architectural mandates.

### 👥 Personas
The framework uses 7 specialized personas to manage the project:
1.  **The TUI Architect:** Owns the `src/dwriter/tui/` domain.
2.  **Core Logic & CLI Engineer:** Owns the `src/dwriter/commands/` and headless utilities.
3.  **AI & RAG Specialist:** Owns the `src/dwriter/ai/` domain and prompt logic.
4.  **QA & Database Lead:** Owns the `src/dwriter/database.py` and codebase quality.
5.  **DevOps & Integrations Engineer:** Owns the `src/dwriter/sync/` and OS-level hooks.
6.  **Technical Auditor:** Owns documentation, `CHANGELOG.md`, and architectural review.
7.  **The Orchestrator:** Acts as the Tech Lead, routing user intent and enforcing guards.

### 🧱 Architectural Guards
The Orchestrator enforces strict, automated limits before any code is accepted:
*   **The UI Isolation Guard:** Prevents the TUI Architect from modifying database logic.
*   **The Stochastic Guard:** Mandates robust `try/except` fallbacks for all AI integrations.
*   **The Test-Driven Adaptation:** If tests fail, the team is automatically forced into a QA persona until the build is green.

---

## 🏗️ Workspace Awareness (`.dwriter-ignore`)

To prevent project-namespace pollution in massive monorepos or specific directories, you can drop a `.dwriter-ignore` file into your repository root.

**Example `.dwriter-ignore`:**
```ini
# Prevent dwriter from auto-tagging in this repo
disable_auto_tag=true
```

When this file is present and `disable_auto_tag=true` is set, `dwriter` will silently bypass the Git branch/repo injection for all entries logged within that workspace.

---

## 🧠 Configuring the AI Engine (Ollama)

The **2nd-Brain** and **Weekly Summary** features require a local or remote AI backend. We recommend using [Ollama](https://ollama.com/) for a private, high-speed local experience.

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com/).

### 2. Pull the Recommended Models
We recommend the **Gemma 4** family for the best balance of speed and reasoning:
```bash
ollama pull gemma4:e4b  # Main Brain (ReAct/Chat)
ollama pull gemma4:e2b  # Daemon (Background/Tagging)
```

### 3. Update your dwriter config
Add an `[ai]` section to your `~/.dwriter/config.toml` (or use `dwriter config edit`):

```toml
[ai]
enabled = true
base_url = "http://localhost:11434/v1"  # Default Ollama API endpoint
chat_model = "gemma4:e4b"               # 2nd-Brain ReAct loop
daemon_model = "gemma4:e2b"             # Background Auto-Tagging

[ai.features]
permission_mode = "append-only"         # Options: read-only, append-only, prompt, danger-full-access
auto_tagging = true
reflection_prompts = true
burnout_detection = true
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

[⬅️ Back to README](../README.md) | [📘 User Manual](./user-manual.md)
