# 🧠 Getting the Most Out of 2nd-Brain

The 2nd-Brain is dwriter's AI assistant — a context-aware productivity coach that lives inside the TUI. It reads your journal, tasks, and git history to answer questions, surface patterns, and help you plan. This guide explains how it works under the hood, and what habits make it dramatically more useful.

---

## How 2nd-Brain Actually Works

Before optimizing your workflow, it helps to understand what the AI actually sees when you ask it a question.

### The Context Stack

Every query is answered using two layers of memory:

**Short-Term Memory (Past 72 Hours)**
Your 20 most recent journal entries and up to 10 pending tasks are always in view. This is the AI's immediate awareness — what you've been doing lately, what's still on your plate.

**Long-Term Memory (Weekly Summaries)**
Up to 4 weeks of compressed weekly summaries are prepended to every query. These summaries capture dominant mood, velocity, key projects, and biggest wins from each past week. They give the AI a sense of your trajectory over time, not just the last three days.

**Targeted Context (On-Demand)**
When your question mentions a project name (e.g. `dwriter`, `&backend`) or a tag (e.g. `deepwork`, `#docs`), the AI automatically fetches up to 15 historical entries for that project or tag — even if they're older than 72 hours. You don't have to do anything; just mention the name naturally in your query.

### The Tool Layer

Beyond static context, 2nd-Brain can actively search your data mid-conversation using four tools:

| Tool | Triggered When You Ask About |
|---|---|
| `search_journal` | Past work, specific notes, time spent on something |
| `get_daily_standup` | What you did yesterday, daily reports, structured summaries |
| `search_todos` | Specific tasks, what's pending, overdue items |
| `fetch_recent_commits` | Recent code changes, what was shipped, git activity |

The AI decides when to call these tools on its own. You don't invoke them explicitly — just ask in natural language.

---

## Logging Habits That Make 2nd-Brain Smarter

The AI can only reason about what you've recorded. These habits produce a richer context and better answers.

### 1. Always Use `&project` and `#tag`

Project names and tags are the primary index the AI uses to retrieve targeted history. An untagged entry is nearly invisible to queries about a specific area of work.

```bash
# Weak — too vague, won't surface in project-specific queries
dwriter add "Fixed a bug"

# Strong — fully indexed, will be found in any query about the backend
dwriter add "Fixed null pointer in auth middleware #bugfix &backend"
```

Be **consistent** with naming. `&backend`, `&back-end`, and `&backend-api` are three separate projects. Pick a convention and stick to it.

### 2. Log at the Moment of Completion, Not the End of the Day

The AI uses timestamps to determine your Golden Hour (peak focus time) and to reconstruct your day for standups. Backdated batch logging at 5pm flattens your timeline and skews all time-based analytics.

```bash
# Log when it actually happened — this is what feeds Golden Hour detection
dwriter add "Merged the auth PR after review #dev &backend"
```

### 3. Use the Timer for Deep Work

Entries created by the timer are automatically prefixed with `⏱️`. The analytics engine uses this prefix to compute your **Deep Work Ratio** — the fraction of your time spent in focused sessions vs. shallow tasks. If you do deep work but never use the timer, the AI has no way to know.

```bash
# A 90-minute deep work block, fully tracked
dwriter timer "90 &dwriter #architecture"
```

### 4. Log Energy and Life Domain When It Matters

The `add` command accepts `--energy` (1–5) and `--domain` flags. These feed the domain/energy distribution analytics, which the AI can use to identify where you're burning out or where you're thriving.

```bash
dwriter add "Wrote the proposal draft &client-x" --energy 4 --domain work
dwriter add "Evening run" --energy 5 --domain health
```

### 5. Write Todos Before You Start, Not After

The **Say-Do Ratio** measures how many tasks you create vs. complete in a week. If you only add tasks once they're already done (to check them off), the ratio is always 100% and the insight is meaningless. Add tasks when you *plan* to do them.

```bash
# Add it when you plan it — gives the AI a before/after signal
dwriter todo "Refactor database layer" --priority high --due friday &backend
```

### 6. Mark Tasks Done Promptly

The **Velocity Delta** compares this week's task completions to last week's. Delayed `done` calls distort which week gets credit for the work.

```bash
dwriter done <id>   # Do this when the task is actually finished
```

---

## Querying the AI Effectively

### Be Specific About Time

The AI's static context only covers 72 hours. For anything older, it needs to use `search_journal` — and it does so more reliably when you give it a time anchor.

```bash
# Vague — may only return recent results
"What did I work on for the backend?"

# Clear — tells the AI to reach into historical data
"What did I work on for the backend last month?"
"Summarize my &backend work from the past 3 weeks"
```

### Mention Projects and Tags by Name

Because targeted context retrieval is triggered by project and tag names, mentioning them explicitly in your query pulls their full history into the AI's context window — even if those entries are weeks old.

```bash
# Pulls targeted history for &dwriter automatically
"How much progress have I made on dwriter this month?"

# Pulls targeted history for #deepwork
"When was the last time I had a real deepwork session?"
```

### Use Standup Queries for Structured Summaries

The `get_daily_standup` tool produces a formatted, structured report. These queries trigger it reliably:

```bash
"Give me my standup for yesterday"
"What did I accomplish on 2026-04-08?"
"Generate a daily report for last Thursday"
"What was I working on two days ago?"
```

You can also just run `dwriter standup` from the CLI for the same output without opening the TUI.

