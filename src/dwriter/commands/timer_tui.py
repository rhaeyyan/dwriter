"""Interactive timer TUI using Textual.

This module provides a real-time pomodoro-style timer with pause/resume
and session logging capabilities.
"""

from __future__ import annotations

from typing import Any

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
from rich.text import Text

from ..ui_utils import HelpOverlay


class TomatoProgressBar(Static):
    """A clean tomato-themed progress bar with filled/empty blocks."""

    DEFAULT_CSS = """
    TomatoProgressBar {
        height: auto;
        margin: 1 0;
        padding: 0;
        background: transparent;
    }

    TomatoProgressBar .timer-display {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    TomatoProgressBar .progress-bar {
        text-align: center;
        padding: 0 0;
    }

    TomatoProgressBar .progress-label {
        text-align: center;
        color: $text-muted;
        padding: 0 0 1 0;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the tomato progress bar.

        Args:
            **kwargs: Additional arguments passed to Static.
        """
        super().__init__("", **kwargs)
        self.progress_pct = 0.0
        self.remaining_seconds = 0
        self.total_seconds = 0

    def set_progress(self, pct: float, remaining: int, total: int) -> None:
        """Set the progress percentage and time info.

        Args:
            pct: Progress percentage (0.0 to 1.0).
            remaining: Remaining seconds.
            total: Total seconds.
        """
        self.progress_pct = max(0.0, min(1.0, pct))
        self.remaining_seconds = remaining
        self.total_seconds = total
        self._update_bar()

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

    def _update_bar(self) -> None:
        """Update the progress bar display."""
        bar_width = 20  # Total width for the bar portion

        filled = int(self.progress_pct * bar_width)
        empty = bar_width - filled

        # Calculate percentage for display
        pct_display = int(self.progress_pct * 100)

        # Build the bar: filled blocks + tomato + empty blocks
        # Use red filled blocks for completed portion
        filled_part = "[red]▮[/red]" * filled if filled > 0 else ""

        # Add tomato emoji at the progress point (if not at end)
        tomato = ""
        if filled < bar_width:
            tomato = "🍅"
            empty -= 1  # Account for tomato width

        # Empty blocks for remaining portion
        empty_part = "[dim]▯[/dim]" * empty if empty > 0 else ""

        # Combine all parts
        bar_text = f"{filled_part}{tomato}{empty_part}"

        # Display: [ bar ] percentage
        self.update(f"[ {bar_text} ] {pct_display}%")


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

    Provides a real-time pomodoro-style timer with pause/resume capability.

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
        height: 1fr;
        align: center middle;
        padding: 1 2;
    }

    #top-controls {
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    #time-display {
        width: auto;
        height: auto;
        text-style: bold;
        padding: 0 2;
    }

    #status-label {
        width: auto;
        height: auto;
        text-style: bold;
        padding: 0 2;
    }

    #button-left, #button-right {
        height: auto;
        align: center middle;
    }

    #button-left Button, #button-right Button {
        margin: 0 1;
        min-width: 6;
    }

    #progress-container {
        height: 1fr;
        align: center middle;
        padding: 1 0;
    }

    #progress-bar {
        width: auto;
        height: auto;
        text-align: center;
        text-style: bold;
    }

    #session-info {
        dock: bottom;
        height: 1;
        background: $panel;
        content-align: center middle;
        padding: 0 2;
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
        ("+", "add_5_min", "+5 min"),
        ("-", "subtract_5_min", "-5 min"),
        ("enter", "finish", "Finish"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("?", "show_help", "Help"),
    ]

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
        self.remaining_seconds = minutes * 60
        self.total_seconds = minutes * 60
        self._is_running = False
        self._is_finished = False
        self.tags = tags or []
        self.project = project
        self._timer_handle: Any = None

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
        from textual.widgets import Button
        from textual.containers import Horizontal
        
        yield Header()
        with Container(id="main-container"):
            # Top row: [+5] [+1] [Status] [-1] [+5]
            with Horizontal(id="top-controls"):
                # Left buttons (green, add time) - order: +5, +1
                with Horizontal(id="button-left"):
                    yield Button("+5", id="btn-plus-5", variant="success")
                    yield Button("+1", id="btn-plus-1", variant="success")
                
                # Status in center
                yield Label(
                    "▶ Running" if self.is_running else "⏸ Paused",
                    id="status-label",
                    classes="running" if self.is_running else "paused",
                )
                
                # Right buttons (red, subtract time) - order: -1, -5
                with Horizontal(id="button-right"):
                    yield Button("-1", id="btn-minus-1", variant="error")
                    yield Button("-5", id="btn-minus-5", variant="error")
            
            # Progress bar centered at bottom: mm:ss [ ▮▮🍅▯▯ ] 40%
            with Container(id="progress-container"):
                yield Label(
                    self._format_progress_line(),
                    id="progress-bar",
                )
        
        # Clean footer with minimal info
        yield Label(
            "Space: Pause/Resume  •  Enter: Finish  •  ?: Help  •  q: Quit",
            id="session-info",
        )
        yield Footer()

    def _format_progress_line(self) -> Text:
        """Format the progress line: mm:ss [ bar ] percentage"""
        elapsed = self.total_seconds - self.remaining_seconds
        progress_pct = elapsed / self.total_seconds if self.total_seconds > 0 else 0
        
        bar_width = 20
        filled = int(progress_pct * bar_width)
        empty = bar_width - filled
        
        # Gradient color palette: green → yellow-green → yellow → orange → red
        gradient_colors = [
            "#44ce1b",    # Green
            "#bbdb44",    # Yellow-green
            "#f7e379",    # Yellow
            "#f2a134",    # Orange
            "#e51f1f",    # Red
        ]
        
        # Build the progress line using Rich Text for proper styling
        time_str = self._format_time(self.remaining_seconds)
        pct_display = int(progress_pct * 100)
        
        # Create styled text
        text = Text()
        text.append(f"{time_str}  [ ", style="bold")
        
        # Filled blocks with gradient based on position in bar (not filled count)
        for i in range(filled):
            # Calculate position in gradient based on block's position in the full bar
            # This ensures gradient flows left-to-right across the entire bar
            gradient_pos = i / (bar_width - 1) if bar_width > 1 else 0
            color = self._get_gradient_color(gradient_pos, gradient_colors)
            text.append("▮", style=color)
        
        # Tomato emoji (shows current position)
        if filled < bar_width:
            text.append("🍅")
            empty -= 1
        
        # Dim empty blocks
        for _ in range(empty):
            text.append("▯", style="dim")
        
        text.append(f" ] {pct_display}%", style="bold")
        
        return text
    
    def _get_gradient_color(self, pos: float, colors: list[str]) -> str:
        """Get interpolated color from gradient palette.
        
        Args:
            pos: Position in gradient (0.0 to 1.0).
            colors: List of hex color strings.
        
        Returns:
            Interpolated hex color string.
        """
        if pos <= 0:
            return colors[0]
        if pos >= 1:
            return colors[-1]
        
        # Find the two colors to interpolate between
        num_segments = len(colors) - 1
        segment = min(int(pos * num_segments), num_segments - 1)
        segment_pos = (pos * num_segments) - segment
        
        color1 = colors[segment]
        color2 = colors[segment + 1]
        
        return self._blend_colors(color1, color2, segment_pos)
    
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
        progress_label = self.query_one("#progress-bar", Label)
        status_label = self.query_one("#status-label", Label)

        # Update the progress line (time + bar + percentage)
        progress_label.update(self._format_progress_line())

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

    def _start_timer(self) -> None:
        """Start the timer countdown."""
        self._is_running = True
        self._update_display()
        self._schedule_tick()

    def _schedule_tick(self) -> None:
        """Schedule the next tick in 1 second."""
        if self._is_running and not self._is_finished:
            self._timer_handle = self.set_timer(1.0, self._tick_and_schedule)

    def _tick_and_schedule(self) -> None:
        """Tick and schedule next tick."""
        self._tick()
        if self._is_running and not self._is_finished:
            self._schedule_tick()

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
        self.notify("Session complete!", timeout=2)
        self._show_session_complete()

    def _show_session_complete(self) -> None:
        """Show the session complete modal."""
        completed_minutes = self.initial_minutes
        default_content = f"Completed {completed_minutes}m timer session"

        def on_dismiss(result: str | None) -> None:
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

        class ConfirmQuitModal(ModalScreen):  # type: ignore[type-arg]
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

            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "yes-btn":
                    self.action_confirm()
                elif event.button.id == "no-btn":
                    self.action_cancel()

        def on_dismiss(confirmed: bool) -> None:
            if confirmed:
                self.notify("Session not logged", timeout=1.5)
                self.exit()

        self.push_screen(ConfirmQuitModal(), on_dismiss)  # type: ignore[arg-type]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for time adjustment."""
        if event.button.id == "btn-plus-1":
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
            self.notify(f"Added {minutes} minute{'s' if minutes > 1 else ''}", timeout=1)
        else:
            self.notify(f"Subtracted {abs(minutes)} minute{'s' if abs(minutes) > 1 else ''}", timeout=1)
        
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
            self._show_quit_confirmation()

    def action_show_help(self) -> None:
        """Show contextual help overlay."""
        self.push_screen(
            HelpOverlay(
                title="⏱️ Timer",
                bindings=[
                    ("space", "toggle_pause", "Pause/Resume timer"),
                    ("+", "add_5_min", "Add 5 minutes"),
                    ("-", "subtract_5_min", "Subtract 5 minutes"),
                    ("enter", "finish", "Finish session early"),
                ],
                tips=[
                    "Default session: 25 minutes (Pomodoro technique)",
                    "Completed sessions auto-log to your journal",
                    "Green buttons (+) add time, red buttons (-) subtract time",
                    "Progress: mm:ss [ ▮▮🍅▯▯ ] percentage",
                ],
            )
        )
