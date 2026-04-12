"""Behavioral analytics engine for dwriter."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func

from ..database import Entry, Tag, Todo


class AnalyticsEngine:
    """Provides behavioral metrics such as work patterns and cognitive load."""

    def __init__(self, db) -> None:  # type: ignore
        """Initialize with a database instance."""
        self.db = db

    def get_task_staleness(self) -> tuple[int, int, int]:
        """Categorize pending tasks by age (fresh, stale, dead)."""
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)
        fourteen_days_ago = now - timedelta(days=14)

        with self.db.Session() as session:
            fresh = session.query(Todo).filter(Todo.status == "pending", Todo.created_at >= three_days_ago).count()
            stale = session.query(Todo).filter(Todo.status == "pending", Todo.created_at < three_days_ago, Todo.created_at >= fourteen_days_ago).count()
            dead = session.query(Todo).filter(Todo.status == "pending", Todo.created_at < fourteen_days_ago).count()
            return fresh, stale, dead

    def get_say_do_ratio(self, days: int = 7) -> tuple[int, int]:
        """Get ratio of tasks added vs completed in a time window."""
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
        """Calculate average unique projects touched per day."""
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

    def get_after_hours_percentage(self, days: int = 45) -> float:
        """Get percentage of entries created after 10 PM."""
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
        """Get average time-to-complete by priority level."""
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

    def get_project_roi(self, days: int = 45) -> list[tuple[str, float, int, int]]:
        """Get top 3 projects by entries per completed task ratio."""
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            entries = (
                session.query(Entry.project)
                .filter(Entry.created_at >= cutoff, Entry.project.isnot(None))
                .all()
            )

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
                ratio = e_count / max(t_count, 1)
                results.append((proj, ratio, e_count, t_count))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:3]

    def get_weekly_pulse(self) -> dict[str, int]:
        """Get activity aggregated by day of week."""
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

    def get_focus_density(self, days: int = 45) -> tuple[int, int, float]:
        """Get ratio of focus sessions to regular entries."""
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
        """Get tags with highest growth between current and previous periods."""
        now = datetime.now()
        current_cutoff = now - timedelta(days=days)
        previous_cutoff = now - timedelta(days=days * 2)

        with self.db.Session() as session:
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

    def get_deep_work_ratio(self, days: int = 45) -> tuple[int, int, float]:
        """Calculate the ratio of deep work sessions vs shallow work.

        Deep work: Focus sessions (starts with ⏱️).
        Shallow work: Standard entries + total Todos added.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        with self.db.Session() as session:
            deep_work = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                Entry.content.like("⏱️%")
            ).count()

            shallow_entries = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                ~Entry.content.like("⏱️%")
            ).count()

            shallow_todos = session.query(Todo).filter(
                Todo.created_at >= cutoff
            ).count()

            shallow_work = shallow_entries + shallow_todos
            total_work = deep_work + shallow_work

            if total_work == 0:
                return 0, 0, 0.0

            return deep_work, shallow_work, round((deep_work / total_work) * 100, 1)

    def get_rolling_burnout_score(self, days: int = 7) -> float:
        """Calculate a normalized burnout risk score (0.0 to 1.0)."""
        after_hours_pct = self.get_after_hours_percentage(days=days)
        added, done = self.get_say_do_ratio(days=days)

        base_score = min(after_hours_pct / 50.0, 1.0) * 0.5

        overload_score = 0.0
        if added > 0:
            completion_rate = done / added
            if completion_rate < 0.5:
                overload_score = (0.5 - completion_rate) * 2 * 0.5

        total_score = min(base_score + overload_score, 1.0)
        return round(total_score, 2)

    def get_weekly_archetype(self, days: int = 7) -> str:
        """Determine the user's productivity persona for the last 7 days."""
        now = datetime.now()
        cutoff = now - timedelta(days=days)

        with self.db.Session() as session:
            # 1. Check for Deep Diver (Focus Ratio)
            total_entries = session.query(Entry).filter(Entry.created_at >= cutoff).count()
            focus_entries = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                Entry.content.like("⏱️%")
            ).count()

            if total_entries > 0 and (focus_entries / total_entries) > 0.4:
                return "The Deep Diver"

            # 2. Check for The Closer (Completions vs Creations)
            created_todos = session.query(Todo).filter(Todo.created_at >= cutoff).count()
            completed_todos = session.query(Todo).filter(
                Todo.status == "completed",
                Todo.completed_at >= cutoff
            ).count()

            if completed_todos > created_todos and completed_todos >= 3:
                return "The Closer"

            # 3. Check for The Archivist (Journaling vs Tasks)
            if total_entries > (created_todos * 3) and total_entries >= 10:
                return "The Archivist"

            # 4. Check for The Firefighter (High Priority Focus)
            urgent_completed = session.query(Todo).filter(
                Todo.status == "completed",
                Todo.completed_at >= cutoff,
                Todo.priority.in_(["urgent", "high"])
            ).count()

            if completed_todos > 0 and (urgent_completed / completed_todos) > 0.5:
                return "The Firefighter"

            return "The Steady Builder"

    def get_golden_hour(self, days: int = 7) -> str:
        """Identify the hour with peak activity density."""
        now = datetime.now()
        cutoff = now - timedelta(days=days)

        with self.db.Session() as session:
            # Combined query for Entry and Todo activity by hour
            entry_stats = session.query(
                func.strftime("%H", Entry.created_at),
                func.count(Entry.id)
            ).filter(Entry.created_at >= cutoff).group_by(func.strftime("%H", Entry.created_at)).all()

            todo_stats = session.query(
                func.strftime("%H", Todo.created_at),
                func.count(Todo.id)
            ).filter(Todo.created_at >= cutoff).group_by(func.strftime("%H", Todo.created_at)).all()

            hourly_counts: dict[str, int] = {}
            for hour, count in entry_stats + todo_stats:
                hourly_counts[hour] = hourly_counts.get(hour, 0) + count

            if not hourly_counts:
                return "N/A"

            peak_hour = max(hourly_counts, key=hourly_counts.get)  # type: ignore
            hour_int = int(peak_hour)
            suffix = "AM" if hour_int < 12 else "PM"
            display_hour = hour_int if hour_int <= 12 else hour_int - 12
            if display_hour == 0:
                display_hour = 12

            return f"{display_hour}:00 {suffix}"

    def get_velocity_delta(self) -> tuple[int, int]:
        """Compare current week completions against the previous week."""
        now = datetime.now()
        current_cutoff = now - timedelta(days=7)
        previous_cutoff = now - timedelta(days=14)

        with self.db.Session() as session:
            current_done = session.query(Todo).filter(
                Todo.status == "completed",
                Todo.completed_at >= current_cutoff
            ).count()

            previous_done = session.query(Todo).filter(
                Todo.status == "completed",
                Todo.completed_at >= previous_cutoff,
                Todo.completed_at < current_cutoff
            ).count()

            if previous_done == 0:
                delta = 100 if current_done > 0 else 0
            else:
                delta = int(((current_done - previous_done) / previous_done) * 100)

            return current_done, delta

    def get_big_rock(self, days: int = 7) -> tuple[str, float] | None:
        """Find the project with the highest activity share."""
        now = datetime.now()
        cutoff = now - timedelta(days=days)

        with self.db.Session() as session:
            total_activity = session.query(Entry).filter(
                Entry.created_at >= cutoff,
                Entry.project.isnot(None)
            ).count()

            if total_activity == 0:
                return None

            project_counts = session.query(
                Entry.project,
                func.count(Entry.id)
            ).filter(
                Entry.created_at >= cutoff,
                Entry.project.isnot(None)
            ).group_by(Entry.project).order_by(func.count(Entry.id).desc()).first()

            if not project_counts:
                return None

            project, count = project_counts
            percentage = (count / total_activity) * 100
            return project, round(percentage, 1)

    def get_domain_energy_distribution(self) -> dict[str, float]:
        """Calculates average energy level per life domain.

        Returns:
            dict[str, float]: Mapping of domain name to average energy level.
        """
        with self.db.Session() as session:
            stats = (
                session.query(Entry.life_domain, func.avg(Entry.energy_level))
                .filter(Entry.life_domain.isnot(None))
                .group_by(Entry.life_domain)
                .all()
            )
            return {domain: round(float(avg), 1) for domain, avg in stats if domain}

    def get_streak_info(self) -> tuple[int, int, int]:
        """Calculates current streak, longest streak, and total entry count.

        Returns:
            tuple[int, int, int]: (current_streak, longest_streak, total_entries).
        """
        total_entries = 0
        current_streak = 0
        longest_streak = 0

        with self.db.Session() as session:
            total_entries = session.query(func.count(Entry.id)).scalar() or 0

            dates_raw = (
                session.query(func.distinct(func.date(Entry.created_at)))
                .order_by(func.date(Entry.created_at))
                .all()
            )
            dates = sorted([datetime.strptime(r[0], "%Y-%m-%d").date() for r in dates_raw if r[0]])

            if dates:
                cs = 1
                ls = 1
                for i in range(1, len(dates)):
                    if (dates[i] - dates[i - 1]).days == 1:
                        cs += 1
                        ls = max(ls, cs)
                    else:
                        cs = 1
                if (datetime.now().date() - dates[-1]).days > 1:
                    current_streak = 0
                else:
                    current_streak = cs
                longest_streak = ls

        return current_streak, longest_streak, total_entries
