"""Timer screen for dwriter TUI.

This module provides a countdown timer for managing focused work sessions
and logging the resulting activity.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch

from ..colors import PROJECT, TAG, get_icon
from ..messages import EntryAdded, TimerStateChanged
from ..parsers import parse_quick_add


class SessionCompleteModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for logging activity upon timer completion."""

    CSS = """
    SessionCompleteModal {
        align: center middle;
    }

    #modal-container {
        width: 64;
        height: auto;
        background: $panel;
        border: solid $success;
        padding: 1 2;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        color: $success;
        margin-top: 1;
    }

    #session-info {
        text-align: center;
        margin-bottom: 1;
        color: $text-muted;
    }

    #edit-input {
        width: 1fr;
        margin-bottom: 1;
    }

    .session-meta {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    #edit-buttons {
        height: auto;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
        width: 18;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "save", "Save"),
    ]

    def __init__(
        self,
        minutes: int,
        default_content: str,
        tags: list[str] | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the session completion modal.

        Args:
            minutes (int): Duration of the session.
            default_content (str): Initial text for the log entry.
            tags (list[str], optional): Pre-defined tags for the session.
            project (str, optional): Pre-defined project for the session.
            **kwargs (Any): Additional arguments for ModalScreen.
        """
        super().__init__(**kwargs)
        self.minutes = minutes
        self.default_content = default_content
        self.tags = tags or []
        self.project = project
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Composes the modal layout."""
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="modal-container"):
            yield Label(f"{get_icon('check', use_emojis)} Session Complete!", id="modal-title")
            yield Label(
                f"Record your {self.minutes} minute{'s' if self.minutes != 1 else ''} of activity:",
                id="session-info",
            )
            yield Input(
                value=self.default_content,
                id="edit-input",
                placeholder="What did you do?",
            )

            if self.tags or self.project:
                meta_parts = []
                if self.tags:
                    tags_markup = " ".join([f"[bold yellow]#{tag}[/]" for tag in self.tags])
                    meta_parts.append(f"Tags: {tags_markup}")
                if self.project:
                    meta_parts.append(f"Project: [{PROJECT}]{self.project}[/]")
                yield Label(
                    " | ".join(meta_parts),
                    id="session-meta",
                    classes="session-meta",
                )

            with Horizontal(id="edit-buttons"):
                yield Button("\\[ LOG ENTRY ]", id="save-btn", variant="success")
                yield Button("\\[ SKIP ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focuses the content input field."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Saves the entry content and dismisses the modal."""
        self.result = self.query_one("#edit-input", Input).value.strip()
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Dismisses the modal without logging."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button interaction events."""
        if event.button.id == "save-btn": self.action_save()
        elif event.button.id == "cancel-btn": self.action_cancel()


class TimerProgressBar(Static):
    """Custom progress visualization component."""

    DEFAULT_CSS = """
    TimerProgressBar {
        width: 100%;
        content-align: center middle;
        height: 1;
    }
    """

    def __init__(self, total_seconds: int = 25 * 60, **kwargs: Any) -> None:
        """Initializes the progress bar.

        Args:
            total_seconds (int): Total session duration.
            **kwargs (Any): Additional arguments for Static.
        """
        super().__init__(**kwargs)
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds

    def update_progress(self, remaining: int, total: int) -> None:
        """Updates internal state and refreshes the bar rendering.

        Args:
            remaining (int): Remaining seconds in the session.
            total (int): Total seconds defined for the session.
        """
        self.remaining_seconds = remaining
        self.total_seconds = total
        self._render_bar()

    def _get_gradient_color(self, position: float) -> str:
        """Retrieves a color based on temporal progress.

        Args:
            position (float): Progress ratio (0.0 to 1.0).

        Returns:
            str: Hex color string.
        """
        if position < 0.25: return "#00e5ff"
        if position < 0.5: return "#ccff00"
        if position < 0.75: return "#ffea00"
        if position < 0.85: return "#ff7b00"
        return "#ff003c"

    def _render_bar(self) -> None:
        """Generates and updates the bar markup."""
        if self.total_seconds <= 0:
            self.update("No time set")
            return

        # Safeguard remaining_seconds to not exceed total_seconds to avoid negative progress
        safe_rem = min(self.remaining_seconds, self.total_seconds)
        progress = 1.0 - (safe_rem / self.total_seconds)
        
        # Ensure progress is within [0, 1]
        progress = max(0.0, min(1.0, progress))
        
        percentage = int(progress * 100)
        bar_width, filled = 30, int(progress * 30)
        empty = bar_width - filled

        time_str = f"{self.remaining_seconds // 60:02d}:{self.remaining_seconds % 60:02d}"
        color = self._get_gradient_color(progress)
        use_emojis = self.app.ctx.config.display.use_emojis
        fill_char, empty_char = ("▮", "▯") if use_emojis else ("#", ".")
        
        self.update(f"[bold #00E5FF]{time_str}[/bold #00E5FF]  [{color}]{fill_char * filled}[/][#313244]{empty_char * empty}[/]  [bold #00E5FF]{percentage}%[/bold #00E5FF]")


