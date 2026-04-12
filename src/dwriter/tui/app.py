"""Unified master app for dwriter TUI.

This module provides the main application class that manages all screens
and provides the global omnibox for quick entry logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import CommandPalette
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import (
    Button,
    ContentSwitcher,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Tab,
    Tabs,
)

from .app_omnibox import OmniboxMixin
from .command_palette import DWriterCommands
from .messages import EntryAdded, SyncStatus, TimerStateChanged, TodoUpdated
from .reminder_coordinator import ReminderCoordinator
from .todo_workflow import TodoWorkflow
from ..sync.coordinator import SyncCoordinator
from .widgets.omnibox import Omnibox
from .parsers import (
    ParsedEntry,
    ParsedTimer,
    ParsedTodo,
    parse_quick_add,
    parse_timer,
    parse_todo_add,
)
from .colors import get_icon
from .themes import THEMES


class DWriterApp(OmniboxMixin, App[None]):
    """Unified Master App for dwriter.

    This app provides a single interface for all dwriter functionality:
    - Dashboard with statistics and calendar
    - Todo board for task management
    - Timer for timer-style sessions
    - Search for fuzzy finding entries and tasks
    - Global omnibox for quick entry logging

    Key bindings:
        Ctrl+P: Open command palette
        /: Focus omnibox (quick-add)
        1-4: Switch between screens
        q: Quit
    """

    TITLE = "dwriter"
    SUB_TITLE = "dwriter"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("/", "focus_omnibox", "Quick Add", show=True),
        Binding("escape", "blur_omnibox", "Unfocus", show=False),
        Binding("1", "switch_mode('dashboard')", "Dashboard", show=False),
        Binding("2", "switch_mode('logs')", "Logs", show=False),
        Binding("3", "switch_mode('todo')", "To-Do", show=False),
        Binding("4", "switch_mode('timer')", "Timer", show=False),
        Binding("5", "switch_mode('settings')", "Settings", show=False),
    ]

    permanent_omnibox = reactive(False)
    sync_status = reactive("Synced")
    git_branch = reactive("")

    def __init__(self, ctx: AppContext, starting_tab: str = "dashboard") -> None:
        """Initialize the dwriter application.

        Args:
            ctx: Application context containing database and configuration.
            starting_tab: The screen to show on launch.
        """
        super().__init__()
        self.ctx = ctx
        self._current_screen: str = starting_tab
        self._todo_workflow = TodoWorkflow(self)
        self._timer_running: bool = False
        self._reminder = ReminderCoordinator(self)
        self._sync = SyncCoordinator(self)

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(show_clock=True)

        # Omnibox - Top command palette for frictionless entry
        date_fmt = self.ctx.config.display.date_format

        # Check config and determine initial visibility class
        is_permanent = self.ctx.config.display.permanent_omnibox
        hidden_class = "" if is_permanent else "hidden"

        with Horizontal(id="omnibox-container", classes=hidden_class):
            yield Omnibox(
                placeholder=f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}",
                id="quick-add",
            )

        with Horizontal(id="omnibox-footer", classes=hidden_class):
            yield Label(
                f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}",
                id="omnibox-hint",
            )
            yield Button("Help", id="help-btn", variant="default")

        # Horizontal Navigation Tabs
        yield Tabs(
            Tab("\\[ DASH ]", id="dashboard"),
            Tab("\\[ LOGS ]", id="logs"),
            Tab("\\[ TO-DO ]", id="todo"),
            Tab("\\[ TIMER ]", id="timer"),
            Tab("", id="tab-spacer", disabled=True),
            Tab("\\[ SETTINGS ]", id="settings"),
            active=self._current_screen,
            id="navigation-tabs",
        )

        # Content Switcher for screen management
        with ContentSwitcher(initial=self._current_screen, id="content-area"):
            from .screens.dashboard import DashboardScreen
            from .screens.logs import LogsScreen
            from .screens.timer import TimerScreen
            from .screens.todo import TodoScreen
            from .screens.configure import ConfigureScreen

            yield DashboardScreen(self.ctx, id="dashboard")
            yield LogsScreen(self.ctx, id="logs")
            yield TodoScreen(self.ctx, id="todo")
            yield TimerScreen(self.ctx, id="timer")
            yield ConfigureScreen(self.ctx, id="settings")

        with Horizontal(id="status-bar"):
            yield Label("", id="status-git")
            yield Label("", id="status-task")

        # Single Footer
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application state."""
        # Detect git branch for status bar
        from ..git_utils import get_git_info
        git_info = get_git_info()
        if git_info:
            self.git_branch = git_info["branch"]

        # Register custom themes
        for theme in THEMES.values():
            self.register_theme(theme)

        # Load and apply configuration
        config = self.ctx.config_manager.load()

        # Apply theme by name
        theme_name = config.display.theme
        if theme_name in THEMES:
            self.theme = theme_name

        # Apply ergonomic mode
        if config.display.ergonomic_mode:
            self.add_class("ergonomic-mode")

        # Sync permanent omnibox setting
        self.permanent_omnibox = config.display.permanent_omnibox

        self.call_after_refresh(self._set_default_size)
        self._update_omnibox_placeholder(self._current_screen)

        # Explicit initial sync of visibility
        self._sync_omnibox_visibility()

        # Keep navigation tabs focused to prevent omnibox from stealing focus
        self.query_one("#navigation-tabs").focus()

        # Background interval to keep omnibox visibility consistent
        self.set_interval(0.2, self._sync_omnibox_visibility)

        # Start background reminder checker if notifications are enabled
        if self.ctx.config.display.notifications_enabled:
            self._reminder.start()

        # Trigger initial background sync pull if auto_sync is enabled
        if self.ctx.config.defaults.auto_sync:
            self._sync.trigger_pull()

    def on_unmount(self) -> None:
        """Cancel the background reminder thread on exit."""
        self._reminder.stop()

    def _set_default_size(self) -> None:
        """Set the default terminal size."""
        self.set_size(90, 45)

    def on_sync_status(self, message: SyncStatus) -> None:
        """Update sync_status reactive from background sync."""
        self.sync_status = message.message

    def watch_git_branch(self, value: str) -> None:
        """Update git branch in status bar."""
        try:
            label = self.query_one("#status-git", Label)
            label.update(f" {value}" if value else "")
        except Exception:
            pass

    def watch_sync_status(self, value: str) -> None:
        """Update sync status in status bar."""
        self._update_status_task()

    def _update_status_task(self) -> None:
        """Update the status-task label with current sync status."""
        try:
            label = self.query_one("#status-task", Label)
            if self.sync_status == "Syncing...":
                label.update("[⟳ Syncing...]")
            elif self.sync_status == "Sync Failed":
                label.update("[✗ Sync Failed]")
            else:
                label.update("[✓ Synced]")
        except Exception:
            pass

    def action_command_palette(self) -> None:
        """Open the command palette with dwriter commands."""
        self.push_screen(CommandPalette(providers=[DWriterCommands]))

    def action_open_help(self) -> None:
        """Open the help screen."""
        from .screens.help_tui import HelpScreen

        self.push_screen(HelpScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "help-btn":
            self.action_open_help()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle horizontal tab navigation."""
        if event.tabs.id == "navigation-tabs" and event.tab.id:
            screen_name = event.tab.id
            switcher = self.query_one("#content-area", ContentSwitcher)
            try:
                switcher.current = screen_name
                self._current_screen = screen_name
                if screen_name != "todo":
                    self._todo_workflow.reset()
                self._update_omnibox_placeholder(screen_name)
            except Exception:
                pass

    def action_switch_mode(self, mode: str) -> None:
        """Switch screen via 1-4 hotkeys by programmatically clicking tabs."""
        tabs = self.query_one("#navigation-tabs", Tabs)
        tabs.active = mode

    def set_size(self, width: int, height: int) -> None:
        """Set the terminal size."""
        try:
            import sys

            sys.stderr.write(f"\033[8;{height};{width}t")
            sys.stderr.flush()
        except Exception:
            pass

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle sidebar navigation selection."""
        if event.option_list.id == "sidebar" and event.option.id:
            screen_name = event.option.id.replace("nav-", "")
            self.mount_screen(screen_name)

    def mount_screen(self, screen_name: str) -> None:
        """Switch to a screen by name using the ContentSwitcher."""
        try:
            switcher = self.query_one("#content-area", ContentSwitcher)
            tabs = self.query_one("#navigation-tabs", Tabs)

            switcher.current = screen_name
            tabs.active = screen_name
            self._current_screen = screen_name
            self._update_omnibox_placeholder(screen_name)
        except Exception as e:
            self.notify(f"Failed to switch screen: {e}", severity="error", timeout=2)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle omnibox input submission.

        Multi-step todo workflow on Todo screen:
        1. Task content (with optional #tag &project inline)
        2. Additional tags/project (or skip with Enter)
        3. Priority (L/N/H/U or skip)
        4. Due date (YYYY-MM-DD, today, tomorrow, Xd, Xw, Xm or skip)

        'q' at any step cancels and resets.
        """
        if message.input.id != "quick-add":
            return

        value = message.value.strip()

        if value == "q" and self._todo_workflow.state.active:
            self._todo_workflow.reset()
            message.input.value = ""
            self.notify("Todo creation cancelled", timeout=1.5)
            return

        if self._todo_workflow.state.active and self._current_screen == "todo":
            self._todo_workflow.handle_step(value, message)
            return

        if value:
            if self._current_screen == "timer":
                parsed_timer: ParsedTimer | None = parse_timer(value)

                if parsed_timer:
                    self._start_timer(
                        minutes=parsed_timer.minutes,
                        tags=parsed_timer.tags,
                        project=parsed_timer.project,
                    )
                    message.input.value = ""
                    return

            if self._current_screen == "todo":
                self._todo_workflow.start(value, message)
            else:
                self._create_journal_entry(value, message)

    def _create_journal_entry(self, value: str, message: Input.Submitted) -> None:
        """Create a journal entry from input."""
        date_format = self.ctx.config.display.date_format
        parsed_entry: ParsedEntry = parse_quick_add(value, date_format=date_format)

        default_tags = list(self.ctx.config.defaults.tags)
        all_tags = default_tags + parsed_entry.tags

        default_project = self.ctx.config.defaults.project
        project = parsed_entry.project or default_project

        entry = self.ctx.db.add_entry(
            content=parsed_entry.content,
            tags=all_tags,
            project=project,
            created_at=parsed_entry.created_at,
        )

        message.input.value = ""
        date_info = (
            f" ({parsed_entry.created_at.strftime('%Y-%m-%d')})"
            if parsed_entry.created_at
            else ""
        )
        self.notify(
            f"Logged: {parsed_entry.content}{date_info}", title="Success", timeout=2
        )

        self.post_message(
            EntryAdded(
                entry_id=entry.id,
                content=entry.content,
                created_at=entry.created_at,
            )
        )

    def _start_timer(self, minutes: int, tags: list[str], project: str | None) -> None:
        """Start a timer session."""
        from .screens.timer import TimerScreen

        self.mount_screen("timer")

        try:
            timer_screen = self.query_one("#timer", TimerScreen)

            timer_screen.tags = tags if tags else []
            timer_screen.project = project
            timer_screen.initial_minutes = minutes
            timer_screen.total_seconds = minutes * 60
            timer_screen.remaining_seconds = minutes * 60
            timer_screen.is_running = True
            timer_screen._start_timer()
            timer_screen.update_session_meta()
            self.notify(f"Timer started: {minutes} minutes", timeout=2)
        except Exception as e:
            self.notify(f"Failed to start timer: {e}", severity="error", timeout=2)

    def _parse_todo_due_date(self, due_str: str) -> Any:
        """Parse a due date string for todos."""
        from ..date_utils import parse_natural_date

        try:
            date_fmt = self.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt)
            return parse_natural_date(due_str, prefer_future=True, format_hint=hint)
        except ValueError:
            return None

    def on_entry_added(self, message: EntryAdded) -> None:
        """Handle EntryAdded messages from the omnibox."""
        from .screens.dashboard import DashboardScreen
        from .screens.logs import LogsScreen

        try:
            dashboard = self.query_one("#dashboard", DashboardScreen)
            dashboard._load_dashboard_data()
        except Exception:
            pass

        try:
            logs = self.query_one("#logs", LogsScreen)
            logs._load_data()
            logs._display_recent_entries()
        except Exception:
            pass

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Handle TodoUpdated messages from the omnibox."""
        from .screens.todo import TodoScreen

        try:
            todo_screen = self.query_one("#todo", TodoScreen)
            todo_screen._load_todos()
        except Exception:
            pass

    def on_timer_state_changed(self, message: TimerStateChanged) -> None:
        """Handle TimerStateChanged messages."""
        self._timer_running = message.is_running
        try:
            tabs = self.query_one("#navigation-tabs", Tabs)
            timer_tab = tabs.query_one("#timer", Tab)
            if message.is_running:
                timer_tab.add_class("timer-running")
            else:
                timer_tab.remove_class("timer-running")
        except Exception:
            pass
