"""Stats command - provides a text-based summary of your productivity."""

from __future__ import annotations

import click
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table

from ..cli import AppContext
from ..stats_utils import calculate_streak
from ..analytics import AnalyticsEngine, InsightGenerator


@click.command()
@click.pass_obj
def stats(ctx: AppContext) -> None:
    """View a text-based summary of your productivity.

    Displays your current streaks, total counts, and behavioral insights
    directly in the terminal.

    To view the full interactive dashboard, run:
      dwriter ui
    """
    # Initialize components and gather analytics
    entries = ctx.db.get_all_entries()
    todos_pending = ctx.db.get_todos(status="pending")
    todos_completed = ctx.db.get_todos(status="completed")
    
    # Process streak metrics
    entry_dates = [e.created_at for e in entries]
    current_streak, longest_streak = calculate_streak(entry_dates)
    
    # Initialize analytics engine and generate behavioral insights
    engine = AnalyticsEngine(ctx.db)
    insight_gen = InsightGenerator(engine)
    insights = insight_gen.generate_insights()
    
    # Render summary to the console
    ctx.console.print("[bold blue]📊 Productivity Summary[/bold blue]\n")
    
    # Render Streak and Activity overview panels
    streak_panel = Panel(
        f"[bold cyan]{current_streak}[/bold cyan] days (Current)\n"
        f"[dim]{longest_streak} days (Longest)[/dim]",
        title="🔥 Streak",
        border_style="cyan",
        expand=False
    )
    
    counts_panel = Panel(
        f"📝 [bold]{len(entries)}[/bold] Entries\n"
        f"✅ [bold]{len(todos_completed)}[/bold] Completed\n"
        f"⏳ [bold]{len(todos_pending)}[/bold] Pending",
        title="📈 Activity",
        border_style="magenta",
        expand=False
    )
    
    ctx.console.print(Columns([streak_panel, counts_panel]))
    ctx.console.print()
    
    # Display behavioral insights
    if insights:
        ctx.console.print("[bold yellow]💡 Behavioral Insights[/bold yellow]")
        for insight in insights[:3]:  # Top-ranked insights
            # Standardize formatting for CLI output
            clean_insight = insight.replace("[n]", "[dim]").replace("[/n]", "[/dim]")
            ctx.console.print(f" {clean_insight}")
        ctx.console.print()

    # Render tag frequency table
    tag_velocity = engine.get_tag_velocity(days=30)
    if tag_velocity:
        table = Table(title="🏷️ Top Tags (Last 30 Days)", box=None, show_header=False)
        table.add_column("Tag", style="bold yellow")
        table.add_column("Count", justify="right")
        table.add_column("Trend", justify="right")
        
        for tag, count, trend in tag_velocity[:5]:
            table.add_row(f"#{tag}", str(count), trend)
        
        ctx.console.print(table)
        ctx.console.print()

    ctx.console.print("[dim]Run [bold]dwriter ui[/bold] for the full interactive dashboard.[/dim]")
