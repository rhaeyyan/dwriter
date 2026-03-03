"""Today command to view today's entries."""

from datetime import datetime

import click

from ..config import ConfigManager
from ..database import Database


@click.command()
@click.pass_context
def today(ctx):
    """Show today's entries.

    Displays all log entries created today, ordered by time.
    """
    db = Database()
    config_manager = ConfigManager()
    config = config_manager.load()

    today_date = datetime.now()
    entries = db.get_entries_by_date(today_date)

    if not entries:
        click.echo("No entries for today. Start logging with:")
        click.echo(click.style('  dwriter add "your task"', bold=True))
        return

    click.echo(click.style(f"Today's Entries ({len(entries)})", bold=True, fg="blue"))
    click.echo("-" * 40)

    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")

        if config.display.show_id:
            click.echo(click.style(f"[{entry.id}]", fg="cyan"), nl=False)
            click.echo(f" {time_str} - {entry.content}")
        else:
            click.echo(f"{time_str} - {entry.content}")

        if entry.tags:
            tags_str = " ".join(f"#{t}" for t in entry.tags)
            click.echo(f"      {tags_str}")

        if entry.project:
            click.echo(f"      Project: {entry.project}")

        click.echo()
