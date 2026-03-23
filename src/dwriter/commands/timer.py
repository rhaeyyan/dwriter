"""Timer command - provides a simple CLI-based focus timer."""

from __future__ import annotations

import time
from typing import Any
from datetime import datetime

import click
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from ..cli import AppContext


@click.command()
@click.argument("args", nargs=-1)
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
    ctx: AppContext, args: tuple[str, ...], tags: tuple[Any, ...], project: str | None
) -> None:
    """Start a focus timer in the terminal.

    Runs a simple countdown progress bar. When the timer finishes,
    it automatically logs the session to your journal.

    You can provide minutes, tags (#tag), and projects (&project)
    directly as arguments or use explicit options.

    [bold yellow]Note:[/bold yellow] When using shorthand like &project or #tag in your shell,
    wrap the command in quotes to avoid shell interpretation:
      dwriter timer "25 &work #deepwork"

    To use the interactive TUI timer with more controls, run:
      dwriter ui --timer

    Examples:
      dwriter timer           # 25-minute timer
      dwriter timer 45        # 45-minute timer
      dwriter timer 15 -t email -p communications
      dwriter timer "15 #email &work"
    """
    minutes = 25
    parsed_tags = []
    parsed_project = None
    parsed_content = None

    if args:
        from ..tui.parsers import parse_timer, parse_quick_add
        arg_str = " ".join(args)
        parsed = parse_timer(arg_str)
        
        if parsed:
            minutes = parsed.minutes
            parsed_tags = parsed.tags
            parsed_project = parsed.project
            parsed_content = parsed.content
        else:
            # If minutes aren't found, try parsing as a regular entry to get tags/project
            # and default to 25 minutes.
            quick_parsed = parse_quick_add(arg_str)
            parsed_tags = quick_parsed.tags
            parsed_project = quick_parsed.project
            parsed_content = quick_parsed.content
            
            # Check if any part of the content can be parsed as minutes
            try:
                for word in arg_str.split():
                    if word.isdigit():
                        minutes = int(word)
                        break
            except (ValueError, IndexError):
                pass

    # Merge default config tags/projects with provided ones
    all_tags = list(ctx.config.defaults.tags) + list(parsed_tags) + list(tags)
    
    # Use explicitly provided project, then parsed project, then default
    if project is None:
        project = parsed_project or ctx.config.defaults.project

    seconds = minutes * 60
    
    ctx.console.print(f"[bold green]Starting {minutes}-minute focus timer...[/bold green]")
    if project:
        ctx.console.print(f"Project: [purple]&{project}[/purple]")
    if all_tags:
        ctx.console.print(f"Tags: [yellow]#{' #'.join(all_tags)}[/yellow]")
    if parsed_content:
        ctx.console.print(f"Focus: [white]{parsed_content}[/white]")
    
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
        log_content = f"⏱️ Finished {minutes}-minute focus session"
        if parsed_content:
            log_content += f": {parsed_content}"
            
        ctx.db.add_entry(
            content=log_content,
            tags=all_tags,
            project=project,
            created_at=datetime.now()
        )
        ctx.console.print("\n[bold green]✅ Session complete and logged to journal![/bold green]")
        
    except KeyboardInterrupt:
        ctx.console.print("\n[yellow]Timer cancelled. Session not logged.[/yellow]")
