"""Delete command for bulk deletion of entries."""

from datetime import datetime

import click

from ..cli import AppContext


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
@click.pass_obj
def delete(ctx: AppContext, before_date: str):
    """Bulk delete old entries.

    Deletes all entries created before the specified date.

    Examples:
        dwriter delete --before 2025-01-01

        dwriter delete --before 2024-12-31
    """
    try:
        cutoff_date = parse_date(before_date)
    except click.BadParameter as e:
        ctx.console.print(f"[red]![/red] {e}")
        return

    # Count entries that will be deleted
    entries = ctx.db.get_entries_in_range(datetime(2000, 1, 1), cutoff_date)

    if not entries:
        ctx.console.print(f"No entries found before {before_date}.")
        return

    ctx.console.print(f"About to delete {len(entries)} entries before {before_date}:")
    ctx.console.print()

    for entry in entries[:10]:  # Show first 10
        date_str = entry.created_at.strftime("%Y-%m-%d")
        time_str = entry.created_at.strftime("%I:%M [bold]%p[/bold]")
        ctx.console.print(f"  [{entry.id}] {date_str} | {time_str}: `{entry.content}`")

    if len(entries) > 10:
        ctx.console.print(f"  ... and {len(entries) - 10} more")

    ctx.console.print()

    if click.confirm(
        click.style(
            "This action cannot be undone. Are you sure?",
            fg="red",
            bold=True,
        )
    ):
        deleted_count = ctx.db.delete_entries_before(cutoff_date)
        ctx.console.print(f"[green]✅[/green] Deleted {deleted_count} entries.")
    else:
        ctx.console.print("Cancelled.")
