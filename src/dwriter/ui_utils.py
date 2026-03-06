"""UI utilities for consistent output formatting."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Static

if TYPE_CHECKING:
    from rich.console import Console

    from .config import Config
    from .database import Entry


def _is_past_date(entry_date: datetime) -> bool:
    """Check if an entry date is before today.

    Args:
        entry_date: The datetime to check.

    Returns:
        True if the date is before today, False otherwise.
    """
    today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    entry_date_only = entry_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return entry_date_only < today


def format_entry_datetime(entry: "Entry") -> tuple[str, Optional[str]]:
    """Format an entry's date and time for display.

    For past dates (before today), returns only the date without time.
    For today's entries, returns both date and time.

    Args:
        entry: The Entry object to format.

    Returns:
        A tuple of (date_str, time_str). time_str is None for past dates.
    """
    date_str = entry.created_at.strftime("%Y-%m-%d")

    if _is_past_date(entry.created_at):
        return date_str, None

    time_str = entry.created_at.strftime("%I:%M %p")
    return date_str, time_str


def display_entry(console: "Console", entry: "Entry", config: "Config") -> None:
    """Display a journal entry to the console.

    Formats and prints a single journal entry with consistent styling,
    including ID (if enabled), date/time, content, tags, and project.
    For past dates (before today), the time component is hidden.

    Args:
        console: The Rich console instance for output.
        entry: The Entry object to display.
        config: The configuration object for display preferences.

    Returns:
        None
    """
    date_str, time_str = format_entry_datetime(entry)

    # Only show time for today's entries
    if time_str is None:
        # Past date - no time shown
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
        tags_str = " ".join(f"[#ffae00]#[/]{t}" for t in entry.tag_names)
        console.print(f"    [#ffae00]Tags:[/#ffae00] {tags_str}")

    if entry.project:
        console.print(f"    [purple]Project:[/purple] {entry.project}")


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
        border: thick $primary;
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
        color: $text;
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
        with Container():
            yield Static(f"❓ {self.title}", classes="help-title")
            yield Static("", classes="help-section")

            with ScrollableContainer(id="help-bindings"):
                for key, _action, desc in self.bindings:
                    yield Static(f"[bold cyan]{key:12}[/]  {desc}", classes="help-desc")

            if self.commands:
                yield Static("\n📝 Commands:", classes="help-section")
                for cmd, desc in self.commands:
                    yield Static(f"  [bold yellow]{cmd}[/]", classes="help-desc")
                    yield Static(f"    {desc}", classes="help-tip")

            if self.tips:
                yield Static("\n💡 Tips:", classes="help-section")
                for tip in self.tips:
                    yield Static(f"  • {tip}", classes="help-tip")

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
