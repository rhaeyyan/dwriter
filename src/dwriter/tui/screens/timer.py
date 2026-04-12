"""Timer screen for dwriter TUI.

This module provides a timer-style timer for focused work sessions.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext
    from ..app import DWriterApp

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch

from ..colors import PROJECT, TAG, get_icon, render_block_bar_rich
from ..messages import EntryAdded, TimerStateChanged
from ..parsers import parse_quick_add


class SessionCompleteModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for logging a completed session."""

    app: DWriterApp

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

            # Show tags and project if provided
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
        margin: 0;
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
            return "#00e5ff"  # Cyan
        elif position < 0.5:
            return "#ccff00"  # Neon green-yellow
        elif position < 0.75:
            return "#ffea00"  # Yellow
        elif position < 0.85:
            return "#ff7b00"  # Orange
        else:
            return "#ff003c"  # Red

    def _render_bar(self) -> None:
        """Render the progress bar with pip-style characters."""
        if self.total_seconds <= 0:
            self.update("No time set")
            return

        progress = 1.0 - (self.remaining_seconds / self.total_seconds)
        percentage = int(progress * 100)

        bar_width = 30
        filled = int(progress * bar_width)
        empty = bar_width - filled

        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"

        color = self._get_gradient_color(progress)
        use_emojis = self.app.ctx.config.display.use_emojis
        fill_char = "▮" if use_emojis else "#"
        empty_char = "▯" if use_emojis else "."
        bar = f"[bold #00E5FF]{time_str}[/bold #00E5FF]  [{color}]{fill_char * filled}[/][#313244]{empty_char * empty}[/]  [bold #00E5FF]{percentage}%[/bold #00E5FF]"
        self.update(bar)


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
        margin-top: 4;
    }

    #timer-control-button {
        min-width: 15;
        height: auto;
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

    #timer-progress-container {
        height: auto;
        align: center middle;
        padding: 0;
        margin-bottom: 1; /* Space below progress bar */
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
        color: $background;
    }

    .running-button {
        background: $success;
        color: $background;
    }

    .finished-button {
        background: $primary;
        color: $background;
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
        Binding("c", "clear_timer", "Reset"),
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
        use_emojis = self.ctx.config.display.use_emojis
        with Container(id="timer-main-container"):
            # Header with title (left) and break toggle (right)
            with Horizontal(id="timer-header"):
                yield Label(f"{get_icon('timer', use_emojis)} Timer", id="timer-title")
                with Horizontal(id="timer-break-mode-container"):
                    yield Label("Break:", id="timer-break-label")
                    yield Switch(
                        value=self.is_break_mode,
                        id="timer-break-switch",
                    )

            # Control button (Start/Pause)
            with Horizontal(id="timer-controls"):
                yield Button(
                    "[ START / PAUSE ]",
                    id="timer-control-button",
                    variant="warning",
                )

            # Progress bar
            with Container(id="timer-progress-container"):
                yield TimerProgressBar(
                    total_seconds=self.total_seconds,
                    id="timer-progress-bar",
                )

            # Session metadata (tags/project) - centered below progress bar
            yield Label("", id="timer-session-meta", classes="timer-session-meta")

            # Adjust buttons with centered label
            with Vertical(id="timer-adjust-section"):
                yield Label("Add/Remove Minutes:", classes="add-time-label")
                with Horizontal(id="timer-adjust-buttons"):
                    yield Button("\\[ +5 MIN ]", id="btn-plus-5", variant="success")
                    yield Button("\\[ +1 MIN ]", id="btn-plus-1", variant="success")
                    yield Button("\\[ -1 MIN ]", id="btn-minus-1", variant="error")
                    yield Button("\\[ -5 MIN ]", id="btn-minus-5", variant="error")

            # Reset button - loads fresh durations from config
            with Horizontal(id="timer-clear-row"):
                yield Button(
                    "\\[ RESET ]",
                    id="timer-clear-button",
                    variant="default",
                )

        yield Label(
            f"Space: Start/Pause  {get_icon('bullet', use_emojis)}  C: Reset  {get_icon('bullet', use_emojis)}  B: Break  {get_icon('bullet', use_emojis)}  Enter: Finish  {get_icon('bullet', use_emojis)}  ?: Help",
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
        """Refresh timer display when the screen becomes visible.
        
        Also reloads work/break durations from the live config so that
        changes saved in the Configure tab take effect immediately.
        """
        # Reload durations from live config (picks up changes from Configure tab)
        self.work_duration = self.ctx.config.timer.work_duration
        self.break_duration = self.ctx.config.timer.break_duration
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

            # Update title with mode — highlight only when running
            use_emojis = self.ctx.config.display.use_emojis
            mode_str = f"{get_icon('glance', use_emojis)} Break" if self.is_break_mode else f"{get_icon('streak', use_emojis)} Focus"
            timer_icon = get_icon("timer", use_emojis)
            if self.is_running:
                timer_title.update(f"[bold $primary]{timer_icon} Timer [{mode_str}][/bold $primary]")
            else:
                timer_title.update(f"[dim]{timer_icon} Timer [{mode_str}][/dim]")

            # Update progress bar
            progress_bar.update_progress(self.remaining_seconds, self.total_seconds)

            # Update control button
            if self.is_finished:
                control_button.label = "\\[ DONE ]"
                control_button.variant = "primary"
                control_button.remove_class("paused-button")
                control_button.remove_class("running-button")
                control_button.add_class("finished-button")
            elif self.is_running:
                control_button.label = "\\[ PAUSE ]"
                control_button.variant = "success"
                control_button.remove_class("paused-button")
                control_button.remove_class("finished-button")
                control_button.add_class("running-button")
            else:
                control_button.label = "\\[ START ]"
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
                # TAG color tags like Todo Board
                tags_str = " ".join([f"[{TAG}]#{tag}[/{TAG}]" for tag in self.tags])
                parts.append(f"Session: {tags_str}")

            if display_project:
                # Theme-aware project label
                parts.append(f"[{PROJECT}]{display_project}[/{PROJECT}]")

            if parts:
                meta_label.update(" | ".join(parts))
            else:
                meta_label.update("")
            
            # Always keep visible to prevent layout jumping
            meta_label.display = True
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
        elif event.button.id == "timer-clear-button":
            self.action_clear_timer()

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

    def action_clear_timer(self) -> None:
        """Reset the timer to default durations from config."""
        if self.is_finished:
            return

        # Stop the timer if running
        if self.is_running:
            self.is_running = False
            if self._timer_handle:
                self._timer_handle.stop()
            self._timer_handle = None

        # Reload durations from live config
        self.work_duration = self.ctx.config.timer.work_duration
        self.break_duration = self.ctx.config.timer.break_duration

        # Reset to the correct default depending on current mode
        default_minutes = self.break_duration if self.is_break_mode else self.work_duration
        self.initial_minutes = default_minutes
        self.remaining_seconds = default_minutes * 60
        self.total_seconds = default_minutes * 60

        # Update button to paused state
        try:
            btn = self.query_one("#timer-control-button", Button)
            btn.label = "⏸ Paused"
            btn.variant = "warning"
        except Exception:
            pass

        self._update_display()
        self.notify(f"Timer reset to {default_minutes} min", timeout=1.5)

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
            self.notify(f"Focus mode: {new_duration} minutes", timeout=1.5)

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