class TimerScreen(Container):
    """Interactive timer interface for focused sessions.

    Manages timer states (work/break), real-time updates, and session
    persistence to the database.
    """

    DEFAULT_CSS = """
    TimerScreen {
        height: 1fr;
        align: center middle;
    }

    #timer-main-container {
        height: 28;
        width: 78;
        align: center top;
        padding: 0 3;
        background: $panel;
        border: solid #3b494c;
        border-title-color: $primary;
    }

    #timer-header {
        height: 3;
        width: 100%;
        margin-bottom: 0;
        padding: 0 2;
        background: $panel;
        align: left top;
    }

    #timer-title {
        text-align: left;
        text-style: bold;
        color: $primary;
        width: 1fr;
        height: 1;
        padding: 0;
        margin-top: 1;
    }

    #timer-break-mode-container {
        height: 3;
        width: auto;
        align: right top;
        padding: 0;
        margin-top: 0;
    }

    #timer-break-label {
        text-align: left;
        padding: 0 1 0 0;
        color: $text-muted;
        width: auto;
        margin-top: 1;
    }

    #timer-break-switch {
        margin: 0;
        height: auto;
    }

    #timer-controls {
        height: auto;
        align: center middle;
        padding: 0;
        margin-top: 1;
    }

    #timer-config-section {
        height: auto;
        margin-top: 1;
        padding: 0 1;
    }

    .config-row {
        height: 3;
        align: center middle;
    }

    .config-label {
        width: 6;
        color: $text-muted;
        text-style: bold;
        content-align: center middle;
        margin-right: 1;
        height: 3;
    }

    #timer-config-section Input {
        width: 1fr;
        margin-right: 1;
        border: solid $border-blurred;
        background: $panel;
    }

    #timer-config-section Input:focus {
        border: solid $accent;
        background: $surface;
    }

    #timer-control-button {
        min-width: 15;
        height: auto;
    }

    #timer-progress-container {
        height: auto;
        align: center middle;
        padding: 0;
        margin-top: 1;
        margin-bottom: 1;
    }

    #timer-clear-row {
        dock: bottom;
        height: auto;
        width: 100%;
        align: right middle;
        padding: 0 1;
        margin-bottom: 1;
    }

    #timer-clear-button {
        min-width: 10;
        height: auto;
    }

    #timer-adjust-buttons {
        height: auto;
        align: center middle;
        padding: 0;
    }

    #timer-adjust-buttons Button {
        margin: 0 1;
        min-width: 6;
    }

    .timer-session-meta {
        text-align: center;
        color: $text-muted;
        height: 2;
        margin-top: 1;
        content-align: center middle;
        width: 100%;
    }

    #timer-adjust-section {
        height: auto;
        align: center middle;
        padding: 0;
    }

    .add-time-label {
        text-align: center;
        width: 100%;
        color: $text-muted;
        padding: 0 0 1 0;
        text-style: italic;
    }

    #timer-session-info {
        dock: bottom;
        height: 1;
        background: $panel;
        content-align: center middle;
        padding: 0 2;
    }

    .paused-button { background: $warning; color: $background; }
    .running-button { background: $success; color: $background; }
    .finished-button { background: $primary; color: $background; }
    """

    BINDINGS = [
        Binding("space", "toggle_pause", "Pause/Resume"),
        Binding("+", "add_5_min", "+5 min"),
        Binding("-", "subtract_5_min", "-5 min"),
        Binding("enter", "finish", "Finish"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("b", "toggle_break_mode", "Break Mode"),
        Binding("c", "clear_timer", "Reset"),
    ]

    remaining_seconds = reactive(25 * 60)
    total_seconds = reactive(25 * 60)
    is_running = reactive(False)
    is_finished = reactive(False)
    is_break_mode = reactive(False)

    def __init__(
        self,
        ctx: AppContext,
        minutes: int = 25,
        tags: list[str] | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the timer screen.

        Args:
            ctx (AppContext): Application context.
            minutes (int): Initial duration.
            tags (list[str], optional): Target tags for the log entry.
            project (str, optional): Target project for the log entry.
            **kwargs (Any): Additional arguments for Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        config = ctx.config_manager.load()
        self.work_duration = config.timer.work_duration
        self.break_duration = config.timer.break_duration
        self.initial_minutes = minutes
        self.total_seconds = minutes * 60
        self._timer_handle: Any = None
        self.tags = tags if tags is not None else []
        self.project = project

    def compose(self) -> ComposeResult:
        """Composes the timer UI components."""
        use_emojis = self.ctx.config.display.use_emojis
        with Container(id="timer-main-container"):
            with Horizontal(id="timer-header"):
                yield Label(f"{get_icon('timer', use_emojis)} Timer", id="timer-title")
                with Horizontal(id="timer-break-mode-container"):
                    yield Label("Break:", id="timer-break-label")
                    yield Switch(value=self.is_break_mode, id="timer-break-switch")

            # Configuration Fields
            with Vertical(id="timer-config-section"):
                with Horizontal(classes="config-row"):
                    yield Label("Mins:", classes="config-label")
                    yield Input(value=str(self.initial_minutes), id="input-duration", placeholder="Min")
                    yield Label("Proj:", classes="config-label")
                    yield Input(value=self.project or "", id="input-project", placeholder="&project")
                
                with Horizontal(classes="config-row"):
                    yield Label("Tags:", classes="config-label")
                    yield Input(value=", ".join(self.tags), id="input-tags", placeholder="tag1, tag2")

            with Horizontal(id="timer-controls"):
                yield Button("[ START / PAUSE ]", id="timer-control-button", variant="warning")

            with Container(id="timer-progress-container"):
                yield TimerProgressBar(total_seconds=self.total_seconds, id="timer-progress-bar")

            yield Label("", id="timer-session-meta", classes="timer-session-meta")

            with Vertical(id="timer-adjust-section"):
                yield Label("Add/Remove Minutes:", classes="add-time-label")
                with Horizontal(id="timer-adjust-buttons"):
                    yield Button("\\[ +5 MIN ]", id="btn-plus-5", variant="success")
                    yield Button("\\[ +1 MIN ]", id="btn-plus-1", variant="success")
                    yield Button("\\[ -1 MIN ]", id="btn-minus-1", variant="error")
                    yield Button("\\[ -5 MIN ]", id="btn-minus-5", variant="error")

            with Horizontal(id="timer-clear-row"):
                yield Button("\\[ RESET ]", id="timer-clear-button", variant="default")

        yield Label(
            f"Space: Start/Pause  {get_icon('bullet', use_emojis)}  C: Reset  {get_icon('bullet', use_emojis)}  B: Break  {get_icon('bullet', use_emojis)}  Enter: Finish",
            id="timer-session-info",
        )

    def on_mount(self) -> None:
        """Initializes the display state on widget mount."""
        self._update_display()
        self.update_session_meta()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handles real-time updates when duration input is modified."""
        if event.input.id == "input-duration" and not self.is_running and not self.is_finished:
            try:
                val = int(event.value)
                if val >= 1:
                    self.initial_minutes = val
                    self.total_seconds = self.remaining_seconds = val * 60
            except ValueError:
                pass

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Synchronizes break mode state with the UI switch."""
        if event.switch.id == "timer-break-switch" and self.is_break_mode != event.value:
            self.action_toggle_break_mode()

    def on_show(self) -> None:
        """Refreshes durations and display metadata when the screen is shown."""
        self.work_duration = self.ctx.config.timer.work_duration
        self.break_duration = self.ctx.config.timer.break_duration
        self._update_display()
        self.update_session_meta()

    def on_unmount(self) -> None:
        """Ensures the background timer is stopped on widget destruction."""
        if self._timer_handle:
            self._timer_handle.stop()
            self._timer_handle = None

    def watch_remaining_seconds(self) -> None:
        """Reactively updates the display when the timer decrements."""
        self._update_display()
        try:
            self.query_one("#timer-progress-bar", TimerProgressBar).update_progress(self.remaining_seconds, self.total_seconds)
        except Exception: pass

    def watch_total_seconds(self) -> None:
        """Reactively updates the progress bar when the total duration changes."""
        try:
            self.query_one("#timer-progress-bar", TimerProgressBar).update_progress(self.remaining_seconds, self.total_seconds)
        except Exception: pass

    def watch_is_running(self) -> None: self._update_display()
    def watch_is_finished(self) -> None: self._update_display()
    def watch_is_break_mode(self) -> None: self._update_display()

    def _update_display(self) -> None:
        """Refreshes the visual state of all timer controls and titles."""
        try:
            control_button = self.query_one("#timer-control-button", Button)
            timer_title = self.query_one("#timer-title", Label)
            use_emojis = self.ctx.config.display.use_emojis
            mode_str = f"{get_icon('glance', use_emojis)} Break" if self.is_break_mode else f"{get_icon('streak', use_emojis)} Focus"
            timer_icon = get_icon("timer", use_emojis)

            if self.is_running: timer_title.update(f"[bold $primary]{timer_icon} Timer [{mode_str}][/bold $primary]")
            else: timer_title.update(f"[dim]{timer_icon} Timer [{mode_str}][/dim]")

            if self.is_finished:
                control_button.label, control_button.variant = "\\[ DONE ]", "primary"
            elif self.is_running:
                control_button.label, control_button.variant = "\\[ PAUSE ]", "success"
            else:
                control_button.label, control_button.variant = "\\[ START ]", "warning"
        except Exception: pass

    def update_session_meta(self) -> None:
        """Refreshes the session metadata labels (tags and project)."""
        try:
            meta_label = self.query_one("#timer-session-meta", Label)
            parts = []
            display_project = "Break" if self.is_break_mode else self.project

            if self.tags and not self.is_break_mode:
                tags_str = " ".join([f"[{TAG}]#{tag}[/{TAG}]" for tag in self.tags])
                parts.append(f"Session: {tags_str}")

            if display_project: parts.append(f"[{PROJECT}]{display_project}[/{PROJECT}]")
            meta_label.update(" | ".join(parts) if parts else "")
            meta_label.display = True
        except Exception:
            self.set_timer(0.1, self.update_session_meta)

    def _start_timer(self) -> None:
        """Initiates the countdown sequence."""
        self.is_running = True
        self._schedule_tick()
        self.post_message(TimerStateChanged(is_running=True, remaining_seconds=self.remaining_seconds))

    def _schedule_tick(self) -> None:
        """Schedules the next temporal increment."""
        if self.is_running and not self.is_finished:
            self._timer_handle = self.set_timer(1.0, self._tick_and_schedule)

    def _tick_and_schedule(self) -> None:
        """Executes a tick and re-schedules."""
        self._tick()
        if self.is_running and not self.is_finished: self._schedule_tick()

    def _stop_timer(self) -> None:
        """Halts the countdown sequence."""
        self.is_running = False
        if self._timer_handle:
            self._timer_handle.stop()
            self._timer_handle = None
        self.post_message(TimerStateChanged(is_running=False, remaining_seconds=self.remaining_seconds))

    def _reset_timer(self) -> None:
        """Resets the timer to default configuration states."""
        self._stop_timer()
        self.is_break_mode, self.is_finished, self.is_running = False, False, False
        self.initial_minutes = self.work_duration
        self.project, self.tags = None, []
        self.remaining_seconds = self.total_seconds = self.initial_minutes * 60
        
        try: self.query_one("#timer-break-switch", Switch).value = False
        except Exception: pass
        self._update_display()
        self.update_session_meta()

    def _tick(self) -> None:
        """Decrements the remaining time."""
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            if self.remaining_seconds == 0: self._timer_finished()

    def _timer_finished(self) -> None:
        """Handles session expiration."""
        self._stop_timer()
        self.is_finished = True
        self.notify("Session complete!")
        self._show_session_complete()

    def _show_session_complete(self) -> None:
        """Displays the completion modal for activity logging."""
        completed_minutes = self.initial_minutes
        default_content = f"Completed {completed_minutes}m timer session"

        def on_dismiss(result: str | None) -> None:
            if result:
                try:
                    parsed = parse_quick_add(result)
                    all_tags = list(self.tags)
                    for tag in parsed.tags:
                        if tag not in all_tags: all_tags.append(tag)

                    project = parsed.project or ("Break" if self.is_break_mode else self.project)
                    entry = self.ctx.db.add_entry(content=parsed.content, tags=all_tags, project=project, created_at=datetime.now())
                    self.post_message(EntryAdded(entry_id=entry.id, content=entry.content, created_at=entry.created_at))
                except Exception as e:
                    self.notify(f"Log error: {e}", severity="error")
            self._reset_timer()

        self.app.push_screen(SessionCompleteModal(minutes=completed_minutes, default_content=default_content, tags=self.tags, project=self.project), on_dismiss)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatches button interaction events."""
        if event.button.id == "timer-control-button": self.action_toggle_pause()
        elif event.button.id == "btn-plus-1": self._adjust_time(1)
        elif event.button.id == "btn-plus-5": self._adjust_time(5)
        elif event.button.id == "btn-minus-1": self._adjust_time(-1)
        elif event.button.id == "btn-minus-5": self._adjust_time(-5)
        elif event.button.id == "timer-clear-button": self.action_clear_timer()

    def _adjust_time(self, minutes: int) -> None:
        """Modifies the current timer duration.

        Args:
            minutes (int): Minutes to add or subtract.
        """
        if self.is_finished: return
        new_total = self.remaining_seconds + (minutes * 60)
        if new_total < 60:
            self.notify("Minimum 1 minute required", severity="warning")
            return

        self.total_seconds = new_total
        self.remaining_seconds = new_total
        self.initial_minutes = new_total // 60
        self._update_display()

    def action_clear_timer(self) -> None:
        """Resets the timer to baseline durations."""
        if self.is_finished: return
        self._stop_timer()
        self.work_duration = self.ctx.config.timer.work_duration
        self.break_duration = self.ctx.config.timer.break_duration
        default_minutes = self.break_duration if self.is_break_mode else self.work_duration
        self.initial_minutes = default_minutes
        new_seconds = default_minutes * 60
        self.total_seconds = new_seconds
        self.remaining_seconds = new_seconds
        self._update_display()

    def action_toggle_break_mode(self) -> None:
        """Switches between focus and break modes."""
        self.is_break_mode = not self.is_break_mode
        new_duration = self.break_duration if self.is_break_mode else self.work_duration
        self.project = "Break" if self.is_break_mode else None
        self.initial_minutes = new_duration
        
        # Update total_seconds first, then remaining_seconds to avoid negative progress in watchers
        new_seconds = new_duration * 60
        self.total_seconds = new_seconds
        self.remaining_seconds = new_seconds
        
        try: self.query_one("#timer-break-switch", Switch).value = self.is_break_mode
        except Exception: pass
        self._update_display()
        self.update_session_meta()

    def action_toggle_pause(self) -> None:
        """Toggles the running state of the timer."""
        if self.is_finished: return
        if not self.is_running:
            # Sync inputs before starting
            try:
                dur_str = self.query_one("#input-duration", Input).value
                self.initial_minutes = int(dur_str)
                # If we're starting fresh, update remaining/total
                if self.remaining_seconds == self.total_seconds:
                    self.total_seconds = self.remaining_seconds = self.initial_minutes * 60
                
                # Strip & and # flags from inputs
                raw_project = self.query_one("#input-project", Input).value
                self.project = raw_project.lstrip("&").strip() or None
                
                tags_str = self.query_one("#input-tags", Input).value
                raw_tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                self.tags = [t.lstrip("#").strip() for t in raw_tags]
                
                self.update_session_meta()
            except ValueError:
                self.notify("Invalid duration", severity="error")
                return

            self._start_timer()
        else:
            self._stop_timer()
        self._update_display()

    def action_add_5_min(self) -> None: self._adjust_time(5)
    def action_subtract_5_min(self) -> None: self._adjust_time(-5)

    def action_finish(self) -> None:
        """Terminates the current session early."""
        if not self.is_finished:
            self._stop_timer()
            self._timer_finished()

    def action_quit(self) -> None:
        """Closes the timer screen."""
        self.remove()
