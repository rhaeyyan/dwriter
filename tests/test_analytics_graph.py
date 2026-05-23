"""Output-parity and correctness tests for the Cypher-backed AnalyticsEngine."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dwriter.analytics.engine import AnalyticsEngine
from dwriter.graph import GraphProjector


@pytest.fixture
def proj(tmp_path: Path) -> GraphProjector:
    return GraphProjector(graph_path=tmp_path / "analytics_test.lbug")


def _entry(
    uuid: str,
    content: str = "did some work",
    project: str = "",
    tags: list[str] | None = None,
    days_ago: int = 0,
    hour: int = 10,
    mood: str = "",
    domain: str = "",
    energy: float = 5.0,
) -> MagicMock:
    e = MagicMock()
    e.uuid = uuid
    e.content = content
    e.project = project
    e.tag_names = tags or []
    e.created_at = datetime.now().replace(hour=hour, minute=0, second=0) - timedelta(days=days_ago)
    e.implicit_mood = mood
    e.life_domain = domain
    e.energy_level = energy
    return e


def _todo(
    uuid: str,
    content: str = "fix something",
    project: str = "",
    tags: list[str] | None = None,
    priority: str = "normal",
    status: str = "pending",
    days_ago: int = 0,
    completed_days_ago: int | None = None,
) -> MagicMock:
    t = MagicMock()
    t.uuid = uuid
    t.content = content
    t.project = project
    t.tag_names = tags or []
    t.priority = priority
    t.status = status
    t.created_at = datetime.now() - timedelta(days=days_ago)
    if completed_days_ago is not None:
        t.completed_at = datetime.now() - timedelta(days=completed_days_ago)
    else:
        t.completed_at = None
    t.due_date = None
    return t


@pytest.fixture
def populated(proj: GraphProjector) -> GraphProjector:
    """Projector with a representative set of entries and todos."""
    entries = [
        _entry("e1", "⏱️ deep focus session", project="auth", days_ago=1, hour=9, domain="work", energy=8.0),
        _entry("e2", "wrote unit tests", project="auth", days_ago=2, hour=10, domain="work", energy=6.0, tags=["testing"]),
        _entry("e3", "reviewed PRs", project="infra", days_ago=3, hour=22, domain="work", energy=4.0, tags=["review"]),
        _entry("e4", "read docs", project="", days_ago=4, hour=14, domain="learning", energy=7.0, tags=["testing"]),
        _entry("e5", "fixed pipeline", project="infra", days_ago=5, hour=11, domain="work", energy=5.0),
        _entry("e6", "journaled thoughts", project="", days_ago=0, hour=20, domain="personal", energy=3.0),
    ]
    todos = [
        _todo("t1", project="auth", priority="high", status="completed", days_ago=5, completed_days_ago=3),
        _todo("t2", project="infra", priority="normal", status="completed", days_ago=6, completed_days_ago=2),
        _todo("t3", project="auth", priority="urgent", status="pending", days_ago=1),
        _todo("t4", project="", priority="low", status="pending", days_ago=20),
        _todo("t5", project="", priority="low", status="pending", days_ago=16),
    ]
    for e in entries:
        proj.project_entry(e)
    for t in todos:
        proj.project_todo(t)
    return proj


@pytest.fixture
def engine(populated: GraphProjector) -> AnalyticsEngine:
    with patch("dwriter.analytics.engine.GraphProjector", return_value=populated):
        return AnalyticsEngine()


class TestReturnTypes:
    """Each method must return the exact type the original did."""

    def test_task_staleness_returns_3_ints(self, engine: AnalyticsEngine) -> None:
        r = engine.get_task_staleness()
        assert isinstance(r, tuple) and len(r) == 3
        assert all(isinstance(x, int) for x in r)

    def test_say_do_ratio_returns_2_ints(self, engine: AnalyticsEngine) -> None:
        r = engine.get_say_do_ratio()
        assert isinstance(r, tuple) and len(r) == 2
        assert all(isinstance(x, int) for x in r)

    def test_context_switches_returns_float(self, engine: AnalyticsEngine) -> None:
        assert isinstance(engine.get_context_switches(), float)

    def test_after_hours_percentage_returns_float(self, engine: AnalyticsEngine) -> None:
        assert isinstance(engine.get_after_hours_percentage(), float)

    def test_priority_fulfillment_returns_dict(self, engine: AnalyticsEngine) -> None:
        r = engine.get_priority_fulfillment()
        assert isinstance(r, dict)
        assert set(r.keys()) == {"urgent", "high", "normal", "low"}

    def test_project_roi_returns_list_of_4tuples(self, engine: AnalyticsEngine) -> None:
        r = engine.get_project_roi()
        assert isinstance(r, list)
        for item in r:
            assert isinstance(item, tuple) and len(item) == 4

    def test_weekly_pulse_returns_dict_7_days(self, engine: AnalyticsEngine) -> None:
        r = engine.get_weekly_pulse()
        assert set(r.keys()) == {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}

    def test_focus_density_returns_3tuple(self, engine: AnalyticsEngine) -> None:
        r = engine.get_focus_density()
        assert isinstance(r, tuple) and len(r) == 3

    def test_tag_velocity_returns_list_of_3tuples(self, engine: AnalyticsEngine) -> None:
        r = engine.get_tag_velocity()
        assert isinstance(r, list)
        for item in r:
            assert isinstance(item, tuple) and len(item) == 3

    def test_deep_work_ratio_returns_3tuple(self, engine: AnalyticsEngine) -> None:
        r = engine.get_deep_work_ratio()
        assert isinstance(r, tuple) and len(r) == 3

    def test_rolling_burnout_score_returns_float(self, engine: AnalyticsEngine) -> None:
        r = engine.get_rolling_burnout_score()
        assert isinstance(r, float) and 0.0 <= r <= 1.0

    def test_weekly_archetype_returns_str(self, engine: AnalyticsEngine) -> None:
        assert isinstance(engine.get_weekly_archetype(), str)

    def test_golden_hour_returns_str(self, engine: AnalyticsEngine) -> None:
        assert isinstance(engine.get_golden_hour(), str)

    def test_velocity_delta_returns_2ints(self, engine: AnalyticsEngine) -> None:
        r = engine.get_velocity_delta()
        assert isinstance(r, tuple) and len(r) == 2

    def test_big_rock_returns_tuple_or_none(self, engine: AnalyticsEngine) -> None:
        r = engine.get_big_rock()
        assert r is None or (isinstance(r, tuple) and len(r) == 2)

    def test_domain_energy_returns_dict_of_floats(self, engine: AnalyticsEngine) -> None:
        r = engine.get_domain_energy_distribution()
        assert isinstance(r, dict)
        for v in r.values():
            assert isinstance(v, float)

    def test_streak_info_returns_3ints(self, engine: AnalyticsEngine) -> None:
        r = engine.get_streak_info()
        assert isinstance(r, tuple) and len(r) == 3
        assert all(isinstance(x, int) for x in r)


class TestCorrectness:
    def test_task_staleness_counts_correctly(self, engine: AnalyticsEngine) -> None:
        fresh, stale, dead = engine.get_task_staleness()
        # t3 is 1 day old (fresh); t4 is 20 days (dead); t5 is 16 days (dead)
        # t1 and t2 are completed so excluded
        assert fresh == 1
        assert dead == 2

    def test_say_do_ratio(self, engine: AnalyticsEngine) -> None:
        added, done = engine.get_say_do_ratio(days=30)
        assert added == 5  # all 5 todos created in last 30 days
        assert done == 2   # t1 and t2 completed in last 30 days

    def test_after_hours_detects_late_entry(self, engine: AnalyticsEngine) -> None:
        # e3 was created at hour 22 → should count as after-hours
        pct = engine.get_after_hours_percentage(days=30)
        assert pct > 0.0

    def test_project_roi_top3_max(self, engine: AnalyticsEngine) -> None:
        results = engine.get_project_roi(days=30)
        assert len(results) <= 3

    def test_focus_density_detects_timer_entry(self, engine: AnalyticsEngine) -> None:
        focus, regular, ratio = engine.get_focus_density(days=30)
        assert focus == 1  # only e1 starts with ⏱️
        assert ratio > 0.0

    def test_domain_energy_covers_projected_domains(self, engine: AnalyticsEngine) -> None:
        dist = engine.get_domain_energy_distribution()
        assert "work" in dist
        assert "learning" in dist

    def test_streak_total_count(self, engine: AnalyticsEngine) -> None:
        _, _, total = engine.get_streak_info()
        assert total == 6  # 6 entries projected

    def test_big_rock_returns_top_project(self, engine: AnalyticsEngine) -> None:
        result = engine.get_big_rock(days=30)
        if result:
            proj, pct = result
            assert isinstance(proj, str)
            assert 0.0 < pct <= 100.0

    def test_empty_graph_returns_safe_defaults(self, proj: GraphProjector) -> None:
        with patch("dwriter.analytics.engine.GraphProjector", return_value=proj):
            e = AnalyticsEngine()
        assert e.get_task_staleness() == (0, 0, 0)
        assert e.get_say_do_ratio() == (0, 0)
        assert e.get_context_switches() == 0.0
        assert e.get_after_hours_percentage() == 0.0
        assert e.get_focus_density() == (0, 0, 0.0)
        assert e.get_streak_info() == (0, 0, 0)
        assert e.get_big_rock() is None
        assert e.get_golden_hour() == "N/A"
        assert e.get_domain_energy_distribution() == {}
