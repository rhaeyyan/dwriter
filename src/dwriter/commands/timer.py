"""Timer command - provides a simple CLI-based focus timer."""

from __future__ import annotations

import time
from typing import Any
from datetime import datetime

import click
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

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
    """Start a focus timer in the terminal.

    Runs a simple countdown progress bar. When the timer finishes,
    it automatically logs the session to your journal.

    To use the interactive TUI timer with more controls, run:
      dwriter ui --timer

    Examples:
      dwriter timer           # 25-minute timer
      dwriter timer 45        # 45-minute timer
      dwriter timer 15 -t email -p communications
    """
    # Merge default config tags/projects with provided ones
    all_tags = list(ctx.config.defaults.tags) + list(tags)
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    seconds = minutes * 60
    
    ctx.console.print(f"[bold green]Starting {minutes}-minute focus timer...[/bold green]")
    if project:
        ctx.console.print(f"Project: [purple]&{project}[/purple]")
    if all_tags:
        ctx.console.print(f"Tags: [yellow]#{' #'.join(all_tags)}[/yellow]")
    
    try:
        # Initialize and run terminal progress bar
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            console=ctx.console,
        ) as progress:
            task = progress.add_task("Focus Session", total=seconds)
            
            while not progress.finished:
                progress.update(task, advance=1)
                time.sleep(1)
        
        # Persistence: Auto-log session to database on completion
        content = f"⏱️ Finished {minutes}-minute focus session"
        ctx.db.add_entry(
            content=content,
            tags=all_tags,
            project=project,
            created_at=datetime.now()
        )
        ctx.console.print("\n[bold green]✅ Session complete and logged to journal![/bold green]")
        
    except KeyboardInterrupt:
        ctx.console.print("\n[yellow]Timer cancelled. Session not logged.[/yellow]")
