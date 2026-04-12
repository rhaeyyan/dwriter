# 📘 dwriter: The Definitive Technical & User Manual (v4.4.0)

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

`todo` is a full command group. Tasks support priority levels (`low`, `normal`, `high`, `urgent`), due dates, tags, and project assignment.

**Creating tasks:**
```bash
dwriter todo "Write unit tests #testing &backend"   # inline quick-add
dwriter todo add "Fix card draw bug" #bug &core      # explicit subcommand
dwriter todo add "Review PR" --due tomorrow --priority high
dwriter todo add "Ship it" --due +5d -t release -p core
```

**Reviewing tasks:**
```bash
dwriter todo list            # pending tasks
dwriter todo list --all      # include completed
dwriter todo list --json     # machine-readable output
```

**Managing tasks:**
```bash
dwriter todo edit <id>       # edit content interactively
dwriter todo rm <id>         # delete a task
```

**Completing and reminders:**
```bash
dwriter done <id>                        # mark complete; auto-logs a journal entry
dwriter done "write tests" --search      # match by content instead of ID
dwriter remind "Call client" --at 3pm    # urgent shortcut with due time
dwriter snooze <id> --for 30m           # push due date forward
dwriter snooze <id> --at "tomorrow 9am"
```

**Technical Detail:** When a task is marked `done`, a corresponding `Entry` is created with a foreign key relation to the `Todo` ID, maintaining a verifiable audit trail of completion.

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
- **Modern Feedback:** During AI reasoning, a sleek **Modern Spinner** (Braille-style) provides non-intrusive feedback, ensuring you know the system is active during complex inference.
- **Throttling Logic:** To preserve terminal performance, the full pulse is cached. Subsequent launches return a minimalist greeting until the next calendar day.
- **Live Context:** The 2nd-Brain re-loads your latest entries and todos each time you open the screen, so entries logged during your session are immediately visible to the AI.
- **Agentic Tool Calls:** The AI has access to four tools it calls automatically based on your query: `search_journal` (past entries), `search_todos` (tasks), `get_daily_standup` (daily reports), and `fetch_recent_commits` (git history). You do not need to invoke these manually.

---

## ✨ 3. AI Intelligence (The "Cognitive" Layer)

dwriter uses local LLMs (via Ollama) and a governed **Analytical Engine** to provide deep insights while maintaining data integrity.

### 🛡️ Intelligence Governance ("Here to Assist" Framework)
All AI-driven insights and interactions are governed by a customizable `permission_mode` to ensure your data is handled according to your preferences. The **Permission Enforcer** gates AI tool execution based on these settings:

- **`read-only`**: AI can only query data and cannot make any changes.
- **`append-only`**: AI can query and create new logs/tasks (default).
- **`prompt`**: AI must ask for your permission before creating or modifying any data.
- **`danger-full-access`**: AI has full read/write/delete permissions.

### 🔍 How RAG Works
When you use `dwriter ask`, the system:
1.  **Vectorizes** your question.
2.  Performs a **Semantic Search** against your history.
3.  Injects the most relevant entries into the LLM's system prompt as "Context."
4.  Generates a response based *only* on your actual history.

### 📉 Context Optimization & Compression
To prevent "Context Bloat" and keep local LLMs performing at peak speeds, **dwriter** implements a **Deterministic Summary Compressor**:
- **Deduplication:** Duplicate status lines and redundant headers are stripped.
- **Priority Loading:** High-signal lines starting with `Summary:`, `- Scope:`, or `- ` (bullets) are prioritized.
- **Strict Budgets:** Context is capped at **4,000 characters** and **60 lines**, providing the model with rich historical signal while preventing context bloat on local hardware.


### 👻 Omnibox Ghost Text
A real-time semantic analysis layer.
- **Trigger:** Typing > 3 words in the Omnibox.
- **Acceptance:** Press `Tab` to cycle through and accept individual tokens. This allows you to accept an AI-suggested project while ignoring a suggested tag.

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

## 📝 5. Obsidian Export

dwriter integrates seamlessly with Obsidian by allowing you to export AI-generated reports and periodic reviews directly to your vault.

### ⚙️ Setup
1. Open your configuration file at `~/.dwriter/config.toml` (or use `dwriter config show` to find the path).
2. Set the `vault_path` under the `[obsidian]` section to the absolute path of your Obsidian vault:
   ```toml
   [obsidian]
   vault_path = "/Users/username/Documents/ObsidianVault"
   ai_reports_folder = "AI Reports"
   reviews_folder = "Reviews"
   ```

### 💻 CLI Export
You can export summaries directly from the command line using the `--obsidian` flag:
- **Daily Standup:** `dwriter standup --obsidian` (saves to the `AI Reports` folder, dated to yesterday)
- **Period Review:** `dwriter review --days 7 --obsidian` (saves to the `Reviews` folder)

### 🧠 2nd-Brain Export
When viewing AI briefings (Catch Up, Weekly Retro, Burnout Check) in the TUI's **Strategic Command Center**, click the **Save to Obsidian (o)** button to write the clean Markdown report directly to your vault.

### 🗂️ Note Types & Dataview
Exported notes use specific frontmatter schemas.
- **AI Reports** have `type: ai-report` and `report-kind` (e.g., standup, weekly-retro).
- **Reviews** have `type: period-review` with `period-start` and `period-end` dates.

**Dataview Example:**
```dataview
LIST FROM "AI Reports" WHERE type = "ai-report"
```

---

## ⚙️ 6. Advanced Configuration

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
