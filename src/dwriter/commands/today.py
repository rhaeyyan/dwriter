"""Today command to view today's entries."""

from datetime import datetime

import click

from ..cli import AppContext


@click.command()
@click.pass_obj
def today(ctx: AppContext):
    """Show today's entries.

    Displays all log entries created today, ordered by time.
    """
    today_date = datetime.now()
    entries = ctx.db.get_entries_by_date(today_date)

    if not entries:
        ctx.console.print(
            'No entries for today. Start logging with:\n'
            '  [bold]dwriter add "your task"[/bold]'
        )
        return

    ctx.console.print(f"[bold blue]Today's Entries ({len(entries)})[/bold blue]")
    ctx.console.print("-" * 40)

    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")

        if ctx.config.display.show_id:
            ctx.console.print(f"[cyan][{entry.id}][/cyan] {time_str} - {entry.content}")
        else:
            ctx.console.print(f"{time_str} - {entry.content}")

        if entry.tag_names:
            tags_str = " ".join(f"#{t}" for t in entry.tag_names)
            ctx.console.print(f"      {tags_str}")

        if entry.project:
            ctx.console.print(f"      Project: {entry.project}")

        ctx.console.print()
