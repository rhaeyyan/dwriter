"""Timer screen for dwriter TUI.

This module provides a timer-style timer for focused work sessions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch

from ...cli import AppContext
from ..messages import EntryAdded, TimerStateChanged
from ..parsers import parse_quick_add


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
        border: thick $success;
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
        tags: list[str] | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the session complete modal.

        Args:
            minutes: Duration of the completed session.
            default_content: Default entry content.
            tags: Optional tags to pre-fill.
            project: Optional project to pre-fill.
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
                f"Record your {self.minutes} minute{'s' if self.minutes != 1 else ''} of activity:",
                id="session-info",
            )
            yield Input(
                value=self.default_content,
                id="edit-input",
                placeholder="What did you do?",
            )

            # Show tags and project if provided
            if self.tags or self.project:
                meta_parts = []
                if self.tags:
                    meta_parts.append(f"Tags: #{', #'.join(self.tags)}")
                if self.project:
                    meta_parts.append(f"Project: {self.project}")
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


class TimerProgressBar(Static):
    """Custom progress bar with gradient pips and tomato indicator."""

    DEFAULT_CSS = """
    TimerProgressBar {
        height: 3;
        margin: 1 0;
        padding: 0 2;
        content-align: center middle;
        background: $panel;
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
        """Render the progress bar with single color pips."""
        if self.total_seconds <= 0:
            self.update("No time set")
            return

        progress = 1.0 - (self.remaining_seconds / self.total_seconds)
        percentage = int(progress * 100)

        bar_width = 30
        filled = int(bar_width * progress)

        from rich.text import Text

        text = Text()

        # Single color for the progress bar
        bar_color = "#f2a134"

        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"

        # Cyan for time and percentage
        text.append(f"{time_str}  [ ", style="cyan")

        for i in range(bar_width):
            if i < filled:
                text.append("▮", style=bar_color)
            elif i == filled:
                text.append("🥭")
            else:
                text.append("▯", style="dim")

        text.append(f" ]  {percentage}%", style="cyan")

        self.update(text)


class TimerScreen(Container):
    """Timer screen for focused work sessions.

    Provides a real-time timer with start/pause capability.
    Timer starts in paused state - press Space or click Start to begin.

    Key bindings:
        Space: Start/Pause timer
        +/-: Add/Subtract 5 minutes
        Enter: Finish session early
        q: Quit without logging
    """

    DEFAULT_CSS = """
    TimerScreen {
        height: 1fr;
        align: center middle;
    }

    #timer-main-container {
        height: auto;
        width: 78;
        align: center middle;
        padding: 2 4;
        background: $panel;
        border: solid $primary;
    }

    #timer-header {
        height: 3;
        width: 100%;
        margin-bottom: 1;
        padding: 0 2;
        background: $panel;
    }

    #timer-title {
        text-align: left;
        text-style: bold;
        color: $secondary;
        width: 1fr;
        padding-top: 1;
    }

    #timer-break-mode-container {
        height: auto;
        width: auto;
        align: right middle;
        padding: 0 1;
    }

    #timer-break-label {
        text-align: right;
        padding: 1 1 0 0;
        color: $text-muted;
        width: auto;
    }

    #timer-break-switch {
        margin: 0;
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

    .timer-session-meta {
        text-align: center;
        color: $text-muted;
        padding: 0 0 1 0;
        content-align: center middle;
        width: 100%;
    }

    #timer-adjust-section {
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    #timer-adjust-buttons {
        height: auto;
        align: center middle;
    }

    #timer-adjust-buttons Button {
        margin: 0 1;
        min-width: 6;
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
        Binding("b", "toggle_break_mode", "Break Mode"),
    ]

    # Reactive properties for timer state
    remaining_seconds = reactive(25 * 60)
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
        """Initialize the timer screen.

        Args:
            ctx: Application context with database and configuration.
            minutes: Initial timer duration in minutes.
            tags: Optional tags for the resulting log entry.
            project: Optional project for the resulting log entry.
            **kwargs: Additional arguments passed to Container.
        """
        # Ensure id is passed to parent Container
        super().__init__(**kwargs)
        self.ctx = ctx
        # Load timer config
        config = ctx.config_manager.load()
        self.work_duration = config.timer.work_duration
        self.break_duration = config.timer.break_duration
        self.initial_minutes = minutes
        self.total_seconds = minutes * 60
        self._timer_handle: Any = None
        # Only use explicitly provided tags, NEVER add default config tags
        self.tags = tags if tags is not None else []
        self.project = project
        # Start in paused state, work mode by default
        self.is_running = False
        self.is_break_mode = False

    def compose(self) -> ComposeResult:
        """Compose the timer UI layout."""
        with Container(id="timer-main-container"):
            # Header with title and break toggle
            with Horizontal(id="timer-header"):
                yield Label("⏱️ Timer", id="timer-title")
                with Horizontal(id="timer-break-mode-container"):
                    yield Label("Break:", id="timer-break-label")
                    yield Switch(
                        value=self.is_break_mode,
                        id="timer-break-switch",
                    )

            # Control button (Start/Pause)
            with Horizontal(id="timer-controls"):
                yield Button(
                    "⏸ Paused",
                    id="timer-control-button",
                    variant="warning",
                )

            # Session metadata (tags/project) - centered below button
            yield Label("", id="timer-session-meta", classes="timer-session-meta")

            # Progress bar
            with Container(id="timer-progress-container"):
                yield TimerProgressBar(
                    total_seconds=self.total_seconds,
                    id="timer-progress-bar",
                )

            # Adjust buttons with centered label
            with Vertical(id="timer-adjust-section"):
                yield Label("Add/Remove Minutes:", classes="add-time-label")
                with Horizontal(id="timer-adjust-buttons"):
                    yield Button("+5", id="btn-plus-5", variant="success")
                    yield Button("+1", id="btn-plus-1", variant="success")
                    yield Button("-1", id="btn-minus-1", variant="error")
                    yield Button("-5", id="btn-minus-5", variant="error")

        yield Label(
            "Space: Start/Pause  •  B: Break Mode  •  Enter: Finish  •  ?: Help  •  q: Quit",
            id="timer-session-info",
        )

    def on_mount(self) -> None:
        """Initialize the timer display on mount (starts paused)."""
        self._update_display()
        self.update_session_meta()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle break mode switch toggle.

        Args:
            event: Switch changed event.
        """
        if event.switch.id == "timer-break-switch":
            # Only toggle if the switch value differs from our state
            # This prevents infinite loops when action_toggle_break_mode updates the switch
            if self.is_break_mode != event.value:
                self.action_toggle_break_mode()

    def on_show(self) -> None:
        """Refresh timer display when the screen becomes visible."""
        self._update_display()
        self.update_session_meta()

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

    def watch_is_break_mode(self) -> None:
        """Reactively update display when break mode changes."""
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
            timer_title = self.query_one("#timer-title", Label)

            # Update title with mode
            mode_str = "🧘 Break" if self.is_break_mode else "💼 Work"
            timer_title.update(f"⏱️ Timer [{mode_str}]")

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

    def update_session_meta(self) -> None:
        """Update the session metadata display (tags/project)."""
        try:
            meta_label = self.query_one("#timer-session-meta", Label)
            # Format: "Session: #tag1 #tag2 | $project" (matching Todo Board colors)
            parts = []

            # If in break mode, override project to "Break"
            display_project = "Break" if self.is_break_mode else self.project

            if self.tags and not self.is_break_mode:
                # Yellow tags like Todo Board
                tags_str = " ".join([f"[yellow]#{tag}[/yellow]" for tag in self.tags])
                parts.append(f"Session: {tags_str}")

            if display_project:
                # Magenta project like Todo Board
                parts.append(f"[magenta]{display_project}[/magenta]")

            if parts:
                meta_label.update(" | ".join(parts))
                meta_label.display = True
            else:
                meta_label.display = False
        except Exception as e:
            # Filter the exception so we ONLY retry if it's a DOM mounting issue
            if "NoMatches" in str(type(e)):
                self.set_timer(0.1, self.update_session_meta)
            else:
                # If it's a different error (like a typo), show it
                self.notify(f"Meta error: {e}", severity="error", timeout=4)

    def _start_timer(self) -> None:
        """Start the timer countdown."""
        self.is_running = True
        self._schedule_tick()
        # Post message so app can update tab styling
        self.post_message(
            TimerStateChanged(is_running=True, remaining_seconds=self.remaining_seconds)
        )

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
        # Post message so app can update tab styling
        self.post_message(
            TimerStateChanged(
                is_running=False, remaining_seconds=self.remaining_seconds
            )
        )

    def _reset_timer(self) -> None:
        """Reset timer to initial state for reuse.
        
        Resets to configured work duration and toggles off break mode.
        """
        self._stop_timer()
        
        # Always reset to work mode after a session is logged
        self.is_break_mode = False
        self.initial_minutes = self.work_duration
        self.project = None
            
        self.remaining_seconds = self.initial_minutes * 60
        self.total_seconds = self.initial_minutes * 60
        
        self.is_finished = False
        self.is_running = False
        # Clear tags from previous session
        self.tags = []
        
        # Update switch state in UI
        try:
            self.query_one("#timer-break-switch", Switch).value = False
        except Exception:
            pass
            
        self._update_display()
        self.update_session_meta()

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
                    # Parse the input for tags and projects using & delimiter
                    parsed = parse_quick_add(result)

                    # Use only the tags specified for this timer session
                    # Merge parsed tags with session tags
                    all_tags = list(self.tags)  # Make a copy
                    for tag in parsed.tags:
                        if tag not in all_tags:
                            all_tags.append(tag)

                    # Use project from parsed input if provided, otherwise use session project
                    # Override with "Break" if in break mode
                    project = parsed.project or (
                        "Break" if self.is_break_mode else self.project
                    )

                    entry = self.ctx.db.add_entry(
                        content=parsed.content,
                        tags=all_tags,
                        project=project,
                        created_at=datetime.now(),
                    )
                    # Show what tags were actually saved
                    tags_display = (
                        f" with tags: {', '.join(all_tags)}" if all_tags else ""
                    )
                    project_display = f" on {project}" if project else ""
                    self.notify(
                        f"Logged{tags_display}{project_display}",
                        title="Success",
                        timeout=3,
                    )
                    # Post message for reactive updates to other screens
                    self.post_message(
                        EntryAdded(
                            entry_id=entry.id,
                            content=entry.content,
                            created_at=entry.created_at,
                        )
                    )
                except Exception as e:
                    self.notify(
                        f"Error logging entry: {e}",
                        severity="error",
                        timeout=3,
                    )
            # Reset timer for immediate reuse - don't remove the screen
            self._reset_timer()

        self.app.push_screen(
            SessionCompleteModal(
                minutes=completed_minutes,
                default_content=default_content,
                tags=self.tags,
                project=self.project,
            ),
            on_dismiss,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for time adjustment and control.

        Args:
            event: Button pressed event.
        """
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

    def action_toggle_break_mode(self) -> None:
        """Toggle between work mode and break mode.

        Work mode uses the configured work duration (default 25 min).
        Break mode uses the configured short break duration (default 5 min)
        and sets the project to 'Break'.
        """
        self.is_break_mode = not self.is_break_mode

        # Update timer duration and project based on mode
        if self.is_break_mode:
            new_duration = self.break_duration
            self.project = "Break"
            self.notify(f"Break mode: {new_duration} minutes", timeout=1.5)
        else:
            new_duration = self.work_duration
            self.project = None
            self.notify(f"Work mode: {new_duration} minutes", timeout=1.5)

        # Update timer
        self.initial_minutes = new_duration
        self.total_seconds = new_duration * 60
        self.remaining_seconds = self.total_seconds

        # Update switch state
        try:
            self.query_one("#timer-break-switch", Switch).value = self.is_break_mode
        except Exception:
            pass

        self._update_display()
        self.update_session_meta()

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

    def action_quit(self) -> None:
        """Quit the timer screen."""
        if self.is_finished:
            self.remove()
        elif self.remaining_seconds == self.total_seconds:
            self.remove()
        else:
            self.notify("Session not logged", timeout=1.5)
            self.remove()
