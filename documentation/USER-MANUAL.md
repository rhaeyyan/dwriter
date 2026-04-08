# 📘 dwriter: The Definitive Technical & User Manual (v4.2.0)

This manual provides a tiered guide to **dwriter**, covering everything from basic journaling to the underlying distributed state architecture. It is designed for both casual users seeking a clean workflow and developers looking to integrate or extend the system.

---

## 🚀 1. The Headless CLI (The "Speed" Layer)

For many, the CLI is the primary interface. It is optimized for zero-latency capture and scriptability.

### ✍️ Logging Entries (`add`)
The `add` command is the heartbeat of dwriter.
- **Basic Usage:** `dwriter add "Content"`
- **Metadata Shorthand:** Use `#tag` for categorization and `&project` for project grouping.
- **Natural Language Dates:** Uses a relative date parser (e.g., `yesterday`, `3 days ago`, `last Friday`).
- **Technical Detail:** Content is sanitized via regex before storage. Metadata is extracted into separate relational tables in the SQLite database to allow for high-speed indexing.

### ✅ Task Management (`todo`)
- **Frictionless Creation:** `dwriter todo "Task !high &api @due:friday"`
- **Priorities:** `!low`, `!normal`, `!high`, `!urgent`.
- **Completion Workflow:** `dwriter done <id>`.
- **Technical Detail:** When a task is marked `done`, a corresponding `Entry` is created with a foreign key relation to the `Todo` ID. This maintains a verifiable audit trail of completion.

### 🤖 Machine-Readable Output (`--json`)
Technical users can pipe dwriter data into other tools (e.g., BitBar, Waybar, or custom scripts).
```bash
dwriter today --json
```
**Schema Example:**
```json
[
  {"id": 101, "content": "Fixed bug", "project": "core", "tags": ["dev"], "created_at": "2026-04-08T12:00:00"}
]
```

---

## 🎨 2. The Unified Dashboard (The "Visual" Layer)

Run `dwriter` to launch the TUI. Built with the **Textual** framework, it provides an async-safe environment for data management.

### ⌨️ Universal Hotkeys
| Key | Action |
| :--- | :--- |
| `1-5` | Switch Screens: 2nd-Brain, Logs, To-Do, Timer, Settings. |
| `/` | Focus the **Omnibox** (Quick-Add) from anywhere. |
| `Ctrl+P` | Launch the **Command Palette** (Fuzzy-find actions). |
| `Ctrl+A` | Apply all pending AI suggestions. |

### 🧠 The 2nd-Brain & 7-Day Pulse
- **The Pulse:** A heavy analytics operation that runs once every 24 hours. It calculates your "Momentum" (task velocity) and identifies your "Big Rock" (the project taking most of your time).
- **Throttling Logic:** To preserve terminal performance, the full pulse is cached. Subsequent launches return a minimalist greeting until the next calendar day.

---

## ✨ 3. AI Intelligence (The "Cognitive" Layer)

dwriter uses local LLMs (via Ollama) to provide "Local RAG" (Retrieval-Augmented Generation).

### 🔍 How RAG Works
When you use `dwriter ask`, the system:
1.  **Vectorizes** your question.
2.  Performs a **Cosine Similarity** search against your SQLite entries.
3.  Injects the top 5 most relevant entries into the LLM's system prompt as "Context."
4.  Generates a response based *only* on your actual history.

### 👻 Omnibox Ghost Text
A real-time semantic analysis layer.
- **Trigger:** Typing > 3 words in the Omnibox.
- **Acceptance:** Press `Tab` to cycle through and accept individual tokens. This allows you to accept an AI-suggested project while ignoring a hallucinated tag.

---

## 🔄 4. Distributed State (The "Sync" Layer)

dwriter uses a **Local-First** approach with a Git-backed synchronization engine.

### 🛡️ CRDT & Conflict Resolution
To prevent data loss across multiple machines, we implement **Lamport Logical Clocks**:
- Every entry/todo has a `uuid` and a `lamport_clock` (integer).
- During `dwriter sync`, the engine compares clocks. The version with the **highest clock value** wins.
- **Atomic Writes:** Data is first serialized to `.jsonl` files using temporary swaps (`os.replace`) to ensure that a power failure during sync never corrupts your primary database.

### 🔀 Workspace Awareness
- **Auto-Tagging:** Detected via `git rev-parse --show-toplevel`.
- **`.dwriter-ignore`:** Technical users can add this to monorepos to prevent dwriter from polling Git metadata in specific subdirectories.

---

## ⚙️ 5. Advanced Configuration

### `config.toml` Schema
Stored in `~/.dwriter/config.toml`. Key sections:
- `[ai]`: Provider, model, and feature toggles.
- `[display]`: Themes, date formats, and UI preferences.
- `[defaults]`: Global project/tags and `auto_sync` toggles.

### 🛠 Troubleshooting
- **Logs:** Background sync and AI errors are logged to `~/.dwriter/logs/sync.log`.
- **Database:** The primary storage is a standard SQLite file at `~/.dwriter/entries.db`. You can query it directly using `sqlite3`.
- **Locking:** If the database is locked, dwriter will retry for 5 seconds before failing. This usually happens if a heavy background sync is in progress.

---

[⬅️ Back to README](../README.md) | [📦 GitHub Repository](https://github.com/rhaeyyan/dwriter)
