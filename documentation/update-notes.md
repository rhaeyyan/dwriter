# dwriter Update Notes

## main-core v1.0.0 - April 10, 2026

A new lightweight branch, `main-core`, has been created from `main` (v3.7.0). It provides all core dwriter features without any AI/LLM dependencies — ideal for users on constrained hardware or those who prefer a fully offline setup.

### ✨ What's New in main-core

#### 1. Cross-Device Sync (CRDT)
- **`dwriter sync --push`** / **`dwriter sync --pull`**: Synchronize your journal and todos across multiple machines using a Git remote as the transport. Lamport clock-based CRDT merge ensures conflict-free sync even when editing offline.
- **`dwriter sync --remote <url>`**: Configure the remote endpoint for sync.
- **`auto_sync = true`** in `[defaults]` config triggers an automatic background pull on TUI launch.

#### 2. Git Auto-Tagging
- **`git_auto_tag = true`** (default) in `[defaults]` config: When running `dwriter add` inside a Git repository, the repo name is applied as `&project` and the branch becomes a `#git-<branch>` tag automatically — keeping work context in your logs without extra typing.

#### 3. Notification Daemon (Linux)
- **`dwriter install-notifications`**: Installs systemd user units (`dwriter-remind.service` + `dwriter-remind.timer`) that run `dwriter --check-only` on a configurable interval (default 5 min). Desktop notifications via `notify-send` fire for urgent tasks due within 30 minutes.
  - `--interval N`: Check every N minutes (1–60).
  - `--dry-run`: Preview unit file content without writing anything.
- **`dwriter uninstall-notifications`**: Disables and removes the systemd units cleanly.
- macOS (launchd) and Windows (Task Scheduler) instructions shown automatically on non-Linux platforms.

#### 4. Machine-Readable JSON Output
- **`dwriter today --json`**: Emit today's entries as a JSON array — pipe into `jq`, scripts, or other tools.
- **`dwriter stats --json`**: Emit streak, activity counts, top tags, and behavioral insights as structured JSON.
- **`dwriter todo list --json`**: Emit the todo list as a JSON array.

#### 5. Enhanced TUI — Omnibox & Status Bar
- **Omnibox**: The quick-add input is now a custom `Omnibox` widget with ghost-text token suggestions. Tab accepts the next suggested `&project` or `#tag` token; any other key clears the suggestion.
- **Permanent Omnibox** (`permanent_omnibox = true` in `[display]`): Pin the omnibox open at all times instead of showing it only on focus.
- **Status Bar**: A slim bottom bar now shows the current git branch and sync status (Synced / Syncing... / Sync Failed).
- **In-app Reminder Toasts**: When `notifications_enabled = true`, the TUI surfaces urgent tasks due within 30 minutes as Textual toast notifications — no separate terminal window needed.

#### 6. Expanded Date Parsing
- **`next <weekday>`**: e.g., `dwriter todo "Meeting @due:next tuesday"`.
- **`+/-N[d|w|mo]`**: Relative shorthand including months (`mo`).
- Natural language error messages now clearly report what was invalid.

### 🔴 Intentionally Excluded (AI-only features)
The following features from `dwriter-ai` are **not** present in `main-core`:
- `dwriter ask` / 2nd-Brain chat screen
- `dwriter compress` / context compression
- Proactive semantic tagging (auto-tagging via LLM on `add`)
- `dwriter stats --narrative` (LLM-written insight prose)
- `embedding` / `implicit_mood` database fields

---

## Version 3.7.0 - April 6, 2026

### 🚀 Key Features

#### 1. 7-Day "Weekly Pulse" Wrap-up
- **Dynamic Metrics Engine**: Integrated advanced behavioral analytics into the core engine. Users are now categorized by **Archetypes** (e.g., "The Deep Diver", "The Closer") based on their rolling 7-day activity.
- **Peak Performance Visualization**: Automated identification of the user's **Golden Hour**, the time window of highest focus and task completion.
- **Momentum & Velocity**: Real-time tracking of task clearing rates compared to the previous week, providing a clear "Momentum Delta."
- **Project Spotlight**: Automated "Big Rock" detection that highlights which project consumed the majority of your bandwidth this week.

#### 2. Headless-First Weekly Summaries
- **`dwriter stats --weekly`**: A new high-signal terminal command that renders the Weekly Pulse wrap-up without launching the TUI.
- **`dwriter standup --weekly`**: Integrated weekly retrospective summaries into the standup generator, supporting multi-format export for Slack, Jira, and Markdown.

### 🛠 Improvements & Fixes
- **Dashboard Refinement**: Replaced the static "Two-Cents" insight box with the dynamic "7-Day Pulse" retrospective.
- **TUI Selector Hardening**: Implemented high-specificity CSS overrides for custom HUD elements to ensure visual consistency across different terminal themes.
- **Styling Harmonization**: Unified the "Quick Add" visual indicators across both the Logs and To-Do screens.

### ⚠️ Known Issues
- **Quick Add Vibrancy**: The `[+]` tab in the To-Do board may exhibit a slight color intensity mismatch compared to the Logs screen button in certain high-contrast themes due to internal Textual rendering logic.
