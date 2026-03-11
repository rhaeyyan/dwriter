"""Examples command - redirects to unified help page."""

import click

from ..cli import AppContext


@click.command()
@click.option(
    "--plain",
    is_flag=True,
    help="Show plain text output (for piping/grep)",
)
@click.pass_obj
def examples(ctx: AppContext, plain: bool) -> None:
    """Show usage examples and workflows.

    Opens the unified help page with integrated examples.
    Use --plain for text output (suitable for piping to grep/less).
    """
    from .help_tui import HelpApp

    if plain:
        # Show plain text help from main CLI
        from ..cli import main

        click.echo(main.get_help(click.Context(main)))
    else:
        # Launch unified help TUI
        app = HelpApp()
        app.run()
