"""UI utilities for consistent output formatting."""

from typing import TYPE_CHECKING, Any, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Markdown, Static

if TYPE_CHECKING:
    from rich.console import Console

    from .config import Config
    from .database import Entry


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
    date_str = entry.created_at.strftime("%Y-%m-%d")
    time_str = entry.created_at.strftime("%I:%M %p")

    if config.display.show_id:
        id_display = f"[magenta][{entry.id}][/magenta] {date_str}"
        console.print(f"{id_display} | [#23c76b]{time_str}[/#23c76b]: {entry.content}")
    else:
        console.print(f"{date_str} | [#23c76b]{time_str}[/#23c76b]: {entry.content}")

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
    ) -> None:
        """Initialize the help overlay.

        Args:
            title: Title displayed at the top of the overlay.
            bindings: List of (key, action, description) tuples.
            tips: Optional list of contextual tips.
        """
        super().__init__()
        self.title = title
        self.bindings = bindings or []
        self.tips = tips or []

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(f"❓ {self.title}", classes="help-title")
            yield Static("", classes="help-section")

            with ScrollableContainer(id="help-bindings"):
                for key, action, desc in self.bindings:
                    yield Static(f"[bold cyan]{key:12}[/]  {desc}", classes="help-desc")

            if self.tips:
                yield Static("\n💡 Tips:", classes="help-section")
                for tip in self.tips:
                    yield Static(f"  • {tip}", classes="help-tip")

            yield Static("\nPress [bold]Esc[/] or [bold]Enter[/] to close", classes="help-close")

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
