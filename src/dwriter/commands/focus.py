"""Focus command for running a Pomodoro timer."""

import time

import click
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

from ..cli import AppContext
from ..ui_utils import display_entry


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
    current_minutes = minutes
    total_minutes = 0

    ctx.console.print("[bold blue]Starting focus session...[/bold blue]")
    ctx.console.print("Press Ctrl+C to cancel entirely.\n")

    try:
        while True:
            duration_seconds = current_minutes * 60

            # Use Rich's Progress bar for a clean, single-line updating timer
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=ctx.console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]🍅 Focusing ({current_minutes}m)...", total=duration_seconds
                )

                for _ in range(duration_seconds):
                    time.sleep(1)
                    progress.advance(task)

            total_minutes += current_minutes

            # Timer finished! Sound a terminal bell
            print("\a", end="")

            ctx.console.print("\n[bold green]✅ Timer finished![/bold green]")

            # Prompt to continue or log
            response = click.prompt(
                "Add more time (in minutes) to continue, "
                "or press Enter to log your entry",
                type=str,
                default="",
                show_default=False,
            )

            response = response.strip()
            if not response:
                break  # User pressed Enter, proceed to logging

            try:
                current_minutes = int(response)
                if current_minutes <= 0:
                    break
                ctx.console.print("-" * 40)
            except ValueError:
                # Non-numeric input means user wants to stop and log
                break

    except KeyboardInterrupt:
        ctx.console.print("\n[yellow]Focus session cancelled.[/yellow]")
        return

    ctx.console.print("\n[bold blue]Focus Session Complete[/bold blue]")
    ctx.console.print(f"Total time focused: [bold]{total_minutes} minutes[/bold]")
    ctx.console.print("-" * 40)

    # Prompt the user for what they accomplished
    content = click.prompt(
        "What did you accomplish?",
        type=str,
        default=f"Completed {total_minutes}m focus session",
        show_default=False,
    )

    if not content.strip():
        ctx.console.print("Entry cancelled.")
        return

    # Merge default config tags/projects with provided ones
    all_tags = list(ctx.config.defaults.tags) + list(tags)
    if project is None and ctx.config.defaults.project:
        project = ctx.config.defaults.project

    # Save to database using the existing context
    entry = ctx.db.add_entry(
        content=content,
        tags=all_tags,
        project=project,
    )

    # Display confirmation matching the standard add command
    if ctx.config.display.show_confirmation:
        display_entry(ctx.console, entry, ctx.config)
