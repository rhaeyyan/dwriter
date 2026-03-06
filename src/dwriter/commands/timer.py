"""Timer command for running a pomodoro-style timer."""

from __future__ import annotations

from typing import Any

import click

from ..cli import AppContext


@click.command()
@click.argument("minutes", type=int, default=25)
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Tags to apply to the resulting entry",
)
@click.option(
    "-p",
    "--project",
    "project",
    default=None,
    help="Project to apply to the resulting entry",
)
@click.pass_obj
def timer(
    ctx: AppContext, minutes: int, tags: tuple[Any, ...], project: str | None
) -> None:
    """Start a timer and log the result.

    Pomodoro-style timer with interactive TUI. When the timer
    completes, you're prompted to log the session as a journal entry.

    Timer Controls:
      - Space: Pause/Resume
      - +: Add 5 minutes
      - -: Subtract 5 minutes
      - Enter: Finish early
      - q/Esc: Quit

    Examples:
      dwriter timer           # Default 25-minute timer
      dwriter timer 30        # Custom duration
      dwriter timer 45 -t deepwork -p backend
    """
    # Merge default config tags/projects with provided ones
    all_tags = list(ctx.config.defaults.tags) + list(tags)
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    # Launch interactive TUI
    from .timer_tui import TimerApp

    app = TimerApp(
        db=ctx.db,
        console=ctx.console,
        minutes=minutes,
        tags=all_tags,
        project=project,
    )
    app.run()
