"""Add command for logging new entries."""

import click

from ..config import ConfigManager
from ..database import Database


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
@click.pass_context
def add(ctx, content: str, tags: tuple, project: str):
    """Add a new log entry.

    CONTENT: The text content of your log entry.

    Examples:
        dwriter add "fixed the race condition in auth"

        dwriter add "fixed login bug" -t bug -t backend

        dwriter add "implemented feature X" --project myapp

        dwriter add "refactored database layer" -t refactor -t backend -p myapp
    """
    db = Database()
    config_manager = ConfigManager()
    config = config_manager.load()

    # Merge default tags with provided tags
    all_tags = list(config.defaults.tags) + list(tags)

    # Use default project if none provided
    if project is None and config.defaults.project:
        project = config.defaults.project

    entry = db.add_entry(content=content, tags=all_tags, project=project)

    if config.display.show_confirmation:
        click.echo(click.style("✅", fg="green") + f" Logged: {entry.content}")

        if entry.tags:
            tags_str = ", ".join(f"#{t}" for t in entry.tags)
            click.echo(f"  Tags: {tags_str}")

        if entry.project:
            click.echo(f"  Project: {entry.project}")
