"""Interactive focus timer TUI using Textual.

This module provides a real-time Pomodoro timer with pause/resume
and session logging capabilities.
"""

from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Static,
)


class GradientBar(Static):
    """A custom gradient progress bar using colored block characters."""

    DEFAULT_CSS = """
    GradientBar {
        height: 1;
        margin: 2 0;
        background: $surface;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the gradient bar.

        Args:
            **kwargs: Additional arguments passed to Static.
        """
        super().__init__("", **kwargs)
        self.progress_pct = 0.0

    def set_progress(self, pct: float) -> None:
        """Set the progress percentage (0.0 to 1.0).

        Args:
            pct: Progress percentage.
        """
        self.progress_pct = max(0.0, min(1.0, pct))
        self._update_bar()

    def _update_bar(self) -> None:
        """Update the bar display with gradient colors."""
        bar_width = 50
        filled_width = int(self.progress_pct * bar_width)

        # Custom gradient palette: green → yellow-green → yellow → orange → red
        palette = [
            (0.0, "#44ce1b"),    # Green
            (0.25, "#bbdb44"),   # Yellow-green
            (0.5, "#f7e379"),    # Yellow
            (0.75, "#f2a134"),   # Orange
            (1.0, "#e51f1f"),    # Red
        ]

        segments = []
        for i in range(bar_width):
            if i < filled_width:
                pct = i / bar_width
                # Find the color for this position
                color = self._interpolate_color(pct, palette)
                segments.append(f"[{color}]▃[/{color}]")
            else:
                segments.append("[dim]─[/dim]")

        self.update("".join(segments))

    def _interpolate_color(self, pct: float, palette: list) -> str:
        """Interpolate color from palette based on percentage.

        Args:
            pct: Position from 0.0 to 1.0.
            palette: List of (position, hex_color) tuples.

        Returns:
            Hex color string.
        """
        # Find the two colors to interpolate between
        for i in range(len(palette) - 1):
            pos1, color1 = palette[i]
            pos2, color2 = palette[i + 1]
            if pos1 <= pct <= pos2:
                if pos2 == pos1:
                    return color1
                # Linear interpolation
                t = (pct - pos1) / (pos2 - pos1)
                return self._blend_colors(color1, color2, t)
        return palette[-1][1]

    def _blend_colors(self, color1: str, color2: str, t: float) -> str:
        """Blend two hex colors.

        Args:
            color1: First hex color (e.g., "#44ce1b").
            color2: Second hex color.
            t: Blend factor (0.0 = color1, 1.0 = color2).

        Returns:
            Blended hex color string.
        """
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return f"#{r:02x}{g:02x}{b:02x}"


