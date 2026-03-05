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

    MINUTES: Duration of the focus session in minutes (default: 25).

    Examples:
        dwriter focus

        dwriter focus 30

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
