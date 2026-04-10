"""Todo command group for managing prospective tasks."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext

import click
from rich.table import Table

from ..date_utils import parse_natural_date
from ..search_utils import find_multiple_matches
from ..tui.colors import DUE_OVERDUE, DUE_SOON, DUE_TODAY, DUE_TOMORROW, PROJECT, TAG


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"], "allow_interspersed_args": True},
)
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
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all tasks, including completed ones (for 'list')",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output data in machine-readable JSON format (for 'list')",
)
@click.pass_context
def todo(
    ctx: click.Context,
    content: tuple[Any, ...],
    tags: tuple[Any, ...],
    project: str | None,
    priority: str,
    due_date_str: str | None,
    show_all: bool,
    output_json: bool,
) -> None:
    """Manage future tasks and to-dos.

    Add, review, and complete tasks. You can use shorthand like #tag
    and &project directly in the content.

    [{TAG}]Note:[/{TAG}] When using &project or #tag in your shell, wrap the
    content in quotes to avoid shell interpretation:
      dwriter todo "Write unit tests #testing &backend"

    If invoked without arguments, launches the interactive todo board.

    Priority Levels:
      - low: Dimmed display, low visibility tasks
      - normal: Default priority, standard display
      - high: Yellow highlight for important tasks
      - urgent: Red highlight for critical tasks

    Examples:
      dwriter todo                         # Launch interactive TUI
      dwriter todo "Draft new relic ideas" -p Mainframe_Mayhem
      dwriter todo "Fix card draw bug" #bug &core
      dwriter todo "Write tests" --due tomorrow
      dwriter todo "Review PR" --due +5d -t code
      dwriter todo list                    # Show pending tasks
      dwriter todo list --all              # Include completed
    """
    # If a subcommand was invoked, Click handles it automatically.
    if ctx.invoked_subcommand is not None:
        return

    # Get the AppContext from parent context
    app_ctx: AppContext = ctx.obj

    # Handle pseudo-subcommands from content
    if content:
        subcommand = content[0]
        args = content[1:]

        if subcommand == "list":
            _execute_list(app_ctx, show_all, output_json)
            return
        elif subcommand == "rm" and args:
            try:
                task_id = int(args[0])
                _execute_rm(app_ctx, task_id)
            except ValueError:
                app_ctx.console.print("[red]Error: 'rm' requires a numeric task ID.[/red]")
            return
        elif subcommand == "edit" and args:
            try:
                task_id = int(args[0])
                _execute_edit(app_ctx, task_id)
            except ValueError:
                app_ctx.console.print("[red]Error: 'edit' requires a numeric task ID.[/red]")
            return
        elif subcommand == "add" and args:
            # Shift content to remove 'add' and proceed to normal add logic
            content = args
        # If it's just 'add' with no args, show error or help
        elif subcommand == "add" and not args:
            app_ctx.console.print("[red]Error: 'add' requires task content.[/red]")
            return

    # Default behavior - add task or launch TUI
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
                # Use configuration to hint at preferred input format
                due_date_format = app_ctx.config.display.due_date_format
                fmt_map = {
                    "YYYY-MM-DD": "%Y-%m-%d",
                    "MM/DD/YYYY": "%m/%d/%Y",
                    "DD/MM/YYYY": "%d/%m/%Y",
                }
                hint = fmt_map.get(due_date_format)
                
                # For todos, we generally prefer future dates
                due_date = parse_natural_date(final_due_str, prefer_future=True, format_hint=hint)
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
                if due_date.hour == 0 and due_date.minute == 0:
                    due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d')})[/dim]"
                else:
                    due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d %H:%M')})[/dim]"

            tags_str = ""
            if task.tag_names:
                tags_str = f" [{TAG}]#{' #'.join(task.tag_names)}[/{TAG}]"

            proj_str = ""
            if task.project:
                proj_str = f" [{PROJECT}]&{task.project}[/{PROJECT}]"

            app_ctx.console.print(
                f"[green]Added Task [{task.id}]:[/green] "
                f"[{color}]{task.priority.upper()}[/{color}] | "
                f"[{color}]{task.content}[/{color}]{tags_str}{proj_str}{due_str}"
            )
    else:
        # No content - launch TUI
        from ..cli import _launch_tui
        _launch_tui(app_ctx, starting_tab="todo")


def _execute_list(ctx: AppContext, show_all: bool, output_json: bool = False) -> None:
    """Internal implementation of todo list."""
    status_filter = None if show_all else "pending"
    tasks = ctx.db.get_todos(status=status_filter)

    if output_json:
        data = [
            {
                "id": t.id,
                "uuid": t.uuid,
                "content": t.content,
                "project": t.project,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "tags": t.tag_names,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ]
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return

    if not tasks:
        ctx.console.print(
            "No tasks found. Relax or add one with [bold]dwriter todo[/bold]!"
        )
        return

    table = Table(title="Your Tasks", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right", style=PROJECT, no_wrap=True)
    table.add_column("Priority", justify="center")
    table.add_column("Task")
    table.add_column("Project", style=PROJECT)
    table.add_column("Tags", style=TAG)
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
                if due_date.hour == 0 and due_date.minute == 0:
                    due_str = f"[{DUE_TODAY}]TODAY[/{DUE_TODAY}]"
                else:
                    due_str = f"[{DUE_TODAY}]{due_date.strftime('%H:%M')}[/{DUE_TODAY}]"
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


def _execute_rm(ctx: AppContext, task_id: int) -> None:
    """Internal implementation of todo rm."""
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


def _execute_edit(ctx: AppContext, task_id: int) -> None:
    """Internal implementation of todo edit."""
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
            # Use configuration to hint at preferred input format
            due_date_format = ctx.config.display.due_date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(due_date_format)
            
            # For todos, we generally prefer future dates
            due_date = parse_natural_date(final_due_str, prefer_future=True, format_hint=hint)
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
            if due_date.hour == 0 and due_date.minute == 0:
                due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d')})[/dim]"
            else:
                due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d %H:%M')})[/dim]"
        
        tags_str = ""
        if task.tag_names:
            tags_str = f" [{TAG}]#{' #'.join(task.tag_names)}[/{TAG}]"
        
        proj_str = ""
        if task.project:
            proj_str = f" [{PROJECT}]&{task.project}[/{PROJECT}]"

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
    "--json",
    "output_json",
    is_flag=True,
    help="Output data in machine-readable JSON format",
)
@click.pass_obj
def todo_list(ctx: AppContext, show_all: bool, output_json: bool) -> None:
    """List pending tasks."""
    _execute_list(ctx, show_all, output_json)


@todo.command("rm")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_rm(ctx: AppContext, task_id: int) -> None:
    """Delete a task entirely."""
    _execute_rm(ctx, task_id)


@todo.command("edit")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_edit(ctx: AppContext, task_id: int) -> None:
    """Edit a task's content interactively."""
    _execute_edit(ctx, task_id)


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

