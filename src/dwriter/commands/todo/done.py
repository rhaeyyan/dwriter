"""done command — mark a task as complete and log it."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ...search_utils import find_multiple_matches


@click.command()
@click.argument("task_identifier")
@click.option(
    "-s",
    "--search",
    "use_search",
    is_flag=True,
    help="Use fuzzy search to find the task by text instead of ID",
)
@click.pass_obj
def done(ctx: AppContext, task_identifier: str, use_search: bool) -> None:
    """Mark a task as complete and log it.

    Completes the task and automatically creates a new daily log
    entry with the task's content, tags, and project.

    TASK_IDENTIFIER: Task ID (number) or search text if using --search.

    Examples:
      dwriter done 42
      dwriter done "write tests cache" --search
    """
    # Determine task ID or search for it
    task_id = None
    if use_search:
        todos = ctx.db.get_todos(status="pending")
        matches = find_multiple_matches(task_identifier, todos, limit=5, threshold=60)

        if not matches:
            ctx.console.print(
                f'[red]![/red] No tasks found matching "{task_identifier}".'
            )
            return

        if len(matches) == 1:
            # Single high-confidence match
            task, score = matches[0]
            ctx.console.print(
                f"[green]Found match:[/green] [{task.id}] {task.content} "
                f"(Match: {int(score)}%)"
            )
            task_id = task.id
        else:
            # Multiple matches - ask user to select
            ctx.console.print(
                f'[yellow]Multiple matches found for "{task_identifier}":[/yellow]'
            )
            for i, (task, score) in enumerate(matches, 1):
                ctx.console.print(
                    f"  {i}. [[cyan]{task.id}[/cyan]] {task.content} "
                    f"[dim]({int(score)}%)[/dim]"
                )

            choice = click.prompt(
                "Which task do you want to mark as done? [1-5]",
                type=int,
                default=1,
            )
            if choice < 1 or choice > len(matches):
                ctx.console.print("[red]Invalid selection.[/red]")
                return
            task, _ = matches[choice - 1]
            task_id = task.id
    else:
        # Try to parse as integer ID
        try:
            task_id = int(task_identifier)
        except ValueError:
            ctx.console.print(
                "[red]![/red] Task identifier must be a number. "
                "Use --search for text search."
            )
            return

    try:
        task = ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    if task.status == "completed":
        ctx.console.print(f"Task {task_id} is already completed.")
        return

    try:
        ctx.db.update_todo(task_id, status="completed", completed_at=datetime.now())

        # Automatically log the completion to the journal
        entry_content = f"Completed: {task.content}"
        entry = ctx.db.add_entry(
            content=entry_content,
            tags=task.tag_names,
            project=task.project,
            created_at=datetime.now(),
        )

        ctx.console.print(f"[bold green]✅ Task {task_id} completed![/bold green]")
        ctx.console.print(f"Logged to today's entries: [white]{entry.content}[/white]")

    except Exception as e:
        ctx.console.print(f"[red]Error completing task: {e}[/red]")
