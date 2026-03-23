"""UI utilities for consistent output formatting."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Static

from .tui.colors import PROJECT, TAG, get_icon

if TYPE_CHECKING:
    from rich.console import Console

    from .config import Config
    from .database import Entry


def format_entry_datetime(entry: "Entry", config: "Optional[Config]" = None) -> tuple[str, Optional[str]]:
    """Format an entry's date and time for display.

    Returns (date_str, time_str). time_str is None for midnight entries.
    """
    dt = entry.created_at

    date_fmt_setting = (config.display.date_format if config else "YYYY-MM-DD")
    if date_fmt_setting == "MM/DD/YYYY":
        date_str = dt.strftime("%m/%d/%Y")
    elif date_fmt_setting == "DD/MM/YYYY":
        date_str = dt.strftime("%d/%m/%Y")
    else:
        date_str = dt.strftime("%Y-%m-%d")

    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return date_str, None

    use_24hr = config.display.clock_24hr if config else False
    time_str = dt.strftime("%H:%M") if use_24hr else dt.strftime("%I:%M %p")
    return date_str, time_str


def display_entry(console: "Console", entry: "Entry", config: "Config") -> None:
    """Display a single journal entry to the console."""
    date_str, time_str = format_entry_datetime(entry)

    if time_str is None:
        prefix = f"[{PROJECT}][{entry.id}][/{PROJECT}] " if config.display.show_id else ""
        console.print(f"{prefix}{date_str}: {entry.content}")
    else:
        prefix = f"[{PROJECT}][{entry.id}][/{PROJECT}] {date_str}" if config.display.show_id else date_str
        console.print(f"{prefix} | [#23c76b]{time_str}[/#23c76b]: {entry.content}")

    if entry.tag_names:
        tags_str = " ".join(f"[{TAG}]#[/]{t}" for t in entry.tag_names)
        console.print(f"    [{TAG}]Tags:[/{TAG}] {tags_str}")

    if entry.project:
        console.print(f"    [{PROJECT}]Project:[/{PROJECT}] &{entry.project}")


class HelpOverlay(ModalScreen[None]):
    """Contextual help overlay showing keybindings and tips."""

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
        """Initialize the help overlay."""
        super().__init__()
        self.title = title
        self.bindings = bindings or []
        self.tips = tips or []
        self.commands = commands or []

    def compose(self) -> ComposeResult:
        """Compose the help overlay layout."""
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
        """Focus the overlay on mount."""
        self.focus()

    def on_key(self, event: Any) -> None:
        """Close overlay on escape, enter, or question mark."""
        if event.key in ("escape", "enter", "question_mark"):
            self.dismiss()

    def on_click(self) -> None:
        """Close overlay on click."""
        self.dismiss()


__all__ = ["display_entry", "HelpOverlay"]
