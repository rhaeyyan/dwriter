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
    """Dwriter - A minimalist journal for the terminal.

    Capture your work without breaking your flow and generate summaries for
    standups or reviews.

    Quick Start:
      dwriter                      # Launch the Unified TUI
      dwriter add "fixed the bug"  # Headless CLI: Quick log
      dwriter todo "write tests"   # Headless CLI: Add task
      dwriter standup              # Generate yesterday's summary

    Unified TUI:
      Run 'dwriter' to launch the interactive dashboard with:
      - Statistics and activity maps
      - Todo board for task management
      - Focus timer for deep work sessions
      - Live fuzzy search across history

    Common Commands:
      add       - Log a new journal entry
      todo      - Manage tasks (Headless CLI)
      done      - Complete a task and log it
      standup   - Generate a summary of yesterday's work
      review    - Review entries from the last N days
      search    - Fuzzy search history (Headless CLI)
      timer     - Focus timer (Headless CLI)
      stats     - Productivity summary (Headless CLI)
      ui        - Launch the interactive dashboard
    """
    try:
        ctx.obj = AppContext()
    except DWriterError as e:
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {e}")
        ctx.exit(1)

    if ctx.invoked_subcommand is None:
        _launch_tui(ctx.obj)
    else:
        # Commands are registered at the bottom but we ensure they are available
        pass


def _launch_tui(ctx_obj: AppContext, starting_tab: str = "dashboard") -> None:
    """Launch the unified TUI.

    Args:
        ctx_obj: Application context.
        starting_tab: The screen to show on launch.
    """
    import sys

    # Force UTF-8 encoding for terminal output to prevent mojibake/character distortion
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    # Force terminal resize to exactly 42 rows by 88 columns (default size)
    sys.stdout.write("\x1b[8;42;88t")
    sys.stdout.flush()

    # Launch the unified TUI
    from .tui.app import DWriterApp

    app = DWriterApp(ctx_obj, starting_tab=starting_tab)
    app.run()


@click.command()
@click.option("--dashboard", "tab", flag_value="dashboard", help="Start on dashboard tab")
@click.option("--logs", "tab", flag_value="logs", help="Start on logs tab")
@click.option("--todo", "tab", flag_value="todo", help="Start on todo tab")
@click.option("--timer", "tab", flag_value="timer", help="Start on timer tab")
@click.option("--search", "tab", flag_value="logs", help="Start on search (logs) tab")
@click.option("--settings", "tab", flag_value="settings", help="Start on settings tab")
@click.pass_obj
def ui(ctx: AppContext, tab: str | None) -> None:
    """Launch the interactive Unified TUI."""
    _launch_tui(ctx, starting_tab=tab or "dashboard")


def _register_commands() -> None:
    """Register all CLI commands."""
    from .commands import (
        add,
        config,
        delete,
        done,
        edit,
        examples,
        help_cmd,
        review,
        search,
        standup,
        stats,
        timer,
        today,
        todo,
        undo,
    )

    # Dispatch and register commands to the main group
    for cmd in [
        add,
        config,
        delete,
        done,
        edit,
        examples,
        timer,
        help_cmd,
        review,
        search,
        stats,
        standup,
        today,
        todo,
        ui,
        undo,
    ]:
        main.add_command(cmd)


# Register commands immediately after definition to make them available for the group
_register_commands()


if __name__ == "__main__":
    main()
