"""Interactive help command."""

import click

from ..cli import AppContext


@click.command()
@click.option(
    "--plain",
    is_flag=True,
    help="Show plain text output (for piping/grep)",
)
@click.pass_obj
def help_cmd(ctx: AppContext, plain: bool) -> None:
    """Show interactive help browser.

    Launches an interactive TUI help browser by default.
    Use --plain for standard Click help output.
    """
    if plain:
        # Show standard Click help
        from ..cli import main

        click.echo(main.get_help(click.Context(main)))
    else:
        from .help_tui import HelpApp

        app = HelpApp()
        should_open_tui = app.run()

        # If user exits help with 'q' or 'escape', launch the main TUI
        if should_open_tui:
            from ..tui.app import DWriterApp

            master_app = DWriterApp(ctx)
            master_app.run()
