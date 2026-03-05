"""Interactive dashboard TUI using Textual.

This module provides a visual dashboard with streak calendar,
weekly charts, and logging statistics.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from textual import work
from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    ScrollableContainer,
    Vertical,
)
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    LoadingIndicator,
    Static,
)

from ..database import Entry


class KPICard(Static):
    """A KPI card displaying a metric with a large number."""

    DEFAULT_CSS = """
    KPICard {
        height: auto;
        padding: 1 2;
        background: $panel;
        border: solid $primary;
    }

    KPICard .kpi-title {
        color: $text-muted;
        text-style: bold;
        padding: 0 0 1 0;
    }

    KPICard .kpi-value {
        text-align: center;
        text-style: bold;
    }
    """

    def __init__(
        self, title: str, value: str, color: str = "$primary", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.color = color

    def on_mount(self) -> None:
        """Render the KPI card."""
        self._update_display()

    def update_value(self, value: str) -> None:
        """Update the KPI value."""
        self.value = value
        self._update_display()

    def _update_display(self) -> None:
        """Update the displayed content."""
        self.update(
            f"[{self.color} bold]{self.value}[/{self.color} bold]\n"
            f"[kpi-title]{self.title}[/kpi-title]"
        )


class EntryDetailScreen(Screen):  # type: ignore[type-arg]
    """Screen showing entries for a selected project or tag."""

    CSS = """
    #entry-container {
        height: 1fr;
        padding: 1 2;
    }

    #entry-header {
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    #entry-table {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("q", "go_back", "Back"),
    ]

    def __init__(
        self,
        db: Any,
        title: str,
        entries: list[Entry],
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.db = db
        self.title = title
        self.entries = entries

    def compose(self) -> ComposeResult:
        """Compose the entry detail screen."""
        yield Header(show_clock=True)
        with ScrollableContainer(id="entry-container"):
            yield Static(
                f"[bold]📋 {self.title}[/bold]\n"
                f"[dim]Press Escape or 'q' to go back[/dim]",
                id="entry-header",
            )
            table: DataTable[str] = DataTable(id="entry-table")
            table.add_columns("Date", "Content", "Project", "Tags")
            for entry in self.entries:
                date_str = entry.created_at.strftime("%Y-%m-%d %H:%M")
                content = (
                    entry.content[:60] + "..."
                    if len(entry.content) > 60
                    else entry.content
                )
                project = entry.project or "-"
                tags = ", ".join(entry.tag_names) if entry.tag_names else "-"
                table.add_row(date_str, content, project, tags)
            yield table
        yield Footer()

    def action_go_back(self) -> None:
        """Return to the main dashboard."""
        self.app.pop_screen()


class StreakCalendar(Static):
    """GitHub-style contribution calendar showing logging streaks."""

    DEFAULT_CSS = """
    StreakCalendar {
        height: auto;
        margin: 1;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    StreakCalendar .day-level-0 {
        color: #D1F8EF;
        background: #D1F8EF;
    }

    StreakCalendar .day-level-1 {
        color: #A1E3F9;
        background: #A1E3F9;
    }

    StreakCalendar .day-level-2 {
        color: #578FCA;
        background: #578FCA;
    }

    StreakCalendar .day-level-3 {
        color: #3674B5;
        background: #3674B5;
    }

    StreakCalendar .day-level-4 {
        color: #155E95;
        background: #155E95;
    }

    StreakCalendar .legend {
        padding: 1 0 0 0;
    }
    """

    def __init__(self, db: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.db = db
        self.entries_by_date: dict[str, int] = {}
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

    def _calculate_streaks(self) -> tuple[int, int]:
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
        # Show last 10 weeks for better readability
        num_weeks = 10
        start_date = today - timedelta(days=num_weeks * 7 - 1)

        # Align start_date to Monday (start of week)
        start_date = start_date - timedelta(days=start_date.weekday())

        # Build calendar data - organize by weeks (columns)
        weeks: list[list[tuple[datetime, int] | None]] = []
        current_week: list[tuple[datetime, int] | None] = []

        current_date = start_date
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            count = self.entries_by_date.get(date_str, 0)
            current_week.append((current_date, count))  # type: ignore[arg-type]

            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

            current_date += timedelta(days=1)

        # Pad last week if needed
        while len(current_week) < 7:
            current_week.append(None)
            current_date += timedelta(days=1)
        if current_week:
            weeks.append(current_week)

        # Limit to num_weeks
        weeks = weeks[-num_weeks:]

        # Build display
        content = ["[bold]📅 Last 10 Weeks[/bold]  "]
        content.append(f"Current: [green]{self.current_streak}d[/green]  ")
        content.append(f"Longest: [yellow]{self.longest_streak}d[/yellow]\n")

        # Month labels - show month name at start of each month
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_line = "    "
        last_month = -1
        for week in weeks:
            if week and week[0] is not None:
                month = week[0][0].month
                if month != last_month:
                    month_line += f"{months[month-1]:<5}"
                    last_month = month
                else:
                    month_line += "     "
        content.append(f"[dim]{month_line}[/dim]\n")

        # Render the grid - each row is a day of week, each column is a week
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        # Color mapping for activity levels (light to dark blue)
        bg_colors = ["#D1F8EF", "#A1E3F9", "#578FCA", "#3674B5", "#155E95"]

        for day_idx in range(7):
            line = f"[bold]{day_names[day_idx]}[/bold] "
            for week in weeks:
                if not week:
                    line += "   "
                    continue
                # Ensure week has enough elements
                while len(week) <= day_idx:
                    week.append(None)
                cell = week[day_idx]
                if cell:
                    _, count = cell
                    level = self._get_level(count)
                    if level == 0:
                        line += " · "  # Light dot for no activity
                    else:
                        # Use colored block with background
                        color = bg_colors[level - 1]
                        line += f"[on {color}]{chr(9608)}[/on {color}] "
                else:
                    line += "   "
            content.append(line + "\n")

        # Legend
        content.append("\n[legend][dim]Less ")
        for color in bg_colors:
            content.append(f"[on {color}]{chr(9608)}[/on {color}]")
        content.append(" More[/dim][/legend]")

        self.update("".join(content))


class ActivitySparkline(Static):
    """Sparkline showing last 30 days of activity with top projects and tags."""

    DEFAULT_CSS = """
    ActivitySparkline {
        height: auto;
        margin: 1;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }
    """

    def __init__(self, db: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.db = db

    def on_mount(self) -> None:
        """Load data and render sparkline."""
        self._render_sparkline()

    def _render_sparkline(self) -> None:
        """Render the activity sparkline with top projects and tags."""
        today = datetime.now().date()
        start_date = today - timedelta(days=29)  # 30 days total

        # Get entry counts by date
        entries_by_date = self.db.get_entries_count_by_date(start_date, today)

        # Build data array for sparkline (fill in zeros for missing days)
        data = []
        for i in range(30):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            data.append(entries_by_date.get(date_str, 0))

        content = ["[bold]📈 30 Days[/bold] "]

        if any(data):
            # Create text-based sparkline
            spark_chars = " ▁▂▃▄▅▆▇█"
            max_val = max(data) if data else 1
            spark_line = ""
            for val in data:
                idx = int((val / max_val) * 8) if max_val > 0 else 0
                spark_line += spark_chars[idx]
            content.append(f"[green]{spark_line}[/green]\n")
            content.append(f"[dim]{min(data)}/{max(data)}/{sum(data)}[/dim]\n")
        else:
            content.append("[dim]No activity[/dim]\n")

        # Get top projects (last 30 days)
        all_entries = self.db.get_all_entries()
        project_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}

        for entry in all_entries:
            entry_date = entry.created_at.date()
            if start_date <= entry_date <= today:
                if entry.project:
                    project_counts[entry.project] = (
                        project_counts.get(entry.project, 0) + 1
                    )
                for tag in entry.tag_names:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Top 3 projects
        top_projects = sorted(
            project_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]
        # Top 5 tags
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Render projects and tags side-by-side (compact format)
        if top_projects or top_tags:
            max_rows = max(len(top_projects), len(top_tags))
            # Header
            content.append("\n[purple]Projects:[/purple] ")
            content.append(" " * 6)
            content.append("[yellow]Tags:[/yellow]\n")

            # Data rows (compact)
            for i in range(max_rows):
                if i < len(top_projects):
                    proj, cnt = top_projects[i]
                    content.append(f"  {proj[:12]:<12}{cnt:>3}")
                else:
                    content.append(" " * 16)
                content.append("  ")
                if i < len(top_tags):
                    tag, cnt = top_tags[i]
                    content.append(f"#{tag[:10]:<10}{cnt:>3}\n")
                else:
                    content.append("\n")

        self.update("".join(content))


class DashboardApp(App):  # type: ignore[type-arg]
    """Interactive dashboard application.

    Provides a visual overview of logging activity with:
    - KPI cards with big numbers
    - GitHub-style contribution calendar
    - 30-day activity sparkline
    - Interactive DataTables for projects and tags
    - Drill-down to view entries

    Key bindings:
        q: Quit
        r: Refresh data
        d: Drill-down into selected item
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }

    #kpi-row {
        height: auto;
        margin: 0 0 1 0;
    }

    #kpi-row KPICard {
        width: 1fr;
        margin: 0 1;
    }

    #charts-row {
        height: 50%;
        margin: 0 0 1 0;
    }

    #charts-left {
        width: 2fr;
        margin: 0 1 0 0;
    }

    #charts-right {
        width: 1fr;
        margin: 0 0 0 1;
    }

    #tables-row {
        height: 50%;
    }

    #tables-left {
        width: 1fr;
        margin: 0 1 0 0;
    }

    #tables-right {
        width: 1fr;
        margin: 0 0 0 1;
    }

    #loading-overlay {
        align: center middle;
        height: 100%;
        width: 100%;
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
        ("d", "drill_down", "Drill Down"),
    ]

    def __init__(self, db: Any, console: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.db = db
        self.console = console
        self.data_loaded = False

        # KPI data
        self.total_entries = 0
        self.current_streak = 0
        self.longest_streak = 0
        self.consistency_pct = 0.0

        # Table data
        self.project_stats: dict[str, int] = {}
        self.tag_stats: dict[str, int] = {}

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            # Loading indicator (will be removed when data loads)
            yield LoadingIndicator(id="loading-overlay")

            # Row 1: KPI Cards
            with Horizontal(id="kpi-row"):
                yield KPICard("Total Entries", "0", color="$primary", id="kpi-total")
                yield KPICard(
                    "Current Streak", "0 days", color="$success", id="kpi-streak"
                )
                yield KPICard(
                    "Longest Streak", "0 days", color="$warning", id="kpi-longest"
                )
                yield KPICard(
                    "Consistency", "0%", color="$info", id="kpi-consistency"
                )

            # Row 2: Charts
            with Horizontal(id="charts-row"):
                with Vertical(id="charts-left"):
                    yield StreakCalendar(self.db, id="calendar")
                with Vertical(id="charts-right"):
                    yield ActivitySparkline(self.db, id="sparkline")

            # Row 3: Interactive Tables
            with Horizontal(id="tables-row"):
                with Vertical(id="tables-left"):
                    projects_table: DataTable[str] = DataTable(id="projects-table")
                    projects_table.add_columns("Project        ", "   Entries")
                    projects_table.cursor_type = "row"
                    yield projects_table
                with Vertical(id="tables-right"):
                    tags_table: DataTable[str] = DataTable(id="tags-table")
                    tags_table.add_columns("Tag            ", "   Entries")
                    tags_table.cursor_type = "row"
                    yield tags_table

        yield Label(
            "r: Refresh | d: Drill Down | q: Quit",
            id="status-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start loading data asynchronously."""
        self._load_dashboard_data()

    @work(exclusive=True, thread=True)
    def _load_dashboard_data(self) -> None:
        """Load all dashboard data in a background thread."""
        # Load entries
        all_entries = self.db.get_all_entries()
        self.total_entries = len(all_entries)

        # Calculate streaks
        entries_by_date: dict[str, int] = {}
        for entry in all_entries:
            date_str = entry.created_at.strftime("%Y-%m-%d")
            entries_by_date[date_str] = entries_by_date.get(date_str, 0) + 1

        self.current_streak, self.longest_streak = self._calculate_streaks(
            entries_by_date
        )

        # Calculate consistency (entries in last 30 days / 30)
        today = datetime.now().date()
        start_date = today - timedelta(days=29)
        entries_in_range = self.db.get_entries_count_by_date(start_date, today)
        total_in_30_days = sum(entries_in_range.values())
        self.consistency_pct = min(100.0, (total_in_30_days / 30) * 100)

        # Load project stats
        self.project_stats = self.db.get_project_stats()

        # Load tag stats
        self.tag_stats = self.db.get_entries_with_tags_count()

        # Update UI on main thread
        self.call_from_thread(self._update_kpis)
        self.call_from_thread(self._update_tables)
        self.call_from_thread(self._hide_loading)

    def _calculate_streaks(self, entries_by_date: dict[str, int]) -> tuple[int, int]:
        """Calculate current and longest streaks."""
        if not entries_by_date:
            return 0, 0

        today = datetime.now().date()
        dates = sorted(
            datetime.strptime(d, "%Y-%m-%d").date()
            for d in entries_by_date.keys()
        )

        # Current streak
        current = 0
        for i in range(14):
            check_date = today - timedelta(days=i)
            if check_date in dates:
                current += 1
            elif i == 0:
                continue
            else:
                break

        # Longest streak
        longest = 1
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                streak += 1
                longest = max(longest, streak)
            else:
                streak = 1

        return current, longest

    def _update_kpis(self) -> None:
        """Update KPI cards with loaded data."""
        kpi_total = self.query_one("#kpi-total", KPICard)
        kpi_streak = self.query_one("#kpi-streak", KPICard)
        kpi_longest = self.query_one("#kpi-longest", KPICard)
        kpi_consistency = self.query_one("#kpi-consistency", KPICard)

        kpi_total.update_value(str(self.total_entries))
        kpi_streak.update_value(f"{self.current_streak} days")
        kpi_longest.update_value(f"{self.longest_streak} days")
        kpi_consistency.update_value(f"{self.consistency_pct:.1f}%")

    def _update_tables(self) -> None:
        """Update DataTables with loaded data."""
        # Projects table
        projects_table = self.query_one("#projects-table", DataTable)
        projects_table.clear()
        for project, count in sorted(
            self.project_stats.items(), key=lambda x: x[1], reverse=True
        )[:15]:
            projects_table.add_row(project, f"     {count}")

        # Tags table
        tags_table = self.query_one("#tags-table", DataTable)
        tags_table.clear()
        for tag, count in sorted(
            self.tag_stats.items(), key=lambda x: x[1], reverse=True
        )[:15]:
            tags_table.add_row(tag, f"     {count}")

    def _hide_loading(self) -> None:
        """Hide the loading indicator."""
        loading = self.query_one("#loading-overlay")
        loading.remove()
        self.data_loaded = True

    def action_quit(self) -> None:  # type: ignore[override]
        """Quit the dashboard."""
        self.exit()

    def action_refresh(self) -> None:
        """Refresh all dashboard data."""
        self.notify("Refreshing data...", timeout=1)
        self._load_dashboard_data()

    def action_drill_down(self) -> None:
        """Drill down into the selected project or tag."""
        if not self.data_loaded:
            self.notify("Data still loading...", timeout=1)
            return

        # Check which table is focused
        focused = self.focused
        if isinstance(focused, DataTable):
            if focused.id == "projects-table":
                self._drill_down_project(focused)
            elif focused.id == "tags-table":
                self._drill_down_tag(focused)
            else:
                self.notify("Select a project or tag first", timeout=1)
        else:
            self.notify("Focus on a project or tag table first", timeout=1)

    def _drill_down_project(self, table: DataTable[str]) -> None:
        """Open drill-down screen for selected project."""
        row_key = table.cursor_row
        if row_key is None:
            self.notify("Select a project first", timeout=1)
            return

        row = table.get_row_at(row_key)
        if row:
            project_name = row[0]
            # Remove any # prefix if present
            if project_name.startswith("#"):
                project_name = project_name[1:]

            # Get entries for this project
            entries = self.db.get_all_entries(project=project_name)
            if entries:
                self.push_screen(
                    EntryDetailScreen(
                        self.db,
                        f"Project: {project_name}",
                        entries[:50],  # Limit to 50 entries
                    )
                )
            else:
                self.notify("No entries found for this project", timeout=1)

    def _drill_down_tag(self, table: DataTable[str]) -> None:
        """Open drill-down screen for selected tag."""
        row_key = table.cursor_row
        if row_key is None:
            self.notify("Select a tag first", timeout=1)
            return

        row = table.get_row_at(row_key)
        if row:
            tag_name = row[0]
            # Remove # prefix
            if tag_name.startswith("#"):
                tag_name = tag_name[1:]

            # Get entries with this tag
            entries = self.db.get_all_entries(tags=[tag_name])
            if entries:
                self.push_screen(
                    EntryDetailScreen(
                        self.db,
                        f"Tag: #{tag_name}",
                        entries[:50],  # Limit to 50 entries
                    )
                )
            else:
                self.notify("No entries found for this tag", timeout=1)
