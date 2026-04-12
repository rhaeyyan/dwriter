"""todo add subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ...date_utils import parse_natural_date
from ...tui.colors import PROJECT, TAG
from ._group import todo


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
    from ...tui.parsers import parse_todo_add
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
