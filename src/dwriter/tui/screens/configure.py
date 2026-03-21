"""Configure screen for dwriter TUI.

This module provides the settings interface for updating application
preferences like themes, time formats, and behavior.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Input,
    Label,
    Select,
    Switch,
)

from ...cli import AppContext
from ..colors import get_icon
from ..themes import THEME_OPTIONS


class ConfigureScreen(Container):
    """Configure screen for managing application settings."""

    DEFAULT_CSS = """
    ConfigureScreen {
        height: 1fr;
    }

    #configure-scroll {
        height: 1fr;
        padding: 1 4;
        overflow-y: scroll;
    }

    .section {
        height: auto;
        width: 1fr;
        margin-bottom: 1;
        padding: 0 1;
        border: solid $border-blurred;
        background: $panel;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: solid $primary;
        width: 1fr;
    }

    .row {
        height: 3;
        width: 100%;
        align: left middle;
    }

    .row-label {
        width: 30;
        color: $foreground;
    }

    .row-help {
        height: 1;
        color: $foreground 60%;
        padding-left: 0;
        margin-bottom: 1;
    }

    #configure-footer {
        height: auto;
        padding: 0 2;
        background: $panel;
        border-top: solid $primary;
    }

    #configure-buttons {
        align: center middle;
        height: 3;
    }

    #configure-buttons Button {
        margin: 0 1;
        min-width: 18;
    }

    #configure-path {
        height: 1;
        text-align: center;
        color: $foreground 60%;
        margin-top: 0;
    }

    Switch {
        width: auto;
    }

    Select {
        width: 1fr;
    }

    .restart-note {
        height: 1;
        text-align: center;
        color: $warning;
        margin-top: 0;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        """Compose the configure UI layout."""
        cfg = self.ctx.config
        use_emojis = cfg.display.use_emojis

        with Vertical(id="configure-scroll"):
            # ── Appearance ─────────────────────────────────────────
            with Container(classes="section"):
                yield Label(f"{get_icon('glance', use_emojis)} Appearance", classes="section-title")
                yield Label("Theme applies live. Emojis need restart.", classes="row-help")

                with Horizontal(classes="row"):
                    yield Label("Theme", classes="row-label")
                    yield Select(THEME_OPTIONS, value=cfg.display.theme, id="theme-select")

                with Horizontal(classes="row"):
                    yield Label("Use Emojis", classes="row-label")
                    yield Switch(value=cfg.display.use_emojis, id="use-emojis-switch")

            # ── Time & Date ─────────────────────────────────────────
            with Container(classes="section"):
                yield Label(f"{get_icon('clock', use_emojis)} Time & Date", classes="section-title")
                yield Label("Requires restart to update display format.", classes="row-help")

                with Horizontal(classes="row"):
                    yield Label("24-Hour Clock", classes="row-label")
                    yield Switch(value=cfg.display.clock_24hr, id="clock-24hr-switch")

                with Horizontal(classes="row"):
                    yield Label("Date Format", classes="row-label")
                    yield Select(
                        [
                            ("YYYY-MM-DD", "YYYY-MM-DD"),
                            ("MM/DD/YYYY", "MM/DD/YYYY"),
                            ("DD/MM/YYYY", "DD/MM/YYYY"),
                        ],
                        value=cfg.display.date_format,
                        id="date-format-select",
                    )

            # ── Editing & Layout ────────────────────────────────────
            with Container(classes="section"):
                yield Label(f"{get_icon('edit', use_emojis)} Editing & Layout", classes="section-title")
                yield Label("Lock mode disables date/time editing.", classes="row-help")

                with Horizontal(classes="row"):
                    yield Label("Lock Mode", classes="row-label")
                    yield Switch(value=cfg.display.lock_mode, id="lock-mode-switch")

            # ── Timer Defaults ──────────────────────────────────────
            with Container(classes="section"):
                yield Label(f"{get_icon('timer', use_emojis)} Timer Defaults", classes="section-title")
                yield Label("Defaults apply on next session or restart.", classes="row-help")

                with Horizontal(classes="row"):
                    yield Label("Focus Duration (min)", classes="row-label")
                    yield Input(value=str(cfg.timer.work_duration), id="work-duration-input")

                with Horizontal(classes="row"):
                    yield Label("Break Duration (min)", classes="row-label")
                    yield Input(value=str(cfg.timer.break_duration), id="break-duration-input")

                with Horizontal(classes="row"):
                    yield Label("Auto-start Breaks", classes="row-label")
                    yield Switch(value=cfg.timer.auto_start_breaks, id="auto-start-breaks-switch")

            # ── Entry Defaults ──────────────────────────────────────
            with Container(classes="section"):
                yield Label(f"{get_icon('tag', use_emojis)} Entry Defaults", classes="section-title")
                yield Label("Baselines for all new log entries.", classes="row-help")

                with Horizontal(classes="row"):
                    yield Label("Default Project", classes="row-label")
                    yield Input(value=cfg.defaults.project or "", id="default-project-input")

                with Horizontal(classes="row"):
                    yield Label("Default Tags", classes="row-label")
                    yield Input(
                        value=", ".join(cfg.defaults.tags),
                        placeholder="tag1, tag2",
                        id="default-tags-input",
                    )

        # ── Footer ──────────────────────────────────────────────────
        with Container(id="configure-footer"):
            with Horizontal(id="configure-buttons"):
                yield Button("\\[ SAVE CHANGES \\]", id="save-config-btn", variant="success")
                yield Button("\\[ RESET TO DEFAULTS \\]", id="reset-config-btn", variant="default")
                yield Button("\\[ CLOSE APP \\]", id="close-app-btn", variant="error")
            yield Label(
                "Some settings marked 'Requires restart' need a full app restart to take effect.",
                classes="restart-note",
            )
            yield Label(
                f"Config: {self.ctx.config_manager.get_config_path()}",
                id="configure-path",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle save and reset button presses."""
        if event.button.id == "save-config-btn":
            self._save_changes()
        elif event.button.id == "reset-config-btn":
            self._reset_defaults()
        elif event.button.id == "close-app-btn":
            self.app.exit()

    def _save_changes(self) -> None:
        """Persist widget values to configuration and update ctx.config in-memory."""
        config = self.ctx.config_manager.load()
        try:
            # Appearance
            theme_val = self.query_one("#theme-select", Select).value
            if theme_val is not Select.BLANK:
                config.display.theme = str(theme_val)

            config.display.use_emojis = bool(self.query_one("#use-emojis-switch", Switch).value)

            # Time & Date
            config.display.clock_24hr = bool(self.query_one("#clock-24hr-switch", Switch).value)

            date_val = self.query_one("#date-format-select", Select).value
            if date_val is not Select.BLANK:
                config.display.date_format = str(date_val)

            # Editing
            config.display.lock_mode = bool(self.query_one("#lock-mode-switch", Switch).value)

            # Timer
            config.timer.work_duration = int(self.query_one("#work-duration-input", Input).value)
            config.timer.break_duration = int(self.query_one("#break-duration-input", Input).value)
            config.timer.auto_start_breaks = bool(
                self.query_one("#auto-start-breaks-switch", Switch).value
            )

            # Defaults
            config.defaults.project = self.query_one("#default-project-input", Input).value or None
            tags_str = self.query_one("#default-tags-input", Input).value
            config.defaults.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            # Save to disk
            self.ctx.config_manager.save(config)

            # Update the live in-memory config so all screens pick it up dynamically
            self.ctx.config = config

            # Apply theme live immediately
            self.app.theme = config.display.theme

            self.app.notify("Configuration saved! Some changes require a restart.", severity="success", timeout=4)
        except ValueError as e:
            self.app.notify(f"Invalid input: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"Failed to save: {e}", severity="error")

    def _reset_defaults(self) -> None:
        """Reset to defaults and reload the UI widgets."""
        self.ctx.config_manager.reset()
        config = self.ctx.config_manager.load()
        self.ctx.config = config

        # Re-populate widgets
        self.query_one("#theme-select", Select).value = config.display.theme
        self.query_one("#use-emojis-switch", Switch).value = config.display.use_emojis
        self.query_one("#clock-24hr-switch", Switch).value = config.display.clock_24hr
        self.query_one("#date-format-select", Select).value = config.display.date_format
        self.query_one("#lock-mode-switch", Switch).value = config.display.lock_mode
        self.query_one("#work-duration-input", Input).value = str(config.timer.work_duration)
        self.query_one("#break-duration-input", Input).value = str(config.timer.break_duration)
        self.query_one("#auto-start-breaks-switch", Switch).value = config.timer.auto_start_breaks
        self.query_one("#default-project-input", Input).value = config.defaults.project or ""
        self.query_one("#default-tags-input", Input).value = ", ".join(config.defaults.tags)

        self.app.theme = config.display.theme
        self.app.notify("Configuration reset to defaults.", severity="warning")
