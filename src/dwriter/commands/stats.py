"""Stats command - launches interactive dashboard."""

import click

from ..cli import AppContext


@click.command()
@click.pass_obj
def stats(ctx: AppContext):
    """Launch interactive dashboard.

    Displays a visual overview of your logging activity including:
    - GitHub-style contribution calendar
    - Weekly activity chart
    - Statistics summary
    - Top tags

    Examples:
        dwriter stats
    """
    from .dashboard_tui import DashboardApp

    app = DashboardApp(
        db=ctx.db,
        console=ctx.console,
    )
    app.run()
