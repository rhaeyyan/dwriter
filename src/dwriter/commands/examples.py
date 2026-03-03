"""Examples command showing usage examples and workflows."""

import click

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
  $ dwriter


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

  # Show config file path
  $ dwriter config path


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
@click.pass_context
def examples(ctx):
    """Show usage examples and workflows.

    Displays comprehensive examples of all dwriter commands
    and common workflows.
    """
    click.echo(EXAMPLES)
