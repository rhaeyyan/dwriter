"""Delete command for bulk deletion of entries."""

from datetime import datetime

import click

from ..database import Database


def parse_date(date_str: str) -> datetime:
    """Parse a date string.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        datetime object.

    Raises:
        click.BadParameter: If the date format is invalid.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter("Date must be in YYYY-MM-DD format")


@click.command()
@click.option(
    "--before",
    "before_date",
    required=True,
    type=str,
    help="Delete entries before this date (YYYY-MM-DD)",
)
@click.pass_context
def delete(ctx, before_date: str):
    """Bulk delete old entries.

    Deletes all entries created before the specified date.

    Examples:
        dwriter delete --before 2025-01-01

        dwriter delete --before 2024-12-31
    """
    db = Database()

    try:
        cutoff_date = parse_date(before_date)
    except click.BadParameter as e:
        click.echo(click.style("!", fg="red") + f" {e}")
        return

    # Count entries that will be deleted
    entries = db.get_entries_in_range(datetime(2000, 1, 1), cutoff_date)

    if not entries:
        click.echo(f"No entries found before {before_date}.")
        return

    click.echo(f"About to delete {len(entries)} entries before {before_date}:")
    click.echo()

    for entry in entries[:10]:  # Show first 10
        date_str = entry.created_at.strftime("%Y-%m-%d")
        click.echo(f"  [{entry.id}] {date_str}: {entry.content}")

    if len(entries) > 10:
        click.echo(f"  ... and {len(entries) - 10} more")

    click.echo()

    if click.confirm(
        click.style(
            "This action cannot be undone. Are you sure?",
            fg="red",
            bold=True,
        )
    ):
        deleted_count = db.delete_entries_before(cutoff_date)
        click.echo(click.style("✅", fg="green") + f" Deleted {deleted_count} entries.")
    else:
        click.echo("Cancelled.")
