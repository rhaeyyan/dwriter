"""2nd-Brain screen for dwriter TUI.

This module provides a Strategic Command Center with high-density insights
from the Analytics Engine and targeted AI synthesis.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from rich.markup import escape
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from ...ai.compression import compress_summary
from ...ai.engine import generate_targeted_briefing


class ThinkingIndicator(Static):
    """Unified thinking indicator with Braille spinner, text, and elapsed timer."""

    DEFAULT_CSS = """
    ThinkingIndicator {
        display: none;
        height: 1;
        margin: 0 2;
    }
    """

    CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    COLORS = ["#D53E0F", "#66D0BC", "#00E5FF", "#FCBF49"]

    def on_mount(self) -> None:
        """Initializes the spinner state and timer."""
        self._frame = 0
        self._start_time: float | None = None
        self.update(self._build_text())
        self.set_interval(0.1, self._update_spinner)

    def start(self) -> None:
        """Start the indicator and reset the timer."""
        import time

        self._start_time = time.monotonic()
        self._frame = 0
        self.update(self._build_text())
        self.display = True

    def stop(self) -> None:
        """Hide the indicator."""
        self.display = False
        self._start_time = None

    def _build_text(self) -> str:
        """Build the indicator text with spinner and elapsed time."""
        import time

        try:
            char = self.CHARS[self._frame]
            color = self.COLORS[self._frame % len(self.COLORS)]
            elapsed = 0.0
            if self._start_time is not None:
                elapsed = time.monotonic() - self._start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"  [{color}]{char}[/] [dim]thinking[/]  [dim]{mins:02d}:{secs:02d}[/]"
        except Exception:
            return "  [dim]thinking...[/]"

    def _update_spinner(self) -> None:
        """Cycles the Braille character and updates the display."""
        if self.display:
            self._frame = (self._frame + 1) % len(self.CHARS)
            self.update(self._build_text())


class ChatMessage(Vertical):
    """Base class for chat messages acting as a full-width container."""

    def __init__(self, content: str, **kwargs: Any) -> None:
        """Initializes the chat message with content."""
        super().__init__(**kwargs)
        self.content = content


class UserChatMessage(ChatMessage):
    """Widget for user chat messages aligned to the right."""

    DEFAULT_CSS = """
    UserChatMessage {
        width: 100%;
        height: auto;
        align-horizontal: right;
        margin: 1 0 0 0;
    }
    .user-label {
        width: auto;
        height: 1;
        color: $primary;
        margin: 0 2 0 0;
    }
    .user-bubble {
        width: auto;
        max-width: 80%;
        height: auto;
        padding: 0 2;
        background: $surface;
        border: none;
        border-right: solid $primary;
        margin: 0 1 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Composes the user message bubble."""
        escaped = escape(self.content)
        yield Static("you", classes="user-label")
        yield Static(escaped, classes="user-bubble")


class AIChatMessage(ChatMessage):
    """Widget for AI chat messages aligned to the left."""

    DEFAULT_CSS = """
    AIChatMessage {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    .ai-label {
        width: auto;
        height: 1;
        margin: 0 0 0 2;
    }
    .ai-bubble {
        width: auto;
        max-width: 96%;
        height: auto;
        padding: 0 2;
        background: $panel;
        border: none;
        border-left: solid #cba6f7;
        margin: 0 0 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Composes the AI message bubble with hanging indentation."""
        lines = self.content.split("\n")
        indented = "\n".join(f"  {line}" if line.strip() else "" for line in lines)
        yield Static("[bold #cba6f7]▸ 2nd-Brain[/]", classes="ai-label")
        yield Static(indented, markup=True, classes="ai-bubble")


class SecondBrainScreen(Vertical):
    """Strategic Command Center for dwriter."""

    DEFAULT_CSS = """
    SecondBrainScreen {
        height: 1fr;
        width: 1fr;
        background: $background;
        padding: 0;
    }

    #insight-triggers {
        height: 3;
        align: center middle;
        background: $surface;
        padding: 0 1;
    }

    #insight-triggers Button {
        margin: 0 1;
        min-width: 15;
        border: none;
        background: $panel;
    }

    #insight-triggers Button.active {
        background: #cba6f7;
        color: #89dceb;
        text-style: bold;
    }

    #insights-hub {
        height: 1fr;
        margin: 0 1 1 1;
        border: solid #cba6f7;
        background: $panel;
        padding: 1 2;
    }

    #insights-narrative {
        height: 1fr;
        overflow-y: scroll;
        margin-top: 1;
    }

    #insights-buttons {
        height: 3;
        align: center middle;
        margin-top: 1;
        background: $surface;
    }

    #insights-buttons Button {
        margin: 0 1;
        min-width: 16;
    }

    #ai-label {
        color: #cba6f7;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the Strategic Command Center screen."""
        super().__init__(**kwargs)
        self.ctx = ctx
        self._context_data: str = ""

    def compose(self) -> ComposeResult:
        """Composes the command center layout with trigger row and hub."""
        with Horizontal(id="insight-triggers"):
            yield Button("Energy", id="trigger-energy")
            yield Button("Momentum", id="trigger-momentum")
            yield Button("Golden Hour", id="trigger-golden-hour")
            yield Button("Stale", id="trigger-stale")
            yield Button("Focus", id="trigger-focus")
            yield Button("Pulse", id="trigger-pulse")

        with Vertical(id="insights-hub"):
            yield Static("[bold #cba6f7]▸ Insights Hub[/]", id="ai-label")
            with Vertical(id="insights-narrative"):
                yield Static(
                    "Welcome to your [bold #cba6f7]Strategic Command Center[/].\n\n"
                    "Select a report above to explore your analytics, or use the "
                    "briefing buttons below for AI-powered synthesis.",
                    id="narrative-text",
                )

            with Horizontal(id="insights-buttons"):
                yield Button("💬 Follow-up", id="btn-ask", variant="primary")
                yield Button("Weekly Retro", id="btn-retro")
                yield Button("Burnout Check", id="btn-burnout")
                yield Button("Catch Up", id="btn-catchup")

        yield ThinkingIndicator(id="thinking-indicator")

    def on_mount(self) -> None:
        """Refreshes primary context upon mounting."""
        self._refresh_context()

    def on_show(self) -> None:
        """Refreshes context when the screen is shown."""
        self._refresh_context()

    def _refresh_context(self) -> None:
        """Assembles the primary context for AI briefings."""
        long_term = ""
        try:
            summaries = self.ctx.db.get_summaries(summary_type="weekly", limit=4)
            if summaries:
                long_term = "[LONG-TERM MEMORY (WEEKLY SUMMARIES)]\n"
                for s in summaries:
                    try:
                        data = json.loads(s.content)
                        week_label = s.period_start.strftime("%b %d")
                        wins = ", ".join(data.get("biggest_wins", [])[:2])
                        mood = data.get("dominant_mood", "N/A")
                        long_term += f"- Week of {week_label}: {mood}. Wins: {wins}\n"
                    except Exception:
                        continue
        except Exception:
            pass

        three_days_ago = datetime.now() - timedelta(days=3)
        entries = self.ctx.db.get_all_entries()
        recent = [e for e in entries if e.created_at >= three_days_ago]

        short_term = "[SHORT-TERM ACTIVITY (PAST 72H)]\n"
        for e in recent[:20]:
            short_term += f"- [{e.created_at.strftime('%Y-%m-%d %H:%M')}] {e.content}\n"

        self._context_data = compress_summary(f"{long_term}\n{short_term}")

    def _set_active_trigger(self, active_id: str) -> None:
        """Updates the active state CSS class on trigger buttons."""
        for btn in self.query("#insight-triggers Button"):
            btn.remove_class("active")
        try:
            self.query_one(f"#{active_id}", Button).add_class("active")
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses for reports, briefings, and modals."""
        button_id = event.button.id
        from .briefing_modals import CatchUpModal, FollowUpModal

        if button_id and button_id.startswith("trigger-"):
            report_type = button_id.removeprefix("trigger-")
            self._set_active_trigger(button_id)
            self._generate_report(report_type)
        elif button_id == "btn-ask":
            self.app.push_screen(FollowUpModal(self.ctx))
        elif button_id == "btn-retro":
            self._generate_briefing("weekly_retro")
        elif button_id == "btn-burnout":
            self._generate_briefing("burnout_check")
        elif button_id == "btn-catchup":
            def _on_catchup_result(criteria: dict[str, Any] | None) -> None:
                if criteria is None:
                    return
                narrative = self.query_one("#narrative-text", Static)
                narrative.update(
                    f"[dim]Preparing Catch Up briefing"
                    f" ({criteria['range_label']})…[/]"
                )
                self._generate_catchup_briefing(criteria)

            self.app.push_screen(CatchUpModal(self.ctx), _on_catchup_result)

    @work(thread=True)
    def _generate_report(self, report_type: str) -> None:
        """Runs a deterministic analytics report in a background thread."""
        from ..report_builders import build_report

        title, body = build_report(report_type, self.ctx.db)
        display_text = f"[bold #cba6f7]▸ {title}[/]\n\n{body}"
        narrative = self.query_one("#narrative-text", Static)
        self.app.call_from_thread(narrative.update, display_text)

    @work(thread=True)
    def _generate_briefing(self, briefing_type: str) -> None:
        """Executes targeted AI synthesis in a background worker."""
        from .briefing_modals import BriefingDisplayModal

        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        self.app.call_from_thread(thinking.start)

        try:
            answer = generate_targeted_briefing(
                briefing_type=briefing_type,
                config=self.ctx.config.ai,
                context_data=self._context_data,
            )

            formatted = self.format_ai_response(answer)

            title_map = {
                "weekly_retro": "Weekly Retrospective",
                "burnout_check": "Burnout & Productivity Check",
            }
            title = title_map.get(briefing_type, "Briefing")

            display_text = f"[bold #cba6f7]▸ {title}[/]\n\n{formatted}"

            modal = BriefingDisplayModal(
                title=title,
                content=display_text,
                raw_content=answer,
                report_kind=briefing_type.replace("_", "-"),
            )

            # Update inline narrative as fallback/record
            narrative = self.query_one("#narrative-text", Static)
            self.app.call_from_thread(narrative.update, display_text)

            # Push the modal for full-screen viewing and export
            self.app.call_from_thread(self.app.push_screen, modal)

        except Exception as e:
            self.app.notify(f"Briefing error: {e}", severity="error")
        finally:
            self.app.call_from_thread(thinking.stop)

    @work(thread=True)
    def _generate_catchup_briefing(self, criteria: dict[str, Any]) -> None:
        """Fetches activity data and runs the Catch Up AI briefing in a background worker."""
        from .briefing_modals import BriefingDisplayModal

        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        self.app.call_from_thread(thinking.start)

        try:
            data = self.ctx.db.get_activity_report_data(
                start_date=criteria["start_date"],
                end_date=criteria["end_date"],
                project=criteria.get("project"),
                tags=criteria.get("tags"),
            )

            answer = generate_targeted_briefing(
                briefing_type="catch_up",
                config=self.ctx.config.ai,
                context_data=f"Catch up Briefing Criteria: {criteria['criteria_str']}",
                extra_data=data,
            )

            formatted = self.format_ai_response(answer)
            title = f"Catch Up: {criteria['range_label']}"
            display_text = f"[bold #cba6f7]▸ {title}[/]\n\n{formatted}"

            modal = BriefingDisplayModal(
                title=title,
                content=display_text,
                raw_content=answer,
                report_kind="catch-up",
                range_label=criteria["range_label"],
            )

            narrative = self.query_one("#narrative-text", Static)
            self.app.call_from_thread(narrative.update, display_text)
            self.app.call_from_thread(self.app.push_screen, modal)

        except Exception as e:
            self.app.notify(f"Catch Up error: {e}", severity="error")
        finally:
            self.app.call_from_thread(thinking.stop)

    @staticmethod
    def format_ai_response(text: str) -> str:
        """Transforms AI-generated Markdown into Rich-compatible markup for UI rendering."""
        text = escape(text)

        # Colorize Tags and Projects
        text = re.sub(r"(?<!\w)#([\w:-]+)", r"[bold #66D0BC]#\1[/]", text)
        text = re.sub(r"(?<!\w)&([\w:-]+)", r"[bold #F77F00]&\1[/]", text)

        # Markdown bold and headers
        text = re.sub(r"\*\*(.*?)\*\*", r"[bold #cba6f7]\1[/]", text)
        text = re.sub(r"^#+\s+(.*?)$", r"[bold #cba6f7]\1[/]", text, flags=re.MULTILINE)

        # Normalize paragraph spacing
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text
