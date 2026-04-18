"""Command-line interface for dwriter.

This module provides the main entry point for the dwriter CLI application.
"""

from __future__ import annotations

from typing import Any

import click
from rich.console import Console

from . import __version__
from .config import ConfigManager
from .database import Database


class DWriterError(Exception):
    """Base exception class for all dwriter-specific errors."""

    pass


class DatabaseError(DWriterError):
    """Exception raised when a database operation fails."""

    pass


class ConfigError(DWriterError):
    """Exception raised when configuration loading or validation fails."""

    pass


class AppContext:
    """Application context for dependency injection.

    Maintains shared instances of the console, configuration, and database
    access layers. This context is passed to Click commands to ensure consistent
    resource usage across the CLI.

    Attributes:
        console (Console): Rich console instance for formatted terminal output.
        config_manager (ConfigManager): Manager for loading and saving settings.
        config (Config): The active application configuration.
        db (Database): Database interface for entries and tasks.
        app (Any): Reference to the active TUI App instance (if running).
    """

    def __init__(self) -> None:
        """Initializes the application context and core services.

        Raises:
            ConfigError: If the configuration cannot be loaded.
            DatabaseError: If the database cannot be initialized.
        """
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

        self._reminders_shown = False
        self.app: Any = None

    def save_config(self) -> None:
        """Saves the active configuration to the user's config file."""
        try:
            self.config_manager.save(self.config)
        except Exception as e:
            self.console.print(f"[red]Error saving configuration: {e}[/red]")

    def check_reminders(self, silent: bool = False, force: bool = False) -> None:
        """Evaluates pending urgent tasks and displays reminder alerts.

        Scans for 'urgent' priority tasks that are past due or due within the
        next 30 minutes. Prevents spam by enforcing a 1-hour cooldown between
        reminders unless forced.

        Args:
            silent (bool): If True, suppresses the header and only shows tasks.
            force (bool): If True, bypasses the cooldown and shows all matches.
        """
        # Skip if already shown in this session (unless forced)
        if self._reminders_shown and not force:
            return

        from datetime import datetime, timedelta

        now = datetime.now()
        # Find pending, urgent tasks with a due date in the past or next 30 mins
        todos = self.db.get_todos(status="pending")
        reminders = [
            t
            for t in todos
            if t.priority == "urgent"
            and t.due_date
            and t.due_date <= now + timedelta(minutes=30)
            and (
                force
                or t.reminder_last_sent is None
                or t.reminder_last_sent < now - timedelta(hours=1)
            )
        ]

        if reminders:
            from .tui.colors import REMINDER_COLOR
            if not silent:
                self.console.print(f"\n[{REMINDER_COLOR}]🔔 ACTIVE REMINDERS:[/{REMINDER_COLOR}]")  # noqa: E501
            self._reminders_shown = True
            for r in reminders:
                if r.due_date:
                    if r.due_date.hour == 0 and r.due_date.minute == 0:
                        due_str = r.due_date.strftime("%Y-%m-%d")
                    else:
                        due_str = r.due_date.strftime("%I:%M %p")
                else:
                    due_str = "No due date"

                self.console.print(
                    f"  [{REMINDER_COLOR}]![/{REMINDER_COLOR}] [{r.id}] {r.content} (Due: {due_str})"  # noqa: E501
                )

                # Update the database so we don't spam them repeatedly
                if not force:
                    self.db.update_todo(r.id, reminder_last_sent=now)

            # Add OS notification check
            if self.config.display.notifications_enabled and not force:
                from .ui_utils import send_system_notification

                for r in reminders:
                    send_system_notification("dwriter Reminder", r.content)
        elif not silent and force:
            self.console.print("[green]No active reminders. You're all caught up![/green]")  # noqa: E501


@click.group(invoke_without_command=True)
@click.option(
    "--check-only", is_flag=True, help="Run reminder checks silently and exit."
)
@click.pass_context
@click.version_option(version=__version__, prog_name="dwriter")
def main(ctx: click.Context, check_only: bool) -> None:
    """Dwriter - A minimalist journal and productivity tool for the terminal.

    Supports natural language date parsing, hashtags (#tag), and project
    tagging (&project).

    Example Usage (Headless CLI):
      dwriter add "Refactored the database layer #dev &dwriter"
      dwriter todo "Complete project documentation @due Friday"

    Example Usage (Visual Dashboard):
      dwriter (no arguments launches the TUI)
    """
    try:
        ctx.obj = AppContext()
    except DWriterError as e:
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {e}")
        ctx.exit(1)

    if check_only:
        ctx.obj.check_reminders(silent=True)
        ctx.exit()

    # We use Click's call_on_close to ensure it prints AFTER the main command output
    ctx.call_on_close(lambda: ctx.obj.check_reminders())

    if ctx.invoked_subcommand is None:
        _launch_tui(ctx.obj)
    else:
        # Commands are registered at the bottom but we ensure they are available
        pass


def _launch_tui(ctx_obj: AppContext, starting_tab: str | None = None) -> None:
    """Initializes and runs the Textual-based User Interface (TUI).

    Configures the terminal environment and launches the unified application.

    Args:
        ctx_obj (AppContext): The application context.
        starting_tab (str | None): The initial screen to display.
            If None, the app decides based on configuration.
    """
    import sys

    # Force UTF-8 encoding for terminal output to prevent character distortion
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    # Set terminal dimensions to recommended default size
    sys.stdout.write("\x1b[8;42;88t")
    sys.stdout.flush()

    # Launch the unified TUI
    from .tui.app import DWriterApp

    app = DWriterApp(ctx_obj, starting_tab=starting_tab)
    app.run()


@click.command()
@click.option("--dashboard", "tab", flag_value="dashboard", help="Start on dashboard screen")  # noqa: E501
@click.option("--2brain", "tab", flag_value="second-brain", help="Start on 2nd-Brain screen")  # noqa: E501
@click.option("--logs", "tab", flag_value="logs", help="Start on logs tab")
@click.option("--todo", "tab", flag_value="todo", help="Start on todo tab")
@click.option("--timer", "tab", flag_value="timer", help="Start on timer tab")
@click.option("--search", "tab", flag_value="logs", help="Start on search (logs) tab")
@click.option("--settings", "tab", flag_value="settings", help="Start on settings tab")
@click.pass_obj
def ui(ctx: AppContext, tab: str | None) -> None:
    """Launches the interactive Visual Dashboard (TUI)."""
    _launch_tui(ctx, starting_tab=tab)


@click.command()
@click.pass_obj
def reminders(ctx: AppContext) -> None:
    """Displays all active reminders for urgent tasks."""
    ctx.check_reminders(silent=False, force=True)


def _register_commands() -> None:
    """Registers all available subcommands to the main Click group."""
    from .commands import (
        add,
        ask,
        compress,
        config,
        delete,
        done,
        edit,
        examples,
        graph,
        help_cmd,
        install_notifications,
        remind,
        review,
        search,
        snooze,
        standup,
        stats,
        sync,
        timer,
        today,
        todo,
        undo,
        uninstall_notifications,
    )


    # Dispatch and register commands to the main group
    for cmd in [
        add,
        ask,
        compress,
        config,
        delete,
        done,
        edit,
        examples,
        graph,
        install_notifications,
        timer,
        help_cmd,
        review,
        remind,
        reminders,
        search,
        snooze,
        stats,
        standup,
        sync,
        today,
        todo,
        ui,
        undo,
        uninstall_notifications,
    ]:
        main.add_command(cmd)



# Register commands immediately after definition to make them available for the group
_register_commands()


if __name__ == "__main__":
    main()
