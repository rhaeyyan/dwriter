"""Undo command for deleting the most recent entry."""

import click

from ..cli import AppContext


@click.command()
@click.pass_obj
def undo(ctx: AppContext):
    """Delete the most recent entry.

    Removes the last logged entry. Use with caution as this action
    cannot be undone.
    """
    latest = ctx.db.get_latest_entry()
    if latest is None:
        ctx.console.print("No entries to undo.")
        return

    ctx.console.print("About to delete:")
    ctx.console.print(f"  [{latest.id}] {latest.content}")

    if click.confirm("Are you sure?"):
        ctx.db.delete_entry(latest.id)
        ctx.console.print("[green]✅[/green] Entry deleted.")
    else:
        ctx.console.print("Cancelled.")
