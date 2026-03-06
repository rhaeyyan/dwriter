"""Examples command showing usage examples and workflows."""

import click

from ..cli import AppContext

EXAMPLES_TEXT = """
dwriter - Usage Examples
═══════════════════════════════════════════════════════════════

1. LOGGING TASKS
───────────────────────────────────────────────────────────────

  # Basic logging
  $ dwriter add "fixed the race condition in auth"

  # With tags
  $ dwriter add "fixed login bug" -t bug -t backend

  # With project
  $ dwriter add "implemented feature X" --project myapp

  # Multiple tags and project
  $ dwriter add "refactored database layer" -t refactor -t backend -p myapp

  # With custom date
  $ dwriter add "Finished report" --date yesterday
  $ dwriter add "Meeting notes" --date "last Friday"
  $ dwriter add "Completed sprint" --date "3 days ago"


2. VIEWING ENTRIES
───────────────────────────────────────────────────────────────

  # Show today's entries
  $ dwriter today

  # Show all entries (default when running dwriter without arguments)
  $ dwriter


3. STANDUP GENERATION
───────────────────────────────────────────────────────────────

  # Generate yesterday's standup (copies to clipboard)
  $ dwriter standup

  # Different formats
  $ dwriter standup --format slack
  $ dwriter standup --format jira
  $ dwriter standup --format markdown

  # Don't copy to clipboard
  $ dwriter standup --no-copy

  # Include pending tasks
  $ dwriter standup --with-todos


4. PERIODIC REVIEWS
───────────────────────────────────────────────────────────────

  # Review last 5 days (default)
  $ dwriter review

  # Review last 7 days
  $ dwriter review --days 7

  # Different output formats
  $ dwriter review --format markdown
  $ dwriter review --format plain
  $ dwriter review --format slack


5. EDITING ENTRIES
───────────────────────────────────────────────────────────────

  # Interactive edit TUI (today's entries)
  $ dwriter edit

  # Edit specific entry by ID
  $ dwriter edit --id 42

  # Search and edit entry
  $ dwriter edit --search "redis cache"

  # Undo last entry
  $ dwriter undo

  # Bulk delete old entries
  $ dwriter delete --before 2025-01-01


6. STATISTICS & DASHBOARD
───────────────────────────────────────────────────────────────

  # Launch interactive dashboard with:
  # - GitHub-style contribution calendar
  # - Weekly activity chart
  # - Statistics summary
  # - Top tags
  $ dwriter stats


7. CONFIGURATION
───────────────────────────────────────────────────────────────

  # View current config
  $ dwriter config show

  # Edit config file
  $ dwriter config edit

  # Reset to defaults
  $ dwriter config reset

  # Show configuration file path
  $ dwriter config path


8. TODO MANAGEMENT
───────────────────────────────────────────────────────────────

  # Launch interactive todo board
  $ dwriter todo

  # Add a new task
  $ dwriter todo "Draft new relic ideas"

  # Add task with project
  $ dwriter todo "Fix card draw bug" -p my_project

  # Add task with priority and tags
  $ dwriter todo "Fix card draw bug" --priority urgent -t bug

  # Options can come before content too
  $ dwriter todo --priority urgent -t bug "Fix card draw bug"

  # List pending tasks (static table)
  $ dwriter todo list

  # List all tasks including completed
  $ dwriter todo list --all

  # Launch interactive todo TUI
  $ dwriter todo list --tui

  # Mark a task as done (auto-logs to journal)
  $ dwriter done 5

  # Mark task done using fuzzy search
  $ dwriter done "card draw bug" --search

  # Delete a task
  $ dwriter todo rm 3

  # Edit a task
  $ dwriter todo edit 2


9. TIMER (POMODORO-STYLE)
───────────────────────────────────────────────────────────────

  # Start default 25-minute timer
  $ dwriter timer

  # Custom duration
  $ dwriter timer 30
  $ dwriter timer 45

  # With tags and project
  $ dwriter timer 45 -t deepwork -p backend


10. SEARCH
───────────────────────────────────────────────────────────────

  # Launch interactive search TUI
  $ dwriter search

  # Fuzzy search entries and todos
  $ dwriter search "auth bug"

  # Filter by project
  $ dwriter search "refactor" -p my_project

  # Filter by tags
  $ dwriter search "cache" -t backend

  # Search only todos
  $ dwriter search "cache" --type todo

  # Limit results
  $ dwriter search "meeting" -n 5


INTERACTIVE TUI MODES
═══════════════════════════════════════════════════════════════

🔍 Interactive Search (dwriter search)
───────────────────────────────────────────────────────────────
  Launch: dwriter search

  Keybindings:
    j/k       Navigate down/up
    Enter     Select item (copy content)
    /         Focus search input
    Ctrl+N    Toggle search type (All/Entries/Todos)
    q/Esc     Quit

  Features:
    - Real-time fuzzy filtering
    - Color-coded match scores (🟢90%+ 🟡75%+ ⚪60%+)
    - Consistent tag/project colors


📋 Interactive Todo Board (dwriter todo)
───────────────────────────────────────────────────────────────
  Launch: dwriter todo

  Keybindings:
    j/k       Navigate down/up
    Space     Mark task complete (auto-logs)
    e         Edit task content
    d         Delete task
    +/-       Increase/decrease priority
    t         Edit tags
    p         Edit project
    r         Refresh
    q/Esc     Quit

  Priority Colors:
    🔴 URGENT  🟡 HIGH  ⚪ NORMAL  ⚫ LOW


✏️ Edit Entries (dwriter edit)
───────────────────────────────────────────────────────────────
  Launch: dwriter edit

  Keybindings:
    j/k       Navigate down/up
    e/Enter   Edit entry content
    t         Edit tags
    p         Edit project
    d         Delete entry
    r         Refresh
    q/Esc     Quit


⏱️ Timer (dwriter timer)
───────────────────────────────────────────────────────────────
  Launch: dwriter timer [MINUTES]

  Keybindings:
    Space     Pause/Resume
    +         Add 5 minutes
    -         Subtract 5 minutes
    Enter     Finish early
    q/Esc     Quit

  Features:
    - Large countdown display
    - Progress bar
    - Auto-prompt to log on completion


📊 Dashboard (dwriter stats)
───────────────────────────────────────────────────────────────
  Launch: dwriter stats

  Features:
    - GitHub-style contribution calendar
    - Current/longest streak tracking
    - Weekly activity bar chart
    - Statistics summary
    - Top 10 tags with usage bars

  Keybindings:
    Tab       Navigate sections
    r         Refresh
    q/Esc     Quit


WORKFLOWS
═══════════════════════════════════════════════════════════════

Morning Standup Workflow
───────────────────────────────────────────────────────────────

  # Throughout the day, log your tasks
  $ dwriter add "reviewed PR #123"
  $ dwriter add "fixed memory leak in cache module" -t bug
  $ dwriter add "deployed to staging" -p backend

  # Next morning, generate standup
  $ dwriter standup
  # Output is copied to clipboard, ready to paste in Slack


Task-to-Journal Workflow
───────────────────────────────────────────────────────────────

  # Add tasks for the day
  $ dwriter todo "Review pull requests" --priority high
  $ dwriter todo "Write unit tests" -p backend

  # List your tasks
  $ dwriter todo list

  # Complete a task (auto-logs to journal)
  $ dwriter done 1
  # Creates journal entry: "Completed: Review pull requests"

  # Generate standup with todos included
  $ dwriter standup --with-todos


Weekly Timesheet Workflow
───────────────────────────────────────────────────────────────

  # Generate weekly summary
  $ dwriter review --days 7 --format markdown


Set Default Project Workflow
───────────────────────────────────────────────────────────────

  # Edit config to set default project
  $ dwriter config edit

  # Add to config file:
  # [defaults]
  # project = "myapp"
  # tags = ["work"]

  # Now all entries will use these defaults
  $ dwriter add "fixed bug"
  # Automatically tagged with project "myapp" and tag "work"


Timer Session Workflow
───────────────────────────────────────────────────────────────

  # Start a timer session
  $ dwriter timer

  # Or custom duration with tags
  $ dwriter timer 45 -t deepwork -p backend

  # Session auto-logs when complete


Interactive Search Workflow
───────────────────────────────────────────────────────────────

  # Launch TUI for browsing
  $ dwriter search

  # Or quick CLI search
  $ dwriter search "auth module" -p backend -t bug
"""


@click.command()
@click.option(
    "--plain",
    is_flag=True,
    help="Show plain text output (for piping/grep)",
)
@click.pass_obj
def examples(ctx: AppContext, plain: bool) -> None:
    """Show usage examples and workflows.

    Launches an interactive TUI browser by default.
    Use --plain for text output (suitable for piping to grep/less).
    """
    if plain:
        ctx.console.print(EXAMPLES_TEXT)
    else:
        from .examples_tui import ExamplesApp

        app = ExamplesApp()
        app.run()
