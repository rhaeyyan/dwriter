"""remind command — quickly set an urgent reminder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ...date_utils import parse_natural_date


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
