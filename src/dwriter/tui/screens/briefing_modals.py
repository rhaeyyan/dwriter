"""Modals for 2nd-Brain briefings and follow-ups."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ...ai.engine import ask_second_brain_agentic
from .second_brain import AIChatMessage, ThinkingIndicator, UserChatMessage


class BriefingDisplayModal(ModalScreen[None]):
    """Modal for displaying a generated AI briefing with export options."""

    DEFAULT_CSS = """
    BriefingDisplayModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #briefing-container {
        width: 80%;
        height: 80%;
        background: $panel;
        border: solid #cba6f7;
        padding: 1 2;
    }
    #briefing-content {
        height: 1fr;
        margin-top: 1;
        overflow-y: scroll;
    }
    #briefing-footer {
        height: 3;
        align: right middle;
        margin-top: 1;
    }
    #briefing-footer Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        title: str,
        content: str,
        raw_content: str = "",
        report_kind: str = "",
        range_label: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.briefing_title = title
        self.content = content  # Rich-tagged, for display only
        self.raw_content = raw_content  # Clean Markdown, for export
        self.report_kind = report_kind  # "weekly-retro" | "burnout-check" | "catch-up"
        self.range_label = range_label  # Catch Up only

    def compose(self) -> ComposeResult:
        with Vertical(id="briefing-container"):
            yield Static(f"[bold #cba6f7]▸ {self.briefing_title}[/]", id="modal-title")
            with ScrollableContainer(id="briefing-content"):
                yield Static(self.content, markup=True)
            with Horizontal(id="briefing-footer"):
                yield Button("Copy (c)", id="btn-copy", variant="primary")
                yield Button("Save to Obsidian (o)", id="btn-obsidian")
                yield Button("Close (Esc)", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-copy":
            self.action_copy()
        elif event.button.id == "btn-obsidian":
            self.action_save_obsidian()
        elif event.button.id == "btn-close":
            self.dismiss()

    def action_copy(self) -> None:
        try:
            import re

            import pyperclip

            # Remove Rich markup for plain text copy
            clean_content = re.sub(r"\[.*?\]", "", self.content)
            pyperclip.copy(clean_content)
            self.app.notify("Report copied to clipboard!", title="Success")
        except Exception:
            self.app.notify("Could not copy report", severity="error")

    def action_save_obsidian(self) -> None:
        """Export the raw briefing content to the configured Obsidian vault."""
        from ...export.obsidian import (
            get_note_path,
            obsidian_is_configured,
            render_ai_report_note,
            write_note,
        )

        # Access app context from the TUI app
        # In dwriter, the App object carries the ctx
        if not hasattr(self.app, "ctx"):
            self.app.notify(
                "Application context not found. Cannot export.", severity="error"
            )
            return

        ctx = getattr(self.app, "ctx")
        obs_cfg = ctx.config.obsidian

        if not obsidian_is_configured(obs_cfg):
            self.app.notify(
                "Obsidian vault not configured. Set obsidian.vault_path in config.",
                severity="warning",
                title="Not Configured",
            )
            return

        now = datetime.now()
        title_map = {
            "weekly-retro": "Weekly Retro",
            "burnout-check": "Burnout Check",
            "catch-up": (
                f"Catch Up ({self.range_label})" if self.range_label else "Catch Up"
            ),
            "standup": "Standup",
        }
        title = title_map.get(self.report_kind, self.briefing_title)

        try:
            note_content = render_ai_report_note(
                title=f"{title} · {now.strftime('%B %d, %Y')}",
                report_kind=self.report_kind,
                content=self.raw_content,
                date=now,
                range_label=self.range_label or None,
            )
            note_path = get_note_path(obs_cfg, self.report_kind, now, title)
            write_note(note_path, note_content)
            self.app.notify(f"Saved to {note_path.name}", title="Saved to Obsidian")
        except (OSError, ValueError) as e:
            self.app.notify(str(e), severity="error", title="Export Failed")

    def on_key(self, event: Any) -> None:
        if event.key == "c":
            self.action_copy()
        elif event.key == "o":
            self.action_save_obsidian()
        elif event.key == "escape":
            self.dismiss()


class CatchUpModal(ModalScreen[dict | None]):
    """Form modal to gather criteria for a 'Catch Up' briefing."""

    DEFAULT_CSS = """
    CatchUpModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #catchup-form {
        width: 66;
        height: auto;
        background: $panel;
        border: solid #cba6f7;
        padding: 1 2;
    }
    .form-label {
        height: 1;
        margin-top: 1;
        color: $primary;
    }
    .field-hint {
        height: 1;
        color: $text-muted;
        text-style: dim;
    }
    #time-range-row {
        height: 3;
        align: left middle;
        margin-top: 1;
    }
    #time-range-label {
        width: 1fr;
        height: 3;
        content-align: left middle;
        color: $primary;
    }
    #btn-range-toggle {
        min-width: 16;
        border: none;
        background: $surface;
    }
    #range-display {
        height: 1;
        margin-bottom: 1;
        color: $primary;
        text-style: dim;
    }
    #custom-range {
        height: auto;
        margin-top: 1;
    }
    .date-row {
        height: 3;
        align: left middle;
    }
    .date-label {
        width: 7;
        height: 3;
        content-align: left middle;
        color: $primary;
    }
    #form-buttons {
        height: 3;
        margin-top: 1;
        align: right middle;
    }
    #form-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self._use_custom_range = False
        self._recent_projects = ctx.db.get_unique_projects()[:6]
        self._recent_tags = ctx.db.get_unique_tags()[:8]

    def compose(self) -> ComposeResult:
        proj_hint = "  ".join(
            f"&{p}" for p in self._recent_projects
        ) if self._recent_projects else "—"
        tag_hint = "  ".join(
            f"#{t}" for t in self._recent_tags
        ) if self._recent_tags else "—"

        with Vertical(id="catchup-form"):
            yield Static("[bold #cba6f7]🏃 Catch Up Briefing[/]")

            yield Static("Project  (optional)", classes="form-label")
            yield Static(proj_hint, classes="field-hint")
            yield Input(
                placeholder="type a project name, e.g. dwriter",
                id="input-project",
            )

            yield Static("Tags  (optional, comma-separated)", classes="form-label")
            yield Static(tag_hint, classes="field-hint")
            yield Input(
                placeholder="e.g. dev, bug, design",
                id="input-tags",
            )

            with Horizontal(id="time-range-row"):
                yield Static("Time Range", id="time-range-label")
                yield Button("Custom Range", id="btn-range-toggle")
            yield Static("Last 7 Days", id="range-display")

            with Vertical(id="custom-range"):
                with Horizontal(classes="date-row"):
                    yield Static("Start", classes="date-label")
                    yield Input(
                        placeholder="YYYY-MM-DD or 'last monday'",
                        id="input-start",
                    )
                with Horizontal(classes="date-row"):
                    yield Static("End", classes="date-label")
                    yield Input(
                        placeholder="YYYY-MM-DD or 'today'",
                        id="input-end",
                        value="today",
                    )

            with Horizontal(id="form-buttons"):
                yield Button("Generate", id="btn-submit", variant="primary")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self._set_range_mode(False)

    def _set_range_mode(self, use_custom: bool) -> None:
        """Updates the time range toggle state, button label, display text, and field visibility."""
        self._use_custom_range = use_custom
        btn = self.query_one("#btn-range-toggle", Button)
        display = self.query_one("#range-display", Static)
        if use_custom:
            btn.label = "Last 7 Days"
            display.update("Custom date range")
        else:
            btn.label = "Custom Range"
            display.update("Last 7 Days")
        self.query_one("#custom-range").display = use_custom

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-cancel":
            self.dismiss(None)
        elif btn_id == "btn-submit":
            criteria = self._collect_criteria()
            if criteria is not None:
                self.dismiss(criteria)
        elif btn_id == "btn-range-toggle":
            self._set_range_mode(not self._use_custom_range)

    def _collect_criteria(self) -> dict | None:
        """Reads and validates form values. Returns criteria dict or None on error."""
        from ...date_utils import parse_natural_date

        project = (
            self.query_one("#input-project", Input).value.strip().lstrip("&") or None
        )
        tags_raw = self.query_one("#input-tags", Input).value.strip()
        tags = (
            [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()] or None
        )

        try:
            if self._use_custom_range:
                start_str = self.query_one("#input-start", Input).value.strip()
                end_str = (
                    self.query_one("#input-end", Input).value.strip() or "today"
                )
                start_date = parse_natural_date(start_str)
                end_date = parse_natural_date(end_str)
                range_label = f"{start_str} → {end_str}"
            else:
                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now()
                range_label = "Last 7 Days"
        except ValueError as e:
            self.app.notify(f"Invalid date: {e}", severity="error")
            return None

        criteria_parts = []
        if project:
            criteria_parts.append(f"Project: &{project}")
        if tags:
            criteria_parts.append(f"Tags: {', '.join('#' + t for t in tags)}")
        criteria_parts.append(f"Range: {range_label}")

        return {
            "project": project,
            "tags": tags,
            "start_date": start_date,
            "end_date": end_date,
            "range_label": range_label,
            "criteria_str": " | ".join(criteria_parts),
        }


class FollowUpModal(ModalScreen[None]):
    """Modal for freeform AI chat (Follow-up)."""
    DEFAULT_CSS = """
    FollowUpModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #chat-container {
        width: 80%;
        height: 80%;
        background: $panel;
        border: solid $primary;
        padding: 0;
    }
    #chat-log {
        height: 1fr;
        padding: 1;
        overflow-y: scroll;
    }
    #chat-input {
        border: none;
        border-top: solid $primary;
        background: $surface;
    }
    #chat-header {
        background: $primary;
        color: $background;
        height: 3;
        align: left middle;
        padding: 0 1;
    }
    #chat-title {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
        color: $background;
    }
    #btn-close-chat {
        min-width: 5;
        border: none;
        background: transparent;
        color: $background;
    }
    #btn-close-chat:hover {
        background: $error 50%;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        with Vertical(id="chat-container"):
            with Horizontal(id="chat-header"):
                yield Static("💬 Follow-up Conversation", id="chat-title")
                yield Button("✕", id="btn-close-chat")
            with Vertical(id="chat-log"):
                yield Static("[dim]Ask anything about your productivity data...[/]")
            yield ThinkingIndicator(id="thinking-indicator")
            yield Input(placeholder="Your question...", id="chat-input")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close-chat":
            self.dismiss()

    def on_key(self, event: Any) -> None:
        if event.key == "escape":
            self.dismiss()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.value.strip()
        if not user_input: return
        
        log = self.query_one("#chat-log", Vertical)
        
        log.mount(UserChatMessage(user_input))
        event.input.value = ""
        
        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        thinking.start()
        self._run_chat(user_input)

    @work(thread=True)
    def _run_chat(self, user_input: str) -> None:
        log = self.query_one("#chat-log", Vertical)
        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        
        try:
            # Simple context for follow-up
            answer = ask_second_brain_agentic(
                prompt=user_input,
                config=self.ctx.config.ai,
                context_data="Context: User is in a follow-up conversation from the Strategic Command Center.",
                app_context=self,
            )
            
            self.app.call_from_thread(thinking.stop)
            self.app.call_from_thread(log.mount, AIChatMessage(answer))
        except Exception as e:
            self.app.call_from_thread(thinking.stop)
            self.app.notify(f"Chat error: {e}", severity="error")
