"""Search command for finding past entries and future to-dos."""

from __future__ import annotations

from typing import Any

import click

from ..cli import AppContext
from ..search_utils import search_items


def format_score(score: float) -> str:
    """Format the rapidfuzz score as a color-coded percentage."""
    percentage = int(score)
    if percentage >= 90:
        return f"[green]{percentage}%[/green]"
    elif percentage >= 75:
        return f"[yellow]{percentage}%[/yellow]"
    else:
        return f"[dim]{percentage}%[/dim]"


@click.command()
@click.argument("query", required=False, default=None)
@click.option(
    "-p",
    "--project",
    "project",
    default=None,
    help="Filter by project before searching",
)
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Filter by tags before searching (can be used multiple times)",
)
@click.option(
    "--type",
    "search_type",
    type=click.Choice(["all", "entry", "todo"]),
    default="all",
    help="Restrict search to entries or todos",
)
@click.option(
    "-n",
    "--limit",
    "limit",
    type=int,
    default=10,
    help="Maximum number of results to show per category",
)
@click.pass_obj
def search(
    ctx: AppContext,
    query: str | None,
    project: str | None,
    tags: tuple[Any, ...],
    search_type: str,
    limit: int,
) -> None:
    """Fuzzy search your journal entries and tasks.

    Uses typo-tolerant fuzzy matching to find relevant entries and todos.
    If omitted, launches interactive search TUI with live filtering.

    Match Scores:
      - 🟢 90%+: Excellent match (green)
      - 🟡 75%+: Good match (yellow)
      - ⚪ 60%+: Partial match (dim)

    Examples:
      dwriter search                    # Launch interactive TUI
      dwriter search "auth bug"         # Fuzzy search all
      dwriter search "refactor" -p my_project
      dwriter search "cache" --type todo
      dwriter search "meeting" -t work -t notes -n 5
    """
    # Launch TUI if no query provided
    if query is None:
        from .search_tui import SearchApp

        tag_list = list(tags) if tags else None
        app = SearchApp(
            db=ctx.db,
            console=ctx.console,
            project=project,
            tags=tag_list,
        )
        app.run()
        return

    # Original static search behavior
    tag_list = list(tags) if tags else None

    # Search Entries
    matched_entries = []
    if search_type in ["all", "entry"]:
        entries = ctx.db.get_all_entries(project=project, tags=tag_list)
        matched_entries = search_items(query, entries, limit=limit, threshold=60)

    # Search To-Dos
    matched_todos = []
    if search_type in ["all", "todo"]:
        todos = ctx.db.get_all_todos(project=project, tags=tag_list)
        matched_todos = search_items(query, todos, limit=limit, threshold=60)

    # Display results
    ctx.console.print(f'[bold blue]🔍 Search Results for "{query}"[/bold blue]\n')

    if matched_entries:
        ctx.console.print("[bold magenta][ENTRIES][/bold magenta]")
        for entry, score in matched_entries:
            from ..ui_utils import format_entry_datetime

            date_str, time_str = format_entry_datetime(entry)
            score_str = format_score(score)
            tags_str = ""
            if entry.tag_names:
                tags_str = " ".join(f"[#ffae00]#[/]{t}" for t in entry.tag_names)
            if entry.project:
                project_str = f" [purple]Project:[/purple] {entry.project}"
            else:
                project_str = ""

            # Display with or without time based on whether it's a past date
            if time_str is None:
                ctx.console.print(
                    f"[magenta][{entry.id}][/magenta] {date_str}: {entry.content}"
                )
            else:
                ctx.console.print(
                    f"[magenta][{entry.id}][/magenta] {date_str} | "
                    f"[#23c76b]{time_str}[/#23c76b]: {entry.content}"
                )
            if tags_str:
                ctx.console.print(f"    [#ffae00]Tags:[/#ffae00] {tags_str}")
            if project_str:
                ctx.console.print(f"    {project_str}")
            ctx.console.print(f"    [dim](Match: {score_str})[/dim]")
        ctx.console.print()

    if matched_todos:
        ctx.console.print("[bold magenta][TO-DOS][/bold magenta]")
        for todo, score in matched_todos:
            priority_color = {
                "urgent": "bold red",
                "high": "yellow",
                "normal": "white",
                "low": "dim",
            }.get(todo.priority, "white")
            score_str = format_score(score)
            tags_str = ""
            if todo.tag_names:
                tags_str = f" [dim]| {', '.join(todo.tag_names)}[/dim]"
            project_str = f" [dim]| {todo.project}[/dim]" if todo.project else ""
            priority_label = (
                f"[{priority_color}]{todo.priority.upper()}[/{priority_color}]"
            )
            ctx.console.print(
                f"[[cyan]{todo.id}[/cyan]] ({priority_label}) "
                f"{todo.content}{tags_str}{project_str} (Match: {score_str})"
            )
        ctx.console.print()

    if search_type == "all" and not matched_entries and not matched_todos:
        ctx.console.print("[dim]No matches found.[/dim]")
    elif not matched_entries and not matched_todos:
        ctx.console.print("[dim]No matches found.[/dim]")
