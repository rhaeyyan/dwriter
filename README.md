# dwriter 📝
v4.10.5
> **Looking for the AI features (2nd-Brain & Facts)?** Switch to the [dwriter-ai branch](https://github.com/rhaeyyan/dwriter/tree/dwriter-ai).
### *The minimalist journal for those who live in the terminal.*

**dwriter** is a high-signal, low-friction journaling tool designed to capture your work without breaking your flow. It bridges the gap between the raw speed of a command-line interface and the visual clarity of a modern dashboard.

Whether you are a software engineer tracking "deep work," a freelancer logging billable hours, or a student managing assignments, **dwriter** stays out of your way until you need it.


---

## ✨ Core Philosophy: Speed & Clarity

Modern productivity apps are often cluttered with distractions. **dwriter** is designed to prioritize your focus:

*   **⚡ Immediate Capture:** Use the "Headless CLI" to log thoughts, tasks, or focus sessions in seconds without leaving your terminal environment.
*   **📈 Weekly Pulse Analytics:** Behavioral analytics engine surfaces archetypes, golden hours, momentum deltas, and project spotlights from your rolling 7-day activity — powered by a LadybugDB graph index.
*   **🎨 Unified Dashboard:** Launch the Terminal User Interface (TUI) to reflect, search your history, or manage a visual todo board.
*   **📖 High-Signal Readability:** All logs feature **hanging indentation**, ensuring multi-line entries align perfectly for rapid scanning.
*   **🤖 Standup Automation:** Instantly transform your raw logs into formatted summaries for Slack, Jira, or Markdown.
*   **📝 Obsidian Integration:** Seamlessly export briefings and periodic reviews directly to your Obsidian vault as clean Markdown notes.
*   **📅 Natural Language:** Talk to your journal like a human. `dwriter add "Fixed the bug" --date "last Friday"` just works.
*   **🔍 Hybrid Search:** FTS and HNSW vector ANN results (`FLOAT[768]` embeddings) fused with Reciprocal Rank Fusion (RRF) for best-match retrieval across your entire history.
*   **🧠 Energy & Mood Tracking:** Log your energy level (1–10) and mood (Flow / Good / Meh / Low) directly from the quick-add and timer forms.

---

## 🚀 Quick Start

Getting started is as simple as a single command. We use **uv**, the fastest Python package manager, to keep your installation clean and isolated.

### 1. Install uv
If you haven't already, install the **uv** package manager:

*   **Linux / macOS:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
*   **Windows (PowerShell):**
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 2. Clone and Install dwriter
Clone the repository and install from the `main` branch.

```bash
git clone https://github.com/rhaeyyan/dwriter.git
cd dwriter
uv tool install .
```

> Looking for AI features (2nd-Brain, semantic tagging, LLM standup)? Switch to the **`dwriter-ai`** branch.

### 3. Keep dwriter Current
To pull the newest features (see **[Update Notes](documentation/update-notes.md)**), navigate to your local directory and run:

```bash
git pull origin main
uv tool install --upgrade .
```

---

## 🎮 How to Use dwriter

### 📊 The Visual Dashboard (TUI)
Launch the full dashboard:

```bash
dwriter
```

Navigate between screens using the tab bar:

- **✅ To-do Board:** Keyboard-driven task board with priorities and overdue detection.
- **⏱️ Focus Timer:** A full-screen countdown that auto-logs your progress with energy and mood capture on session complete.
- **🔍 Search/Edit:** Live-filtering fuzzy search across all your history with refined indentation.
- **📈 Weekly Pulse:** Behavioral analytics updated every 24 hours, powered by graph queries.

**Observability:** The TUI features a persistent **Status Bar** that displays your current active Git branch and real-time **Background Sync** monitoring (`[✅ Synced]`, `[🧠 Syncing...]`).

**dwriter** operates in two modes: the **Fast Command-Line** (for speed) and the **Visual Dashboard** (for depth).

### ✍️ The Fast Command-Line (Headless)
Capture your work the moment it happens. No switching windows, no distractions.

```bash
# Log a quick entry (Always use "quotes" for #tags or &projects)
dwriter add "Refactored the auth layer #backend &project-x"

# Start a 25-minute focus session with shorthand notation
dwriter timer "25 &feature-y #deepwork"

# Add a task to your todo list
dwriter todo add "Review the pull request" --priority urgent

# Machine-Readable Output (JSON) for automation
dwriter stats --json
dwriter today --json
```

### 🔍 Managing the Graph Index
dwriter maintains a LadybugDB graph index used for analytics and search. It updates automatically whenever you add an entry.

```bash
# Incrementally sync new entries into the graph (runs automatically, but can be forced)
dwriter graph rebuild

# Wipe and fully reconstruct the graph index from scratch
dwriter graph rebuild --full
```

---

## 💡 Mastering the Workflow

**dwriter** is designed to be your frictionless "brain-to-terminal" bridge. It adapts to your mental state, allowing you to capture everything from high-level project goals to fleeting creative sparks.

### 🏃 Frictionless Capture (The "Keys-Down" Loop)
- **Instant Entry:** `dwriter add "Idea: build a moisture sensor for the garden #someday"`
- **Workspace Awareness:** Inside a Git repo, `dwriter add` automatically appends branch and repository tags. Use a `.dwriter-ignore` file to disable this in specific projects.
- **Ghost Text Suggestions:** As you type in the TUI omnibox, token suggestions appear in dim "ghost text." Press `Tab` to selectively accept a `&project` or `#tag` token.
- **Zero Double-Entry:** Use `dwriter done <id>` to complete a task; it's automatically moved to your journal.
- **Auto-Sync:** Changes are automatically pulled on startup and pushed to your remote 10 seconds after your last edit.
- **Auto-Graph Sync:** Adding an entry (headless or TUI) automatically triggers an incremental graph index update in the background.

### 🎨 Creative Organization & Retrieval
- **Total Freedom:** Use `#tags` and `&projects` however you like (e.g., `#draft`, `&home:renovation`).
- **Fuzzy Search:** Don't worry about perfect spelling. Use `/` in the TUI or `dwriter search "query"`.
- **Hybrid Search:** The graph index fuses full-text and vector similarity results using Reciprocal Rank Fusion (RRF) for more precise retrieval.
- **Hierarchical Depth:** Use colons to organize complex structures like `&client:acme:q4-report`.

### 🧘 Deep Reflection (The Visual Dashboard)
- **The Dashboard:** Run `dwriter ui` to manage your todo board and activity map.
- **Visual History:** Revisit your work through a chronological log.
- **Easy Correction:** Use the interactive `dwriter edit` to quickly fix typos.
- **Energy & Mood:** Each entry can carry an energy level (1–10 slider) and a mood tag (🌊 Flow / 😊 Good / 😐 Meh / 😔 Low), recorded from quick-add and timer completion forms.

### 🔄 Multi-Device Synchronization
Keep your journal consistent across every machine you use. **dwriter** uses a Git-backed synchronization engine to ensure your data merges flawlessly without corruption.

```bash
# Connect to your private sync repository
dwriter sync --remote "https://github.com/user/my-journal-sync.git"

# Push or pull manually
dwriter sync --push
dwriter sync --pull
```

---

## 🛠️ Tech Stack

**dwriter** is built with a focus on local-first performance and modern terminal aesthetics.

- **Language:** Python 3.10+
- **UI Framework:** [Textual](https://textual.textualize.io/) (TUI) & [Rich](https://rich.readthedocs.io/) (CLI)
- **Primary Database:** SQLite (write-of-record)
- **Graph Index:** [LadybugDB](https://github.com/rhaeyyan/ladybug) ≥ 0.15.3 (KuzuDB-backed; FTS + HNSW vector search)
- **Search:** RapidFuzz (fuzzy CLI), FTS5 + HNSW vector ANN (Graph Index), RRF hybrid fusion
- **Tooling:** [uv](https://github.com/astral-sh/uv) (Package Management), Ruff (Linting), Mypy (Types), Pytest (Testing)

---

## 📖 Explore Further

| Document | Description |
| :--- | :--- |
| 📘 **[User Manual](documentation/user-manual.md)** | **The complete technical guide to every feature.** |
| 📓 **[Development History](documentation/development-history.md)** | **The agentic engineering journal, documenting the CLI to Textual TUI transition.** |
| 🚀 **[Update Notes](documentation/update-notes.md)** | **New in v4.10.5:** Vector projection & hybrid search. v4.10.4: Incremental graph index + auto-sync. v4.10.3: Energy/mood forms + timer fix. |
| 🛠️ **[Command Reference](documentation/HEADLESS-README.md)** | A complete guide to every CLI command and flag, including `dwriter graph rebuild`. |
| 📖 **[Creative Use Cases](documentation/USE_CASES.md)** | 20 ways to use dwriter for brewing, fitness, travel, and more. |
| ⚙️ **[Dev & Config Guide](documentation/DEV-and-CONFIG.md)** | Customizing your themes, default projects, and dev setup. CQRS architecture overview. |

---

## ❓ Troubleshooting & Tips

*   **Shell Characters:** Always wrap your entries in `"quotes"` if they contain `#tags` or `&projects`.
*   **Clipboard:** On Linux, install `xclip` or `xsel` to enable copy-to-clipboard.
*   **Customization:** Run `dwriter config edit` to tweak your default settings.
*   **Sync push error (`src refspec main does not match any`):** Fixed in v4.8.5 — just run `dwriter sync` again and it self-heals. On older versions, run `git -C ~/.dwriter/sync branch -m master main` once, then retry.
*   **Graph index out of date:** Run `dwriter graph rebuild` to incrementally sync, or `dwriter graph rebuild --full` to wipe and reconstruct from scratch. The index updates automatically on every `dwriter add`, but a manual rebuild is useful after bulk imports or sync pulls.

---
