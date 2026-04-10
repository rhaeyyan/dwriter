"""Today command to view today's entries."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click

from ..ui_utils import display_entry


@click.command()
@click.option("--json", "output_json", is_flag=True, help="Output data in machine-readable JSON format.")
@click.pass_obj
def today(ctx: AppContext, output_json: bool) -> None:
    """Show today's entries.

    Displays all log entries created today, ordered by time.
    This is the default command when running `dwriter` without arguments.

    Examples:
      dwriter today
      dwriter    # Same as 'dwriter today'
    """
    today_date = datetime.now()
    entries = ctx.db.get_entries_by_date(today_date)

    if output_json:
        data = [
            {
                "id": e.id,
                "uuid": e.uuid,
                "content": e.content,
                "project": e.project,
                "tags": e.tag_names,
                "created_at": e.created_at.isoformat(),
                "life_domain": e.life_domain,
                "energy_level": e.energy_level,
            }
            for e in entries
        ]
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return

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
