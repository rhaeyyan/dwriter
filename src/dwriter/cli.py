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
        
        self._reminders_shown = False

    def check_reminders(self, silent: bool = False, force: bool = False) -> None:
        """Check for active reminders and print a footer alert.

        Args:
            silent: If True, only prints reminders, no header.
            force: If True, ignores the 1-hour cooldown and shows all active reminders.
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
            if not silent:
                self.console.print("\n[bold red]🔔 ACTIVE REMINDERS:[/bold red]")
            self._reminders_shown = True
            for r in reminders:
                if r.due_date.hour == 0 and r.due_date.minute == 0:
                    due_str = r.due_date.strftime("%Y-%m-%d")
                else:
                    due_str = r.due_date.strftime("%I:%M %p")
                
                self.console.print(
                    f"  [red]![/red] [{r.id}] {r.content} (Due: {due_str})"
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
            self.console.print("[green]No active reminders. You're all caught up![/green]")


@click.group(invoke_without_command=True)
@click.option(
    "--check-only", is_flag=True, help="Run reminder checks silently and exit."
)
@click.pass_context
@click.version_option(version=__version__, prog_name="dwriter")
def main(ctx: click.Context, check_only: bool) -> None:
    """Dwriter - A minimalist journal for the terminal.
... (rest of docstring)
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


@click.command()
@click.pass_obj
def reminders(ctx: AppContext) -> None:
    """Show active reminders (urgent tasks due soon)."""
    ctx.check_reminders(silent=False, force=True)


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
        remind,
        search,
        snooze,
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
        remind,
        reminders,
        search,
        snooze,
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
