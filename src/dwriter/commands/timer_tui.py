"""Interactive timer TUI using Textual.

This module provides a real-time timer with pause/resume
and session logging capabilities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, Static


class TimerProgressBar(Static):
    """Custom progress bar with gradient pips and tomato indicator."""

    DEFAULT_CSS = """
    TimerProgressBar {
        height: 3;
        margin: 1 0;
        content-align: center middle;
    }

    .progress-label {
        text-style: bold;
    }

    .progress-gradient {
        padding: 0 1;
    }
    """

    def __init__(self, total_seconds: int = 25 * 60, **kwargs: Any) -> None:
        """Initialize the progress bar.

        Args:
            total_seconds: Total duration in seconds.
            **kwargs: Additional arguments passed to Static.
        """
        super().__init__(**kwargs)
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds

    def update_progress(self, remaining: int, total: int) -> None:
        """Update the progress bar.

        Args:
            remaining: Remaining seconds.
            total: Total seconds.
        """
        self.remaining_seconds = remaining
        self.total_seconds = total
        self._render_bar()

    def _get_gradient_color(self, position: float) -> str:
        """Get color for a pip based on its position in the bar.

        Args:
            position: Position from 0.0 (left) to 1.0 (right).

        Returns:
            Hex color string (green → yellow → orange → red).
        """
        if position < 0.25:
            return "#00ff00"  # Green
        elif position < 0.5:
            return "#7fff00"  # Green-yellow
        elif position < 0.75:
            return "#ffff00"  # Yellow
        elif position < 0.85:
            return "#ffa500"  # Orange
        else:
            return "#ff0000"  # Red

    def _render_bar(self) -> None:
        """Render the progress bar with gradient pips and mango indicator."""
        if self.total_seconds <= 0:
            self.update("[dim]No time set[/dim]")
            return

        progress = 1.0 - (self.remaining_seconds / self.total_seconds)
        int(progress * 100)

        self._render_bar()

    def _render_bar(self) -> None:
        """Render the progress bar with gradient pips and mango indicator."""
        if self.total_seconds <= 0:
            self.update("No time set")
            return

        progress = 1.0 - (self.remaining_seconds / self.total_seconds)
        percentage = int(progress * 100)

        # Build progress bar
        bar_width = 30
        filled = int(bar_width * progress)

        # Build the bar - use plain text without markup
        bar_parts = []
        for i in range(bar_width):
            if i < filled:
                bar_parts.append("▮")
            elif i == filled:
                bar_parts.append("🥭")
            else:
                bar_parts.append("▯")

        bar_str = "".join(bar_parts)

        # Format time display
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"

        self.update(f"{time_str}  [ {bar_str} ]  {percentage}%")


class SessionCompleteModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for logging a completed session."""

    CSS = """
    SessionCompleteModal {
        align: center middle;
    }

    #modal-container {
        width: 80;
        height: auto;
        background: $surface;
        border: solid $success;
        padding: 1 3;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        color: $success;
        padding: 1 0;
    }

    #session-info {
        text-align: center;
        padding: 0 0 1 0;
    }

    #edit-input {
        width: 100%;
        margin: 1 0;
    }

    #session-meta {
        text-align: center;
        color: $text-muted;
        padding: 0 0 1 0;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
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
        tags: list[Any] | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the session complete modal.

        Args:
            minutes: Duration of the completed session.
            default_content: Default entry content.
            tags: Optional tags for the entry.
            project: Optional project for the entry.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.minutes = minutes
        self.default_content = default_content
        self.tags = tags or []
        self.project = project
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="modal-container"):
            yield Label("✅ Session Complete!", id="modal-title")
            yield Label(
                f"Completed {self.minutes} minutes of focused work",
                id="session-info",
            )
            yield Input(
                value=self.default_content,
                id="edit-input",
                placeholder="What did you accomplish?",
            )

            # Show tags and project if provided
            if self.tags or self.project:
                meta_parts = []
                if self.tags:
                    tags_str = " ".join([f"#{tag}" for tag in self.tags])
                    meta_parts.append(f"Session: {tags_str}")
                if self.project:
                    meta_parts.append(f"${self.project}")
                yield Label(
                    " | ".join(meta_parts),
                    id="session-meta",
                    classes="session-meta",
                )

            with Container(id="edit-buttons"):
                yield Button("Log Entry", id="save-btn", variant="success")
                yield Button("Skip", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Save the session log."""
        input_widget = self.query_one("#edit-input", Input)
        self.result = input_widget.value.strip()
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel logging."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class TimerApp(App):  # type: ignore[type-arg]
    """Interactive timer application.

    Provides a real-time timer with pause/resume capability.
    Timer starts automatically on mount.

    Key bindings:
        Space: Pause/Resume timer
        +/-: Add/Subtract 5 minutes
        Enter: Finish session early
        q: Quit without logging
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: auto;
        width: auto;
        align: center middle;
        padding: 2 4;
        background: $panel;
        border: solid #45475a;
    }

    #timer-title {
        text-align: center;
        text-style: bold;
        padding: 0 0 1 0;
        color: $text-muted;
    }

    #timer-controls {
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    #timer-control-button {
        min-width: 15;
        height: 3;
    }

    #timer-adjust-buttons {
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    #timer-adjust-buttons Button {
        margin: 0 1;
        min-width: 6;
    }

    #timer-progress-container {
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    #session-info {
        dock: bottom;
        height: 1;
        background: $panel;
        content-align: center middle;
        padding: 0 2;
    }

    .paused-button {
        background: $warning;
        color: $foreground;
    }

    .running-button {
        background: $success;
        color: $foreground;
    }

    .finished-button {
        background: $accent;
        color: $foreground;
    }
    """

    BINDINGS = [
        Binding("space", "toggle_pause", "Pause/Resume"),
        Binding("+", "add_5_min", "+5 min"),
        Binding("-", "subtract_5_min", "-5 min"),
        Binding("enter", "finish", "Finish"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("?", "goto_help", "Help", show=True),
    ]

    # Reactive properties for timer state
    remaining_seconds = reactive(25 * 60)
    is_running = reactive(False)
    is_finished = reactive(False)

    def __init__(
        self,
        db: Any,
        console: Any,
        minutes: int = 25,
        tags: list[Any] | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the timer application.

        Args:
            db: Database instance for logging sessions.
            console: Rich console instance.
            minutes: Initial timer duration in minutes.
            tags: Optional tags for the session entry.
            project: Optional project for the session entry.
            **kwargs: Additional arguments passed to App.
        """
        super().__init__(**kwargs)
        self.db = db
        self.console = console
        self.initial_minutes = minutes
        self.total_seconds = minutes * 60
        self._timer_handle: Any = None
        self.tags = tags or []
        self.project = project
        # Start in paused state - user must press Space or click to start
        self.is_running = False

    def compose(self) -> ComposeResult:
        """Compose the timer UI layout."""
        yield Header()
        with Container(id="main-container"):
            yield Label("⏱️ Timer", id="timer-title")

            # Control button (Start/Pause)
            with Horizontal(id="timer-controls"):
                yield Button(
                    "⏸ Paused",
                    id="timer-control-button",
                    variant="warning",
                )

            # Progress bar
            with Container(id="timer-progress-container"):
                yield TimerProgressBar(
                    total_seconds=self.total_seconds,
                    id="timer-progress-bar",
                )

            # Adjust buttons
            with Horizontal(id="timer-adjust-buttons"):
                yield Button("+5", id="btn-plus-5", variant="success")
                yield Button("+1", id="btn-plus-1", variant="success")
                yield Button("-1", id="btn-minus-1", variant="error")
                yield Button("-5", id="btn-minus-5", variant="error")

        yield Label(
            "Space: Start/Pause  •  Enter: Finish  •  ?: Help  •  q: Quit",
            id="session-info",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the timer display on mount."""
        self._update_display()

    def on_unmount(self) -> None:
        """Clean up timer on unmount."""
        if self._timer_handle is not None:
            self._timer_handle.stop()
            self._timer_handle = None

    def watch_remaining_seconds(self) -> None:
        """Reactively update display when remaining seconds change."""
        self._update_display()
        # Update progress bar
        try:
            progress_bar = self.query_one("#timer-progress-bar", TimerProgressBar)
            progress_bar.update_progress(self.remaining_seconds, self.total_seconds)
        except Exception:
            pass

    def watch_is_running(self) -> None:
        """Reactively update display when running state changes."""
        self._update_display()

    def watch_is_finished(self) -> None:
        """Reactively update display when finished state changes."""
        self._update_display()

    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted time string.
        """
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _update_display(self) -> None:
        """Update the timer display."""
        try:
            control_button = self.query_one("#timer-control-button", Button)
            progress_bar = self.query_one("#timer-progress-bar", TimerProgressBar)

            # Update progress bar
            progress_bar.update_progress(self.remaining_seconds, self.total_seconds)

            # Update control button
            if self.is_finished:
                control_button.label = "✅ Complete!"
                control_button.variant = "success"
                control_button.remove_class("paused-button")
                control_button.remove_class("running-button")
                control_button.add_class("finished-button")
            elif self.is_running:
                control_button.label = "▶ Running"
                control_button.variant = "success"
                control_button.remove_class("paused-button")
                control_button.remove_class("finished-button")
                control_button.add_class("running-button")
            else:
                control_button.label = "⏸ Paused"
                control_button.variant = "warning"
                control_button.remove_class("running-button")
                control_button.remove_class("finished-button")
                control_button.add_class("paused-button")
        except Exception:
            pass

    def _start_timer(self) -> None:
        """Start the timer countdown."""
        self.is_running = True
        self._schedule_tick()

    def _schedule_tick(self) -> None:
        """Schedule the next tick in 1 second."""
        if self.is_running and not self.is_finished:
            self._timer_handle = self.set_timer(1.0, self._tick_and_schedule)

    def _tick_and_schedule(self) -> None:
        """Tick and schedule next tick."""
        self._tick()
        if self.is_running and not self.is_finished:
            self._schedule_tick()

    def _stop_timer(self) -> None:
        """Stop the timer countdown."""
        self.is_running = False
        if self._timer_handle is not None:
            self._timer_handle.stop()
            self._timer_handle = None

    def _tick(self) -> None:
        """Decrement the timer by one second."""
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            if self.remaining_seconds == 0:
                self._timer_finished()

    def _timer_finished(self) -> None:
        """Handle timer completion."""
        self._stop_timer()
        self.is_finished = True
        self.notify("Session complete!", timeout=2)
        self._show_session_complete()

    def _show_session_complete(self) -> None:
        """Show the session complete modal with tags and project."""
        completed_minutes = self.initial_minutes
        default_content = f"Completed {completed_minutes}m timer session"

        def on_dismiss(result: str | None) -> None:
            if result:
                try:
                    entry = self.db.add_entry(
                        content=result,
                        tags=self.tags,
                        project=self.project,
                        created_at=datetime.now(),
                    )
                    self.notify(f"Entry logged: {entry.content}", timeout=2)
                except Exception as e:
                    self.notify(
                        f"Error logging entry: {e}",
                        severity="error",
                        timeout=3,
                    )
            self.exit()

        self.push_screen(
            SessionCompleteModal(
                minutes=completed_minutes,
                default_content=default_content,
                tags=self.tags,
                project=self.project,
            ),
            on_dismiss,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for time adjustment and control."""
        if event.button.id == "timer-control-button":
            # Toggle pause/resume when clicking the control button
            self.action_toggle_pause()
        elif event.button.id == "btn-plus-1":
            self._adjust_time(1)
        elif event.button.id == "btn-plus-5":
            self._adjust_time(5)
        elif event.button.id == "btn-minus-1":
            self._adjust_time(-1)
        elif event.button.id == "btn-minus-5":
            self._adjust_time(-5)

    def _adjust_time(self, minutes: int) -> None:
        """Adjust timer by specified minutes.

        Args:
            minutes: Minutes to add (positive) or subtract (negative).
        """
        if self.is_finished:
            return

        seconds_to_adjust = minutes * 60
        new_total = self.remaining_seconds + seconds_to_adjust

        if new_total < 60:
            self.notify("Minimum 1 minute required", severity="warning", timeout=1.5)
            return

        self.remaining_seconds = new_total
        self.total_seconds = new_total
        self.initial_minutes = self.remaining_seconds // 60

        if minutes > 0:
            msg = f"Added {minutes} minute{'s' if minutes > 1 else ''}"
            self.notify(msg, timeout=1)
        else:
            msg = f"Subtracted {abs(minutes)} minute"
            msg += "s" if abs(minutes) > 1 else ""
            self.notify(msg, timeout=1)

        self._update_display()

    def action_toggle_pause(self) -> None:
        """Toggle timer pause/resume."""
        if self.is_finished:
            return

        if self.is_running:
            self._stop_timer()
            self.notify("Timer paused", timeout=1)
        else:
            self._start_timer()
            self.notify("Timer resumed", timeout=1)
        self._update_display()

    def action_add_5_min(self) -> None:
        """Add 5 minutes to the timer."""
        self._adjust_time(5)

    def action_subtract_5_min(self) -> None:
        """Subtract 5 minutes from the timer."""
        self._adjust_time(-5)

    def action_finish(self) -> None:
        """Finish the session early."""
        if self.is_finished:
            return

        self._stop_timer()
        self._timer_finished()

    def action_quit(self) -> None:  # type: ignore[override]
        """Quit the timer with confirmation."""
        if self.is_finished:
            self.exit()
        elif self.remaining_seconds == self.total_seconds:
            # Timer hasn't started, quit without confirmation
            self.exit()
        else:
            self.notify("Session not logged", timeout=1.5)
            self.exit()

    def action_goto_help(self) -> None:
        """Navigate to the help TUI."""
        from .help_tui import HelpScreen

        self.push_screen(HelpScreen())
