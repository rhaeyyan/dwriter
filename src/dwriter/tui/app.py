"""Unified master app for dwriter TUI.

This module provides the main application class that manages all screens
and provides the global omnibox for quick entry logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    Tab,
    Tabs,
)

from .ai_handlers import AIHandlersMixin
from .colors import get_icon
from .command_palette import DWriterCommands
from .messages import (
    EntryAdded,
    SyncStatus,
    TimerStateChanged,
    TodoUpdated,
)
from .parsers import (
    ParsedEntry,
    parse_quick_add,
    parse_timer,
)
from .reminder_coordinator import ReminderCoordinator
from .themes import THEMES
from .todo_workflow import TodoWorkflow
from .widgets.omnibox import Omnibox


class DWriterApp(AIHandlersMixin, App[None]):
    """Unified Master App for dwriter.

    This app provides a single interface for all dwriter functionality:
    - 2nd-Brain for interactive AI assistance
    - Todo board for task management
    - Timer for timer-style sessions
    - Search for fuzzy finding entries and tasks
    - Global omnibox for quick entry logging

    Key bindings:
        Ctrl+P: Open command palette
        /: Focus omnibox (quick-add)
        1-5: Switch between screens
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
        Binding("1", "switch_to_primary", "Primary", show=False),
        Binding("2", "switch_mode('logs')", "Logs", show=False),
        Binding("3", "switch_mode('todo')", "To-Do", show=False),
        Binding("4", "switch_mode('timer')", "Timer", show=False),
        Binding("5", "switch_mode('settings')", "Settings", show=False),
        # Dashboard is kept as hidden fallback if needed
        Binding("0", "switch_mode('dashboard')", "Dashboard", show=False),
        Binding("ctrl+a", "apply_recommendation", "Apply Suggestion", show=False),
    ]

    permanent_omnibox = reactive(False)
    is_processing = reactive(False)
    sync_status = reactive("Synced")
    git_branch = reactive("")
    pending_recommendation: reactive = reactive(None)  # type: ignore[type-arg]

    def __init__(self, ctx: AppContext, starting_tab: str | None = None) -> None:
        """Initialize the dwriter application.

        Args:
            ctx: Application context containing database and configuration.
            starting_tab: The screen to show on launch.
        """
        super().__init__()
        self.ctx = ctx
        self.ctx.app = self
        # Initialize reactive directly from config
        self.permanent_omnibox = self.ctx.config.display.permanent_omnibox

        # If AI is disabled, default starting tab is dashboard instead of second-brain
        if starting_tab is None:
            starting_tab = "second-brain" if self.ctx.config.ai.enabled else "dashboard"

        self._current_screen: str = starting_tab
        self._timer_running: bool = False
        self._todo_workflow: TodoWorkflow = TodoWorkflow(self)
        self._reminder_coordinator: ReminderCoordinator = ReminderCoordinator(self)
        from ..sync.coordinator import SyncCoordinator
        self._sync_coordinator: SyncCoordinator = SyncCoordinator(self)

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(show_clock=True)

        # Omnibox - Centralized command palette for rapid entry
        date_fmt = self.ctx.config.display.date_format

        # Check config and determine initial class
        is_permanent = self.ctx.config.display.permanent_omnibox
        hidden_class = "" if is_permanent else "hidden"

        # Apply hidden_class to the Containers
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

        # Horizontal Navigation Tabs - Reordered to put 2nd-Brain first
        # If AI is disabled, show Dashboard as the first tab
        ai_enabled = self.ctx.config.ai.enabled
        first_tab_label = "\\[ 2ND-BRAIN ]" if ai_enabled else "\\[ DASHBOARD ]"
        first_tab_id = "second-brain" if ai_enabled else "dashboard"

        yield Tabs(
            Tab(first_tab_label, id=first_tab_id),
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
            from .screens.configure import ConfigureScreen
            from .screens.dashboard import DashboardScreen
            from .screens.logs import LogsScreen
            from .screens.second_brain import SecondBrainScreen
            from .screens.timer import TimerScreen
            from .screens.todo import TodoScreen

            yield SecondBrainScreen(self.ctx, id="second-brain")
            yield LogsScreen(self.ctx, id="logs")
            yield TodoScreen(self.ctx, id="todo")
            yield TimerScreen(self.ctx, id="timer")
            yield ConfigureScreen(self.ctx, id="settings")
            yield DashboardScreen(self.ctx, id="dashboard")

        with Horizontal(id="status-bar"):
            yield Label("", id="status-git")
            yield Label("", id="status-task")

        # Single Footer
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application state."""
        # Register git info
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

        # Sync permanent omnibox setting - this will trigger the watcher
        self.permanent_omnibox = config.display.permanent_omnibox

        self.call_after_refresh(self._set_default_size)
        self._update_omnibox_placeholder(self._current_screen)

        # Explicit initial sync of visibility
        self._sync_omnibox_visibility()

        # CRITICAL: Explicitly focus the navigation tabs on startup.
        # This prevents the omnibox from stealing focus and appearing when hidden.
        self.query_one("#navigation-tabs").focus()

        # Add a background check to ensure visibility stays in sync
        self.set_interval(0.2, self._sync_omnibox_visibility)

        # Start background reminder checker if enabled
        if self.ctx.config.display.notifications_enabled:
            self._reminder_coordinator.start()

        # Trigger initial background sync pull
        if self.ctx.config.defaults.auto_sync:
            self._sync_coordinator.trigger_pull()

    def on_unmount(self) -> None:
        """Cancel the background reminder thread on exit."""
        self._reminder_coordinator.stop()

    def watch_git_branch(self, value: str) -> None:
        """Update git branch in status bar."""
        try:
            label = self.query_one("#status-git", Label)
            if value:
                label.update(f" {value}")
            else:
                label.update("")
        except Exception:
            pass

    def watch_is_processing(self, value: bool) -> None:
        """Update processing indicator in status bar."""
        self._update_status_task()

    def watch_sync_status(self, value: str) -> None:
        """Update sync status in status bar."""
        self._update_status_task()

    def _update_status_task(self) -> None:
        """Centralized helper to update the status-task label."""
        try:
            label = self.query_one("#status-task", Label)
            if self.is_processing:
                label.update("[🧠 Processing...]")
            elif self.sync_status == "Syncing...":
                label.update("[🧠 Syncing...]")
            elif self.sync_status == "Sync Failed":
                label.update("[❌ Sync Failed]")
            else:
                label.update("[✅ Synced]")
        except Exception:
            pass

    def watch_permanent_omnibox(self, value: bool) -> None:
        """Update omnibox visibility when the reactive setting changes."""
        try:
            # Sync classes directly
            self.query_one("#omnibox-container").set_class(not value, "hidden")
            self.query_one("#omnibox-footer").set_class(not value, "hidden")
        except Exception:
            pass
        self._sync_omnibox_visibility()

    def _sync_omnibox_visibility(self) -> None:
        """Central logic for omnibox visibility using CSS classes and focus management."""
        try:
            is_permanent = self.permanent_omnibox

            # Use focused property from app state safely
            current_focused = self.focused
            is_omnibox_focused = (
                current_focused is not None and
                getattr(current_focused, "id", None) == "quick-add"
            )

            show = is_permanent or is_omnibox_focused

            # Use set_class to handle visibility via CSS
            container = self.query_one("#omnibox-container")
            footer = self.query_one("#omnibox-footer")
            omnibox = self.query_one("#quick-add", Omnibox)

            container.set_class(not show, "hidden")
            footer.set_class(not show, "hidden")

            # Manage focusability: if not permanent and not focused, disable focus to prevent
            # Textual from auto-focusing it on startup or during navigation.
            # We ONLY re-enable it if permanent is ON or we explicitly want to focus it (via hotkey).
            if not is_permanent and not is_omnibox_focused:
                omnibox.can_focus = False
            else:
                omnibox.can_focus = True

        except Exception:
            pass

    def _set_default_size(self) -> None:
        """Set the default terminal size."""
        self.set_size(90, 42)

    def action_command_palette(self) -> None:
        """Open the command palette with dwriter commands."""
        self.push_screen(CommandPalette(providers=[DWriterCommands]))

    def action_focus_omnibox(self) -> None:
        """Focus the quick-add input."""
        # Force visibility so it can successfully receive focus
        self.query_one("#omnibox-container").remove_class("hidden")
        self.query_one("#omnibox-footer").remove_class("hidden")

        omnibox = self.query_one("#quick-add", Omnibox)
        omnibox.can_focus = True
        omnibox.focus()
        self._sync_omnibox_visibility()

    def action_blur_omnibox(self) -> None:
        """Remove focus from the omnibox when pressing escape."""
        if self.focused is not None and self.focused.id == "quick-add":
            if self._todo_workflow.state.active:
                self._todo_workflow.reset()
                self.notify("Todo creation cancelled", timeout=1.5)
            self.set_focus(None)
            # Re-sync will handle can_focus = False if needed
            self._sync_omnibox_visibility()

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

    def action_switch_mode(self, mode: str) -> None:  # type: ignore[override]
        """Switch screen via hotkeys."""
        tabs = self.query_one("#navigation-tabs", Tabs)
        tabs.active = mode

    def action_switch_to_primary(self) -> None:
        """Switch to the primary landing screen (2nd-Brain or Dashboard)."""
        mode = "second-brain" if self.ctx.config.ai.enabled else "dashboard"
        self.action_switch_mode(mode)

    def set_size(self, width: int, height: int) -> None:
        """Set the terminal size."""
        try:
            import sys
            sys.stderr.write(f"\033[8;{height};{width}t")
            sys.stderr.flush()
        except Exception:
            pass

    def _update_omnibox_placeholder(self, screen_name: str) -> None:
        """Update the omnibox placeholder and hint based on the current screen."""
        use_emojis = self.ctx.config.display.use_emojis
        bullet = get_icon("bullet", use_emojis)
        try:
            omnibox = self.query_one("#quick-add", Omnibox)
            hint = self.query_one("#omnibox-hint", Label)

            if screen_name == "todo":
                if self._todo_workflow.state.active:
                    step = self._todo_workflow.state.step
                    if step == "task":
                        omnibox.placeholder = "Enter task description..."
                        hint.update(f"Task text with optional #tag &project {bullet} 'q' to cancel")
                    elif step == "tags":
                        current_tags = ", ".join(self._todo_workflow.state.tags) if self._todo_workflow.state.tags else "none"
                        hint.update(f"Current: {current_tags} {bullet} Add more #tag &project or Enter to skip")
                        omnibox.placeholder = "Add tags/project (or press Enter to skip)..."
                    elif step == "priority":
                        omnibox.placeholder = "Priority: L=Low, N=Normal, H=High, U=Urgent (or Enter for Normal)"
                        hint.update(f"Task: {self._todo_workflow.state.content[:40]}... {bullet} 'q' to cancel")
                    elif step == "due_date":
                        date_fmt = self.ctx.config.display.date_format
                        omnibox.placeholder = f"Due date: {date_fmt}, today, tomorrow, 5d, 2w, 3m (or Enter for none)"
                        hint.update(f"Priority: {self._todo_workflow.state.priority.upper()} {bullet} 'q' to cancel")
                else:
                    omnibox.placeholder = "Enter Task and press Enter to start multi-step add"
                    hint.update(f"Enter Task and press Enter to start multi-step add {bullet} 'q' to cancel")
            elif screen_name == "timer":
                omnibox.placeholder = "Start timer... (use #tag &project MINUTES)"
                hint.update(f"Press / to focus {bullet} Enter: #tag &project 15 starts 15min timer")
            elif screen_name == "second-brain":
                date_fmt = self.ctx.config.display.date_format
                omnibox.placeholder = f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}"
                hint.update(
                    f"#tag &project YOUR-ENTRY {bullet} #tag &project YOUR-ENTRY {date_fmt}"
                )
            else:
                date_fmt = self.ctx.config.display.date_format
                omnibox.placeholder = f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}"
                hint.update(f"#tag &project YOUR-ENTRY {bullet} #tag &project YOUR-ENTRY {date_fmt}")
        except Exception:
            pass

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle omnibox input submission."""
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
                parsed_timer = parse_timer(value)
                if parsed_timer:
                    self._start_timer(minutes=parsed_timer.minutes, tags=parsed_timer.tags, project=parsed_timer.project)
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
        all_tags = list(self.ctx.config.defaults.tags) + parsed_entry.tags
        project = parsed_entry.project or self.ctx.config.defaults.project

        async def add_entry_worker() -> None:
            entry = self.ctx.db.add_entry(
                content=parsed_entry.content,
                tags=all_tags,
                project=project,
                created_at=parsed_entry.created_at
            )
            self.notify(f"Logged: {parsed_entry.content}")
            self.post_message(EntryAdded(
                entry_id=entry.id,
                content=entry.content,
                created_at=entry.created_at
            ))

        self.run_worker(add_entry_worker())
        message.input.value = ""

    def _start_timer(self, minutes: int, tags: list[str], project: str | None) -> None:
        """Start a timer session."""
        from .screens.timer import TimerScreen
        self.mount_screen("timer")  # type: ignore[attr-defined]
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
            self.notify(f"Timer started: {minutes} minutes")
        except Exception:
            pass

    def on_sync_status(self, message: SyncStatus) -> None:
        """Handle SyncStatus messages to update the TUI state."""
        self.sync_status = message.message

    def on_entry_added(self, message: EntryAdded) -> None:
        """Handle EntryAdded messages."""
        try:
            from .screens.dashboard import DashboardScreen
            dashboard = self.query_one("#dashboard", DashboardScreen)
            dashboard._load_dashboard_data()
        except Exception:
            pass
        try:
            from .screens.logs import LogsScreen
            logs = self.query_one("#logs", LogsScreen)
            logs._load_data()
            logs._display_recent_entries()
        except Exception:
            pass

        # Trigger auto-sync if it's a real entry (id > 0)
        if message.entry_id > 0:
            self._sync_coordinator.trigger_push_debounced()

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Handle TodoUpdated messages."""
        try:
            from .screens.todo import TodoScreen
            todo_screen = self.query_one("#todo", TodoScreen)
            todo_screen._load_todos()
        except Exception:
            pass

        # Trigger auto-sync if it's a real update (id > 0)
        if message.todo_id > 0:
            self._sync_coordinator.trigger_push_debounced()

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

