"""Dashboard screen for dwriter TUI."""

from datetime import datetime, timedelta
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import LoadingIndicator, Static, TabbedContent, TabPane

from ...analytics import AnalyticsEngine
from ...cli import AppContext


class KPICard(Static):
    """A minimal KPI card."""

    DEFAULT_CSS = """
    KPICard {
        width: 1fr;
        border: heavy $secondary;
        background: transparent;
        margin: 0 1;
        padding: 1 0;
        content-align: center middle;
    }
    .kpi-title { color: $text-muted; text-align: center; }
    .kpi-value { text-style: bold; text-align: center; }
    """

    def __init__(
        self, title: str, value: str, color: str = "$primary", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.val = value
        self.color = color

    def on_mount(self) -> None:
        self.update(
            f"[{self.color}]{self.val}[/{self.color}]\n[kpi-title]{self.title}[/kpi-title]"
        )


class StreakCalendar(Static):
    """GitHub-style activity calendar rendered with Btop density."""

    DEFAULT_CSS = """
    StreakCalendar {
        border: round $primary;
        background: $panel;
        padding: 1 2;
        margin: 0 1 1 1;
        height: auto;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self.entries_by_date: dict[str, int] = {}
        self.current_streak = 0
        self.longest_streak = 0

    def on_mount(self) -> None:
        self._load_data()

    def on_resize(self, event: Any) -> None:
        if hasattr(self, "entries_by_date") and self.entries_by_date:
            self._render_calendar()

    def _load_data(self) -> None:
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

        content = ["[bold]📅 History[/bold]\n"]

        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
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
        content.append(f"[dim bold]{month_line}[/dim bold]\n")

        day_names = ["   ", "Mon", "   ", "Wed", "   ", "Fri", "   "]
        level_styles = {
            0: "[#313244]■[/]",  # dim - no activity
            1: "[#a6e3a1]■[/]",  # green - low
            2: "[#f9e2af]■[/]",  # yellow - medium
            3: "[#fab387]■[/]",  # orange - high
            4: "[#f38ba8]■[/]",  # red - very high
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

        content.append("[dim]    Less ")
        for i in range(5):
            content.append(f"{level_styles[i]} ")
        content.append("More[/dim]")

        self.update("".join(content))


class ActivitySparkline(Static):
    """Sparkline showing activity heatmap rendered with Unicode Braille."""

    DEFAULT_CSS = """
    ActivitySparkline {
        border: round $primary;
        background: $panel;
        padding: 0 2;
        margin: 0 1 0 1;
        height: auto;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self._data_loaded = False

    def on_mount(self) -> None:
        self._render_sparkline()
        self._data_loaded = True

    def on_resize(self, event: Any) -> None:
        if self._data_loaded:
            self._render_sparkline()

    def refresh_data(self) -> None:
        """Force refresh of the sparkline data."""
        self._render_sparkline()

    def _render_sparkline(self) -> None:
        today = datetime.now()
        # Fixed 30-day window for sparkline
        num_days = 30
        start_date = today - timedelta(days=num_days - 1)
        entries_by_date = self.ctx.db.get_entries_count_by_date(start_date, today)

        data = []
        for i in range(num_days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            data.append(entries_by_date.get(date_str, 0))

        # Get container width for centering
        container_width = self.size.width if self.size.width > 10 else 60
        content_width = num_days  # Each day is one character

        # Calculate padding for center alignment
        padding = max(0, (container_width - content_width) // 2)
        padding_str = " " * padding

        # Initialize content list
        content = []

        # Get top 5 trending tags
        engine = AnalyticsEngine(self.ctx.db)
        tag_velocity = engine.get_tag_velocity(days=30)
        top_tags = tag_velocity[:5]

        # Add trending tags at the top, evenly spaced
        if top_tags:
            # Calculate spacing for even distribution across container width
            tag_spacing = container_width // len(top_tags)
            tags_line = ""
            for i, (tag, count, _trend) in enumerate(top_tags):
                tag_display = f"#{tag}({count})"
                # Minimal padding - just center within allocated space
                if i == 0:
                    # First tag: center in first slot
                    tag_padding = max(0, (tag_spacing - len(tag_display)) // 2)
                    tags_line += (
                        " " * tag_padding
                        + f"[yellow]#{tag}[/yellow][#89dceb]({count})[/#89dceb]"
                    )
                else:
                    # Subsequent tags: fixed spacing from previous
                    spacing = max(1, tag_spacing - len(tag_display))
                    tags_line += (
                        " " * spacing
                        + f"[yellow]#{tag}[/yellow][#89dceb]({count})[/#89dceb]"
                    )
            content.append(f"{tags_line}\n\n")

        if any(data):
            spark_chars = " ⠀⡀⣀⣄⣤⣦⣶⣷⣿"
            max_val = max(data) if data else 1
            colors = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f38ba8"]

            spark_line = ""
            for val in data:
                if val == 0:
                    idx = 0
                else:
                    idx = max(1, int((val / max_val) * 8)) if max_val > 0 else 0
                color_idx = (
                    int((val / max_val) * (len(colors) - 1)) if max_val > 0 else 0
                )
                color = colors[color_idx]
                spark_line += f"[{color}]{spark_chars[idx]}[/{color}]"

            # Center the sparkline
            content.append(f"{padding_str}{spark_line}\n")

            # Center-align the stats
            low_val = min(data)
            high_val = max(data)
            total_val = sum(data)
            stats_text = (
                f"Entries: Low: {low_val}  |  High: {high_val}  |  Total: {total_val}"
            )
            stats_padding = max(0, (container_width - len(stats_text)) // 2)
            content.append(f"{' ' * stats_padding}[dim]{stats_text}[/dim]")
        else:
            no_activity_text = "[dim]No activity[/dim]"
            no_activity_padding = max(0, (container_width - len("No activity")) // 2)
            content.append(f"{' ' * no_activity_padding}{no_activity_text}")

        self.update("".join(content))


class ContextSwitchCard(Static):
    """Context switch behavioral insight."""

    DEFAULT_CSS = "ContextSwitchCard { border: round $primary; background: $panel; padding: 0 2; height: 6; }"

    def update_data(self, switches: float) -> None:
        if switches <= 2:
            level = "Low"
            level_style = "green"
        elif switches <= 4:
            level = "Med"
            level_style = "yellow"
        else:
            level = "High"
            level_style = "red"

        content = [
            f"[bold]🔄 Context Switches [{level_style}]{level}[/{level_style}][/bold]\n\n"
        ]
        content.append(f"[dim]Projects per day:[/dim] {switches:.1f}")
        self.update("".join(content))


class ContextFrictionCard(Static):
    """Combined Context Switches and Friction Ratio card."""

    DEFAULT_CSS = "ContextFrictionCard { border: round $primary; background: $panel; padding: 0 2; height: 13; }"

    def _draw_bar(self, value: float, max_val: float, width: int = 17) -> str:
        """Draws a pip bar with gradient coloring based on value: light green → yellow → orange → red."""
        if max_val <= 0:
            return f"[#313244]{'･' * width}[/]"
        filled = int((value / max_val) * width)
        if value > 0 and filled == 0:
            filled = 1
        empty = width - filled

        # Color based on the actual ratio value (not relative)
        if value <= 1.0:
            color = "#a6e3a1"  # light green - low friction
        elif value <= 2.0:
            color = "#f9e2af"  # yellow - moderate friction
        elif value <= 3.5:
            color = "#fab387"  # orange - high friction
        else:
            color = "#f38ba8"  # red - very high friction

        return f"[{color}]{'￭' * filled}[/][#313244]{'･' * empty}[/]"

    def _get_status_display(self, ratio: float) -> tuple[str, str]:
        """Get status label and color based on friction ratio.

        Args:
            ratio: Friction ratio value.

        Returns:
            Tuple of (status_label, color_code).
        """
        if ratio > 3.5:
            return "Time Hog", "#f38ba8"  # red - high ratio
        elif ratio > 2.0:
            return "Prioritized", "#f9e2af"  # yellow - mid ratio
        else:
            return "Avg Activity", "#a6e3a1"  # green - same as Fresh bar

    def update_data(self, switches: float, roi_data: list[Any]) -> None:
        # Context switches section
        if switches <= 2:
            level = "Low"
            level_style = "green"
        elif switches <= 4:
            level = "Med"
            level_style = "yellow"
        else:
            level = "High"
            level_style = "red"

        # Count active projects from roi_data
        active_projects = len(roi_data) if roi_data else 0

        content = [
            f"[bold]🔄 Context Switches [{level_style}]{level}[/{level_style}][/bold]\n\n"
        ]
        content.append(
            f"[dim]Projects/day:[/dim] {switches:.1f}    [dim]Active:[/dim] {active_projects}"
        )

        # Friction Ratio section
        content.append("\n\n[bold]⚙️ Friction Ratio[/bold]\n")
        if not roi_data:
            content.append("[dim]Not enough data yet...[/dim]")
        else:
            max_ratio = max([r[1] for r in roi_data] + [1.0])
            for proj, ratio, _e, _t in roi_data[:3]:
                safe_proj = proj[:12] if proj else "none"
                status_label, status_color = self._get_status_display(ratio)
                content.append(
                    f"[dim]{safe_proj:<12}[/dim] [bold]{ratio:>4.1f}[/bold] [{status_color}]{status_label}[/{status_color}]\n"
                )
                content.append(f"{self._draw_bar(ratio, max_ratio, 17)}\n")
        self.update("".join(content))


class TodoHealthCard(Static):
    """Combined To-do Health and Workload card."""

    DEFAULT_CSS = "TodoHealthCard { border: round $error; background: $panel; padding: 0 2; height: 13; }"

    def _draw_bar(
        self, value: int, max_val: int, width: int = 15, color: str = "white"
    ) -> str:
        """Draws the ［ ￭￭￭￭￭･････ ］ style bar."""
        if max_val <= 0:
            return f"［ [#313244]{'･' * width}[/] ］"
        filled = int((value / max_val) * width)
        if value > 0 and filled == 0:
            filled = 1
        empty = width - filled
        return f"［ [{color}]{'￭' * filled}[/][#313244]{'･' * empty}[/] ］"

    def update_data(
        self, fresh: int, stale: int, dead: int, added: int, done: int
    ) -> None:
        max_val = max((fresh, stale, dead, 1))

        # Colors for each category
        fresh_color = "#a6e3a1"  # light green
        stale_color = "#f9e2af"  # yellow
        stuck_color = "#f38ba8"  # red

        # Workload status
        diff = added - done
        if diff > 0:
            status = f"+{diff} backlog"
            status_style = "yellow"
            warning_icon = "⚠️"
        elif diff < 0:
            status = "Up to Date"
            status_style = "green"
            warning_icon = "✅"
        else:
            status = "Balanced"
            status_style = "green"
            warning_icon = "✓"

        # Completion rate
        total = added + done
        completion_rate = round((done / total * 100) if total > 0 else 0, 0)

        # Throughput (tasks completed per day average)
        throughput = round(done / 7, 1) if done > 0 else 0

        # Colors for stats
        label_color = "#8c92a6"  # gray for labels (matches To-Do Health dim)
        value_color = "#89dceb"  # teal for numbers

        content = ["[bold]📋 To-do Health[/bold]\n\n"]
        # Fresh bar with matching color number
        content.append(
            f"[dim]Fresh[/dim] {self._draw_bar(fresh, max_val, 15, fresh_color)} [{fresh_color}]{fresh}[/]\n"
        )
        # Stale bar with matching color number
        content.append(
            f"[dim]Stale[/dim] {self._draw_bar(stale, max_val, 15, stale_color)} [{stale_color}]{stale}[/]\n"
        )
        # Stuck bar with matching color number
        content.append(
            f"[dim]Stuck[/dim] {self._draw_bar(dead, max_val, 15, stuck_color)} [{stuck_color}]{dead}[/]\n"
        )
        content.append(
            f"\n[bold]⚡ Workload [{status_style}]{warning_icon} {status}[/bold]\n"
        )
        content.append(
            f" [{label_color}]Added:[/{label_color}] [{value_color}]{added}[/]      [{label_color}]Done:[/{label_color}] [{value_color}]{done}[/]\n"
        )
        content.append(
            f" [{label_color}]Completion:[/{label_color}] [{value_color}]{completion_rate:.0f}%[/]\n"
        )
        content.append(
            f" [{label_color}]Throughput:[/{label_color}] [{value_color}]{throughput}/day[/]"
        )
        self.update("".join(content))


class DashboardScreen(Container):
    """The Analytics Dashboard."""

    DEFAULT_CSS = """
    DashboardScreen { height: 1fr; background: transparent; }
    #dashboard-loading { dock: top; margin-top: 1; }
    #dashboard-tabs { height: 1fr; }
    #overview-pane, #activity-pane {
        height: 1fr;
        overflow-y: auto;
        padding: 0;
    }
    #dashboard-kpi-row { height: auto; margin-bottom: 1; }

    /* Layout grid rules */
    .insights-row { height: auto; margin: 0; padding: 0; }
    .half-card-left { width: 1fr; margin-right: 1; margin-bottom: 1; }
    .half-card-right { width: 1fr; margin-bottom: 1; }
    .full-card { width: 1fr; margin-bottom: 1; }
    .full-card-last { width: 1fr; margin-bottom: 1; }
    
    /* Card heights */
    TodoHealthCard { height: 13; }
    ContextFrictionCard { height: 13; }
    ActivitySparkline { height: auto; }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="dashboard-loading")

        with TabbedContent(initial="overview-pane", id="dashboard-tabs"):
            with TabPane("📊 Overview", id="overview-pane"):
                # 1. Top Row: BI Performance KPIs
                with Horizontal(id="dashboard-kpi-row"):
                    yield KPICard(
                        "Total Entries", "0", color="$primary", id="kpi-total"
                    )
                    yield KPICard(
                        "Current Streak", "0 days", color="$success", id="kpi-streak"
                    )
                    yield KPICard(
                        "Longest", "0 days", color="$warning", id="kpi-longest"
                    )
                    yield KPICard(
                        "Consistency", "0%", color="$info", id="kpi-consistency"
                    )

                yield StreakCalendar(self.ctx, id="calendar")

            with TabPane("📈 Trends", id="activity-pane"):
                # 30-day heatmap spanning full width
                yield ActivitySparkline(self.ctx, id="sparkline-activity")

                # Two cards side by side: Todo Health and Context/Friction
                with Horizontal(classes="insights-row"):
                    yield TodoHealthCard(classes="half-card-left", id="todo-health")
                    yield ContextFrictionCard(
                        classes="half-card-right", id="context-friction"
                    )

    def on_mount(self) -> None:
        self._load_dashboard_data()

    def on_show(self) -> None:
        """Refresh data when the dashboard screen becomes visible."""
        self._load_dashboard_data()

    @work(exclusive=True, thread=True)
    def _load_dashboard_data(self) -> None:
        """Fetch all data in the background to prevent UI lag."""
        self.total_entries = self.ctx.db.get_all_entries_count()

        # Calculate streaks
        entries = self.ctx.db.get_all_entries()
        dates = sorted({e.created_at.date() for e in entries})

        self.current_streak = 0
        self.longest_streak = 0

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

        # Consistency (last 30 days)
        today = datetime.now().date()
        start_date = today - timedelta(days=29)
        active_days = sum(1 for d in dates if d >= start_date)
        self.consistency = int((active_days / 30) * 100)

        # Behavioral Analytics
        engine = AnalyticsEngine(self.ctx.db)
        fresh, stale, dead = engine.get_task_staleness()
        added, done = engine.get_say_do_ratio(days=7)
        switches = engine.get_context_switches(days=7)
        roi_data = engine.get_project_roi(days=30)

        # Weekly data
        start_date_week = today - timedelta(days=6)
        entries_by_date = self.ctx.db.get_entries_count_by_date(start_date_week, today)
        weekly_data = [
            entries_by_date.get(
                (start_date_week + timedelta(days=i)).strftime("%Y-%m-%d"), 0
            )
            for i in range(7)
        ]

        if hasattr(self.app, "call_from_thread"):
            self.app.call_from_thread(self._update_kpis)
            self.app.call_from_thread(
                self._update_ui,
                fresh,
                stale,
                dead,
                added,
                done,
                switches,
                roi_data,
                weekly_data,
            )

    def _update_kpis(self) -> None:
        try:
            kpi_total = self.query_one("#kpi-total", KPICard)
            kpi_total.update(
                f"[{kpi_total.color}]{self.total_entries}[/{kpi_total.color}]\n[kpi-title]Total Entries[/kpi-title]"
            )

            kpi_streak = self.query_one("#kpi-streak", KPICard)
            kpi_streak.update(
                f"[{kpi_streak.color}]{self.current_streak} days[/{kpi_streak.color}]\n[kpi-title]Current Streak[/kpi-title]"
            )

            kpi_longest = self.query_one("#kpi-longest", KPICard)
            kpi_longest.update(
                f"[{kpi_longest.color}]{self.longest_streak} days[/{kpi_longest.color}]\n[kpi-title]Longest[/kpi-title]"
            )

            kpi_consistency = self.query_one("#kpi-consistency", KPICard)
            kpi_consistency.update(
                f"[{kpi_consistency.color}]{self.consistency}%[/{kpi_consistency.color}]\n[kpi-title]Consistency[/kpi-title]"
            )
        except Exception as e:
            import sys

            print(f"KPI update error: {e}", file=sys.stderr)

    def _update_ui(
        self, fresh, stale, dead, added, done, switches, roi_data, weekly_data
    ) -> None:
        """Push fetched data into the charts."""
        try:
            self.query_one("#todo-health", TodoHealthCard).update_data(
                fresh, stale, dead, added, done
            )
            self.query_one("#context-friction", ContextFrictionCard).update_data(
                switches, roi_data
            )
            self.query_one("#sparkline-activity", ActivitySparkline).refresh_data()

            # Hide the loading spinner
            loading = self.query_one("#dashboard-loading")
            loading.display = False
        except Exception as e:
            import sys

            print(f"UI update error: {e}", file=sys.stderr)
