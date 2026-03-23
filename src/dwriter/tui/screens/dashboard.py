"""Dashboard screen for dwriter TUI."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import LoadingIndicator, Static

from ...analytics import AnalyticsEngine, InsightGenerator
from ..colors import PROJECT, TAG, get_icon


class UnifiedPulsePanel(Static):
    """Unified panel for activity heatmap and 'Two-Cents' insights."""

    DEFAULT_CSS = """
    UnifiedPulsePanel {
        border: solid $secondary;
        border-title-color: $primary;
        background: $panel;
        padding: 0 2;
        margin: 1 1 0 1;
        height: auto;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self.nudges: list[str] = []
        self.sparkline_data: list[int] = []

    def on_mount(self) -> None:
        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{get_icon('tips', use_emojis)} Two-Cents"

    def update_data(self, nudges: list[str], sparkline_data: list[int]) -> None:
        try:
            self.nudges = nudges
            self.sparkline_data = sparkline_data
            
            use_emojis = self.ctx.config.display.use_emojis
            content = []

            # 1. Render Sparkline Heatmap at the top
            if self.sparkline_data and any(self.sparkline_data):
                # Using a tiny braille dot (U+2801) for 0-activity instead of space
                # providing a subtle placeholder for the "Today" slot if empty.
                spark_chars = "⠂⡀⣀⣄⣤⣦⣶⣷⣿" if use_emojis else "·.:-=+*#%"
                max_val = max(self.sparkline_data)
                # Map colors dynamically from theme or fallback to defaults
                theme = getattr(self.app, "theme_variables", {})
                colors = [
                    theme.get("surface", "#45475a"),
                    theme.get("success", "#a6e3a1"),
                    theme.get("warning", "#f9e2af"),
                    theme.get("error", "#f38ba8"),
                ]

                # Centering calculation based on 45 characters
                container_width = self.size.width if self.size.width > 10 else 80
                padding_str = " " * max(0, (container_width - 45) // 2)

                spark_line = ""
                for val in self.sparkline_data:
                    idx = max(1, int((val / max_val) * 8)) if val > 0 else 0
                    color_idx = int((val / max_val) * (len(colors) - 1)) if val > 0 else 0
                    # For 0 activity (val == 0), use a very dim color for the placeholder dot
                    c = colors[0] if val == 0 else colors[color_idx or 1]
                    spark_line += f"[{c}]{spark_chars[idx]}[/]"
                
                content.append(f"{padding_str}{spark_line}\n")
                
                # Perfect 45-character alignment for the labels:
                # 7 (45d ago) + 1 (space) + 15 (─) + 1 (•) + 15 (─) + 1 (space) + 5 (Today) = 45
                day_count_text = "[dim]45d ago[/] ─────────────── • ────────────── [dim]Today[/]"
                content.append(f"{padding_str}{day_count_text}\n\n")

            # 2. Render Insights below
            if not nudges:
                content.append("✨ [bold #a6e3a1]Current Status:[/] [n]Your workload distribution appears consistent across active projects.[/]")
            else:
                for i, n in enumerate(nudges):
                    if n:
                        content.append(f" {n}")
                        if i < len(nudges) - 1:
                            content.append("\n\n")
            
            # Final styling: replace [n] placeholder with a readable off-white color
            # and ensure trailing [/] are present. 
            # #cdd6f4 is Catppuccin Mocha 'Text' color, which provides great contrast.
            final_markup = "".join(content).replace("[n]", "[#cdd6f4]").replace("[/n]", "[/]")
            if not final_markup:
                final_markup = "[dim]No activity data to analyze yet.[/]"
                
            self.update(final_markup)
        except Exception as e:
            import sys
            print(f"Pulse update error: {e}", file=sys.stderr)
            self.update(f"[red]Error loading insights: {e}[/]")


class StreakCalendar(Static):
    """GitHub-style activity calendar rendered with Btop density."""

    DEFAULT_CSS = """
    StreakCalendar {
        border: solid $secondary;
        border-title-color: $primary;
        background: $panel;
        padding: 1 2;
        margin: 1 1 0 1;
        height: auto;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self.entries_by_date: dict[str, int] = {}
        self.total_entries = 0
        self.current_streak = 0
        self.longest_streak = 0

    def on_mount(self) -> None:
        self._load_data()

    def on_resize(self, event: Any) -> None:
        if hasattr(self, "entries_by_date") and self.entries_by_date:
            self._render_calendar()

    def _load_data(self) -> None:
        self.total_entries = self.ctx.db.get_all_entries_count()
        entries = self.ctx.db.get_all_entries()
        dates = sorted({e.created_at.date() for e in entries})

        if dates:
            current_streak = 1
            longest_streak = 1
            for i in range(1, len(dates)):
                if (dates[i] - dates[i - 1]).days == 1:
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    current_streak = 1
            if (datetime.now().date() - dates[-1]).days > 1:
                self.current_streak = 0
            else:
                self.current_streak = current_streak
            self.longest_streak = longest_streak

        today = datetime.now().date()
        start_date = today - timedelta(days=365)
        self.entries_by_date = self.ctx.db.get_entries_count_by_date(start_date, today)
        self._render_calendar()

    def _get_level(self, count: int) -> int:
        if count == 0:
            return 0
        if count <= 2:
            return 1
        if count <= 5:
            return 2
        if count <= 8:
            return 3
        return 4

    def _render_calendar(self) -> None:
        today = datetime.now().date()
        container_width = self.size.width if self.size.width > 10 else 74
        num_weeks = max(10, (container_width - 4) // 2)

        start_date = today - timedelta(days=num_weeks * 7 - 1)
        start_date = start_date - timedelta(days=start_date.weekday())

        weeks: list[list[tuple[datetime, int] | None] | None] = []
        current_week: list[tuple[datetime, int] | None] = []

        current_date = start_date
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            count = self.entries_by_date.get(date_str, 0)
            current_week.append((current_date, count))

            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

            current_date += timedelta(days=1)

        while len(current_week) < 7:
            current_week.append(None)
            current_date += timedelta(days=1)
        if current_week:
            weeks.append(current_week)

        weeks = weeks[-num_weeks:]

        use_emojis = self.ctx.config.display.use_emojis
        self.border_title = f"{get_icon('history', use_emojis)} History"
        content = []

        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        month_line_chars = [" "] * (4 + len(weeks) * 2)
        last_month = -1

        for i, week in enumerate(weeks):
            if week and week[0] is not None:
                month = week[0][0].month
                if month != last_month:
                    month_name = months[month - 1]
                    pos = 4 + (i * 2)
                    for j, char in enumerate(month_name):
                        if pos + j < len(month_line_chars):
                            month_line_chars[pos + j] = char
                    last_month = month

        month_line = "".join(month_line_chars).rstrip()
        content.append(f"[dim bold]{month_line}[/dim bold]\n\n")

        day_names = ["   ", "Mon", "   ", "Wed", "   ", "Fri", "   "]
        theme = getattr(self.app, "theme_variables", {})
        level_styles = {
            0: f"[{theme.get('surface', '#313244')}]{'■' if use_emojis else '-'}[/]",
            1: f"[{theme.get('success', '#a6e3a1')}]{'■' if use_emojis else '#'}[/]",
            2: f"[{theme.get('warning', '#f9e2af')}]{'■' if use_emojis else '#'}[/]",
            3: f"[{theme.get('accent', '#fab387')}]{'■' if use_emojis else '#'}[/]",
            4: f"[{theme.get('error', '#f38ba8')}]{'■' if use_emojis else '#'}[/]",
        }

        for day_idx in range(7):
            line = f"[dim]{day_names[day_idx]}[/dim] "
            for week in weeks:
                if not week:
                    line += "  "
                    continue
                while len(week) <= day_idx:
                    week.append(None)
                cell = week[day_idx]
                if cell:
                    _, count = cell
                    level = self._get_level(count)
                    line += f"{level_styles[level]} "
                else:
                    line += "  "
            content.append(line + "\n")

        content.append(
            f"\n[dim]    Total: [bold]{self.total_entries}[/]  |  "
            f"Streak: [bold]{self.current_streak}d[/]  |  "
            f"Longest: [bold]{self.longest_streak}d[/][/]"
        )

        self.update("".join(content))


class DashboardScreen(Container):
    """The Analytics Dashboard."""

    DEFAULT_CSS = """
    DashboardScreen { height: 1fr; background: transparent; }
    #dashboard-loading { dock: top; margin-top: 0; }
    #dashboard-main-container {
        height: 1fr;
        overflow-y: auto;
        padding: 0;
    }

    #zone-pulse { height: auto; margin: 0; padding: 0; width: 100%; }
    #zone-narrative { height: auto; margin: 0; padding: 0; width: 100%; }

    StreakCalendar { height: auto; }
    """

    BINDINGS = [
        Binding("c", "copy_report", "Copy Report", show=True),
    ]

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="dashboard-loading")

        with ScrollableContainer(id="dashboard-main-container"):
            with Vertical(id="zone-pulse"):
                yield UnifiedPulsePanel(self.ctx, id="pulse-panel")

            with Vertical(id="zone-narrative"):
                yield StreakCalendar(self.ctx, id="calendar")

    def action_copy_report(self) -> None:
        """Generate and copy a markdown report of current KPIs."""
        engine = AnalyticsEngine(self.ctx.db)
        fresh, stale, dead = engine.get_task_staleness()
        switches = engine.get_context_switches(days=7)
        deep_count, shallow_count, deep_ratio = engine.get_deep_work_ratio(days=7)
        burnout = engine.get_rolling_burnout_score(days=7)

        report = f"# dwriter Performance Report\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        report += "## 📊 High-Level Metrics\n"
        report += f"- **To-Do Health**: {fresh} Fresh / {stale} Stale / {dead} Stuck\n"
        report += f"- **Context Switches**: {switches:.1f} per day\n"
        report += (f"- **Deep Work Ratio**: {deep_ratio:.1f}% ({deep_count} sessions vs "
                  f"{shallow_count} shallow tasks)\n")
        report += f"- **Burnout Risk Score**: {burnout:.2f}/1.00\n\n"
        report += "## 💡 Coach's Insights\n"

        insight_gen = InsightGenerator(engine)
        import re
        for n in insight_gen.generate_insights():
            clean_n = re.sub(r"\[.*?\]", "", n)
            report += f"- {clean_n}\n"

        try:
            import pyperclip
            pyperclip.copy(report)
            self.app.notify("Report copied to clipboard!", title="Export Success")
        except Exception:
            self.app.notify("Could not copy report", title="Export Error", severity="error")

    def on_mount(self) -> None:
        self._load_dashboard_data()

    def on_show(self) -> None:
        self._load_dashboard_data()

    @work(exclusive=True, thread=True)
    def _load_dashboard_data(self) -> None:
        try:
            engine = AnalyticsEngine(self.ctx.db)
            
            # 1. Fetch Insights
            insight_gen = InsightGenerator(engine)
            nudges = insight_gen.generate_insights()

            # 2. Fetch Sparkline Data (45 days)
            today = datetime.now()
            num_days = 45
            start_date = today - timedelta(days=num_days - 1)
            entries_by_date = self.ctx.db.get_entries_count_by_date(start_date, today)
            spark_data = []
            for i in range(num_days):
                date = start_date + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                spark_data.append(entries_by_date.get(date_str, 0))

            if hasattr(self.app, "call_from_thread"):
                self.app.call_from_thread(self._update_ui, nudges, spark_data)
        except Exception as e:
            import sys
            print(f"Data load error: {e}", file=sys.stderr)
            if hasattr(self.app, "call_from_thread"):
                self.app.call_from_thread(self._hide_loading)

    def _hide_loading(self) -> None:
        """Fallback to hide loading indicator on error."""
        try:
            loading = self.query_one("#dashboard-loading")
            loading.display = False
        except Exception:
            pass

    def _update_ui(self, nudges, spark_data) -> None:
        try:
            pulse_panel = self.query_one("#pulse-panel", UnifiedPulsePanel)
            if pulse_panel:
                pulse_panel.update_data(nudges, spark_data)
            
            calendar = self.query_one("#calendar", StreakCalendar)
            if calendar:
                calendar._load_data()
                
            self.query_one("#dashboard-loading").display = False
        except Exception as e:
            import sys
            print(f"UI update error: {e}", file=sys.stderr)
            self._hide_loading()
