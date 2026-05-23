"""Behavioral analytics engine for dwriter — Cypher-backed via LadybugDB."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from ..graph import GraphProjector


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _hour(iso: str) -> int:
    return datetime.fromisoformat(iso).hour


def _dow(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%a")


class AnalyticsEngine:
    """Behavioral metrics backed by the LadybugDB graph index.

    The graph index must be populated (via sync pull or `dw graph rebuild`)
    for results to be meaningful. If the index is empty, methods return
    zero/empty defaults rather than raising errors.

    The `db` constructor argument is retained for API compatibility with
    existing call sites but is unused; the engine reads from the graph index.
    """

    def __init__(self, db: Any = None) -> None:
        """Initialize with an optional db argument (unused, kept for compatibility)."""
        self._g = GraphProjector()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _count(self, cypher: str, params: dict[str, Any] | None = None) -> int:
        rows = self._g.run_cypher(cypher, params)
        return int(rows[0]["n"]) if rows else 0

    def _cutoff(self, days: int) -> str:
        return _iso(datetime.now() - timedelta(days=days))

    # ------------------------------------------------------------------
    # Public API — return types identical to original
    # ------------------------------------------------------------------

    def get_task_staleness(self) -> tuple[int, int, int]:
        """Categorize pending tasks by age (fresh, stale, dead)."""
        c3 = self._cutoff(3)
        c14 = self._cutoff(14)
        fresh = self._count(
            "MATCH (t:Todo) WHERE t.status = 'pending'"
            " AND t.created_at >= $c RETURN count(t) AS n",
            {"c": c3},
        )
        stale = self._count(
            "MATCH (t:Todo) WHERE t.status = 'pending'"
            " AND t.created_at < $c3 AND t.created_at >= $c14 RETURN count(t) AS n",
            {"c3": c3, "c14": c14},
        )
        dead = self._count(
            "MATCH (t:Todo) WHERE t.status = 'pending'"
            " AND t.created_at < $c RETURN count(t) AS n",
            {"c": c14},
        )
        return fresh, stale, dead

    def get_say_do_ratio(self, days: int = 7) -> tuple[int, int]:
        """Get ratio of tasks added vs completed in a time window."""
        c = self._cutoff(days)
        added = self._count(
            "MATCH (t:Todo) WHERE t.created_at >= $c RETURN count(t) AS n", {"c": c}
        )
        done = self._count(
            "MATCH (t:Todo) WHERE t.status = 'completed'"
            " AND t.completed_at >= $c RETURN count(t) AS n",
            {"c": c},
        )
        return added, done

    def get_context_switches(self, days: int = 7) -> float:
        """Calculate average unique projects touched per day."""
        rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.created_at >= $c AND e.project <> ''"
            " RETURN e.created_at AS dt, e.project AS proj",
            {"c": self._cutoff(days)},
        )
        days_map: dict[date, set[str]] = {}
        for row in rows:
            d = datetime.fromisoformat(row["dt"]).date()
            days_map.setdefault(d, set()).add(row["proj"])
        if not days_map:
            return 0.0
        return round(sum(len(p) for p in days_map.values()) / len(days_map), 1)

    def get_after_hours_percentage(self, days: int = 45) -> float:
        """Get percentage of entries created after 10 PM."""
        rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.created_at >= $c RETURN e.created_at AS dt",
            {"c": self._cutoff(days)},
        )
        if not rows:
            return 0.0
        after = sum(1 for r in rows if _hour(r["dt"]) >= 22)
        return round((after / len(rows)) * 100, 1)

    def get_priority_fulfillment(self) -> dict[str, float]:
        """Get average time-to-complete by priority level."""
        rows = self._g.run_cypher(
            "MATCH (t:Todo) WHERE t.status = 'completed' AND t.completed_at <> ''"
            " RETURN t.priority AS priority, t.created_at AS created_at,"
            " t.completed_at AS completed_at"
        )
        times: dict[str, list[float]] = {
            "urgent": [], "high": [], "normal": [], "low": []
        }
        for r in rows:
            if r["created_at"] and r["completed_at"]:
                delta = (
                    datetime.fromisoformat(r["completed_at"])
                    - datetime.fromisoformat(r["created_at"])
                ).total_seconds() / 86400
                p = r["priority"] or "normal"
                if p in times:
                    times[p].append(delta)
        return {
            p: (round(sum(t) / len(t), 1) if t else 0.0)
            for p, t in times.items()
        }

    def get_project_roi(self, days: int = 45) -> list[tuple[str, float, int, int]]:
        """Get top 3 projects by entries per completed task ratio."""
        c = self._cutoff(days)
        entry_rows = self._g.run_cypher(
            "MATCH (e:Entry)-[:ENTRY_IN_PROJECT]->(p:Project)"
            " WHERE e.created_at >= $c RETURN p.name AS proj",
            {"c": c},
        )
        todo_rows = self._g.run_cypher(
            "MATCH (t:Todo)-[:TODO_IN_PROJECT]->(p:Project)"
            " WHERE t.status = 'completed'"
            " AND t.completed_at >= $c RETURN p.name AS proj",
            {"c": c},
        )
        stats: dict[str, dict[str, int]] = {}
        for r in entry_rows:
            stats.setdefault(r["proj"], {"e": 0, "t": 0})["e"] += 1
        for r in todo_rows:
            stats.setdefault(r["proj"], {"e": 0, "t": 0})["t"] += 1
        results = [
            (proj, s["e"] / max(s["t"], 1), s["e"], s["t"])
            for proj, s in stats.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:3]

    def get_weekly_pulse(self) -> dict[str, int]:
        """Get activity aggregated by day of week."""
        result = dict.fromkeys(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 0)
        rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.created_at <> '' RETURN e.created_at AS dt"
        )
        for r in rows:
            result[_dow(r["dt"])] = result.get(_dow(r["dt"]), 0) + 1
        return result

    def get_focus_density(self, days: int = 45) -> tuple[int, int, float]:
        """Get ratio of focus sessions to regular entries."""
        c = self._cutoff(days)
        total = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c RETURN count(e) AS n", {"c": c}
        )
        if total == 0:
            return 0, 0, 0.0
        focus = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c AND e.content STARTS WITH '⏱️'"
            " RETURN count(e) AS n",
            {"c": c},
        )
        return focus, total - focus, round((focus / total) * 100, 1)

    def get_tag_velocity(self, days: int = 7) -> list[tuple[str, int, str]]:
        """Get tags with highest growth between current and previous periods."""
        now = datetime.now()
        cur_cutoff = _iso(now - timedelta(days=days))
        prev_cutoff = _iso(now - timedelta(days=days * 2))

        def _tag_counts(from_: str, to_: str | None = None) -> dict[str, int]:
            if to_:
                q = (
                    "MATCH (e:Entry)-[:ENTRY_HAS_TAG]->(t:Tag)"
                    " WHERE e.created_at >= $from AND e.created_at < $to"
                    " RETURN t.name AS name"
                )
                rows = self._g.run_cypher(q, {"from": from_, "to": to_})
            else:
                q = (
                    "MATCH (e:Entry)-[:ENTRY_HAS_TAG]->(t:Tag)"
                    " WHERE e.created_at >= $from RETURN t.name AS name"
                )
                rows = self._g.run_cypher(q, {"from": from_})
            counts: dict[str, int] = {}
            for r in rows:
                counts[r["name"]] = counts.get(r["name"], 0) + 1
            return counts

        current = _tag_counts(cur_cutoff)
        previous = _tag_counts(prev_cutoff, cur_cutoff)
        result = []
        for tag in set(current) | set(previous):
            cur = current.get(tag, 0)
            prev = previous.get(tag, 0)
            if prev == 0:
                trend = "↑NEW" if cur > 0 else "—"
            else:
                g = ((cur - prev) / prev) * 100
                trend = (
                    f"↑{g:.0f}%" if g > 50
                    else f"↗{g:.0f}%" if g > 0
                    else f"↓{abs(g):.0f}%" if g < -50
                    else f"↘{abs(g):.0f}%" if g < 0
                    else "—"
                )
            if cur > 0:
                result.append((tag, cur, trend))
        return sorted(result, key=lambda x: x[1], reverse=True)[:10]

    def get_deep_work_ratio(self, days: int = 45) -> tuple[int, int, float]:
        """Calculate ratio of deep work sessions vs shallow work."""
        c = self._cutoff(days)
        deep = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c AND e.content STARTS WITH '⏱️'"
            " RETURN count(e) AS n",
            {"c": c},
        )
        shallow_e = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c"
            " AND NOT e.content STARTS WITH '⏱️' RETURN count(e) AS n",
            {"c": c},
        )
        shallow_t = self._count(
            "MATCH (t:Todo) WHERE t.created_at >= $c RETURN count(t) AS n", {"c": c}
        )
        shallow = shallow_e + shallow_t
        total = deep + shallow
        if total == 0:
            return 0, 0, 0.0
        return deep, shallow, round((deep / total) * 100, 1)

    def get_rolling_burnout_score(self, days: int = 7) -> float:
        """Calculate a normalized burnout risk score (0.0 to 1.0)."""
        after_hours_pct = self.get_after_hours_percentage(days=days)
        added, done = self.get_say_do_ratio(days=days)
        base = min(after_hours_pct / 50.0, 1.0) * 0.5
        overload = 0.0
        if added > 0:
            rate = done / added
            if rate < 0.5:
                overload = (0.5 - rate) * 2 * 0.5
        return round(min(base + overload, 1.0), 2)

    def get_weekly_archetype(self, days: int = 7) -> str:
        """Determine the user's productivity persona for the last N days."""
        c = self._cutoff(days)
        total_e = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c RETURN count(e) AS n", {"c": c}
        )
        focus_e = self._count(
            "MATCH (e:Entry) WHERE e.created_at >= $c AND e.content STARTS WITH '⏱️'"
            " RETURN count(e) AS n",
            {"c": c},
        )
        if total_e > 0 and (focus_e / total_e) > 0.4:
            return "The Deep Diver"

        created_t = self._count(
            "MATCH (t:Todo) WHERE t.created_at >= $c RETURN count(t) AS n", {"c": c}
        )
        completed_t = self._count(
            "MATCH (t:Todo) WHERE t.status = 'completed' AND t.completed_at >= $c"
            " RETURN count(t) AS n",
            {"c": c},
        )
        if completed_t > created_t and completed_t >= 3:
            return "The Closer"

        if total_e > (created_t * 3) and total_e >= 10:
            return "The Archivist"

        urgent_done = self._count(
            "MATCH (t:Todo) WHERE t.status = 'completed' AND t.completed_at >= $c"
            " AND (t.priority = 'urgent' OR t.priority = 'high') RETURN count(t) AS n",
            {"c": c},
        )
        if completed_t > 0 and (urgent_done / completed_t) > 0.5:
            return "The Firefighter"

        return "The Steady Builder"

    def get_golden_hour(self, days: int = 7) -> str:
        """Identify the hour with peak combined entry + todo activity."""
        c = self._cutoff(days)
        e_rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.created_at >= $c RETURN e.created_at AS dt",
            {"c": c},
        )
        t_rows = self._g.run_cypher(
            "MATCH (t:Todo) WHERE t.created_at >= $c RETURN t.created_at AS dt",
            {"c": c},
        )
        hourly: dict[int, int] = {}
        for r in e_rows + t_rows:
            if r["dt"]:
                h = _hour(r["dt"])
                hourly[h] = hourly.get(h, 0) + 1
        if not hourly:
            return "N/A"
        h = max(hourly, key=hourly.get)  # type: ignore[arg-type]
        suffix = "AM" if h < 12 else "PM"
        disp = h if h <= 12 else h - 12
        return f"{disp or 12}:00 {suffix}"

    def get_velocity_delta(self) -> tuple[int, int]:
        """Compare current week completions against the previous week."""
        cur = self._cutoff(7)
        prev = self._cutoff(14)
        cur_done = self._count(
            "MATCH (t:Todo) WHERE t.status = 'completed' AND t.completed_at >= $c"
            " RETURN count(t) AS n",
            {"c": cur},
        )
        prev_done = self._count(
            "MATCH (t:Todo) WHERE t.status = 'completed'"
            " AND t.completed_at >= $p AND t.completed_at < $c RETURN count(t) AS n",
            {"p": prev, "c": cur},
        )
        if prev_done == 0:
            delta = 100 if cur_done > 0 else 0
        else:
            delta = int(((cur_done - prev_done) / prev_done) * 100)
        return cur_done, delta

    def get_big_rock(self, days: int = 7) -> tuple[str, float] | None:
        """Find the project with the highest activity share."""
        c = self._cutoff(days)
        rows = self._g.run_cypher(
            "MATCH (e:Entry)-[:ENTRY_IN_PROJECT]->(p:Project)"
            " WHERE e.created_at >= $c RETURN p.name AS proj, count(e) AS cnt"
            " ORDER BY cnt DESC",
            {"c": c},
        )
        if not rows:
            return None
        total = sum(r["cnt"] for r in rows)
        top = rows[0]
        return top["proj"], round((top["cnt"] / total) * 100, 1)

    def get_domain_energy_distribution(self) -> dict[str, float]:
        """Calculates average energy level per life domain."""
        rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.life_domain <> ''"
            " RETURN e.life_domain AS domain, avg(e.energy_level) AS avg_e"
        )
        return {r["domain"]: round(float(r["avg_e"]), 1) for r in rows if r["domain"]}

    def get_streak_info(self) -> tuple[int, int, int]:
        """Calculates current streak, longest streak, and total entry count."""
        total = self._count("MATCH (e:Entry) RETURN count(e) AS n")
        rows = self._g.run_cypher(
            "MATCH (e:Entry) WHERE e.created_at <> '' RETURN e.created_at AS dt"
        )
        date_strs = sorted({r["dt"][:10] for r in rows if r.get("dt")})
        dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in date_strs]

        if not dates:
            return 0, 0, total

        cs = ls = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                cs += 1
                ls = max(ls, cs)
            else:
                cs = 1

        current_streak = 0 if (datetime.now().date() - dates[-1]).days > 1 else cs
        return current_streak, ls, total
