"""Stats command - launches interactive dashboard."""

import click

from ..cli import AppContext
from ..stats_utils import calculate_streak


@click.command()
@click.pass_obj
def stats(ctx: AppContext):
    """Launch interactive dashboard.

    Displays a visual overview of your logging activity including:

    Dashboard Features:
      - GitHub-style contribution calendar
      - Current and longest streak tracking
      - Weekly activity bar chart (last 8 weeks)
      - Statistics summary (total entries, tasks, tags, projects)
      - Top 10 tags with usage bars

    Keybindings:
      - Tab: Navigate between sections
      - r: Refresh all data
      - q/Esc: Quit

    Examples:
      dwriter stats
    """
    from .dashboard_tui import DashboardApp

    app = DashboardApp(
        db=ctx.db,
        console=ctx.console,
    )
    app.run()
