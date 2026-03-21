"""Interactive help TUI using Textual with comprehensive command documentation."""

from __future__ import annotations

from typing import Any

import click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    MarkdownViewer,
    TabbedContent,
    TabPane,
)


def _get_cli_app() -> click.Group:
    """Get the main CLI app."""
    try:
        from ..cli import main as cli_app

        return cli_app
    except ImportError:
        import sys
        from pathlib import Path

        src_path = str(Path(__file__).parent.parent.parent)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from dwriter.cli import main as cli_app

        return cli_app


class HelpScreen(Screen[Any]):
    """The main interactive help browser screen."""

    BINDINGS = [
        Binding("q,escape", "close", "Close", show=True),
        Binding("t", "toggle_toc", "ToC", show=True),
        Binding("1", "switch_tab(0)", "1st", show=False),
        Binding("2", "switch_tab(1)", "2nd", show=False),
        Binding("3", "switch_tab(2)", "3rd", show=False),
        Binding("4", "switch_tab(3)", "4th", show=False),
        Binding("5", "switch_tab(4)", "5th", show=False),
        Binding("6", "switch_tab(5)", "6th", show=False),
        Binding("7", "switch_tab(6)", "7th", show=False),
        Binding("8", "switch_tab(7)", "8th", show=False),
        Binding("tab", "next_tab", "Next Tab", show=False),
    ]

    def action_close(self) -> None:
        """Close the help screen and return to the dashboard."""
        self.dismiss(True)

    # Command categories with their sub-tabs
    CATEGORY_CONFIG = [
        ("📝 Logging", "logging", ["add", "today"]),
        ("✅ Todos", "todos", ["todo", "done"]),
        ("📊 Reports", "reports", ["standup", "review", "stats"]),
        ("✏️ Editing", "editing", ["edit", "delete", "undo"]),
        ("🔍 Search", "search", ["search"]),
        ("⏱️ Timer", "timer", ["timer"]),
        ("⚙️ Config", "config", ["config"]),
        ("❓ Help", "help", ["help"]),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cli_app = _get_cli_app()
        self._loaded_subtabs: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="logging"):
            for label, tab_id, subtabs in self.CATEGORY_CONFIG:
                with TabPane(label, id=tab_id):
                    if len(subtabs) == 1:
                        yield MarkdownViewer(
                            id=f"{tab_id}-{subtabs[0]}-viewer",
                            show_table_of_contents=False,
                        )
                    else:
                        nested_id = f"{tab_id}-nested"
                        with TabbedContent(
                            initial=f"{tab_id}-{subtabs[0]}", id=nested_id
                        ):
                            for subtab_id in subtabs:
                                pane_id = f"{tab_id}-{subtab_id}"
                                display_name = subtab_id.replace("_", " ").title()
                                with TabPane(display_name, id=pane_id):
                                    yield MarkdownViewer(
                                        id=f"{pane_id}-viewer",
                                        show_table_of_contents=False,
                                    )
        yield Footer()

    def on_mount(self) -> None:
        """Load the first tab's content on mount."""
        self._load_subtab_content("logging", "add")

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        """Lazy-load markdown content when tab is activated."""
        if not event.pane.id:
            return

        # Determine if this is an outer tab (single word) or a sub-tab
        parts = event.pane.id.split("-")

        if len(parts) == 1:
            # Outer tab - load its first subtab
            category = event.pane.id
            for _label, tab_id, subtabs in self.CATEGORY_CONFIG:
                if tab_id == category and subtabs:
                    self._load_subtab_content(category, subtabs[0])
                    break
        elif len(parts) >= 2:
            # This is a sub-tab
            category = parts[0]
            subtab = "-".join(parts[1:])

            valid_categories = [
                "logging",
                "todos",
                "reports",
                "editing",
                "search",
                "timer",
                "config",
                "help",
            ]
            if category not in valid_categories:
                return

            self._load_subtab_content(category, subtab)

    def _load_subtab_content(self, category: str, subtab: str) -> None:
        """Load markdown content for a sub-tab if not already loaded."""
        subtab_id = f"{category}-{subtab}"
        if subtab_id in self._loaded_subtabs:
            return

        viewer = self.query_one(f"#{subtab_id}-viewer", MarkdownViewer)
        content = self._get_content(category, subtab)
        if content:
            viewer.document.update(content)
            self._loaded_subtabs.add(subtab_id)

    def _get_content(self, category: str, subtab: str) -> str:
        """Get markdown content for a category and sub-tab."""
        content_map = {
            "logging": {
                "add": self._get_add_content(),
                "today": self._get_today_content(),
            },
            "todos": {
                "todo": self._get_todo_content(),
                "done": self._get_done_content(),
            },
            "reports": {
                "standup": self._get_standup_content(),
                "review": self._get_review_content(),
                "stats": self._get_stats_content(),
            },
            "editing": {
                "edit": self._get_edit_content(),
                "delete": self._get_delete_content(),
                "undo": self._get_undo_content(),
            },
            "search": {
                "search": self._get_search_content(),
            },
            "timer": {
                "timer": self._get_timer_content(),
            },
            "config": {
                "config": self._get_config_content(),
            },
            "help": {
                "help": self._get_help_content(),
            },
        }
        return content_map.get(category, {}).get(subtab, "")

    def _get_add_content(self) -> str:
        return """# `dwriter add`

Log a new journal entry with tags and projects.

---

## Usage

```bash
dwriter add <content> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `-t, --tag <TAG>` | Add a tag (can be used multiple times) |
| `-p, --project <PROJECT>` | Assign to a project |
| `-d, --date <DATE>` | Log for a specific date (natural language supported) |

## Examples

### Basic logging
```bash
dwriter add "fixed the race condition in auth"
```

### With tags
```bash
dwriter add "fixed login bug" -t bug -t backend
```

### With project
```bash
dwriter add "implemented feature X" --project myapp
```

### Multiple tags and project
```bash
dwriter add "refactored database layer" -t refactor -t backend -p myapp
```

### With custom date
```bash
dwriter add "Finished report" --date yesterday
dwriter add "Meeting notes" --date "last Friday"
dwriter add "Completed sprint" --date "3 days ago"
```

## Supported Date Formats

| Format | Example | Description |
|--------|---------|-------------|
| Relative | `today`, `yesterday`, `tomorrow` | Common relative dates |
| Days ago | `3 days ago`, `5 days ago` | Specific days in past |
| Last weekday | `last Monday`, `last Friday` | Most recent weekday |
| Standard | `2024-01-15` | ISO format |
| US format | `01/15/2024` | Month/Day/Year |
| Named | `January 15, 2024` | Full date name |

## Tips

💡 **Quick logging**: Just run `dwriter add "your task"` for simple entries

💡 **Natural language dates**: Use `yesterday`, `last Monday`, `3 days ago`, etc.

💡 **Multiple tags**: Use `-t` multiple times: `-t bug -t backend -t urgent`

💡 **Omnibox shortcut**: In TUI, press `/` and type `#tag &project Your entry`
"""

    def _get_today_content(self) -> str:
        return """# `dwriter today`

Show today's journal entries.

---

## Usage

```bash
dwriter today
```

## Description

Displays all journal entries logged for the current day in chronological order.

## Examples

### View today's entries
```bash
dwriter today
```

## Tips

💡 **Quick view**: Shows entries with timestamps, tags, and projects

💡 **Empty output**: If no entries exist for today, the output will be empty

💡 **Alternative**: Run `dwriter` (no arguments) to see all entries

💡 **TUI view**: Use the Logs screen (press `2` in TUI) for interactive view
"""

    def _get_todo_content(self) -> str:
        return """# `dwriter todo`

Manage todo tasks interactively.

---

## Usage

```bash
dwriter todo [OPTIONS]
dwriter todo <content> [OPTIONS]
dwriter todo add <content> [OPTIONS]
dwriter todo list [OPTIONS]
dwriter todo rm <ID>
dwriter todo edit <ID>
```

## Options

| Option | Description |
|--------|-------------|
| `--priority <LEVEL>` | Set priority: `low`, `normal`, `high`, `urgent` |
| `--due <DATE>` | Set due date (e.g., `tomorrow`, `+5d`, `+1w`, `2024-01-15`) |
| `-t, --tag <TAG>` | Add a tag (can be used multiple times) |
| `-p, --project <PROJECT>` | Assign to a project |

## Due Date Formats

| Format | Example | Description |
|--------|---------|-------------|
| Relative | `tomorrow` | Tomorrow |
| Days shorthand | `+5d` | 5 days from now |
| Weeks shorthand | `+2w` | 2 weeks from now |
| Months shorthand | `+1m` | 1 month from now (approx. 30 days) |
| Explicit days | `3 days` | 3 days from now |
| Explicit weeks | `2 weeks` | 2 weeks from now |
| Weekday | `last Friday` | Most recent Friday |
| Standard date | `2024-01-15` | Specific date |

## Due Date Display

| Display | Meaning | Color |
|---------|---------|-------|
| `OVERDUE` | Past due | Red (appears FIRST!) |
| `TODAY` | Due today | Bold Orange |
| `TOMORROW` | Due tomorrow | Orange |
| `13d` | 13 days until due | Cyan |
| `2m` | 2 months until due | Dim Cyan |
| `–` | No due date set | Dim |

## Examples

### Launch interactive board
```bash
dwriter todo
```

### Add a new task (direct)
```bash
dwriter todo "write unit tests"
```

### Add task with due date
```bash
dwriter todo "write documentation" --due tomorrow
dwriter todo "review PR" --due +5d -t code
```

### With priority
```bash
dwriter todo "fix critical bug" --priority urgent
```

### With tags and project
```bash
dwriter todo "fix card draw bug" --priority urgent -t bug -p backend
```

### Using explicit `add` subcommand (recommended)
```bash
dwriter todo add "Complete report" -p Project -t writing --due +3d
dwriter todo add "Schedule meeting" --due tomorrow --priority high
```

### List tasks
```bash
dwriter todo list
dwriter todo list --all
dwriter todo list --tui
```

## Keybindings (Interactive TUI Mode)

| Key | Action |
|-----|--------|
| `a` | Add new task |
| `j/k` | Navigate down/up |
| `Space` | Mark task complete (auto-logs to journal) |
| `e` | Edit task (content, due date, tags, project) |
| `d` | Delete task |
| `+/-` | Change priority |
| `1/2/3` | Switch tabs (Pending/Completed/All) |
| `Tab` | Cycle tabs |
| `q/Esc` | Quit |

> **Note:** Tags and projects can be edited via the `e` (Edit) dialog using comma-separated input.

## Tips

💡 **Auto-logging**: Completed tasks automatically create journal entries

💡 **Priority colors**: 🔴 Urgent | 🟡 High | ⚪ Normal | ⚫ Low

💡 **Due dates**: Tasks show days until due (e.g., `13d`) or `TODAY`/`TOMORROW`

💡 **Smart sorting**: Tasks are sorted by:
  1. Priority (urgent → high → normal → low)
  2. Due date urgency (OVERDUE → TODAY → TOMORROW → other)
  3. Creation date (newest first)

💡 **Options first**: When using `dwriter todo` directly, put options before content:
```bash
dwriter todo --priority high -t feature "implement new API"
```

💡 **Use `todo add`**: For clarity, use the explicit subcommand:
```bash
dwriter todo add "implement new API" --priority high -t feature
```

💡 **Edit everything with `e`**: Press `e` to edit content, due date, tags, and project in one dialog
"""

    def _get_done_content(self) -> str:
        return """# `dwriter done`

Mark a task as complete.

---

## Usage

```bash
dwriter done <TASK_ID>
dwriter done <SEARCH_QUERY> --search
```

## Options

| Option | Description |
|--------|-------------|
| `--search` | Use fuzzy search to find the task |

## Examples

### Complete task by ID
```bash
dwriter done 5
```

### Complete task by searching
```bash
dwriter done "card draw bug" --search
```

## What Happens

When you mark a task as done:

1. ✅ Task is marked complete in the todo list
2. 📝 A journal entry is automatically created: `"Completed: <task content>"`
3. 🏷️ Tags and project are preserved in the journal entry

## Tips

💡 **Auto-logging**: This is the fastest way to log completed work

💡 **Fuzzy search**: Use `--search` when you don't remember the task ID

💡 **Standup ready**: Completed tasks appear in `dwriter standup` output

💡 **TUI shortcut**: In Todo Board, press `Space` or `Enter` to complete tasks
"""

    def _get_standup_content(self) -> str:
        return """# `dwriter standup`

Generate a standup summary from yesterday's entries.

---

## Usage

```bash
dwriter standup [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--format <FORMAT>` | Output format: `slack` (default), `jira`, `markdown`, `plain` |
| `--with-todos` | Include completed tasks in the summary |
| `--no-copy` | Don't copy to clipboard |

## Examples

### Generate standup (default Slack format)
```bash
dwriter standup
```

### Different formats
```bash
dwriter standup --format slack
dwriter standup --format jira
dwriter standup --format markdown
dwriter standup --format plain
```

### Include completed todos
```bash
dwriter standup --with-todos
```

### Don't copy to clipboard
```bash
dwriter standup --no-copy
```

## Output Formats

### Slack (default)
```
*Yesterday's Progress:*
• fixed the race condition in auth
• implemented feature X
• reviewed PR #123
```

### Markdown
```markdown
## Yesterday's Progress

- fixed the race condition in auth
- implemented feature X
- reviewed PR #123
```

### Jira
```
* Yesterday's Progress:
** fixed the race condition in auth
** implemented feature X
** reviewed PR #123
```

## Tips

💡 **Auto-copy**: Output is automatically copied to clipboard (use `--no-copy` to disable)

💡 **Yesterday only**: By default, shows entries from the previous day

💡 **Format once**: Generate in markdown for documentation, Slack for chat

💡 **Include todos**: Use `--with-todos` to include completed tasks in summary
"""

    def _get_review_content(self) -> str:
        return """# `dwriter review`

Generate a multi-day period review.

---

## Usage

```bash
dwriter review [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--days <N>` | Number of days to review (default: 5) |
| `--format <FORMAT>` | Output format: `markdown`, `plain`, `slack` |

## Examples

### Review last 5 days (default)
```bash
dwriter review
```

### Review last 7 days
```bash
dwriter review --days 7
```

### Review last 14 days
```bash
dwriter review --days 14
```

### Markdown format
```bash
dwriter review --format markdown
```

### Plain text format
```bash
dwriter review --format plain
```

## Output Structure

```
## Period Review (Last N Days)

### Summary
- Total entries: X
- Days active: Y/N
- Top projects: ...

### Entries by Day
[Day-by-day breakdown]

### Top Tags
[tag usage statistics]
```

## Tips

💡 **Weekly reviews**: Use `--days 7` for weekly retrospectives

💡 **Timesheet prep**: Great for generating weekly timesheets

💡 **Pattern spotting**: Review longer periods to spot work patterns

💡 **Sprint reports**: Use `--days 14` for bi-weekly sprint summaries
"""

    def _get_stats_content(self) -> str:
        return """# `dwriter stats`

Launch the interactive statistics dashboard.

---

## Usage

```bash
dwriter stats
```

## Dashboard Features

### Overview Tab
- **KPI Cards**: Total entries, current streak, longest streak, consistency %
- **Contribution Calendar**: GitHub-style activity heatmap (365 days)
- **Streak Tracking**: Current and longest logging streaks
- **30-Day Sparkline**: Braille character visualization of recent activity

### Activity Tab
- **Weekly Chart**: Bar chart showing entries per week (last 8 weeks)
- **Top Projects**: Table of most-used projects with counts
- **Top Tags**: Table of most-used tags with visual usage bars

## Keybindings

| Key | Action |
|-----|--------|
| `Tab` | Navigate between sections |
| `r` | Refresh data |
| `1/2` | Switch tabs (Overview / Activity) |
| `d` | Drill down into selected project/tag |
| `q/Esc` | Quit |

## Tips

💡 **Motivation**: Watch your streak grow to stay consistent

💡 **Insights**: Identify which projects/tags get the most attention

💡 **Consistency**: Aim for daily entries to build the habit

💡 **Visual feedback**: The calendar heatmap shows your activity at a glance
"""

    def _get_edit_content(self) -> str:
        return """# `dwriter edit`

Edit journal entries interactively.

---

## Usage

```bash
dwriter edit [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--id <ID>` | Edit a specific entry by ID |
| `--search <QUERY>` | Search and edit an entry |
| `--date <DATE>` | Edit entries from a specific date |

## Examples

### Launch interactive editor (today's entries)
```bash
dwriter edit
```

### Edit specific entry by ID
```bash
dwriter edit --id 42
```

### Search and edit
```bash
dwriter edit --search "redis cache"
```

### Edit entries from specific date
```bash
dwriter edit --date 2025-01-15
```

## Keybindings (Interactive Mode)

| Key | Action |
|-----|--------|
| `j/k` | Navigate down/up |
| `e/Enter` | Edit entry content |
| `t` | Edit tags (comma-separated) |
| `p` | Edit project name |
| `d` | Delete entry (with confirmation) |
| `r` | Refresh list |
| `q/Esc` | Quit |

## Tips

💡 **Today only**: Default view shows only today's entries

💡 **Quick delete**: Use `dwriter undo` to quickly delete the last entry

💡 **Bulk cleanup**: Use `dwriter delete --before <date>` for old entries

💡 **TUI alternative**: Use the Logs screen (press `2` in TUI) for interactive editing
"""

    def _get_delete_content(self) -> str:
        return """# `dwriter delete`

Bulk delete old journal entries.

---

## Usage

```bash
dwriter delete [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--before <DATE>` | Delete all entries before this date |
| `--force` | Skip confirmation prompt |

## Examples

### Delete entries older than a date
```bash
dwriter delete --before 2025-01-01
```

### Delete with confirmation
```bash
dwriter delete --before 2024-06-01 --force
```

## ⚠️ Warning

This action is **permanent** and cannot be undone. Always:

1. Review what will be deleted first
2. Consider exporting important entries
3. Use `--force` only when certain

## Tips

💡 **Yearly cleanup**: Run annually to remove old entries

💡 **Check first**: Run `dwriter` to review entries before deleting

💡 **Backup**: Consider backing up your database before bulk operations
"""

    def _get_undo_content(self) -> str:
        return """# `dwriter undo`

Quickly delete the most recent entry.

---

## Usage

```bash
dwriter undo
```

## Description

Instantly removes the last logged journal entry. This is a quick way to fix mistakes without going through the interactive editor.

## Examples

### Undo last entry
```bash
dwriter undo
```

## What Gets Deleted

The most recently created entry, regardless of:
- Date assigned
- Tags
- Project

## ⚠️ Warning

- **Single entry only**: Only deletes the very last entry
- **No confirmation**: Deletes immediately
- **Cannot be reversed**: Make sure this is what you want

## Tips

💡 **Quick fix**: Perfect for accidental double-entries

💡 **Mistake recovery**: Use right after realizing an error

💡 **Safer alternative**: Use `dwriter edit` for more control
"""

    def _get_search_content(self) -> str:
        return """# `dwriter search`

Fuzzy search through entries and todos.

---

## Usage

```bash
dwriter search [QUERY] [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `-p, --project <PROJECT>` | Filter by project |
| `-t, --tag <TAG>` | Filter by tag |
| `--type <TYPE>` | Search type: `all`, `entry`, `todo` |
| `-n, --limit <N>` | Limit number of results |

## Examples

### Launch interactive search
```bash
dwriter search
```

### Fuzzy search
```bash
dwriter search "auth bug"
```

### Filter by project
```bash
dwriter search "refactor" -p my_project
```

### Filter by tag
```bash
dwriter search "cache" -t backend
```

### Search only todos
```bash
dwriter search "cache" --type todo
```

### Limit results
```bash
dwriter search "meeting" -n 5
```

## Keybindings (Interactive Mode)

| Key | Action |
|-----|--------|
| `j/k` | Navigate down/up |
| `Enter` | Select item (copy content) |
| `/` | Focus search input |
| `Ctrl+N` | Toggle search type |
| `q/Esc` | Quit |

## Match Scores

- 🟢 **90%+**: Excellent match (success)
- 🟡 **75%+**: Good match (yellow)
- ⚪ **60%+**: Weak match (dim)

## Tips

💡 **Fuzzy matching**: Forgives typos and partial matches

💡 **Filter first**: Use `-p` and `-t` to narrow results before searching

💡 **Real-time**: Results update as you type in interactive mode

💡 **Copy to clipboard**: Press `Enter` on a result to copy its content
"""

    def _get_timer_content(self) -> str:
        return """# `dwriter timer`

Timer-style focus timer.

---

## Usage

```bash
dwriter timer [MINUTES] [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `-t, --tag <TAG>` | Add tags to the session log |
| `-p, --project <PROJECT>` | Assign session to a project |

## Examples

### Start default 25-minute timer
```bash
dwriter timer
```

### Custom duration
```bash
dwriter timer 30
dwriter timer 45
```

### With tags and project
```bash
dwriter timer 45 -t deepwork -p backend
```

## Keybindings (TUI Mode)

| Key | Action |
|-----|--------|
| `Space` | Pause/Resume timer |
| `+` | Add 5 minutes |
| `-` | Subtract 5 minutes |
| `Enter` | Finish session early |
| `q/Esc` | Quit (with confirmation) |

## What Happens on Completion

When the timer finishes:

1. ⏱️ Session completes
2. 📝 Journal entry is created: `"Completed X minute focus session"`
3. 🏷️ Tags and project are preserved

## Progress Bar Display

```
15:00  [ ▮▮▮▮▮🥭▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯ ]  40%
 ↑      ↑                    ↑    ↑
time   pips                 dim   percentage
       mango at 40%
```

## Tips

💡 **Timer technique**: Default 25 minutes follows the classic method

💡 **Auto-logging**: Completed sessions automatically log to your journal

💡 **Adjust on the fly**: Use `+` and `-` to extend or shorten sessions

💡 **Omnibox shortcut**: Type `#tag &project 15` in TUI to start a 15-minute timer
"""

    def _get_config_content(self) -> str:
        return """# `dwriter config`

View and manage configuration.

---

## Usage

```bash
dwriter config <COMMAND>
```

## Commands

| Command | Description |
|---------|-------------|
| `show` | Display current configuration |
| `edit` | Open config file in editor |
| `reset` | Reset to default values |
| `path` | Show config file location |

## Examples

### View current config
```bash
dwriter config show
```

### Edit configuration
```bash
dwriter config edit
```

### Reset to defaults
```bash
dwriter config reset
```

### Show config file path
```bash
dwriter config path
```

## Configuration File

Location: `~/.dwriter/config.toml`

### Example Configuration

```toml
[defaults]
project = "myapp"
tags = ["work"]

[display]
show_id = true
show_time = true

[standup]
format = "slack"
copy_to_clipboard = true
```

## Configuration Options

| Section | Option | Description | Default |
|---------|--------|-------------|---------|
| `[defaults]` | `project` | Default project for new entries | `null` |
| `[defaults]` | `tags` | Default tags for new entries | `[]` |
| `[standup]` | `format` | Default standup format | `"bullets"` |
| `[standup]` | `copy_to_clipboard` | Auto-copy standup to clipboard | `true` |
| `[review]` | `default_days` | Default number of days to review | `5` |
| `[review]` | `format` | Default review format | `"markdown"` |
| `[display]` | `show_id` | Show entry IDs in output | `true` |
| `[display]` | `show_time` | Show timestamps | `true` |
| `[display]` | `colors` | Enable colored output | `true` |

## Tips

💡 **Set defaults**: Configure default project and tags to speed up logging

💡 **Customize display**: Toggle ID and time display preferences

💡 **Format preferences**: Set your preferred standup output format
"""

    def _get_help_content(self) -> str:
        return """# `dwriter help`

Access interactive help and documentation.

---

## Usage

```bash
dwriter help [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--plain` | Show plain text help (for piping/grep) |

## Examples

### Launch interactive help browser
```bash
dwriter help
```

### Plain text help
```bash
dwriter help --plain
```

### Pipe to grep
```bash
dwriter help --plain | grep -i "tag"
```

## Interactive Features

### Navigation
- **Tabbed interface**: Browse by category (8 tabs)
- **Nested tabs**: Drill down to specific commands
- **Keyboard shortcuts**: Quick navigation with number keys

### Content
- **Command reference**: Full documentation for each command
- **Usage examples**: Practical examples for common tasks
- **Tips and tricks**: Helpful hints for efficient usage

## Keybindings

| Key | Action |
|-----|--------|
| `1-8` | Switch to category tab |
| `Tab` | Cycle through tabs |
| `t` | Toggle table of contents |
| `q/Esc` | Quit |

## Tips

💡 **Explore**: Browse all commands to discover features

💡 **Search**: Use `--plain` with grep to find specific topics

💡 **Quick reference**: Keep this handy when learning dwriter

💡 **In-app help**: Press `?` in any TUI screen for context-sensitive help
"""

    def action_switch_tab(self, index: int) -> None:
        """Switch to tab by index."""
        tabbed = self.query_one(TabbedContent)
        tabs = [
            "logging",
            "todos",
            "reports",
            "editing",
            "search",
            "timer",
            "config",
            "help",
        ]
        if 0 <= index < len(tabs):
            tabbed.active = tabs[index]

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = [
            "logging",
            "todos",
            "reports",
            "editing",
            "search",
            "timer",
            "config",
            "help",
        ]
        current_idx = tabs.index(tabbed.active)
        next_idx = (current_idx + 1) % len(tabs)
        tabbed.active = tabs[next_idx]

    def action_toggle_toc(self) -> None:
        """Toggle the Table of Contents sidebar."""
        tabbed = self.query_one(TabbedContent)
        active_category = tabbed.active

        # Find the first subtab for this category
        for _label, tab_id, subtabs in self.CATEGORY_CONFIG:
            if tab_id == active_category and subtabs:
                subtab_id = f"{active_category}-{subtabs[0]}"
                try:
                    viewer = self.query_one(f"#{subtab_id}-viewer", MarkdownViewer)
                    viewer.show_table_of_contents = not viewer.show_table_of_contents
                except Exception:
                    pass
                break


class HelpApp(App[bool]):
    """Standalone app for interactive help."""

    def on_mount(self) -> None:
        def on_dismiss(result: bool | None) -> None:
            self.exit(result or False)

        self.push_screen(HelpScreen(), on_dismiss)


if __name__ == "__main__":
    app = HelpApp()
    app.run()
