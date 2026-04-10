"""Insight widgets for dwriter Strategic Command Center.

This module contains deterministic visual components that display productivity
metrics derived from the Analytics Engine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual.widgets import Static

from ...analytics import AnalyticsEngine


class InsightCard(Static):
    """Base class for all insight cards in the Command Center."""

    DEFAULT_CSS = """
    InsightCard {
        border: solid $secondary;
        border-title-color: $primary;
        background: $panel;
        padding: 0 1;
        margin: 0;
        height: auto;
    }
    """


class EnergyRadar(InsightCard):
    """Visualizes average energy level per life domain."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the EnergyRadar widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'🔋' if use_emojis else '[E]'} Energy Radar"
        self.update_data()

    def update_data(self) -> None:
        """Fetches energy distribution data and updates the widget content."""
        engine = AnalyticsEngine(self.ctx.db)
        distribution = engine.get_domain_energy_distribution()

        if not distribution:
            self.update("[dim]No energy data yet.[/]")
            return

        lines = []
        for domain, avg in distribution.items():
            # Use progress-bar style
            pct = int(avg * 10)
            bar_width = 10
            filled = int(pct * bar_width / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            lines.append(f"{domain:<10} {bar} {avg:.1f}")

        self.update("\n".join(lines))


class MomentumGauge(InsightCard):
    """Visualizes say-do ratio and velocity trends."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the MomentumGauge widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'⚡' if use_emojis else '[M]'} Momentum Gauge"
        self.update_data()

    def update_data(self) -> None:
        """Calculates momentum metrics and updates the widget content."""
        engine = AnalyticsEngine(self.ctx.db)
        added, done = engine.get_say_do_ratio(days=7)
        _, delta = engine.get_velocity_delta()

        say_do = (done / max(added, 1)) * 100
        bar_width = 10
        filled = int(say_do * bar_width / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        trend_icon = "↑" if delta >= 0 else "↓"
        trend_color = "success" if delta >= 0 else "error"

        content = [
            f"Say-Do   {bar} {say_do:.0f}%",
            f"Velocity [{trend_color}]{trend_icon}{abs(delta)}%[/] vs last week",
        ]
        self.update("\n".join(content))


class GoldenHourWidget(InsightCard):
    """Displays peak productivity windows."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the GoldenHour widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'🕒' if use_emojis else '[T]'} Golden Hour"
        self.update_data()

    def update_data(self) -> None:
        """Retrieves the golden hour and updates the widget content."""
        engine = AnalyticsEngine(self.ctx.db)
        peak = engine.get_golden_hour()

        content = [
            f"Peak: [bold $accent]{peak}[/]",
            "[dim]Trend: ↗ High Efficiency[/]",
        ]
        self.update("\n".join(content))


class StaleGraveyard(InsightCard):
    """Surfaces old pending tasks for quick action."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the StaleGraveyard widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'⚠️' if use_emojis else '[!]'} Stale Graveyard"
        self.update_data()

    def update_data(self) -> None:
        """Fetches the oldest pending tasks and updates the widget content."""
        from datetime import datetime

        stale_todos = self.ctx.db.get_stale_todos(limit=3)

        if not stale_todos:
            self.update("[dim]No stale tasks. Clean slate![/]")
            return

        lines = []
        now = datetime.now()
        for t in stale_todos:
            days_old = (now - t.created_at).days
            proj = f"&{t.project}" if t.project else ""
            content = t.content[:20] + "..." if len(t.content) > 20 else t.content
            lines.append(f"{proj:<8} {content} [dim]({days_old}d)[/]")

        self.update("\n".join(lines))


class TopFocusWidget(InsightCard):
    """Displays top tags and project focus."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the TopFocus widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'🏷️' if use_emojis else '[#]'} Top Focus"
        self.update_data()

    def update_data(self) -> None:
        """Calculates tag velocity and updates the widget content."""
        engine = AnalyticsEngine(self.ctx.db)
        tag_velocity = engine.get_tag_velocity(days=7)

        if not tag_velocity:
            self.update("[dim]No tag data yet.[/]")
            return

        lines = []
        for tag, count, trend in tag_velocity[:3]:
            lines.append(f"#{tag:<10} {count:>2} {trend}")

        self.update("\n".join(lines))


class PulseCard(InsightCard):
    """Displays the 7-day productivity archetype and a quick nudge."""

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the PulseCard widget."""
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        """Initializes the border title and triggers the first data update."""
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{'🎭' if use_emojis else '[P]'} 7-Day Pulse"
        self.update_data()

    def update_data(self) -> None:
        """Determines the weekly archetype and updates the widget content."""
        engine = AnalyticsEngine(self.ctx.db)
        archetype = engine.get_weekly_archetype()

        content = [
            f"Archetype: [bold #cba6f7]{archetype}[/]",
            "\n[dim]\"Stay focused on your 'Big Rock' this week.\"[/]",
        ]
        self.update("\n".join(content))
