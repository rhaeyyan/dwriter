"""Help command - provides CLI help and TUI guidance."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click


@click.command()
@click.pass_obj
def help_cmd(ctx: AppContext) -> None:
    """Show dwriter help and usage information.

    Displays the standard command-line help.
    To launch the interactive TUI dashboard, just run:
      dwriter
    """
    from ..cli import main

    ctx.console.print("[bold blue]Dwriter Help[/bold blue]\n")
    click.echo(main.get_help(click.Context(main)))

    ctx.console.print("\n[dim]Tip: Run [bold]dwriter ui[/bold] for the interactive TUI command center.[/dim]")  # noqa: E501
