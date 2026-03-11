"""Behavioral analytics engine for dwriter.

This module provides advanced behavioral metrics to help users understand
their work patterns, cognitive load, and potential burnout risks.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .database import Entry, Tag, Todo


class AnalyticsEngine:
    """Analytics engine for behavioral insights.

    This class provides metrics that go beyond simple counts to reveal
    patterns in user behavior, task management, and productivity.

    Attributes:
        db: Database instance for querying data.
    """

    def __init__(self, db) -> None:  # type: ignore
        """Initialize the analytics engine.

        Args:
            db: Database instance with Session factory.
        """
        self.db = db

    def get_task_staleness(self) -> tuple[int, int, int]:
        """Get pending tasks categorized by age using optimized SQL.

        Returns:
            Tuple of (fresh <3d, stale 3-14d, dead >14d) pending tasks.
        """
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)
        fourteen_days_ago = now - timedelta(days=14)
        
        with self.db.Session() as session:
            # Categorize in a single query
            fresh = session.query(Todo).filter(Todo.status == "pending", Todo.created_at >= three_days_ago).count()
            stale = session.query(Todo).filter(Todo.status == "pending", Todo.created_at < three_days_ago, Todo.created_at >= fourteen_days_ago).count()
            dead = session.query(Todo).filter(Todo.status == "pending", Todo.created_at < fourteen_days_ago).count()
            return fresh, stale, dead

    def get_say_do_ratio(self, days: int = 7) -> tuple[int, int]:
        """Get ratio of tasks added vs completed in a time window using SQL counts.

        Args:
            days: Number of days to look back.

        Returns:
            Tuple of (added, completed) tasks in the last X days.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            added = session.query(Todo).filter(Todo.created_at >= cutoff).count()
            done = (
                session.query(Todo)
                .filter(
                    Todo.status == "completed",
                    Todo.completed_at >= cutoff,
                )
                .count()
            )
            return added, done

    def get_context_switches(self, days: int = 7) -> float:
        """Get average unique projects touched per day.

        High context switching indicates cognitive overload and
        fragmented attention.

        Args:
            days: Number of days to analyze.

        Returns:
            Average unique projects per day.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            entries = (
                session.query(Entry.created_at, Entry.project)
                .filter(Entry.created_at >= cutoff, Entry.project.isnot(None))
                .all()
            )

            days_map: dict[date, set[str]] = {}
            for dt, proj in entries:
                d = dt.date()
                if d not in days_map:
                    days_map[d] = set()
                days_map[d].add(proj)

            if not days_map:
                return 0.0
            return round(
                sum(len(projs) for projs in days_map.values()) / len(days_map),
                1,
            )

    def get_after_hours_percentage(self, days: int = 30) -> float:
        """Get percentage of entries created after 10 PM using SQL.

        Args:
            days: Number of days to analyze.

        Returns:
            Percentage of entries created after 10 PM.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            total = session.query(Entry).filter(Entry.created_at >= cutoff).count()
            if total == 0:
                return 0.0

            # Use SQLite strftime to filter hours
            after_hours = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                func.strftime("%H", Entry.created_at) >= "22"
            ).count()
            
            return round((after_hours / total) * 100, 1)

    def get_priority_fulfillment(self) -> dict[str, float]:
        """Get average time-to-complete by priority level.

        Reveals whether urgent tasks are actually completed faster
        than lower priority items.

        Returns:
            Dictionary mapping priority levels to avg days to complete.
        """
        with self.db.Session() as session:
            completed = (
                session.query(Todo)
                .filter(
                    Todo.status == "completed",
                    Todo.completed_at.isnot(None),
                )
                .all()
            )

            priority_times: dict[str, list[float]] = {
                "urgent": [],
                "high": [],
                "normal": [],
                "low": [],
            }

            for todo in completed:
                if todo.completed_at and todo.created_at:
                    days = (todo.completed_at - todo.created_at).total_seconds() / 86400
                    priority_times[todo.priority].append(days)

            return {
                priority: (round(sum(times) / len(times), 1) if times else 0.0)
                for priority, times in priority_times.items()
            }

    def get_project_roi(self, days: int = 30) -> list[tuple[str, float, int, int]]:
        """Get top 3 highest-friction projects by entries per completed task ratio.

        Args:
            days: Number of days to analyze.

        Returns:
            List of (project_name, ratio, entries, tasks) tuples sorted by friction.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            # Count entries per project
            entries = (
                session.query(Entry.project)
                .filter(Entry.created_at >= cutoff, Entry.project.isnot(None))
                .all()
            )

            # Count completed todos per project
            todos = (
                session.query(Todo.project)
                .filter(
                    Todo.status == "completed",
                    Todo.completed_at >= cutoff,
                    Todo.project.isnot(None),
                )
                .all()
            )

            project_stats: dict[str, dict[str, int]] = {}
            for (e,) in entries:
                proj = e
                if proj not in project_stats:
                    project_stats[proj] = {"entries": 0, "todos": 0}
                project_stats[proj]["entries"] += 1

            for (t,) in todos:
                proj = t
                if proj not in project_stats:
                    project_stats[proj] = {"entries": 0, "todos": 0}
                project_stats[proj]["todos"] += 1

            results: list[tuple[str, float, int, int]] = []
            for proj, stats in project_stats.items():
                e_count = stats["entries"]
                t_count = stats["todos"]
                # Prevent division by zero; if 0 tasks completed, it's pure friction
                ratio = e_count / max(t_count, 1)
                results.append((proj, ratio, e_count, t_count))

            # Sort by highest friction (most entries per task)
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:3]

    def get_weekly_pulse(self) -> dict[str, int]:
        """Get activity aggregated by day of week using SQL.

        Reveals patterns like "Tuesday Slump" or "Friday Surge".

        Returns:
            Dictionary mapping day names (Mon, Tue, etc.) to entry counts.
        """
        # SQLite %w returns 0-6 where 0 is Sunday
        # We need to map this to Mon-Sun (Mon is 1, Sun is 0)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        result = dict.fromkeys(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 0)

        with self.db.Session() as session:
            stats = session.query(
                func.strftime("%w", Entry.created_at),
                func.count(Entry.id)
            ).group_by(func.strftime("%w", Entry.created_at)).all()

            for day_idx_str, count in stats:
                name = day_names[int(day_idx_str)]
                result[name] = count

            return result

    def get_focus_density(self, days: int = 30) -> tuple[int, int, float]:
        """Get ratio of focus sessions to regular entries using SQL.

        Focus sessions are entries with content starting with "⏱️".

        Args:
            days: Number of days to analyze.

        Returns:
            Tuple of (focus_sessions, regular_entries, focus_percentage).
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            total = session.query(Entry).filter(Entry.created_at >= cutoff).count()
            if total == 0:
                return 0, 0, 0.0

            focus_sessions = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                Entry.content.like("⏱️%")
            ).count()
            
            regular = total - focus_sessions

            return (
                focus_sessions,
                regular,
                round((focus_sessions / total) * 100, 1),
            )

    def get_tag_velocity(self, days: int = 7) -> list[tuple[str, int, str]]:
        """Get tags with highest week-over-week growth.

        Args:
            days: Number of days to analyze (should be multiple of 7).

        Returns:
            List of (tag, count, trend) tuples sorted by growth.
        """
        now = datetime.now()
        current_cutoff = now - timedelta(days=days)
        previous_cutoff = now - timedelta(days=days * 2)

        with self.db.Session() as session:
            # Current period tags
            current_entries = (
                session.query(Entry.id).filter(Entry.created_at >= current_cutoff).all()
            )
            current_entry_ids = {e[0] for e in current_entries}

            current_tags: dict[str, int] = {}
            if current_entry_ids:
                tag_results = (
                    session.query(Tag.name)
                    .filter(Tag.entry_id.in_(current_entry_ids))
                    .all()
                )
                for (name,) in tag_results:
                    current_tags[name] = current_tags.get(name, 0) + 1

            # Previous period tags
            previous_entries = (
                session.query(Entry.id)
                .filter(
                    Entry.created_at >= previous_cutoff,
                    Entry.created_at < current_cutoff,
                )
                .all()
            )
            previous_entry_ids = {e[0] for e in previous_entries}

            previous_tags: dict[str, int] = {}
            if previous_entry_ids:
                tag_results = (
                    session.query(Tag.name)
                    .filter(Tag.entry_id.in_(previous_entry_ids))
                    .all()
                )
                for (name,) in tag_results:
                    previous_tags[name] = previous_tags.get(name, 0) + 1

            # Calculate growth
            result = []
            all_tags = set(current_tags.keys()) | set(previous_tags.keys())

            for tag in all_tags:
                current = current_tags.get(tag, 0)
                previous = previous_tags.get(tag, 0)

                if previous == 0:
                    trend = "↑NEW" if current > 0 else "—"
                else:
                    growth = ((current - previous) / previous) * 100
                    if growth > 50:
                        trend = f"↑{growth:.0f}%"
                    elif growth > 0:
                        trend = f"↗{growth:.0f}%"
                    elif growth < -50:
                        trend = f"↓{abs(growth):.0f}%"
                    elif growth < 0:
                        trend = f"↘{abs(growth):.0f}%"
                    else:
                        trend = "—"

                if current > 0:
                    result.append((tag, current, trend))

            return sorted(result, key=lambda x: x[1], reverse=True)[:10]
