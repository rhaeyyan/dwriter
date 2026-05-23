"""Todo command group definition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ...date_utils import parse_natural_date
from ...tui.colors import PROJECT, TAG
from ._helpers import _execute_edit, _execute_list, _execute_rm


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"], "allow_interspersed_args": True},  # noqa: E501
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
                app_ctx.console.print("[red]Error: 'rm' requires a numeric task ID.[/red]")  # noqa: E501
            return
        elif subcommand == "edit" and args:
            try:
                task_id = int(args[0])
                _execute_edit(app_ctx, task_id)
            except ValueError:
                app_ctx.console.print("[red]Error: 'edit' requires a numeric task ID.[/red]")  # noqa: E501
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
        from ...tui.parsers import parse_todo_add
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
                due_date = parse_natural_date(final_due_str, prefer_future=True, format_hint=hint)  # noqa: E501
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
                    due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d %H:%M')})[/dim]"  # noqa: E501

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
        from ...cli import _launch_tui
        _launch_tui(app_ctx, starting_tab="todo")
