"""Add command for logging new entries."""

import click

from ..cli import AppContext
from ..date_utils import parse_date_or_default


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
def add(ctx: AppContext, content: str, tags: tuple, project: str, date_str: str):
    """Add a new log entry.

    CONTENT: The text content of your log entry.

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
        date_str = entry.created_at.strftime("%Y-%m-%d")
        time_str = entry.created_at.strftime("%I:%M %p")

        if ctx.config.display.show_id:
            ctx.console.print(
                f"[magenta][{entry.id}][/magenta] {date_str} | [#23c76b]{time_str}[/#23c76b]: {entry.content}"
            )
        else:
            ctx.console.print(f"{date_str} | [#23c76b]{time_str}[/#23c76b]: {entry.content}")

        if entry.tag_names:
            tags_str = " ".join(f"[#ffae00]#[/]{t}" for t in entry.tag_names)
            ctx.console.print(f"    [#ffae00]Tags:[/#ffae00] {tags_str}")

        if entry.project:
            ctx.console.print(f"    [purple]Project:[/purple] {entry.project}")
