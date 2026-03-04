"""Todo command group for managing prospective tasks."""

from datetime import datetime

import click
from rich.table import Table

from ..cli import AppContext
from ..search_utils import find_multiple_matches


@click.group()
def todo():
    """Manage future tasks and to-dos.

    Add, review, and complete tasks. When a task is marked as done,
    it automatically generates a daily log entry for your standup.
    """
    pass


@todo.command("add")
@click.argument("content")
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Add a tag to the task (can be used multiple times)",
)
@click.option(
    "-p",
    "--project",
    "project",
    default=None,
    help="Set project name",
)
@click.option(
    "--priority",
    type=click.Choice(["low", "normal", "high", "urgent"]),
    default="normal",
    help="Set task priority",
)
@click.pass_obj
def todo_add(ctx: AppContext, content: str, tags: tuple, project: str, priority: str):
    """Add a new pending task.

    CONTENT: The text describing your task.

    Examples:
        dwriter todo add "Draft new relic ideas" -p Mainframe_Mayhem

        dwriter todo add "Fix card draw bug" --priority urgent -t bug
    """
    all_tags = list(ctx.config.defaults.tags) + list(tags)
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    task = ctx.db.add_todo(
        content=content,
        priority=priority,
        project=project,
        tags=all_tags,
    )

    priority_colors = {
        "urgent": "bold red",
        "high": "yellow",
        "normal": "white",
        "low": "dim",
    }
    color = priority_colors.get(priority, "white")

    if ctx.config.display.show_confirmation:
        ctx.console.print(
            f"[green]Added Task [{task.id}]:[/green] [{color}]{task.content}[/{color}]"
        )


@todo.command("list")
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all tasks, including completed ones",
)
@click.pass_obj
def todo_list(ctx: AppContext, show_all: bool):
    """List pending tasks.

    Displays your tasks in a formatted table. By default, only
    pending tasks are shown.
    """
    status_filter = None if show_all else "pending"
    tasks = ctx.db.get_todos(status=status_filter)

    if not tasks:
        ctx.console.print(
            "No tasks found. Relax or add one with [bold]dwriter todo add[/bold]!"
        )
        return

    table = Table(title="Your Tasks", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right", style="magenta", no_wrap=True)
    table.add_column("Priority", justify="center")
    table.add_column("Task")
    table.add_column("Project", style="purple")
    table.add_column("Tags", style="#ffae00")

    priority_styles = {
        "urgent": ("[bold red]URGENT[/bold red]", "bold red"),
        "high": ("[yellow]HIGH[/yellow]", "yellow"),
        "normal": ("NORMAL", "white"),
        "low": ("[dim]LOW[/dim]", "dim"),
    }

    for task in tasks:
        p_label, p_style = priority_styles.get(task.priority, ("NORMAL", "white"))

        content_str = (
            f"[strike]{task.content}[/strike]"
            if task.status == "completed"
            else f"[{p_style}]{task.content}[/{p_style}]"
        )

        tags_str = ", ".join(task.tag_names) if task.tag_names else ""
        project_str = task.project or ""

        table.add_row(
            str(task.id),
            p_label,
            content_str,
            project_str,
            tags_str,
        )

    ctx.console.print(table)


@todo.command("done")
@click.argument("task_identifier")
@click.option(
    "-s",
    "--search",
    "use_search",
    is_flag=True,
    help="Use fuzzy search to find the task by text instead of ID",
)
@click.pass_obj
def todo_done(ctx: AppContext, task_identifier: str, use_search: bool):
    """Mark a task as complete and log it.

    TASK_IDENTIFIER: Task ID (number) or search text if using --search.

    This completes the task and automatically creates a new daily log
    entry with the task's content, tags, and project.

    Examples:
        dwriter todo done 42

        dwriter todo done "write tests cache" --search
    """
    # Determine task ID or search for it
    task_id = None
    if use_search:
        todos = ctx.db.get_todos(status="pending")
        matches = find_multiple_matches(task_identifier, todos, limit=5, threshold=60)

        if not matches:
            ctx.console.print(
                f"[red]![/red] No tasks found matching \"{task_identifier}\"."
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
                f"[yellow]Multiple matches found for \"{task_identifier}\":[/yellow]"
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
        # 1. Mark the task as completed
        ctx.db.update_todo(task_id, status="completed", completed_at=datetime.now())

        # 2. Automatically log the entry
        entry_content = f"Completed: {task.content}"
        entry = ctx.db.add_entry(
            content=entry_content,
            tags=task.tag_names,
            project=task.project,
            created_at=datetime.now(),
        )

        ctx.console.print(f"[bold green]✅ Task {task_id} completed![/bold green]")
        ctx.console.print(
            f"Logged to today's entries: [white]{entry.content}[/white]"
        )

    except Exception as e:
        ctx.console.print(f"[red]Error completing task: {e}[/red]")


@todo.command("rm")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_rm(ctx: AppContext, task_id: int):
    """Delete a task entirely."""
    if click.confirm(f"Are you sure you want to delete task {task_id}?"):
        success = ctx.db.delete_todo(task_id)
        if success:
            ctx.console.print(f"[green]✅[/green] Task {task_id} deleted.")
        else:
            ctx.console.print(f"[red]![/red] Task {task_id} not found.")
    else:
        ctx.console.print("Cancelled.")


@todo.command("edit")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_edit(ctx: AppContext, task_id: int):
    """Edit a task's content interactively."""
    try:
        task = ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    edited_content = click.edit(task.content)

    if edited_content is None:
        ctx.console.print("No changes made.")
        return

    edited_content = edited_content.strip()

    if not edited_content:
        ctx.console.print(
            "Task content cannot be empty. Use 'todo rm' to delete."
        )
        return

    if edited_content != task.content:
        ctx.db.update_todo(task_id, content=edited_content)
        ctx.console.print(f"[green]✅[/green] Task {task_id} updated.")
    else:
        ctx.console.print("No changes made.")
