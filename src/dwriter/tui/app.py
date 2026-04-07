"""Unified master app for dwriter TUI.

This module provides the main application class that manages all screens
and provides the global omnibox for quick entry logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ..cli import AppContext

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import CommandPalette
from textual.containers import Horizontal
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

from .colors import get_icon
from .command_palette import DWriterCommands
from .messages import EntryAdded, TimerStateChanged, TodoUpdated
from .parsers import (
    ParsedEntry,
    ParsedTodo,
    parse_quick_add,
    parse_timer,
    parse_todo_add,
)
from .themes import THEMES

TodoStep = Literal["task", "tags", "priority", "due_date"]


class TodoInputState:
    """State tracker for multi-step todo input workflow."""

    def __init__(self) -> None:
        """Initialize the todo input state."""
        self.active: bool = False
        self.step: TodoStep = "task"
        self.content: str = ""
        self.tags: list[str] = []
        self.project: str = ""
        self.priority: str = "normal"
        self.due_date: str = ""


class DWriterApp(App[None]):
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

    # Theme colors handled by themes.py
    CSS = """
    $text-muted: #8c92a6;
    $panel-light: #45475a;
    $border-muted: #45475a;

    #omnibox-container {
        height: auto;
        border: solid $border-muted;
        background: $panel;
        margin: 0 1;
        padding: 0 1;
    }

    #quick-add {
        width: 1fr;
        margin-right: 1;
    }

    #omnibox-hint {
        width: 1fr;
        height: 1;
        color: $text-muted;
        padding: 0 2;
    }

    #omnibox-footer {
        height: auto;
        margin: 0 1 1 1;
        padding: 0;
    }

    #help-btn, #settings-btn {
        width: auto;
        min-width: 0;
        height: 1;
        background: transparent;
        border: none;
        padding: 0 1;
        margin: 0;
        color: $primary;
    }

    #help-btn:hover, #settings-btn:hover {
        background: $surface;
        text-style: bold;
    }

    Tabs {
        background: transparent;
        border: none;
    }

    Tab {
        background: transparent;
        color: $primary;
        margin: 0 1 0 0;
        padding: 0 2;
    }

    Tab:hover {
        background: $surface;
        color: $foreground;
        text-style: bold;
    }

    Tab.-active {
        background: $primary;
        color: $background;
        text-style: bold;
    }

    Tab.timer-running {
        background: transparent;
        color: #00FF7F;
        text-style: bold;
    }

    Tab#settings {
        width: auto;
    }

    Tab#tab-spacer {
        width: 1fr;
        border: none;
        background: transparent;
    }
    
    Tab#tab-spacer:hover {
        background: transparent;
    }
    
    Tab#tab-spacer.-active {
        background: transparent;
    }

    #content-area {
        height: 1fr;
        width: 1fr;
        background: transparent;
        border: none;
        margin: 0;
        padding: 0 1;
    }

    .todo-panel, .search-panel, .card {
        height: 100%;
        border: solid $border-muted;
        background: $panel;
        margin: 0;
        padding: 0 1;
    }

    .active-panel, .search-panel:focus-within, .todo-panel:focus-within {
        border: solid $accent;
    }

    .panel-title {
        text-style: bold;
        padding: 0;
        margin-bottom: 0;
        border-bottom: solid $border-muted;
    }

    #pending-title {
        color: $warning;
        border-bottom: solid $warning;
    }

    #completed-title {
        color: $success;
        border-bottom: solid $success;
    }

    ListItem {
        padding: 0;
        margin-bottom: 1;
    }

    ListItem:focus {
        background: $surface;
    }

    ListView {
        background: transparent;
        scrollbar-size-vertical: 1;
        scrollbar-gutter: stable;
    }

    #dashboard-main-container {
        height: 1fr;
        padding: 0;
        overflow-y: auto;
    }

    #dashboard-kpi-row {
        height: 5;
        min-height: 5;
    }

    KPICard {
        border: solid $border-muted;
        background: $panel;
        margin: 0 0 0 1;
        padding: 0;
    }

    StreakCalendar, ActivitySparkline {
        border: solid $border-muted;
        background: $panel;
        margin: 0 0 0 1;
        padding: 0 1;
    }

    DataTable {
        border: solid $border-muted;
        border-title-color: $success;
        margin: 0;
        background: transparent;
    }

    TabPane {
        padding: 0 1;
    }

    TabbedContent {
        height: 1fr;
    }

    HelpScreen {
        align: center middle;
        background: rgba(13, 15, 24, 0.85);
    }

    #help-main-container {
        width: 100;
        height: 80%;
        background: transparent;
    }

    .help-row {
        height: 1fr;
        margin: 0;
    }

    .help-panel {
        width: 1fr;
        height: 100%;
        border: solid $border-muted;
        background: $panel;
        margin: 0 1;
        padding: 0 2;
    }

    .help-panel:focus-within {
        border: solid $accent;
    }

    .help-title {
        text-style: bold;
        color: $secondary;
        padding: 0;
        border-bottom: solid $border-muted;
        margin-bottom: 0;
    }

    .help-content {
        color: $foreground;
        height: 1fr;
    }

    #help-footer {
        dock: bottom;
        height: 1;
        text-align: center;
        color: $text-muted;
        margin-top: 0;
    }

    Screen.ergonomic-mode #content-area {
        padding: 0 4;
    }

    Screen.ergonomic-mode .todo-panel,
    Screen.ergonomic-mode .search-panel {
        border: none;
        border-top: solid $panel-light;
        padding: 0 3;
    }

    Screen.ergonomic-mode ListItem {
        padding: 1 0;
    }

    Button {
        border: none;
        height: auto;
        min-height: 1;
        min-width: 8;
        padding: 0 1;
        background: transparent;
    }
    
    Button.-success { color: $success; text-style: bold; }
    Button.-success:hover, Button.-success:focus { background: $success 20%; color: $success; text-style: reverse bold; }
    
    Button.-warning { color: $warning; text-style: bold; }
    Button.-warning:hover, Button.-warning:focus { background: $warning 20%; color: $warning; text-style: reverse bold; }
    
    Button.-error { color: $error; text-style: bold; }
    Button.-error:hover, Button.-error:focus { background: $error 20%; color: $error; text-style: reverse bold; }
    
    Button.-primary { color: $primary; text-style: bold; }
    Button.-primary:hover, Button.-primary:focus { background: $primary 20%; color: $primary; text-style: reverse bold; }
    
    Button.-default { color: $foreground 70%; text-style: bold; }
    Button.-default:hover, Button.-default:focus { color: $foreground; background: $surface; text-style: reverse bold; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("/", "focus_omnibox", "Quick Add", show=True),
        Binding("escape", "blur_omnibox", "Unfocus", show=False),
        Binding("1", "switch_mode('second-brain')", "2nd-Brain", show=False),
        Binding("2", "switch_mode('logs')", "Logs", show=False),
        Binding("3", "switch_mode('todo')", "To-Do", show=False),
        Binding("4", "switch_mode('timer')", "Timer", show=False),
        Binding("5", "switch_mode('settings')", "Settings", show=False),
        # Dashboard is kept as hidden fallback if needed
        Binding("0", "switch_mode('dashboard')", "Dashboard", show=False),
    ]

    def __init__(self, ctx: AppContext, starting_tab: str = "second-brain") -> None:
        """Initialize the dwriter application.

        Args:
            ctx: Application context containing database and configuration.
            starting_tab: The screen to show on launch.
        """
        super().__init__()
        self.ctx = ctx
        self._current_screen: str = starting_tab
        self._todo_state: TodoInputState = TodoInputState()
        self._timer_running: bool = False

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(show_clock=True)

        # Omnibox - Centralized command palette for rapid entry
        date_fmt = self.ctx.config.display.date_format
        with Horizontal(id="omnibox-container"):
            yield Input(
                placeholder=f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}",
                id="quick-add",
            )

        with Horizontal(id="omnibox-footer"):
            yield Label(
                f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}",
                id="omnibox-hint",
            )
            yield Button("Help", id="help-btn", variant="default")

        # Horizontal Navigation Tabs - Reordered to put 2nd-Brain first
        yield Tabs(
            Tab("\\[ 2ND-BRAIN ]", id="second-brain"),
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

        # Single Footer
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application state."""
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

        self.call_after_refresh(self._set_default_size)
        self._update_omnibox_placeholder(self._current_screen)

    def _set_default_size(self) -> None:
        """Set the default terminal size."""
        self.set_size(90, 45)

    def action_command_palette(self) -> None:
        """Open the command palette with dwriter commands."""
        self.push_screen(CommandPalette(providers=[DWriterCommands]))

    def action_focus_omnibox(self) -> None:
        """Focus the quick-add input."""
        self.query_one("#quick-add", Input).focus()

    def action_blur_omnibox(self) -> None:
        """Remove focus from the omnibox when pressing escape."""
        if self.focused is not None and self.focused.id == "quick-add":
            if self._todo_state.active:
                self._reset_todo_state()
                self.notify("Todo creation cancelled", timeout=1.5)
            self.set_focus(None)

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
                    self._reset_todo_state()
                self._update_omnibox_placeholder(screen_name)
            except Exception:
                pass

    def action_switch_mode(self, mode: str) -> None:
        """Switch screen via hotkeys."""
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

    def _update_omnibox_placeholder(self, screen_name: str) -> None:
        """Update the omnibox placeholder and hint based on the current screen."""
        use_emojis = self.ctx.config.display.use_emojis
        bullet = get_icon("bullet", use_emojis)
        try:
            omnibox = self.query_one("#quick-add", Input)
            hint = self.query_one("#omnibox-hint", Label)

            if screen_name == "todo":
                if self._todo_state.active:
                    step = self._todo_state.step
                    if step == "task":
                        omnibox.placeholder = "Enter task description..."
                        hint.update(f"Task text with optional #tag &project {bullet} 'q' to cancel")
                    elif step == "tags":
                        current_tags = ", ".join(self._todo_state.tags) if self._todo_state.tags else "none"
                        hint.update(f"Current: {current_tags} {bullet} Add more #tag &project or Enter to skip")
                        omnibox.placeholder = "Add tags/project (or press Enter to skip)..."
                    elif step == "priority":
                        omnibox.placeholder = "Priority: L=Low, N=Normal, H=High, U=Urgent (or Enter for Normal)"
                        hint.update(f"Task: {self._todo_state.content[:40]}... {bullet} 'q' to cancel")
                    elif step == "due_date":
                        date_fmt = self.ctx.config.display.date_format
                        omnibox.placeholder = f"Due date: {date_fmt}, today, tomorrow, 5d, 2w, 3m (or Enter for none)"
                        hint.update(f"Priority: {self._todo_state.priority.upper()} {bullet} 'q' to cancel")
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
        if value == "q" and self._todo_state.active:
            self._reset_todo_state()
            message.input.value = ""
            self.notify("Todo creation cancelled", timeout=1.5)
            return

        if self._todo_state.active and self._current_screen == "todo":
            self._handle_todo_step(value, message)
            return

        if value:
            if self._current_screen == "timer":
                parsed_timer = parse_timer(value)
                if parsed_timer:
                    self._start_timer(minutes=parsed_timer.minutes, tags=parsed_timer.tags, project=parsed_timer.project)
                    message.input.value = ""
                    return

            if self._current_screen == "todo":
                self._start_todo_workflow(value, message)
            else:
                self._create_journal_entry(value, message)

    def _start_todo_workflow(self, value: str, message: Input.Submitted) -> None:
        """Start the multi-step todo creation workflow."""
        parsed: ParsedTodo = parse_todo_add(value)
        self._todo_state.active = True
        self._todo_state.step = "tags"
        self._todo_state.content = parsed.content
        self._todo_state.tags = parsed.tags
        self._todo_state.project = parsed.project or ""
        self._todo_state.priority = parsed.priority
        message.input.value = ""
        self._update_omnibox_placeholder("todo")

    def _handle_todo_step(self, value: str, message: Input.Submitted) -> None:
        """Handle a step in the multi-step todo workflow."""
        step = self._todo_state.step
        if step == "tags":
            if value:
                parsed: ParsedTodo = parse_todo_add(value)
                for tag in parsed.tags:
                    if tag not in self._todo_state.tags:
                        self._todo_state.tags.append(tag)
                if parsed.project:
                    self._todo_state.project = parsed.project
            self._todo_state.step = "priority"
            message.input.value = ""
            self._update_omnibox_placeholder("todo")
        elif step == "priority":
            value_lower = value.lower().strip()
            if value_lower == "l": self._todo_state.priority = "low"
            elif value_lower == "h": self._todo_state.priority = "high"
            elif value_lower == "u": self._todo_state.priority = "urgent"
            else: self._todo_state.priority = "normal"
            self._todo_state.step = "due_date"
            message.input.value = ""
            self._update_omnibox_placeholder("todo")
        elif step == "due_date":
            due_date = None
            if value and value.lower() != "none":
                due_date = self._parse_todo_due_date(value)
            all_tags = list(self.ctx.config.defaults.tags) + self._todo_state.tags
            project = self._todo_state.project or self.ctx.config.defaults.project
            todo = self.ctx.db.add_todo(content=self._todo_state.content, priority=self._todo_state.priority, tags=all_tags, project=project, due_date=due_date)
            message.input.value = ""
            self.notify(f"Todo added: {self._todo_state.content}")
            self.post_message(TodoUpdated(todo_id=todo.id, action="added"))
            self._reset_todo_state()

    def _reset_todo_state(self) -> None:
        """Reset the multi-step todo input state."""
        self._todo_state = TodoInputState()
        self._update_omnibox_placeholder("todo")

    def _create_journal_entry(self, value: str, message: Input.Submitted) -> None:
        """Create a journal entry from input."""
        date_format = self.ctx.config.display.date_format
        parsed_entry: ParsedEntry = parse_quick_add(value, date_format=date_format)
        all_tags = list(self.ctx.config.defaults.tags) + parsed_entry.tags
        project = parsed_entry.project or self.ctx.config.defaults.project
        entry = self.ctx.db.add_entry(content=parsed_entry.content, tags=all_tags, project=project, created_at=parsed_entry.created_at)
        message.input.value = ""
        self.notify(f"Logged: {parsed_entry.content}")
        self.post_message(EntryAdded(entry_id=entry.id, content=entry.content, created_at=entry.created_at))

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
            self.notify(f"Timer started: {minutes} minutes")
        except Exception:
            pass

    def _parse_todo_due_date(self, due_str: str) -> Any:
        """Parse a due date string for todos."""
        from ..date_utils import parse_natural_date
        try:
            date_fmt = self.ctx.config.display.date_format
            fmt_map = {"YYYY-MM-DD": "%Y-%m-%d", "MM/DD/YYYY": "%m/%d/%Y", "DD/MM/YYYY": "%d/%m/%Y"}
            hint = fmt_map.get(date_fmt)
            return parse_natural_date(due_str, prefer_future=True, format_hint=hint)
        except Exception:
            return None

    def on_entry_added(self, message: EntryAdded) -> None:
        """Handle EntryAdded messages."""
        try:
            from .screens.dashboard import DashboardScreen
            dashboard = self.query_one("#dashboard", DashboardScreen)
            dashboard._load_dashboard_data()
        except Exception: pass
        try:
            from .screens.logs import LogsScreen
            logs = self.query_one("#logs", LogsScreen)
            logs._load_data()
            logs._display_recent_entries()
        except Exception: pass

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Handle TodoUpdated messages."""
        try:
            from .screens.todo import TodoScreen
            todo_screen = self.query_one("#todo", TodoScreen)
            todo_screen._load_todos()
        except Exception: pass

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
        except Exception: pass
