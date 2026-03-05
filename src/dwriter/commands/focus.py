"""Focus command for running a Pomodoro timer."""

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
def focus(ctx: AppContext, minutes: int, tags: tuple, project: str):
    """Start a focus timer and log the result.

    Pomodoro-style focus timer with interactive TUI. When the timer
    completes, you're prompted to log the session as a journal entry.

    Timer Controls:
      - Space: Pause/Resume
      - +: Add 5 minutes
      - -: Subtract 5 minutes
      - Enter: Finish early
      - q/Esc: Quit

    Examples:
      dwriter focus           # Default 25-minute timer
      dwriter focus 30        # Custom duration
      dwriter focus 45 -t deepwork -p backend
    """
    # Merge default config tags/projects with provided ones
    all_tags = list(ctx.config.defaults.tags) + list(tags)
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    # Launch interactive TUI
    from .focus_tui import FocusTimerApp

    app = FocusTimerApp(
        db=ctx.db,
        console=ctx.console,
        minutes=minutes,
        tags=all_tags,
        project=project,
    )
    app.run()
