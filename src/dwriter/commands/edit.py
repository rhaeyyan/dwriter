"""Edit command for managing entries interactively."""

from __future__ import annotations

from datetime import datetime

import click

from ..cli import AppContext
from ..search_utils import find_multiple_matches


def _handle_search_edit(ctx: AppContext, search_query: str) -> int | None:
    """Handle search-based entry editing.

    Args:
        ctx: The application context.
        search_query: The search query string.

    Returns:
        The entry ID if found, None otherwise.
    """
    entries = ctx.db.get_all_entries()
    matches = find_multiple_matches(search_query, entries, limit=5, threshold=60)

    if not matches:
        ctx.console.print(f'[red]![/red] No entries found matching "{search_query}".')
        return None

    if len(matches) == 1:
        entry, score = matches[0]
        ctx.console.print(
            f"[green]Found match:[/green] [{entry.id}] {entry.content} "
            f"(Match: {int(score)}%)"
        )
        return entry.id  # type: ignore[no-any-return]

    ctx.console.print(f'[yellow]Multiple matches found for "{search_query}":[/yellow]')
    for i, (entry, score) in enumerate(matches, 1):
        date_str = entry.created_at.strftime("%Y-%m-%d")
        ctx.console.print(
            f"  {i}. [[cyan]{entry.id}[/cyan]] {date_str}: {entry.content} "
            f"[dim]({int(score)}%)[/dim]"
        )

    choice = click.prompt("Which entry do you want to edit? [1-5]", type=int, default=1)
    if choice < 1 or choice > len(matches):
        ctx.console.print("[red]Invalid selection.[/red]")
        return None

    entry, _ = matches[choice - 1]
    return entry.id  # type: ignore[no-any-return]


def _edit_single_entry(ctx: AppContext, entry_id: int) -> None:
    """Edit a single entry by ID.

    Args:
        ctx: The application context.
        entry_id: The ID of the entry to edit.
    """
    try:
        entry = ctx.db.get_entry(entry_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Entry {entry_id} not found.")
        return

    edited_content = click.edit(entry.content)

    if edited_content is None:
        ctx.console.print("No changes made.")
        return

    edited_content = edited_content.strip()

    if not edited_content:
        if click.confirm("Content is empty. Delete this entry?"):
            ctx.db.delete_entry(entry_id)
            ctx.console.print("[green]✅[/green] Entry deleted.")
        return

    if edited_content != entry.content:
        ctx.db.update_entry(entry_id, content=edited_content)
        ctx.console.print("[green]✅[/green] Entry updated.")
    else:
        ctx.console.print("No changes made.")


def _bulk_edit_today(ctx: AppContext) -> None:
    """List today's entries and suggest UI or ID-based editing.

    Args:
        ctx: The application context.
    """
    entries = ctx.db.get_entries_by_date(datetime.now())
    
    if not entries:
        ctx.console.print("[yellow]No entries found for today.[/yellow]")
        ctx.console.print("Run [bold]dwriter ui[/bold] to see your full history.")
        return

    ctx.console.print("[bold cyan]Today's Entries:[/bold cyan]")
    for entry in entries:
        ctx.console.print(f"  [[magenta]{entry.id}[/magenta]] {entry.content}")
    
    ctx.console.print("\nTo edit a specific entry, run: [bold]dwriter edit --id <ID>[/bold]")
    ctx.console.print("To use the interactive editor, run: [bold]dwriter ui --logs[/bold]")


@click.command()
@click.option(
    "-i",
    "--id",
    "entry_id",
    type=int,
    default=None,
    help="Edit a specific entry by ID",
)
@click.option(
    "-s",
    "--search",
    "search_query",
    default=None,
    help="Search for an entry by text (fuzzy match)",
)
@click.pass_obj
def edit(ctx: AppContext, entry_id: int | None, search_query: str | None) -> None:
    """Edit or delete entries.

    If no ID or search is provided, it lists today's entries.
    To use the full interactive editor, run:
      dwriter ui --logs

    Examples:
      dwriter edit                  # List today's entries
      dwriter edit --id 42          # Edit specific entry
      dwriter edit --search "redis cache"  # Search and edit
    """
    if search_query is not None:
        entry_id = _handle_search_edit(ctx, search_query)
        if entry_id is None:
            return

    if entry_id is not None:
        _edit_single_entry(ctx, entry_id)
    else:
        _bulk_edit_today(ctx)
