# 🧠 The 2nd-Brain: Strategic Command Center

The 2nd-Brain is dwriter's AI-powered mission control — a context-aware productivity coach that lives inside the TUI. It synthesizes your journal, tasks, and git history to provide high-density insights and automated retrospectives.

---

## The Strategic Command Center

When you open the 2nd-Brain screen in the TUI, you are presented with the **Strategic Command Center**. It is divided into three functional areas:

### 1. Insight Triggers (Deterministic Analytics)
The top row of buttons provides instant, data-driven reports generated directly from your local database. These are factual and update in real-time.

| Trigger | What It Shows |
|---|---|
| **Energy** | **Energy Radar**: Average energy levels across life domains (Work, Health, etc.). |
| **Momentum** | **Say-Do Ratio**: Tasks created vs. completed, and your **Velocity Delta** vs. last week. |
| **Golden Hour** | Your peak productivity window and an activity heatmap by day of the week. |
| **Stale** | **Stale Task Report**: Age breakdown of pending items and a list of the oldest tasks. |
| **Focus** | Top 6 most active tags, your **Big Rock** project, and context-switching frequency. |
| **Pulse** | **Weekly Snapshot**: A high-level collection of behavioral signals and your **Deep Work Ratio**. |

### 2. The Insights Hub
The central panel where all reports and AI briefings are rendered. It uses a high-density, readable format with color-coded projects (`&project`) and tags (`#tag`).

### 3. AI Briefing Buttons (Synthesis)
The bottom row triggers LLM-powered analysis that "thinks" about your data to provide qualitative feedback.

| Briefing | Purpose |
|---|---|
| **💬 Follow-up** | Opens a chat interface for freeform questions about your work, goals, or history. |
| **Weekly Retro** | Generates a deep-dive retrospective of your past 7 days, identifying wins and friction. |
| **Burnout Check** | Analyzes late-night sessions and energy logs to warn you if you're pushing too hard. |
| **Catch Up** | A flexible tool to summarize specific work. You can filter by **Project**, **Tags**, and **Date Range**. |

---

## How 2nd-Brain Actually Works

Beyond the UI, the AI uses a sophisticated multi-layered memory system to answer your questions.

### The Context Stack

Every AI query is answered using four layers of memory:

**Fact Memory (Durable Preferences)**
The AI maintains a list of extracted "Facts" — durable preferences, recurring goals, and persistent constraints (e.g., *"I prefer backend work in the morning"*, *"I am allergic to Java"*). These are automatically extracted via the **Closed Learning Loop**.

**Short-Term Memory (Past 72 Hours)**
Your 20 most recent journal entries and up to 10 pending tasks are always in view. This is the AI's immediate awareness.

**Long-Term Memory (Weekly Summaries)**
Up to 4 weeks of compressed weekly summaries are prepended to every query. They give the AI a sense of your trajectory over time, not just the last few days.

**Targeted Context (On-Demand)**
When your question mentions a project name (e.g. `&dwriter`) or a tag (e.g. `#deepwork`), the AI automatically fetches up to 15 historical entries for that specific anchor — even if they are months old.

### The Tool Layer

In **Follow-up** mode, the 2nd-Brain can actively search your data mid-conversation using tools:

**Graph-backed tools (recommended):**
- `search_facts`: Searches the **Fact Index** for durable user preferences and goals.
- `run_cypher`: Executes a Cypher query against the graph index for graph traversals and cross-entity aggregation (e.g. *"What projects co-occur with #friction?"*).
- `search_graph`: Full-text search over journal entries or todos using the graph index FTS engine.

**Legacy tools (retained for compatibility):**
- `search_journal`: Fuzzy search over past work and specific notes.
- `get_daily_standup`: Structured daily report for a given date.
- `search_todos`: Fuzzy search over tasks and overdue items.
- `fetch_recent_commits`: Recent code changes and git activity.

---

## Logging Habits That Make 2nd-Brain Smarter

The AI can only reason about what you've recorded. These habits produce a richer context and better answers.

### 1. Always Use `&project` and `#tag`
Project names and tags are the primary index the AI uses to retrieve targeted history.
```bash
# Strong — fully indexed, will be found in any query about the backend
dwriter add "Fixed null pointer in auth middleware #bugfix &backend"
```

### 2. Log at the Moment of Work
The AI uses timestamps to determine your **Golden Hour** and to reconstruct your day. Backdated batch logging at 5pm flattens your timeline and destroys the accuracy of your productivity heatmap.

### 3. Use the Timer for Deep Work
Entries created by the timer are automatically tagged as focused sessions. The analytics engine uses this to compute your **Deep Work Ratio**. If you don't use the timer, the AI assumes all work is "shallow."
```bash
dwriter timer "90 &dwriter #architecture"
```

### 4. Log Energy and Domain
The `add` command accepts `--energy` (1–10) and `--domain` flags. These feed the **Energy Radar** and **Burnout Check**.
```bash
dwriter add "Wrote the proposal draft &client-x" --energy 8 --domain work
```

---

## Effective AI Querying

### Use the "Catch Up" Briefing for Specifics
Instead of a broad query, use the **Catch Up** button to target exactly what you need:
- *"What did I do for &backend between last Tuesday and Friday?"*
- *"Summarize everything tagged #design from the last month."*

### Ask for Pattern Analysis in Follow-up
The AI is most valuable when you ask it to compare, explain, or advise.
- *"Why do I keep missing deadlines on the backend project?"*
- *"What's been draining my energy this week?"*
- *"What should I focus on today based on my backlog?"*

---

## Configuration Tips

### Tune AI Permission Mode
The `permission_mode` setting controls how much the AI can modify your data.
```toml
[ai.features]
permission_mode = "read-only"   # Options: read-only, append-only, prompt, danger-full-access
```

| Mode | Capability |
|---|---|
| `read-only` | Search and summarize only — no writes. |
| `append-only` | Can add entries/tasks, cannot delete or modify. |
| `prompt` | Asks for confirmation before any write. |
| `danger-full-access` | Full read/write/delete access. |

---

[⬅️ Back to README](../README.md)
