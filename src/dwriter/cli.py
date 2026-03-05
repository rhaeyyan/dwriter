"""Command-line interface for dwriter.

This module provides the main entry point for the dwriter CLI application.
"""

from __future__ import annotations

import click
from rich.console import Console

from . import __version__
from .config import ConfigManager
from .database import Database


class DWriterError(Exception):
    """Base exception for dwriter errors."""

    pass


class DatabaseError(DWriterError):
    """Exception raised for database-related errors."""

    pass


class ConfigError(DWriterError):
    """Exception raised for configuration-related errors."""

    pass


class AppContext:
    """Application context for dependency injection.

    This class holds shared instances of Console, ConfigManager, and Database
    that are injected into CLI commands via Click's context mechanism.

    Attributes:
        console: Rich console for formatted output.
        config: Configuration manager instance.
        db: Database instance.
    """

    def __init__(self) -> None:
        """Initialize the application context."""
        self.console = Console()
        try:
            self.config_manager = ConfigManager()
            self.config = self.config_manager.load()
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}") from e

        try:
            self.db = Database()
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}") from e


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="dwriter")
def main(ctx: click.Context) -> None:
    """Dwriter - A low-friction terminal journaling tool.

    Track daily tasks and generate standup summaries with minimal effort.

    Quick Start:
      dwriter add "fixed the race condition in auth"
      dwriter add "implemented feature X" -t feature -p myapp
      dwriter todo "write unit tests" --priority high
      dwriter done 1
      dwriter standup
      dwriter review --days 7

    Interactive TUI Modes:
      dwriter search    - Fuzzy search with live filtering
      dwriter todo      - Interactive todo board
      dwriter edit      - Edit today's entries
      dwriter focus     - Pomodoro timer
      dwriter stats     - Dashboard with calendar & charts

    Common Commands:
      add       - Log a new entry
      todo      - Manage tasks
      done      - Complete a task
      standup   - Generate yesterday's summary
      review    - Review last N days
      search    - Fuzzy search entries/todos
      focus     - Start focus timer
      stats     - View statistics dashboard
      edit      - Edit entries
      config    - Manage settings
    """
    try:
        ctx.obj = AppContext()
    except DWriterError as e:
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {e}")
        ctx.exit(1)

    if ctx.invoked_subcommand is None:
        from .commands import today

        ctx.invoke(today)


def _register_commands() -> None:
    """Register all CLI commands."""
    from .commands import (
        add,
        config,
        delete,
        done,
        edit,
        examples,
        focus,
        help_cmd,
        review,
        search,
        standup,
        stats,
        today,
        todo,
        undo,
    )

    for cmd in [
        add,
        config,
        delete,
        done,
        edit,
        examples,
        focus,
        help_cmd,
        review,
        search,
        stats,
        standup,
        today,
        todo,
        undo,
    ]:
        main.add_command(cmd)


_register_commands()


if __name__ == "__main__":
    main()
