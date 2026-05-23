"""MoodPicker widget for the quick-add form."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Button

MOODS: list[tuple[str, str]] = [
    ("flow", "🌊 Flow"),
    ("good", "😊 Good"),
    ("meh", "😐 Meh"),
    ("low", "😔 Low"),
]


class MoodPicker(Horizontal):
    """Keyboard-navigable mood selector.

    Selected mood is None until the user picks one.
    Clicking the active mood again deselects it.
    """

    BINDINGS = [
        Binding("left", "prev_mood", show=False),
        Binding("right", "next_mood", show=False),
    ]

    DEFAULT_CSS = """
    MoodPicker {
        height: 1;
        width: auto;
        align: left middle;
    }

    MoodPicker .mood-btn {
        border: none;
        background: transparent;
        min-width: 12;
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }

    MoodPicker .mood-btn.selected {
        color: #89dceb;
        text-style: bold;
    }
    """

    selected: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """Yield mood buttons."""
        for key, label in MOODS:
            yield Button(label, id=f"mood-{key}", classes="mood-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle mood button selection; toggle off on repeat press."""
        btn_id = event.button.id or ""
        if not btn_id.startswith("mood-"):
            return
        event.stop()
        key = btn_id.removeprefix("mood-")
        self._select(key)

    def _select(self, key: str) -> None:
        self.selected = key if self.selected != key else None
        for btn in self.query(".mood-btn"):
            btn.remove_class("selected")
        if self.selected:
            try:
                self.query_one(f"#mood-{self.selected}", Button).add_class("selected")
            except Exception:
                pass

    def action_prev_mood(self) -> None:
        """Cycle selection left."""
        keys = [k for k, _ in MOODS]
        if self.selected is None:
            self._select(keys[-1])
        else:
            idx = keys.index(self.selected)
            self._select(keys[(idx - 1) % len(keys)])

    def action_next_mood(self) -> None:
        """Cycle selection right."""
        keys = [k for k, _ in MOODS]
        if self.selected is None:
            self._select(keys[0])
        else:
            idx = keys.index(self.selected)
            self._select(keys[(idx + 1) % len(keys)])

    def reset(self) -> None:
        """Clear selection after submission."""
        self.selected = None
        for btn in self.query(".mood-btn"):
            btn.remove_class("selected")
