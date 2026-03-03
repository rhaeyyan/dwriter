"""Command-line interface for Day Writer.

This module provides the main entry point for the dwriter CLI application.
"""

import click

from . import __version__


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="dwriter")
def main(ctx):
    """Day Writer - A low-friction terminal journaling tool.

    Track daily tasks and generate standup summaries with minimal effort.

    Examples:
        dwriter add "fixed the race condition in auth"

        dwriter add "implemented feature X" -t feature -p myapp

        dwriter standup

        dwriter review --days 7
    """
    if ctx.invoked_subcommand is None:
        from .commands import today

        ctx.invoke(today)


def _register_commands():
    """Register all CLI commands."""
    from .commands import (
        add,
        config,
        delete,
        edit,
        examples,
        review,
        standup,
        stats,
        today,
        undo,
    )

    for cmd in [
        add,
        config,
        delete,
        edit,
        examples,
        review,
        stats,
        standup,
        today,
        undo,
    ]:
        main.add_command(cmd)


_register_commands()


if __name__ == "__main__":
    main()
