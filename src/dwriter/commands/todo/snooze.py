"""snooze command — delay an active reminder."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ...date_utils import parse_natural_date


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

    Examples:
      dwriter snooze 42 --for 15m
      dwriter snooze 42 --at 5pm
    """
    try:
        ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    if not at_time and not for_duration:
        ctx.console.print("[yellow]Hint:[/yellow] Use --at or --for to specify snooze time.")  # noqa: E501
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
