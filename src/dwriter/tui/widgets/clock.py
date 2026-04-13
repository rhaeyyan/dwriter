"""Custom clock widget for dwriter TUI.

This module provides a configurable clock widget that supports
both 24-hour and 12-hour time formats.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.widgets import Static


class Clock(Static):
    """A custom clock widget that respects 24hr/12hr user preference.

    This widget updates every second and displays the current time
    in either 24-hour or 12-hour format based on configuration.

    Example:
        clock = Clock(use_24hr=True)
    """

    DEFAULT_CSS = """
    Clock {
        dock: top;
        height: 1;
        text-align: right;
        padding: 0 2;
        color: $foreground 60%;
    }
    """

    def __init__(self, use_24hr: bool = True, **kwargs: Any) -> None:
        """Initialize the clock widget.

        Args:
            use_24hr: Whether to use 24-hour format (vs 12-hour with AM/PM).
            **kwargs: Additional arguments passed to Static.
        """
        super().__init__(**kwargs)
        self._use_24hr = use_24hr

    def on_mount(self) -> None:
        """Start the clock update timer."""
        self._update_time()
        self.set_interval(1, self._update_time)

    def _update_time(self) -> None:
        """Update the clock display with current time."""
        if self._use_24hr:
            time_str = datetime.now().strftime("%H:%M")
        else:
            time_str = datetime.now().strftime("%I:%M %p")
        self.update(time_str)

    def set_format(self, use_24hr: bool) -> None:
        """Update the clock format.

        Args:
            use_24hr: Whether to use 24-hour format.
        """
        self._use_24hr = use_24hr
        self._update_time()
