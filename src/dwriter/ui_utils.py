"""UI utilities for consistent output formatting."""

from typing import TYPE_CHECKING

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
