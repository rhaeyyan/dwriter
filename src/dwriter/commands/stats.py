"""Stats command - provides a text-based summary of your productivity."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click
from rich.columns import Columns
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from ..ai.engine import get_ai_client
from ..ai.schemas.extraction import AITaskNarrative
from ..analytics import AnalyticsEngine, InsightGenerator
from ..stats_utils import calculate_streak
from ..tui.colors import PROJECT, TAG


@click.command()
@click.option("--weekly", is_flag=True, help="Show the 7-day Weekly Pulse wrap-up summary.")  # noqa: E501
@click.option("--narrative", is_flag=True, help="Generate an AI-powered 'Spotify Wrapped' style narrative.")  # noqa: E501
@click.option("--json", "output_json", is_flag=True, help="Output data in machine-readable JSON format.")  # noqa: E501
@click.pass_obj
def stats(ctx: AppContext, weekly: bool, narrative: bool, output_json: bool) -> None:
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

    # Initialize analytics engine and generate insights
    engine = AnalyticsEngine(ctx.db)
    insight_gen = InsightGenerator(engine)

    if weekly:
        insights = insight_gen.generate_weekly_wrapup()
        insights_title = "🎭 Weekly Pulse Wrap-up"
    else:
        insights = insight_gen.generate_insights()
        insights_title = "💡 Behavioral Insights"

    tag_velocity = engine.get_tag_velocity(days=30)

    if output_json:
        data = {
            "streaks": {
                "current": current_streak,
                "longest": longest_streak
            },
            "counts": {
                "entries": len(entries),
                "completed_todos": len(todos_completed),
                "pending_todos": len(todos_pending)
            },
            "insights": {
                "title": insights_title,
                "items": insights
            },
            "top_tags": [
                {"tag": tag, "count": count, "trend": trend}
                for tag, count, trend in tag_velocity[:5]
            ]
        }
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return

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
        border_style=PROJECT,
        expand=False
    )

    ctx.console.print(Columns([streak_panel, counts_panel]))
    ctx.console.print()

    # Phase 5: AI Narrative
    if narrative and ctx.config.ai.enabled:
        _display_ai_narrative(ctx, engine, weekly)

    # Display insights
    if insights:
        ctx.console.print(f"[{TAG}]{insights_title}[/{TAG}]")
        for insight in (insights if weekly else insights[:3]):
            # Standardize formatting for CLI output
            clean_insight = insight.replace("[n]", "[dim]").replace("[/n]", "[/dim]")
            ctx.console.print(f" {clean_insight}")
        ctx.console.print()

    # Render tag frequency table
    tag_velocity = engine.get_tag_velocity(days=30)
    if tag_velocity:
        table = Table(title="🏷️ Top Tags (Last 30 Days)", box=None, show_header=False)
        table.add_column("Tag", style=TAG)
        table.add_column("Count", justify="right")
        table.add_column("Trend", justify="right")

        for tag, count, trend in tag_velocity[:5]:
            table.add_row(f"#{tag}", str(count), trend)

        ctx.console.print(table)
        ctx.console.print()

    ctx.console.print("[dim]Run [bold]dwriter ui[/bold] for the full interactive dashboard.[/dim]")  # noqa: E501


def _display_ai_narrative(ctx: AppContext, engine: AnalyticsEngine, weekly: bool) -> None:  # noqa: E501
    """Generate and display an AI-powered narrative summary."""
    days = 7 if weekly else 30
    since = datetime.now() - timedelta(days=days)

    entries = ctx.db.get_all_entries()
    recent_entries = [e for e in entries if e.created_at >= since]

    todos = ctx.db.get_all_todos()
    recent_todos = [t for t in todos if t.created_at >= since]
    completed = [t for t in recent_todos if t.status == "completed"]

    data_summary = (
        f"Period: Last {days} days\n"
        f"Total Entries: {len(recent_entries)}\n"
        f"Total Tasks: {len(recent_todos)}\n"
        f"Completed Tasks: {len(completed)}\n"
        f"Sample Tasks: {[t.content for t in completed[:10]]}\n"
        f"Sample Entries: {[e.content for e in recent_entries[:10]]}"
    )

    with Status("Generating AI Narrative...", console=ctx.console) as status:
        try:
            client = get_ai_client(ctx.config.ai)
            narrative = client.chat.completions.create(
                model=ctx.config.ai.chat_model,
                response_model=AITaskNarrative,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate a comprehensive, narrative-style productivity report. "  # noqa: E501
                            "Be conversational but concise. Identify the biggest win and the main struggle."  # noqa: E501
                        ),
                    },
                    {"role": "user", "content": data_summary},
                ],
            )

            ctx.console.print(Panel(
                f"[bold green]🏆 Biggest Win:[/bold green] {narrative.biggest_win}\n"
                f"[bold red]🧗 Main Struggle:[/bold red] {narrative.main_struggle}\n"
                f"[bold blue]🎯 Suggested Focus:[/bold blue] {narrative.suggested_focus}\n\n"  # noqa: E501
                f"[italic]{narrative.summary}[/italic]",
                title="✨ AI Narrative Wrap-up",
                border_style="magenta"
            ))
            ctx.console.print()
        except Exception as e:
            status.stop()
            ctx.console.print(f"[red]Error generating AI narrative:[/red] {e}\n")
