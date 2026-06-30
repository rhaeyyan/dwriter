"""UI utilities for consistent output formatting."""

import textwrap
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Static

from .tui.colors import PROJECT, TAG, get_icon, get_weekday_color

if TYPE_CHECKING:
    from rich.console import Console

    from .config import Config
    from .database import Entry


def wrap_with_hanging_indent(
    text: str,
    width: int = 80,
    initial_indent: str = "",
    subsequent_indent: str = "    ",
    break_on_hyphens: bool = True
) -> str:
    """Wraps text with a hanging indent for better readability.

    Args:
        text: The text to wrap.
        width: The maximum width of the wrapped lines.
        initial_indent: Indentation for the first line.
        subsequent_indent: Indentation for all lines after the first.
        break_on_hyphens: Whether to break words on hyphens.

    Returns:
        The wrapped text with hanging indents.
    """
    if not text:
        return ""

    wrapper = textwrap.TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=True,
        break_on_hyphens=break_on_hyphens,
        replace_whitespace=False
    )

    # Handle multiple paragraphs
    lines = text.splitlines()
    wrapped_lines = [wrapper.fill(line) if line.strip() else "" for line in lines]
    return "\n".join(wrapped_lines)


def format_entry_datetime(
    entry: "Entry",
    config: "Config | None" = None
) -> tuple[str, str | None]:
    """Format an entry's date and time for display.

    Returns (date_str, time_str). time_str is None for midnight entries.
    """
    dt = entry.created_at

    date_fmt_setting = (config.display.date_format if config else "YYYY-MM-DD")

    # Map TOML display names to strftime formats
    fmt_map = {
        "YYYY-MM-DD": "%Y-%m-%d",
        "MM/DD/YYYY": "%m/%d/%Y",
        "DD/MM/YYYY": "%d/%m/%Y",
    }

    strftime_fmt = fmt_map.get(date_fmt_setting, "%Y-%m-%d")
    date_str = dt.strftime(strftime_fmt)

    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return date_str, None

    use_24hr = config.display.clock_24hr if config else False
    time_str = dt.strftime("%H:%M") if use_24hr else dt.strftime("%I:%M %p")
    return date_str, time_str


def display_entry(console: "Console", entry: "Entry", config: "Config") -> None:
    """Display a single journal entry with a weekday-colored gutter rail.

    Layout::

          Wkdy · <date> · <time> · <domain>                      #id
        ▌ <content, wrapped under the rail>
        ▌ #tag · #tag · &project

    The weekday label and the rail share the day's color (see
    ``WEEKDAY_COLORS``), so a list of entries reads as colored day-bands down
    the gutter. ``life_domain`` is read defensively so this renderer stays
    portable to the AI-free ``main`` branch where the column does not exist.
    """
    width = console.width if console.width > 0 else 80
    date_str, time_str = format_entry_datetime(entry, config)

    weekday = entry.created_at.weekday()
    rail_color = get_weekday_color(weekday)
    weekday_abbr = entry.created_at.strftime("%a")
    rail = f"[{rail_color}]▌[/{rail_color}] "

    # --- Header line: weekday colored, everything else dim, id right-aligned ---
    plain_parts = [weekday_abbr, date_str]
    styled_parts = [
        f"[{rail_color}]{weekday_abbr}[/{rail_color}]",
        f"[dim]{date_str}[/dim]",
    ]
    if time_str:
        plain_parts.append(time_str)
        styled_parts.append(f"[dim]{time_str}[/dim]")
    domain = getattr(entry, "life_domain", None)
    if domain:
        plain_parts.append(domain)
        styled_parts.append(f"[dim]{domain}[/dim]")

    plain_header = " · ".join(plain_parts)
    styled_header = " [dim]·[/dim] ".join(styled_parts)

    if config.display.show_id:
        plain_id = f"#{entry.id}"
        pad = max(width - 2 - len(plain_header) - len(plain_id), 1)
        console.print(f"  {styled_header}{' ' * pad}[dim]{plain_id}[/dim]")
    else:
        console.print(f"  {styled_header}")

    # --- Body: each wrapped line carries the rail in the day's color ---
    content_width = max(width - 2, 20)
    wrapped_content = wrap_with_hanging_indent(
        entry.content,
        width=content_width,
        initial_indent="",
        subsequent_indent="",
    )
    for line in wrapped_content.split("\n"):
        console.print(f"{rail}{line}")

    # --- Footer: tags then project, on a single railed line ---
    footer_parts = [f"[{TAG}]#{t}[/{TAG}]" for t in entry.tag_names]
    if entry.project:
        footer_parts.append(f"[{PROJECT}]&{entry.project}[/{PROJECT}]")
    if footer_parts:
        console.print(f"{rail}{' [dim]·[/dim] '.join(footer_parts)}")


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
        bindings: list[tuple[str, str, str]] | None = None,
        tips: list[str] | None = None,
        commands: list[tuple[str, str]] | None = None,
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




def send_system_notification(title: str, message: str) -> None:
    """Send a lightweight desktop notification based on the OS."""
    import subprocess
    import sys

    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'display notification "{message}" with title "{title}"',
                ],
                check=False,
                capture_output=True,
            )
        elif sys.platform == "linux":  # Linux
            subprocess.run(
                ["notify-send", title, message], check=False, capture_output=True
            )
        elif sys.platform == "win32":  # Windows
            # Adhering to the prompt's suggested PowerShell command
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"New-BurntToastNotification -Text '{title}', '{message}'",
                ],
                check=False,
                capture_output=True,
            )
    except Exception:
        pass  # Fail silently. We never want to crash for a notification failure.


__all__ = ["display_entry", "HelpOverlay", "send_system_notification"]