@click.command("remind")
@click.argument("content", required=True, nargs=-1)
@click.option(
    "--at",
    "due_date_str",
    required=True,
    help="When to remind you (e.g., '2pm', 'tomorrow', '+2h')",
)
@click.pass_obj
def remind(ctx: AppContext, content: tuple[Any, ...], due_date_str: str) -> None:
    """Quickly set an urgent reminder.

    Acts as a shortcut for 'todo add --priority urgent --due <time>'.
    """
    content_str = " ".join(content)

    # Use existing natural language parser
    try:
        # Use configuration to hint at preferred input format
        due_date_format = ctx.config.display.due_date_format
        fmt_map = {
            "YYYY-MM-DD": "%Y-%m-%d",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
        }
        hint = fmt_map.get(due_date_format)
        
        # Reminders explicitly prefer future dates
        due_date = parse_natural_date(due_date_str, prefer_future=True, format_hint=hint)
    except ValueError as e:
        ctx.console.print(f"[red]Error:[/red] {e}")
        return

    # Create the task as an urgent Todo
    task = ctx.db.add_todo(
        content=content_str,
        priority="urgent",  # Hardcoded to urgent for reminders
        due_date=due_date,
    )

    ctx.console.print(
        f"[green]Reminder set for {due_date.strftime('%Y-%m-%d %H:%M')}:[/green] {task.content}"
    )


@click.command("snooze")
@click.argument("task_id", type=int)
@click.option(
    "--at",
    "at_time",
    help="Snooze until a specific time (e.g., '3pm', 'tomorrow 9am')",
)
@click.option(
    "--for",
    "for_duration",
    help="Snooze for a relative duration (e.g., '30m', '2h')",
)
@click.pass_obj
def snooze(
    ctx: AppContext, task_id: int, at_time: str | None, for_duration: str | None
) -> None:
    """Delay an active reminder.

    Reschedules the task's due date. If the task wasn't already 'urgent',
    it will be marked as such to ensure it stays in the reminder loop.

    EXAMPLES:
      dwriter snooze 42 --for 15m
      dwriter snooze 42 --at 5pm
    """
    try:
        task = ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    if not at_time and not for_duration:
        ctx.console.print("[yellow]Hint:[/yellow] Use --at or --for to specify snooze time.")
        at_time = click.prompt("Snooze until? (e.g., +15m, 2pm)", type=str)

    due_str = at_time or (f"+{for_duration}" if for_duration else None)
    if not due_str:
        return

    try:
        # Use configuration to hint at preferred input format
        due_date_format = ctx.config.display.due_date_format
        fmt_map = {
            "YYYY-MM-DD": "%Y-%m-%d",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
        }
        hint = fmt_map.get(due_date_format)
        
        # Snooze always prefers future
        new_due = parse_natural_date(due_str, prefer_future=True, format_hint=hint)
    except ValueError as e:
        ctx.console.print(f"[red]Error:[/red] {e}")
        return

    ctx.db.update_todo(
        task_id,
        due_date=new_due,
        priority="urgent",  # Ensure it remains/becomes a reminder
        reminder_last_sent=None,  # Reset cooldown
    )

    ctx.console.print(
        f"[green]Snoozed Task {task_id} until {new_due.strftime('%H:%M')}[/green] "
        f"[dim]({new_due.strftime('%Y-%m-%d')})[/dim]"
    )
