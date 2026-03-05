"""Interactive dashboard TUI using Textual.

This module provides a visual dashboard with streak calendar,
weekly charts, and logging statistics.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Label, Static


class StreakCalendar(Static):
    """GitHub-style contribution calendar showing logging streaks."""

    DEFAULT_CSS = """
    StreakCalendar {
        height: auto;
        margin: 1 2;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    StreakCalendar .title {
        text-style: bold;
        padding: 0 0 1 0;
    }

    StreakCalendar .calendar-grid {
        grid-size: 53 7;
        grid-gutter: 1;
    }

    StreakCalendar .day-cell {
        width: 1;
        height: 1;
    }

    StreakCalendar .day-empty {
        color: $surface;
    }

    StreakCalendar .day-level-0 {
        color: #161b22;
        background: #161b22;
    }

    StreakCalendar .day-level-1 {
        color: #0e4429;
        background: #0e4429;
    }

    StreakCalendar .day-level-2 {
        color: #006d32;
        background: #006d32;
    }

    StreakCalendar .day-level-3 {
        color: #26a641;
        background: #26a641;
    }

    StreakCalendar .day-level-4 {
        color: #39d353;
        background: #39d353;
    }

    StreakCalendar .month-label {
        color: $text-muted;
        padding: 1 0 0 0;
    }
    """

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.entries_by_date: Dict[str, int] = {}
        self.current_streak = 0
        self.longest_streak = 0

    def on_mount(self) -> None:
        """Load data and render calendar."""
        self._load_data()
        self._render_calendar()

    def _load_data(self) -> None:
        """Load entry data from database."""
        all_entries = self.db.get_all_entries()
        self.entries_by_date = {}
        for entry in all_entries:
            date_str = entry.created_at.strftime("%Y-%m-%d")
            self.entries_by_date[date_str] = (
                self.entries_by_date.get(date_str, 0) + 1
            )

        # Calculate streaks
        self.current_streak, self.longest_streak = self._calculate_streaks()

    def _calculate_streaks(self) -> Tuple[int, int]:
        """Calculate current and longest streaks.

        Returns:
            Tuple of (current_streak, longest_streak) in days.
        """
        if not self.entries_by_date:
            return 0, 0

        today = datetime.now().date()
        dates = sorted(
            datetime.strptime(d, "%Y-%m-%d").date()
            for d in self.entries_by_date.keys()
        )

        # Calculate current streak
        current = 0
        for i in range(14):  # Check last 14 days for current streak
            check_date = today - timedelta(days=i)
            if check_date in dates:
                current += 1
            elif i == 0:
                continue  # Today might not have entries yet
            else:
                break

        # Calculate longest streak
        longest = 1
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                streak += 1
                longest = max(longest, streak)
            else:
                streak = 1

        return current, longest

    def _get_level(self, count: int) -> int:
        """Get contribution level based on entry count.

        Args:
            count: Number of entries on a day.

        Returns:
            Level from 0-4.
        """
        if count == 0:
            return 0
        elif count == 1:
            return 1
        elif count == 2:
            return 2
        elif count <= 4:
            return 3
        else:
            return 4

    def _render_calendar(self) -> None:
        """Render the contribution calendar."""
        today = datetime.now().date()
        start_date = today - timedelta(days=364)  # 52 weeks

        # Build calendar data
        weeks = []
        current_week = []

        # Pad first week
        day_of_week = start_date.weekday()
        for _ in range(day_of_week):
            current_week.append(None)

        current_date = start_date
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            count = self.entries_by_date.get(date_str, 0)
            current_week.append((current_date, count))

            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

            current_date += timedelta(days=1)

        # Pad last week
        while len(current_week) < 7:
            current_week.append(None)
        if current_week:
            weeks.append(current_week)

        # Build display
        content = ["[bold]📅 Contribution Calendar[/bold]\n"]
        content.append(
            f"Current Streak: [green]{self.current_streak} days[/green] | "
            f"Longest Streak: [yellow]{self.longest_streak} days[/yellow]\n\n"
        )

        # Month labels
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_line = "      "
        last_month = -1
        for week in weeks:
            if week[0] is not None:
                month = week[0][0].month
                if month != last_month:
                    month_line += f"{months[month-1]} "
                    last_month = month
                else:
                    month_line += "    "
        content.append(f"[dim]{month_line}[/dim]\n")

        # Day labels
        content.append("[dim]Mon    [/dim]")

        # Render grid
        for day_idx in range(7):
            day_line = "[dim]"
            if day_idx == 0:
                day_line += "M      [/dim]"
            elif day_idx == 2:
                day_line += "W      [/dim]"
            elif day_idx == 4:
                day_line += "F      [/dim]"
            else:
                day_line += "       [/dim]"
            content.append(day_line)

        content.append("\n")

        # Render weeks as columns (transposed for display)
        for day_idx in range(7):
            line = ""
            for week in weeks:
                if day_idx < len(week) and week[day_idx] is not None:
                    _, count = week[day_idx]
                    level = self._get_level(count)
                    if level == 0:
                        line += "░"
                    else:
                        line += f"[day-level-{level}]█[/day-level-{level}]"
                else:
                    line += " "
            content.append(line + "\n")

        self.update("".join(content))


class WeeklyBarChart(Static):
    """Bar chart showing entries per week."""

    DEFAULT_CSS = """
    WeeklyBarChart {
        height: auto;
        margin: 1 2;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    WeeklyBarChart .title {
        text-style: bold;
        padding: 0 0 1 0;
    }
    """

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db

    def on_mount(self) -> None:
        """Load data and render chart."""
        self._render_chart()

    def _render_chart(self) -> None:
        """Render the weekly bar chart."""
        today = datetime.now().date()
        weeks_data = []

        # Get last 8 weeks
        for i in range(7, -1, -1):
            week_start = today - timedelta(days=i * 7)
            week_end = week_start + timedelta(days=6)
            count = 0

            all_entries = self.db.get_all_entries()
            for entry in all_entries:
                entry_date = entry.created_at.date()
                if week_start <= entry_date <= week_end:
                    count += 1

            weeks_data.append((week_start.strftime("%m/%d"), count))

        # Find max for scaling
        max_count = max((w[1] for w in weeks_data), default=1)
        if max_count == 0:
            max_count = 1

        # Build chart
        content = ["[bold]📊 Weekly Activity[/bold]\n\n"]
        bar_height = 5

        for row in range(bar_height, 0, -1):
            threshold = (row / bar_height) * max_count
            line = f"{int(threshold):>3} │"

            for _, count in weeks_data:
                if count >= threshold:
                    if count >= threshold * 0.8:
                        line += "[green]██[/green]"
                    else:
                        line += "[yellow]░░[/yellow]"
                else:
                    line += "  "
            content.append(line + "\n")

        # X-axis
        content.append("    └" + "─" * 16 + "\n")

        # Labels
        labels = "      "
        for label, _ in weeks_data[::2]:  # Show every other label
            labels += f"{label} "
        content.append(f"[dim]{labels}[/dim]\n")

        self.update("".join(content))


class StatsSummary(Static):
    """Summary statistics widget."""

    DEFAULT_CSS = """
    StatsSummary {
        height: auto;
        margin: 1 2;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    StatsSummary .stat-row {
        padding: 0 0 0 1;
    }
    """

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db

    def on_mount(self) -> None:
        """Load and display stats."""
        self._render_stats()

    def _render_stats(self) -> None:
        """Render statistics."""
        all_entries = self.db.get_all_entries()
        all_todos = self.db.get_all_todos()

        total_entries = len(all_entries)
        total_todos = len(all_todos)
        completed_todos = sum(1 for t in all_todos if t.status == "completed")

        # Get unique projects and tags
        projects = set(e.project for e in all_entries if e.project)
        tags = set()
        for e in all_entries:
            tags.update(e.tag_names)

        # First and last entry dates
        if all_entries:
            dates = [e.created_at for e in all_entries]
            first_entry = min(dates).strftime("%Y-%m-%d")
            last_entry = max(dates).strftime("%Y-%m-%d")
        else:
            first_entry = "N/A"
            last_entry = "N/A"

        content = [
            "[bold]📈 Statistics Summary[/bold]\n\n",
            f"[stat-row]📝 Total Entries: [cyan]{total_entries}[/cyan][/stat-row]\n",
            f"[stat-row]✅ Completed Tasks: [green]{completed_todos}[/green]/{total_todos}[/stat-row]\n",
            f"[stat-row]🏷️ Unique Tags: [yellow]{len(tags)}[/yellow][/stat-row]\n",
            f"[stat-row]📁 Projects: [purple]{len(projects)}[/purple][/stat-row]\n",
            f"[stat-row]📅 First Entry: [dim]{first_entry}[/dim][/stat-row]\n",
            f"[stat-row]📅 Last Entry: [dim]{last_entry}[/dim][/stat-row]\n",
        ]

        self.update("".join(content))


class TopTags(Static):
    """Widget showing most used tags."""

    DEFAULT_CSS = """
    TopTags {
        height: auto;
        margin: 1 2;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    TopTags .tag-item {
        padding: 0 0 0 1;
    }
    """

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db

    def on_mount(self) -> None:
        """Load and display top tags."""
        self._render_tags()

    def _render_tags(self) -> None:
        """Render top tags list."""
        all_entries = self.db.get_all_entries()

        # Count tag usage
        tag_counts: Dict[str, int] = {}
        for entry in all_entries:
            for tag in entry.tag_names:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        content = ["[bold]🏷️ Top Tags[/bold]\n\n"]

        if not sorted_tags:
            content.append("[dim]No tags yet[/dim]\n")
        else:
            max_count = sorted_tags[0][1] if sorted_tags else 1
            for tag, count in sorted_tags:
                bar_len = int((count / max_count) * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                content.append(
                    f"[tag-item][yellow]#{tag}[/yellow] "
                    f"[dim]{bar}[/dim] [cyan]{count}[/cyan][/tag-item]\n"
                )

        self.update("".join(content))


class DashboardApp(App):
    """Interactive dashboard application.

    Provides a visual overview of logging activity with:
    - GitHub-style contribution calendar
    - Weekly activity chart
    - Statistics summary
    - Top tags

    Key bindings:
        q: Quit
        r: Refresh data
        Tab: Next section
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 1fr;
    }

    #top-row {
        height: 1fr;
    }

    #left-column {
        width: 2fr;
    }

    #right-column {
        width: 1fr;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("tab", "next_section", "Next"),
    ]

    def __init__(self, db, console, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.console = console

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Header()
        with Container(id="main-container"):
            with Horizontal(id="top-row"):
                with Vertical(id="left-column"):
                    yield StreakCalendar(self.db, id="calendar")
                    yield WeeklyBarChart(self.db, id="weekly-chart")
                with Vertical(id="right-column"):
                    yield StatsSummary(self.db, id="stats")
                    yield TopTags(self.db, id="top-tags")
        yield Label(
            "r: Refresh | Tab: Navigate | q: Quit",
            id="status-bar",
        )
        yield Footer()

    def action_quit(self) -> None:
        """Quit the dashboard."""
        self.exit()

    def action_refresh(self) -> None:
        """Refresh all dashboard data."""
        self.notify("Refreshing data...", timeout=1)
        for widget in self.query(StreakCalendar):
            widget._load_data()
            widget._render_calendar()
        for widget in self.query(WeeklyBarChart):
            widget._render_chart()
        for widget in self.query(StatsSummary):
            widget._render_stats()
        for widget in self.query(TopTags):
            widget._render_tags()
        self.notify("Dashboard refreshed!", timeout=1.5)

    def action_next_section(self) -> None:
        """Cycle focus through sections."""
        widgets = list(self.query("*"))
        focused = self.focused
        if focused is None:
            if widgets:
                widgets[0].focus()
        else:
            try:
                idx = widgets.index(focused)
                next_idx = (idx + 1) % len(widgets)
                widgets[next_idx].focus()
            except ValueError:
                if widgets:
                    widgets[0].focus()
