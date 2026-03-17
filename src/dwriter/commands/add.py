"""Add command for logging new entries."""

from __future__ import annotations

from typing import Any

import click

from ..cli import AppContext
from ..date_utils import parse_date_or_default
from ..ui_utils import display_entry


@click.command()
@click.argument("content")
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Add a tag (can be used multiple times)",
)
@click.option(
    "-p",
    "--project",
    "project",
    default=None,
    help="Set project name",
)
@click.option(
    "-d",
    "--date",
    "date_str",
    default=None,
    help="Set entry date using natural language (e.g., 'yesterday', "
    "'last Friday', '3 days ago') or standard date format (YYYY-MM-DD)",
)
@click.pass_obj
def add(
    ctx: AppContext,
    content: str,
    tags: tuple[Any, ...],
    project: str | None,
    date_str: str | None,
) -> None:
    """Add a new log entry.

    Quickly capture tasks, notes, or accomplishments with optional
    tags and project categorization. Supports backdated entries
    using natural language dates.

    Supported Date Formats:
      - Relative: today, yesterday, tomorrow
      - Days ago: 3 days ago, 2 weeks ago
      - Last weekday: last Monday, last Friday
      - Standard: 2024-01-15, 01/15/2024

    Examples:
      dwriter add "fixed the race condition in auth"

      dwriter add "fixed login bug" -t bug -t backend

      dwriter add "implemented feature X" --project myapp

      dwriter add "refactored database layer" -t refactor -t backend -p myapp

      dwriter add "Finished report" --date yesterday

      dwriter add "Meeting notes" --date "last Friday"

      dwriter add "Completed sprint" --date "3 days ago"
    """
    # Merge default tags with provided tags
    all_tags = list(ctx.config.defaults.tags) + list(tags)

    # Use default project if none provided
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    # Parse the date (or use current time if not provided)
    entry_date = parse_date_or_default(date_str)

    entry = ctx.db.add_entry(
        content=content, tags=all_tags, project=project, created_at=entry_date
    )

    if ctx.config.display.show_confirmation:
        display_entry(ctx.console, entry, ctx.config)
