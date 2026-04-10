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
        color: $background;
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
            def _on_catchup_result(criteria: dict | None) -> None:
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
        from ...analytics import AnalyticsEngine, InsightGenerator

        engine = AnalyticsEngine(self.ctx.db)
        lines: list[str] = []
        title = ""

        if report_type == "energy":
            title = "🔋 Energy Radar"
            distribution = engine.get_domain_energy_distribution()
            if not distribution:
                lines.append(
                    "[dim]No energy data yet. Add entries with life domain "
                    "classifications to populate this report.[/]"
                )
            else:
                lines.append("[bold]Average energy level by life domain[/]\n")
                for domain, avg in sorted(
                    distribution.items(), key=lambda x: x[1], reverse=True
                ):
                    bar_width = 14
                    filled = int((avg / 10) * bar_width)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    color = (
                        "#a6e3a1" if avg >= 7 else "#f9e2af" if avg >= 5 else "#f38ba8"
                    )
                    lines.append(
                        f"  [bold]{domain:<12}[/] [{color}]{bar}[/]"
                        f"  [bold #cba6f7]{avg:.1f}[/]"
                    )

        elif report_type == "momentum":
            title = "⚡ Momentum Report"
            added, done = engine.get_say_do_ratio(days=7)
            current_cleared, delta = engine.get_velocity_delta()
            say_do = (done / max(added, 1)) * 100
            bar_width = 14
            filled = int(say_do * bar_width / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            trend_color = "#a6e3a1" if delta >= 0 else "#f38ba8"
            trend_icon = "↑" if delta >= 0 else "↓"
            completion_color = (
                "#a6e3a1" if say_do >= 70 else "#f9e2af" if say_do >= 40 else "#f38ba8"
            )
            lines.append("[bold]Say-Do Ratio  (last 7 days)[/]\n")
            lines.append(
                f"  [{completion_color}]{bar}[/]  [bold #cba6f7]{say_do:.0f}%[/]"
            )
            lines.append(f"  {done} completed  /  {added} added\n")
            lines.append("[bold]Velocity Delta[/]\n")
            lines.append(
                f"  [{trend_color}]{trend_icon} {abs(delta)}%[/] vs. last week"
                f"  ({current_cleared} tasks cleared)"
            )

        elif report_type == "golden-hour":
            title = "🕒 Golden Hour"
            peak = engine.get_golden_hour()
            pulse = engine.get_weekly_pulse()
            lines.append("[bold]Peak Productivity Window[/]\n")
            lines.append(f"  [bold #cba6f7]{peak}[/]  ← highest activity density\n")
            if pulse:
                lines.append("[bold]Activity by Day of Week[/]\n")
                max_count = max(pulse.values()) or 1
                for day, count in pulse.items():
                    bar_width = 14
                    filled = int((count / max_count) * bar_width)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    lines.append(f"  [bold]{day:<4}[/] {bar}  [dim]{count}[/]")

        elif report_type == "stale":
            title = "⚠️ Stale Task Report"
            fresh, stale, dead = engine.get_task_staleness()
            stale_todos = self.ctx.db.get_stale_todos(limit=7)
            total = fresh + stale + dead
            lines.append("[bold]Task Age Breakdown[/]\n")
            lines.append(f"  [bold #a6e3a1]Fresh[/]  (< 3 days)    {fresh}")
            lines.append(f"  [bold #f9e2af]Stale[/]  (3–14 days)   {stale}")
            lines.append(f"  [bold #f38ba8]Dead[/]   (> 14 days)   {dead}")
            lines.append("  [dim]──────────────────────────[/]")
            lines.append(f"  Total pending: {total}\n")
            if stale_todos:
                now = datetime.now()
                lines.append("[bold]Oldest Pending Tasks[/]\n")
                for t in stale_todos:
                    days_old = (now - t.created_at).days
                    proj = (
                        f"[bold #F77F00]&{t.project}[/] " if t.project else ""
                    )
                    snippet = (
                        t.content[:32] + "…" if len(t.content) > 32 else t.content
                    )
                    age_color = (
                        "#f38ba8" if days_old > 14 else
                        "#f9e2af" if days_old > 3 else "#a6e3a1"
                    )
                    lines.append(
                        f"  {proj}{snippet}  [{age_color}]{days_old}d[/]"
                    )

        elif report_type == "focus":
            title = "🏷️ Focus Report"
            tag_velocity = engine.get_tag_velocity(days=14)
            big_rock = engine.get_big_rock(days=7)
            context_switches = engine.get_context_switches(days=7)
            lines.append("[bold]Top Tags  (last 14 days)[/]\n")
            if tag_velocity:
                for tag, count, trend in tag_velocity[:6]:
                    trend_color = (
                        "#a6e3a1" if "↑" in trend or "↗" in trend
                        else "#f38ba8" if "↓" in trend or "↘" in trend
                        else "#cdd6f4"
                    )
                    lines.append(
                        f"  [bold #66D0BC]#{tag:<14}[/]"
                        f" {count:>3}  [{trend_color}]{trend}[/]"
                    )
            else:
                lines.append("  [dim]No tag data yet.[/]")
            if big_rock:
                proj, pct = big_rock
                lines.append("\n[bold]Big Rock[/]\n")
                lines.append(
                    f"  [bold #F77F00]&{proj}[/] claimed"
                    f" [bold #cba6f7]{pct:.0f}%[/] of your bandwidth"
                )
            lines.append("\n[bold]Context Switches[/]\n")
            switch_color = (
                "#f38ba8" if context_switches > 4
                else "#f9e2af" if context_switches > 2
                else "#a6e3a1"
            )
            lines.append(
                f"  [{switch_color}]{context_switches:.1f}[/] avg projects/day"
            )

        elif report_type == "pulse":
            title = "🎭 Weekly Pulse"
            wrapup = InsightGenerator(engine).generate_weekly_wrapup()
            lines.append("[bold]7-Day Snapshot[/]\n")
            for insight in wrapup:
                lines.append(f"  {insight}")
            deep_work, shallow_work, deep_ratio = engine.get_deep_work_ratio(days=7)
            focus_color = (
                "#a6e3a1" if deep_ratio >= 30
                else "#f9e2af" if deep_ratio >= 15
                else "#f38ba8"
            )
            lines.append("\n[bold]Deep Work Ratio[/]\n")
            lines.append(
                f"  [{focus_color}]{deep_ratio:.0f}%[/] deep"
                f"  ({deep_work} sessions vs {shallow_work} shallow)"
            )

        body = "\n".join(lines)
        display_text = f"[bold #cba6f7]▸ {title}[/]\n\n{body}"
        narrative = self.query_one("#narrative-text", Static)
        self.app.call_from_thread(narrative.update, display_text)

    @work(thread=True)
    def _generate_briefing(self, briefing_type: str) -> None:
        """Executes targeted AI synthesis in a background worker."""
        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        self.app.call_from_thread(thinking.start)

        try:
            answer = generate_targeted_briefing(
                briefing_type=briefing_type,
                config=self.ctx.config.ai,
                context_data=self._context_data,
            )

            formatted = self.format_ai_response(answer)

            narrative = self.query_one("#narrative-text", Static)
            title_map = {
                "weekly_retro": "Weekly Retrospective",
                "burnout_check": "Burnout & Productivity Check",
            }
            title = title_map.get(briefing_type, "Briefing")

            display_text = f"[bold #cba6f7]▸ {title}[/]\n\n{formatted}"
            self.app.call_from_thread(narrative.update, display_text)

        except Exception as e:
            self.app.notify(f"Briefing error: {e}", severity="error")
        finally:
            self.app.call_from_thread(thinking.stop)

    @work(thread=True)
    def _generate_catchup_briefing(self, criteria: dict) -> None:
        """Fetches activity data and runs the Catch Up AI briefing in a background worker."""
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
            display_text = (
                f"[bold #cba6f7]▸ Catch Up: {criteria['range_label']}[/]\n\n{formatted}"
            )
            narrative = self.query_one("#narrative-text", Static)
            self.app.call_from_thread(narrative.update, display_text)

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
