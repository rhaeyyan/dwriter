"""Custom Omnibox widget for dwriter.

This module provides a specialized Input widget with 'ghost text' support
for AI-powered autocomplete suggestions and selective Tab-acceptance.
"""

from __future__ import annotations

import re
from typing import Any

from rich.segment import Segment
from rich.style import Style
from textual.reactive import reactive
from textual.widgets import Input


class Omnibox(Input):
    """A specialized input for rapid entry with ghost-text suggestions.

    Attributes:
        ghost_text: Dim gray suggestions to append to the input.
        pending_tokens: List of suggested tokens (&project, #tag) yet to be accepted.
    """

    DEFAULT_CSS = """
    Omnibox {
        width: 1fr;
        margin-right: 1;
        background: transparent;
        border: none;
    }
    """

    ghost_text = reactive("")
    pending_tokens: list[str] = []

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Omnibox widget.

        Args:
            **kwargs: Arguments passed to the Textual Input widget.
        """
        super().__init__(**kwargs)
        self.pending_tokens = []

    def watch_ghost_text(self, value: str) -> None:
        """Update pending tokens when ghost text changes."""
        if value:
            # Extract &project and #tags
            self.pending_tokens = re.findall(r"([&#][\w:-]+)", value)
        else:
            self.pending_tokens = []

    def _on_key(self, event: Any) -> None:
        """Handle key events for Tab-acceptance and ghost text clearing."""
        if event.key == "tab" and self.pending_tokens:
            # Accept the first pending token
            token = self.pending_tokens.pop(0)

            # Append to current value with a space if needed
            current = self.value.rstrip()
            if current and not current.endswith((" ", "#", "&")):
                self.value = f"{current} {token} "
            else:
                self.value = f"{current}{token} "

            # Update ghost text to show remaining tokens
            self.ghost_text = " ".join(self.pending_tokens)

            # Prevent default Tab behavior (switching focus)
            event.prevent_default()
            event.stop()
        elif event.key not in ("shift+tab", "ctrl+a", "ctrl+c", "enter"):
            # Clear ghost text on any other typing (except functional keys)
            if self.ghost_text:
                self.ghost_text = ""
                self.pending_tokens = []

    def render_line(self, y: int) -> list[Segment]:
        """Override to render dim ghost text at the end of the input buffer."""
        segments = super().render_line(y)

        # Only render ghost text on the line where the cursor/text is (y=0 for Input)
        if y == 0 and self.ghost_text and self.value:
            # Add a space before ghost text if the value doesn't end with one
            prefix = " " if not self.value.endswith(" ") else ""
            segments.append(Segment(f"{prefix}{self.ghost_text}", Style(color="#626262", italic=True)))

        return segments
