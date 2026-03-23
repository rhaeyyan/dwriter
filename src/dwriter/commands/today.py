"""Today command to view today's entries."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

from datetime import datetime

import click

from ..ui_utils import display_entry


@click.command()
@click.pass_obj
def today(ctx: AppContext) -> None:
    """Show today's entries.

    Displays all log entries created today, ordered by time.
    This is the default command when running `dwriter` without arguments.

    Examples:
      dwriter today
      dwriter    # Same as 'dwriter today'
    """
    today_date = datetime.now()
    entries = ctx.db.get_entries_by_date(today_date)

    if not entries:
        ctx.console.print(
            "No entries for today. Start logging with:\n"
            '  [bold]dwriter add "your task"[/bold]'
        )
        return

    ctx.console.print(f"[bold blue]Today's Entries ({len(entries)})[/bold blue]")
    ctx.console.print("-" * 40)

    for entry in entries:
        display_entry(ctx.console, entry, ctx.config)
        ctx.console.print()
