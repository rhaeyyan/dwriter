"""UI utilities for consistent output formatting."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Static

from .tui.colors import TAG, get_icon

if TYPE_CHECKING:
    from rich.console import Console

    from .config import Config
    from .database import Entry


def format_entry_datetime(entry: "Entry", config: "Optional[Config]" = None) -> tuple[str, Optional[str]]:
    """Format an entry's date and time for display.

    If the time is exactly 00:00 (midnight), it is treated as a date-only
    entry and time_str will be None.

    Args:
        entry: The Entry object to format.
        config: Optional configuration object. If provided, uses clock_24hr
                and date_format settings. Defaults to ISO date + 12hr time.

    Returns:
        A tuple of (date_str, time_str). time_str is None for midnight entries.
    """
    dt = entry.created_at

    # Determine date format
    date_fmt_setting = (config.display.date_format if config else "YYYY-MM-DD")
    if date_fmt_setting == "MM/DD/YYYY":
        date_str = dt.strftime("%m/%d/%Y")
    elif date_fmt_setting == "DD/MM/YYYY":
        date_str = dt.strftime("%d/%m/%Y")
    else:
        date_str = dt.strftime("%Y-%m-%d")

    # Check if time is exactly midnight (00:00:00) — treat as date-only
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return date_str, None

    # Determine time format
    use_24hr = config.display.clock_24hr if config else False
    time_str = dt.strftime("%H:%M") if use_24hr else dt.strftime("%I:%M %p")
    return date_str, time_str


def display_entry(console: "Console", entry: "Entry", config: "Config") -> None:
    """Display a journal entry to the console.

    Formats and prints a single journal entry with consistent styling,
    including ID (if enabled), date/time, content, tags, and project.

    Args:
        console: The Rich console instance for output.
        entry: The Entry object to display.
        config: The configuration object for display preferences.

    Returns:
        None
    """
    date_str, time_str = format_entry_datetime(entry)

    # Only show time if provided (non-midnight)
    if time_str is None:
        if config.display.show_id:
            console.print(
                f"[magenta][{entry.id}][/magenta] {date_str}: {entry.content}"
            )
        else:
            console.print(f"{date_str}: {entry.content}")
    else:
        # Today's entry - show time
        if config.display.show_id:
            id_display = f"[magenta][{entry.id}][/magenta] {date_str}"
            console.print(
                f"{id_display} | [#23c76b]{time_str}[/#23c76b]: {entry.content}"
            )
        else:
            console.print(
                f"{date_str} | [#23c76b]{time_str}[/#23c76b]: {entry.content}"
            )

    if entry.tag_names:
        tags_str = " ".join(f"[{TAG}]#[/]{t}" for t in entry.tag_names)
        console.print(f"    [{TAG}]Tags:[/{TAG}] {tags_str}")

    if entry.project:
        console.print(f"    [purple]Project:[/purple] &{entry.project}")


class HelpOverlay(ModalScreen[None]):
    """Reusable contextual help overlay for TUI screens.

    Displays keybindings and context-specific tips in a modal overlay.
    Triggered by pressing '?' in any TUI screen.

    Attributes:
        title: The title shown at the top of the overlay.
        bindings: List of (key, action, description) tuples to display.
        tips: Optional list of contextual tips for the current screen.
    """

    DEFAULT_CSS = """
    HelpOverlay {
        background: $background 80%;
        align: center middle;
    }

    HelpOverlay > Container {
        width: 80%;
        height: 70%;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    HelpOverlay .help-title {
        text-style: bold;
        color: $primary;
        padding: 1 0;
        text-align: center;
    }

    HelpOverlay .help-section {
        padding: 1 0;
    }

    HelpOverlay .help-key {
        color: $primary;
        text-style: bold;
        width: 12;
    }

    HelpOverlay .help-desc {
        color: $foreground;
    }

    HelpOverlay .help-tip {
        color: $warning;
        padding: 1 0;
    }

    HelpOverlay .help-close {
        text-align: center;
        padding: 1 0;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        title: str = "Help",
        bindings: Optional[list[tuple[str, str, str]]] = None,
        tips: Optional[list[str]] = None,
        commands: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        """Initialize the help overlay.

        Args:
            title: Title displayed at the top of the overlay.
            bindings: List of (key, action, description) tuples.
            tips: Optional list of contextual tips.
            commands: Optional list of (command, description) tuples to display.
        """
        super().__init__()
        self.title = title
        self.bindings = bindings or []
        self.tips = tips or []
        self.commands = commands or []

    def compose(self) -> ComposeResult:
        """Compose the help overlay layout."""
        # Safety check for app.ctx.config
        use_emojis = True
        try:
            use_emojis = self.app.ctx.config.display.use_emojis
        except Exception:
            pass

        with Container():
            yield Static(f"{get_icon('question', use_emojis)} {self.title}", classes="help-title")
            yield Static("", classes="help-section")

            with ScrollableContainer(id="help-bindings"):
                for key, _action, desc in self.bindings:
                    yield Static(f"[bold cyan]{key:12}[/]  {desc}", classes="help-desc")

            if self.commands:
                yield Static(f"\n{get_icon('note', use_emojis)} Commands:", classes="help-section")
                for cmd, desc in self.commands:
                    yield Static(f"  [bold yellow]{cmd}[/]", classes="help-desc")
                    yield Static(f"    {desc}", classes="help-tip")

            if self.tips:
                yield Static(f"\n{get_icon('tips', use_emojis)} Tips:", classes="help-section")
                for tip in self.tips:
                    yield Static(f"  {get_icon('bullet', use_emojis)} {tip}", classes="help-tip")

            close_msg = "\nPress [bold]Esc[/] or [bold]Enter[/] to close"
            yield Static(close_msg, classes="help-close")

    def on_mount(self) -> None:
        """Focus the overlay for immediate keyboard capture."""
        self.focus()

    def on_key(self, event: Any) -> None:
        """Handle key events to close the overlay."""
        if event.key in ("escape", "enter", "question_mark"):
            self.dismiss()

    def on_click(self) -> None:
        """Close overlay on click outside."""
        self.dismiss()


# Re-export for convenience
__all__ = ["display_entry", "HelpOverlay"]
