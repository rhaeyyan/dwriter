"""Energy slider widget for the quick-add form."""

from __future__ import annotations

from textual.binding import Binding
from textual.events import Click
from textual.reactive import reactive
from textual.widgets import Static

_MIN = 1
_MAX = 10
_TRACK_WIDTH = 18


class EnergySlider(Static):
    """Horizontal 1-10 energy slider navigable by keyboard or click.

    Renders as:  ══════════════●────  7
    Left/right arrows move the handle one step.
    Clicking a position on the track jumps to that value.
    """

    BINDINGS = [
        Binding("left", "decrement", show=False),
        Binding("right", "increment", show=False),
    ]

    DEFAULT_CSS = """
    EnergySlider {
        width: 28;
        height: 1;
        background: transparent;
    }
    """

    value: reactive[int] = reactive(7)

    def render(self) -> str:
        """Render the slider track with handle and value label."""
        pos = int(((self.value - _MIN) / (_MAX - _MIN)) * (_TRACK_WIDTH - 1))
        filled = "═" * pos
        empty = "─" * (_TRACK_WIDTH - 1 - pos)
        color = (
            "#a6e3a1" if self.value >= 8
            else "#f9e2af" if self.value >= 5
            else "#f38ba8"
        )
        return (
            f"[{color}]{filled}[/][bold {color}]●[/][dim]{empty}[/]"
            f"  [{color}]{self.value}[/]"
        )

    def action_increment(self) -> None:
        """Move the handle right."""
        self.value = min(self.value + 1, _MAX)

    def action_decrement(self) -> None:
        """Move the handle left."""
        self.value = max(self.value - 1, _MIN)

    async def on_click(self, event: Click) -> None:
        """Jump to the clicked track position."""
        # x=0 maps to _MIN, x=_TRACK_WIDTH-1 maps to _MAX
        x = max(0, min(event.x, _TRACK_WIDTH - 1))
        self.value = round(_MIN + (x / (_TRACK_WIDTH - 1)) * (_MAX - _MIN))
        self.focus()