### Ask for Pattern Analysis, Not Just Facts

The AI is most valuable when you use it for reflection, not just retrieval. Questions that ask it to compare, explain, or advise draw on the full analytics context.

```bash
# Factual (useful but limited)
"List my pending tasks"

# Analytical (draws on archetype, velocity, insights)
"Why do I keep missing deadlines on the backend project?"
"What's been draining my energy this week?"
"Am I spending too much time on admin tasks?"
"What should I focus on today based on my backlog?"
```

### Ask About Git Activity

If you're working inside a git repository, the AI can pull recent commit history on demand.

```bash
"What did I ship this week?"
"Summarize my recent commits for the standup"
"What was the last thing I merged?"
```

---

## Understanding the Analytics

### Daily Insights (`dwriter stats`)

These insights fire automatically based on thresholds measured over the last 7–45 days:

| Insight | What It Measures | What Triggers It |
|---|---|---|
| **Burnout Warning** | After-hours session percentage (45-day window) | >70% of sessions extending past normal hours |
| **Watch Your Pace** | Same metric, lower severity | >40% after-hours rate |
| **Great Follow-through** | Say-Do Ratio (7 days) | Completed ≥80% of created tasks |
| **Backlog Alert** | Say-Do Ratio (7 days) | Completed <40% of created tasks |
| **Context Switcher** | Average projects touched per day (7 days) | Switching >4 projects/day |
| **Project Friction** | Entry count vs. task completions per project (45 days) | >3:1 journal entries to completions with >5 entries |
| **Staleness Alert** | Tasks not touched in >14 days | >30% of pending tasks are stale |
| **Focus Time Needed** | Deep Work Ratio (7 days) | <20% of entries from timer sessions |
| **High Focus** | Same metric, positive trigger | >50% of entries from timer sessions |
| **Active Focus** | Tag velocity (45 days) | Always shown — displays your top 3 most active tags |

**Practical implication**: if you want Burnout Warning to fire accurately, log consistently at the time you actually work. If you batch-log in the morning for yesterday, every entry looks like it was created at 9am regardless of when the work happened.

### Weekly Pulse (`dwriter stats --weekly`)

The Weekly Pulse fires four specific metrics:

**Archetype** — Your productivity persona for the week, determined by behavioral signals:

| Archetype | How You Earn It |
|---|---|
| The Deep Diver | >40% of entries came from timer sessions |
| The Closer | Completed more tasks than you created, and closed ≥3 |
| The Archivist | 3x more journal entries than tasks, with ≥10 entries total |
| The Firefighter | >50% of completions were high or urgent priority |
| The Steady Builder | Default — solid, consistent work without a dominant pattern |

**Golden Hour** — The hour of day with the highest combined entry + task creation activity over 7 days. Accurate only if you log at the moment of work.

**The Big Rock** — The project that claimed the largest share of your logged entries (requires `&project` tagging — untagged entries don't count).

**Momentum** — Percentage change in task completions vs. the previous week. Positive means you cleared more tasks this week than last.

### AI Narrative (`dwriter stats --narrative`)

Generates a Spotify Wrapped-style prose summary using the same underlying metrics, written by the AI in natural language. Good for sharing with a manager or including in a weekly review doc.

---

## Configuration Tips

### Enable Auto-Tagging

With `git_auto_tag = true` (default), every `dwriter add` inside a git repo automatically applies the repo name as `&project` and the branch as `#git-<branch>`. This means your journal entries are project-indexed with zero extra effort when working in code.

```toml
[defaults]
git_auto_tag = true
```

### Set a Default Project

If most of your work lives in one project, set a default so you don't have to type `&project` every time:

```toml
[defaults]
project = "dwriter"
tags = ["dev"]
```

Default tags and project are applied to every entry, including TUI omnibox submissions. They stack with any tags you add inline.

### Tune AI Permission Mode

The `permission_mode` setting controls how aggressively the AI can act on tool calls. If you're just using 2nd-Brain for read-only analysis, `read-only` is the safest option.

```toml
[ai]
[ai.features]
permission_mode = "read-only"   # Options: read-only, append-only, prompt, danger-full-access
```

| Mode | What the AI Can Do |
|---|---|
| `read-only` | Search and summarize only — no writes |
| `append-only` | Can add entries/tasks, cannot delete or modify |
| `prompt` | Asks for confirmation before any write |
| `danger-full-access` | Full read/write/delete access |

### Keep the Weekly Summary Running

Weekly summaries are the backbone of the AI's long-term memory. They're generated automatically in the background, but only when you have enough data. If you journal infrequently (fewer than 3–4 entries/week), summaries may be sparse or missing, and the AI's long-term context will be thin.

---

## Quick Reference: Best Queries for Common Goals

| Goal | Query |
|---|---|
| Morning plan | `"What's my priority list for today based on what's pending?"` |
| End-of-day review | `"Summarize what I got done today"` |
| Standup prep | `"Give me my standup for yesterday"` |
| Project deep-dive | `"How is the &backend project tracking this week?"` |
| Burnout check | `"Am I overworking based on my recent logs?"` |
| Focus advice | `"What should I work on first today?"` |
| Week retrospective | `"What was my biggest win this week?"` |
| Git summary | `"What did I ship this week?"` |
| Backlog triage | `"What tasks have I been ignoring the longest?"` |
| Energy pattern | `"When am I most productive during the day?"` |

---

[⬅️ Back to README](../README.md)
