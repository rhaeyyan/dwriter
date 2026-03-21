"""Todo command group for managing prospective tasks."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import click
from rich.table import Table

from ..cli import AppContext
from ..date_utils import parse_natural_date
from ..search_utils import find_multiple_matches
from ..tui.colors import DUE_OVERDUE, DUE_SOON, DUE_TODAY, DUE_TOMORROW, TAG


@click.group(invoke_without_command=True)
@click.argument("content", required=False, nargs=-1)
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
@click.option(
    "--due",
    "due_date_str",
    default=None,
    help="Set due date (e.g., 'tomorrow', '+5d', '+1w', '+1m', '2024-01-15')",
)
@click.pass_context
def todo(
    ctx: click.Context,
    content: tuple[Any, ...],
    tags: tuple[Any, ...],
    project: str | None,
    priority: str,
    due_date_str: str | None,
) -> None:
    """Manage future tasks and to-dos.

    Add, review, and complete tasks. When a task is marked as done,
    it automatically generates a daily log entry for your standup.

    If invoked without arguments, launches the interactive todo board
    with keyboard navigation for completing, editing, and managing tasks.

    Priority Levels:
      - low: Dimmed display, low visibility tasks
      - normal: Default priority, standard display
      - high: Yellow highlight for important tasks
      - urgent: Red highlight for critical tasks

    Due Date Formats:
      - Relative: tomorrow, +5d, +1w, +1m
      - Days/weeks: 3 days, 2 weeks
      - Weekday: last Monday, Friday
      - Standard: 2024-01-15, 01/15/2024

    Examples:
      dwriter todo                         # Launch interactive TUI
      dwriter todo "Draft new relic ideas" -p Mainframe_Mayhem
      dwriter todo "Fix card draw bug" --priority urgent -t bug
      dwriter todo --priority urgent -t bug "Fix card draw bug"
      dwriter todo "Write tests" --due tomorrow
      dwriter todo "Review PR" --due +5d -t code
      dwriter todo add "Task" -p Project -t tag --due +3d  # Explicit subcommand
      dwriter todo list                    # Show pending tasks
      dwriter todo list --all              # Include completed
      dwriter todo list --tui              # Interactive mode
    """
    # Check if first content token is a known subcommand
    if content and content[0] in todo.commands:
        subcommand_name = content[0]
        cmd = todo.commands[subcommand_name]
        # Invoke with remaining args
        rest = list(content[1:])
        sub_ctx = cmd.make_context(ctx.info_name, rest, parent=ctx)
        return sub_ctx.command.invoke(sub_ctx)  # type: ignore[no-any-return]

    # Get the AppContext from parent context
    app_ctx = ctx.obj

    # Default behavior - add task or show list
    content_str = " ".join(content) if content else None

    if content_str is not None:
        # Extract metadata from content if present
        from ..tui.parsers import parse_todo_add
        parsed = parse_todo_add(content_str)
        
        # Merge default tags, content-extracted tags, and explicitly provided tags
        all_tags = list(app_ctx.config.defaults.tags) + list(parsed.tags) + list(tags)
        
        # Merge content-extracted priority if not explicitly set to non-default
        if priority == "normal" and parsed.priority != "normal":
            priority = parsed.priority

        # Use explicitly provided project, then content-extracted project, then default
        if project is None:
            project = parsed.project or app_ctx.config.defaults.project

        # Use the cleaned content
        content_str = parsed.content

        # Parse due date if provided
        due_date = None
        # Use content-extracted due date if not explicitly provided
        final_due_str = due_date_str or parsed.due_date
        
        if final_due_str is not None:
            try:
                due_date = parse_natural_date(final_due_str)
            except ValueError as e:
                app_ctx.console.print(f"[red]Error:[/red] {e}")
                return

        task = app_ctx.db.add_todo(
            content=content_str,
            priority=priority,
            project=project,
            tags=all_tags,
            due_date=due_date,
        )

        priority_colors = {
            "urgent": "bold red",
            "high": "yellow",
            "normal": "white",
            "low": "dim",
        }
        color = priority_colors.get(priority, "white")

        if app_ctx.config.display.show_confirmation:
            due_str = ""
            if due_date:
                due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d')})[/dim]"

            tags_str = ""
            if task.tag_names:
                tags_str = f" [{TAG}]#{' #'.join(task.tag_names)}[/{TAG}]"

            proj_str = ""
            if task.project:
                proj_str = f" [purple]&{task.project}[/purple]"

            app_ctx.console.print(
                f"[green]Added Task [{task.id}]:[/green] "
                f"[{color}]{task.priority.upper()}[/{color}] | "
                f"[{color}]{task.content}[/{color}]{tags_str}{proj_str}{due_str}"
            )
    else:
        # No content - launch interactive TUI
        from .todo_tui import TodoApp

        app = TodoApp(
            db=app_ctx.db,
            console=app_ctx.console,
            show_all=False,
        )
        app.run()


@todo.command("add")
@click.argument("content", required=True, nargs=-1)
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
@click.option(
    "--due",
    "due_date_str",
    default=None,
    help="Set due date (e.g., 'tomorrow', '+5d', '+1w', '+1m', '2024-01-15')",
)
@click.pass_obj
def todo_add(
    ctx: AppContext,
    content: tuple[Any, ...],
    tags: tuple[Any, ...],
    project: str | None,
    priority: str,
    due_date_str: str | None,
) -> None:
    """Add a new task to your todo list.

    Creates a new prospective task with optional priority, project, tags,
    and due date.

    CONTENT: The task description (can contain multiple words).

    Options:
      -t, --tag: Add a tag (can be used multiple times)
      -p, --project: Set project name
      --priority: Set priority (low, normal, high, urgent)
      --due: Set due date using natural language

    Due Date Formats:
      tomorrow, +5d, +1w, +1m, 3 days, 2 weeks,
      last Friday, 2024-01-15, etc.

    Examples:
      dwriter todo add "Write unit tests" -t testing --priority high
      dwriter todo add "Review PR" -p Mainframe -t code --due tomorrow
      dwriter todo add "Draft documentation" --due +5d -t docs
    """
    content_str = " ".join(content)

    # Extract metadata from content if present
    from ..tui.parsers import parse_todo_add
    parsed = parse_todo_add(content_str)
    
    # Merge default tags, content-extracted tags, and explicitly provided tags
    all_tags = list(ctx.config.defaults.tags) + list(parsed.tags) + list(tags)

    # Merge content-extracted priority if not explicitly set to non-default
    if priority == "normal" and parsed.priority != "normal":
        priority = parsed.priority

    # Use explicitly provided project, then content-extracted project, then default
    if project is None:
        project = parsed.project or ctx.config.defaults.project

    # Use the cleaned content
    content_str = parsed.content

    # Parse due date if provided
    due_date = None
    # Use content-extracted due date if not explicitly provided
    final_due_str = due_date_str or parsed.due_date
    
    if final_due_str is not None:
        try:
            due_date = parse_natural_date(final_due_str)
        except ValueError as e:
            ctx.console.print(f"[red]Error:[/red] {e}")
            return

    task = ctx.db.add_todo(
        content=content_str,
        priority=priority,
        project=project,
        tags=all_tags,
        due_date=due_date,
    )

    priority_colors = {
        "urgent": "bold red",
        "high": "yellow",
        "normal": "white",
        "low": "dim",
    }
    color = priority_colors.get(priority, "white")

    if ctx.config.display.show_confirmation:
        due_str = ""
        if due_date:
            due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d')})[/dim]"
        
        tags_str = ""
        if task.tag_names:
            tags_str = f" [{TAG}]#{' #'.join(task.tag_names)}[/{TAG}]"
        
        proj_str = ""
        if task.project:
            proj_str = f" [purple]&{task.project}[/purple]"

        ctx.console.print(
            f"[green]Added Task [{task.id}]:[/green] "
            f"[{color}]{task.priority.upper()}[/{color}] | "
            f"[{color}]{task.content}[/{color}]{tags_str}{proj_str}{due_str}"
        )


@todo.command("list")
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all tasks, including completed ones",
)
@click.option(
    "--tui",
    "use_tui",
    is_flag=True,
    help="Launch interactive TUI mode",
)
@click.pass_obj
def todo_list(ctx: AppContext, show_all: bool, use_tui: bool) -> None:
    """List pending tasks.

    Displays your tasks in a formatted table with priority colors.
    By default, only pending tasks are shown.

    Options:
      --all: Include completed tasks (shown with strikethrough)
      --tui: Launch interactive TUI for managing tasks

    Examples:
      dwriter todo list
      dwriter todo list --all
      dwriter todo list --tui
    """
    # Launch TUI if requested
    if use_tui:
        from .todo_tui import TodoApp

        app = TodoApp(
            db=ctx.db,
            console=ctx.console,
            show_all=show_all,
        )
        app.run()
        return

    status_filter = None if show_all else "pending"
    tasks = ctx.db.get_todos(status=status_filter)

    if not tasks:
        ctx.console.print(
            "No tasks found. Relax or add one with [bold]dwriter todo[/bold]!"
        )
        return

    table = Table(title="Your Tasks", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right", style="magenta", no_wrap=True)
    table.add_column("Priority", justify="center")
    table.add_column("Task")
    table.add_column("Project", style="#ff00ff")
    table.add_column("Tags", style="#00ff00")
    table.add_column("Due", style="cyan", justify="center")

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
        project_str = f"&{task.project}" if task.project else ""

        # Format due date
        due_str = ""
        if task.due_date:
            due_date = task.due_date
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            due_date_only = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_until = (due_date_only - today).days

            if days_until < 0:
                due_str = f"[{DUE_OVERDUE}]{due_date.strftime('%Y-%m-%d')}[/{DUE_OVERDUE}]"
            elif days_until == 0:
                due_str = f"[{DUE_TODAY}]TODAY[/{DUE_TODAY}]"
            elif days_until == 1:
                due_str = f"[{DUE_TOMORROW}]Tomorrow[/{DUE_TOMORROW}]"
            elif days_until <= 7:
                due_str = f"[{DUE_SOON}]{days_until}d[/{DUE_SOON}]"
            else:
                due_str = due_date.strftime("%Y-%m-%d")

        table.add_row(
            str(task.id),
            p_label,
            content_str,
            project_str,
            tags_str,
            due_str,
        )

    ctx.console.print(table)


@todo.command("rm")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_rm(ctx: AppContext, task_id: int) -> None:
    """Delete a task entirely.

    Removes a task from your todo list. Requires confirmation.

    Examples:
      dwriter todo rm 3
    """
    try:
        ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

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
def todo_edit(ctx: AppContext, task_id: int) -> None:
    """Edit a task's content interactively.

    Opens the task content in your default editor for modification.

    Examples:
      dwriter todo edit 2
    """
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
        ctx.console.print("Task content cannot be empty. Use 'todo rm' to delete.")
        return

    if edited_content != task.content:
        ctx.db.update_todo(task_id, content=edited_content)
        ctx.console.print(f"[green]✅[/green] Task {task_id} updated.")
    else:
        ctx.console.print("No changes made.")


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