class SessionCompleteModal(ModalScreen):
    """Modal dialog for logging a completed focus session."""

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
        tags: Optional[list] = None,
        project: Optional[str] = None,
        **kwargs,
    ):
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
        self.result: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="modal-container"):
            yield Label("✅ Focus Session Complete!", id="modal-title")
            yield Label(
                f"Completed {self.minutes} minutes of focused work",
                id="session-info",
            )
            yield Input(
                value=self.default_content,
                id="edit-input",
                placeholder="What did you accomplish?",
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

    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class FocusTimerApp(App):
    """Interactive focus timer application.

    Provides a real-time Pomodoro timer with pause/resume capability.

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

    #timer-container {
        height: 1fr;
        align: center middle;
    }

    #timer-display {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
    }

    #timer-label {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        padding: 1 0;
    }

    #status-label {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        padding: 1 0;
    }

    #progress-container {
        width: 100%;
        height: auto;
        padding: 1 4;
    }

    #gradient-progress {
        height: 1;
        margin: 2 0;
    }

    #session-info {
        dock: bottom;
        height: auto;
        background: $panel;
        content-align: center middle;
        padding: 1 0;
    }

    .paused {
        color: $warning;
    }

    .running {
        color: $success;
    }

    .finished {
        color: $accent;
    }
    """

    BINDINGS = [
        ("space", "toggle_pause", "Pause/Resume"),
        ("+", "add_time", "+5 min"),
        ("-", "subtract_time", "-5 min"),
        ("enter", "finish", "Finish"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(
        self,
        db,
        console,
        minutes: int = 25,
        tags: Optional[list] = None,
        project: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the focus timer application.

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
        self.remaining_seconds = minutes * 60
        self.total_seconds = minutes * 60
        self._is_running = False
        self._is_finished = False
        self.tags = tags or []
        self.project = project
        self._timer_handle: Optional[int] = None

    @property
    def is_running(self) -> bool:
        """Check if timer is running."""
        return self._is_running

    @property
    def is_finished(self) -> bool:
        """Check if timer is finished."""
        return self._is_finished

    def compose(self) -> ComposeResult:
        """Compose the timer UI layout."""
        yield Header()
        with Vertical():
            with Container(id="timer-container"):
                yield Label(
                    self._format_time(self.remaining_seconds),
                    id="timer-display",
                )
                yield Label("Focus Timer", id="timer-label")
                yield Label(
                    "▶ Running" if self.is_running else "⏸ Paused",
                    id="status-label",
                    classes="running" if self.is_running else "paused",
                )
            with Container(id="progress-container"):
                yield GradientBar(id="gradient-progress")
        yield Label(
            "Space: Pause/Resume | +/-: Adjust Time | Enter: Finish | q: Quit",
            id="session-info",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start the timer on mount."""
        self._update_display()
        self._start_timer()

    def on_unmount(self) -> None:
        """Clean up timer on unmount."""
        if self._timer_handle is not None:
            self.set_timer(self._timer_handle, None)

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
        timer_display = self.query_one("#timer-display", Label)
        status_label = self.query_one("#status-label", Label)
        gradient_bar = self.query_one("#gradient-progress", GradientBar)

        timer_display.update(self._format_time(self.remaining_seconds))

        if self.is_finished:
            status_label.update("✅ Complete!")
            status_label.remove_class("running")
            status_label.remove_class("paused")
            status_label.add_class("finished")
        elif self.is_running:
            status_label.update("▶ Running")
            status_label.remove_class("paused")
            status_label.remove_class("finished")
            status_label.add_class("running")
        else:
            status_label.update("⏸ Paused")
            status_label.remove_class("running")
            status_label.remove_class("finished")
            status_label.add_class("paused")

        # Update gradient bar based on progress
        elapsed = self.total_seconds - self.remaining_seconds
        progress_pct = elapsed / self.total_seconds if self.total_seconds > 0 else 0
        gradient_bar.set_progress(progress_pct)

    def _start_timer(self) -> None:
        """Start the timer countdown."""
        self._is_running = True
        self._update_display()
        self._timer_handle = self.set_interval(1, self._tick)

    def _stop_timer(self) -> None:
        """Stop the timer countdown."""
        self._is_running = False
        self._update_display()
        if self._timer_handle is not None:
            self.set_timer(self._timer_handle, None)
            self._timer_handle = None

    def _tick(self) -> None:
        """Decrement the timer by one second."""
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()

            if self.remaining_seconds == 0:
                self._timer_finished()

    def _timer_finished(self) -> None:
        """Handle timer completion."""
        self._stop_timer()
        self._is_finished = True
        self.notify("Focus session complete!", timeout=2)
        self._show_session_complete()

    def _show_session_complete(self) -> None:
        """Show the session complete modal."""
        completed_minutes = self.initial_minutes
        default_content = f"Completed {completed_minutes}m focus session"

        def on_dismiss(result: Optional[str]) -> None:
            if result:
                try:
                    entry = self.db.add_entry(
                        content=result,
                        tags=self.tags,
                        project=self.project,
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

    def _show_quit_confirmation(self) -> None:
        """Show quit confirmation modal."""

        class ConfirmQuitModal(ModalScreen):
            """Confirmation dialog for quitting."""

            CSS = """
            ConfirmQuitModal {
                align: center middle;
            }

            #confirm-container {
                width: 60;
                height: auto;
                background: $surface;
                border: thick $warning;
                padding: 1 3;
            }

            #confirm-message {
                text-align: center;
                padding: 1 0;
            }

            #confirm-buttons {
                align: center middle;
                padding: 1 0;
            }
            """

            BINDINGS = [
                ("y", "confirm", "Yes"),
                ("n", "cancel", "No"),
                ("escape", "cancel", "Cancel"),
            ]

            def compose(self) -> ComposeResult:
                with Container(id="confirm-container"):
                    yield Label(
                        "Quit without logging this session?",
                        id="confirm-message",
                    )
                    with Container(id="confirm-buttons"):
                        yield Button("Quit", id="yes-btn", variant="warning")
                        yield Button("Continue", id="no-btn", variant="default")

            def action_confirm(self) -> None:
                self.dismiss(True)

            def action_cancel(self) -> None:
                self.dismiss(False)

            def on_button_pressed(self, event) -> None:
                if event.button.id == "yes-btn":
                    self.action_confirm()
                elif event.button.id == "no-btn":
                    self.action_cancel()

        def on_dismiss(confirmed: bool) -> None:
            if confirmed:
                self.notify("Session not logged", timeout=1.5)
                self.exit()

        self.push_screen(ConfirmQuitModal(), on_dismiss)

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

    def action_add_time(self) -> None:
        """Add 5 minutes to the timer."""
        if self.is_finished:
            return

        self.remaining_seconds += 5 * 60
        self.total_seconds += 5 * 60
        self.initial_minutes += 5
        self._update_display()
        self.notify("Added 5 minutes", timeout=1)

    def action_subtract_time(self) -> None:
        """Subtract 5 minutes from the timer (minimum 1 minute)."""
        if self.is_finished:
            return

        if self.remaining_seconds > 5 * 60:
            self.remaining_seconds -= 5 * 60
            self.total_seconds -= 5 * 60
            self.initial_minutes -= 5
            self._update_display()
            self.notify("Subtracted 5 minutes", timeout=1)
        else:
            self.notify("Minimum 1 minute required", severity="warning", timeout=1.5)

    def action_finish(self) -> None:
        """Finish the session early."""
        if self.is_finished:
            return

        self._stop_timer()
        self._timer_finished()

    def action_quit(self) -> None:
        """Quit the timer with confirmation."""
        if self.is_finished:
            self.exit()
        elif self.remaining_seconds == self.total_seconds:
            # Timer hasn't started, quit without confirmation
            self.exit()
        else:
            self._show_quit_confirmation()
