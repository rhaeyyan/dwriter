"""Examples command showing usage examples and workflows."""

import click

from ..cli import AppContext

EXAMPLES = """
Day Writer - Usage Examples
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


2. VIEWING ENTRIES
───────────────────────────────────────────────────────────────

  # Show today's entries
  $ dwriter today

  # Show all entries (default when running dwriter without arguments)
  $ dwriter today


3. STANDUP GENERATION
───────────────────────────────────────────────────────────────

  # Generate yesterday's standup (copies to clipboard)
  $ dwriter standup

  # Different formats
  $ dwriter standup --format slack
  $ dwriter standup --format jira

  # Don't copy to clipboard
  $ dwriter standup --no-copy


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

  # Interactive edit (opens today's entries in editor)
  $ dwriter edit

  # Edit specific entry by ID
  $ dwriter edit --id 42

  # Undo last entry
  $ dwriter undo

  # Bulk delete old entries
  $ dwriter delete --before 2025-01-01


6. STATISTICS
───────────────────────────────────────────────────────────────

  # Show logging stats and streak
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

  # Add a new task
  $ dwriter todo "Draft new relic ideas"

  # Add task with project
  $ dwriter todo "Fix card draw bug" -p my_project

  # Add task with priority and tags
  $ dwriter todo "Fix card draw bug" --priority urgent -t bug

  # Options can come before content too
  $ dwriter todo --priority urgent -t bug "Fix card draw bug"

  # List pending tasks
  $ dwriter todo list

  # Mark a task as done (auto-logs to journal)
  $ dwriter done 5

  # Mark task done using fuzzy search
  $ dwriter done "card draw bug" --search

  # Delete a task
  $ dwriter todo rm 3

  # Edit a task
  $ dwriter todo edit 2


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
"""


@click.command()
@click.pass_obj
def examples(ctx: AppContext):
    """Show usage examples and workflows.

    Displays comprehensive examples of all dwriter commands
    and common workflows.
    """
    ctx.console.print(EXAMPLES)
