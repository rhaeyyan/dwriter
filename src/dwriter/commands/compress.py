"""Compression command for generating weekly activity summaries.

This module provides the 'compress' command, which aggregates and summarizes
weekly user activity into a structured format for long-term historical retrieval.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click
from rich.panel import Panel
from rich.status import Status


@click.command()
@click.option(
    "--force",
    is_flag=True,
    help="Re-generate even if a summary already exists for this period.",
)
@click.pass_obj
def compress(ctx: AppContext, force: bool) -> None:
    """Aggregates and summarizes the previous week's activity using AI.

    The command pre-computes a structured weekly retrospective that serves as
    long-term memory for the AI assistant, allowing for efficient historical
    trend analysis.

    Args:
        ctx: The application context.
        force: If True, regenerates the summary even if one already exists
            for the period.

    Examples:
        dwriter compress            # Summarize the previous week
        dwriter compress --force    # Re-generate an existing summary
    """
    if not ctx.config.ai.enabled:
        ctx.console.print("[yellow]AI features are disabled in config.[/yellow]")
        return

    from ..ai.summarizer import compress_week, get_week_bounds

    period_start, period_end = get_week_bounds()

    # Verify if a summary for the current period already exists
    existing = ctx.db.get_latest_summary(summary_type="weekly")
    if existing and not force:
        if existing.period_start == period_start:
            ctx.console.print(
                f"[dim]Summary for week of "
                f"{period_start.strftime('%b %d')} already exists. "
                f"Use [bold]--force[/bold] to regenerate.[/dim]"
            )
            return

    ctx.console.print(
        f"[bold #cba6f7]Compressing week of "
        f"{period_start.strftime('%b %d')} — "
        f"{period_end.strftime('%b %d')}...[/bold #cba6f7]"
    )

    with Status(
        "[bold #cba6f7]Running AI summarization...[/bold #cba6f7]",
        console=ctx.console,
    ):
        try:
            summary = compress_week(
                db=ctx.db,
                config=ctx.config.ai,
                period_start=period_start,
                period_end=period_end,
            )
        except Exception as e:
            ctx.console.print(f"\n[red]Summarization failed:[/red] {e}")
            ctx.console.print(
                "[dim]Ensure Ollama is running with the configured model.[/dim]"
            )
            return

    # Format the summary for console display
    wins = "\n".join(f"  • {w}" for w in summary.biggest_wins)
    friction = "\n".join(f"  • {f}" for f in summary.friction_points)
    projects = ", ".join(f"&{p}" for p in summary.key_projects) or "None"
    tags = ", ".join(f"#{t}" for t in summary.key_tags) or "None"

    output = (
        f"[bold green]Wins:[/bold green]\n{wins}\n\n"
        f"[bold red]Friction:[/bold red]\n{friction}\n\n"
        f"[bold cyan]Mood:[/bold cyan] {summary.dominant_mood}\n"
        f"[bold cyan]Velocity:[/bold cyan] {summary.velocity}\n"
        f"[bold cyan]Projects:[/bold cyan] {projects}\n"
        f"[bold cyan]Tags:[/bold cyan] {tags}"
    )

    ctx.console.print(
        Panel(
            output,
            title=f"📦 Weekly Summary — {period_start.strftime('%b %d')}",
            border_style="#cba6f7",
        )
    )
    ctx.console.print("[green]✅ Summary saved to long-term memory.[/green]")
