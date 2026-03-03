"""Undo command for deleting the most recent entry."""

import click

from ..database import Database


@click.command()
@click.pass_context
def undo(ctx):
    """Delete the most recent entry.

    Removes the last logged entry. Use with caution as this action
    cannot be undone.
    """
    db = Database()

    latest = db.get_latest_entry()
    if latest is None:
        click.echo("No entries to undo.")
        return

    click.echo("About to delete:")
    click.echo(f"  [{latest.id}] {latest.content}")

    if click.confirm("Are you sure?"):
        db.delete_entry(latest.id)
        click.echo(click.style("✅", fg="green") + " Entry deleted.")
    else:
        click.echo("Cancelled.")
