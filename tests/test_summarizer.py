"""Tests for the summarization engine and database summary methods."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dwriter.ai.summarizer import WeeklySummary, get_week_bounds
from dwriter.database import Database


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink()


# ---------------------------------------------------------------------------
# Week Bounds Tests
# ---------------------------------------------------------------------------


class TestGetWeekBounds:
    """Tests for the deterministic week boundary calculation."""

    def test_returns_monday_to_sunday(self):
        """Verify bounds are always Mon 00:00 to Sun 23:59:59."""
        start, end = get_week_bounds()

        assert start.weekday() == 0, "period_start must be a Monday"
        assert end.weekday() == 6, "period_end must be a Sunday"
        assert start.hour == 0 and start.minute == 0 and start.second == 0
        assert end.hour == 23 and end.minute == 59 and end.second == 59

    def test_reference_date_within_week(self):
        """A reference date should return the week containing that date."""
        # Wednesday, 2026-04-01
        ref = datetime(2026, 4, 1, 14, 30)
        start, end = get_week_bounds(ref)

        assert start == datetime(2026, 3, 30, 0, 0, 0)  # Monday
        assert end == datetime(2026, 4, 5, 23, 59, 59)  # Sunday

    def test_reference_on_monday(self):
        """A Monday reference should return that same week."""
        ref = datetime(2026, 3, 30, 0, 0, 0)  # Monday
        start, end = get_week_bounds(ref)

        assert start == datetime(2026, 3, 30, 0, 0, 0)
        assert end == datetime(2026, 4, 5, 23, 59, 59)

    def test_reference_on_sunday(self):
        """A Sunday reference should return the week ending that Sunday."""
        ref = datetime(2026, 4, 5, 18, 0, 0)  # Sunday
        start, end = get_week_bounds(ref)

        assert start == datetime(2026, 3, 30, 0, 0, 0)
        assert end == datetime(2026, 4, 5, 23, 59, 59)


# ---------------------------------------------------------------------------
# Summary JSON Round-trip Tests
# ---------------------------------------------------------------------------


class TestWeeklySummarySchema:
    """Tests for the WeeklySummary Pydantic model."""

    def test_json_roundtrip(self):
        """Verify model_dump_json -> model_validate_json fidelity."""
        original = WeeklySummary(
            biggest_wins=["Shipped v3.8", "Fixed race condition", "Merged PR #42"],
            friction_points=["Deployment blocked", "CI flaky", "Unclear spec"],
            dominant_mood="Focused",
            velocity="Completed 12 tasks, added 8 — net positive.",
            key_projects=["dwriter", "mainframe"],
            key_tags=["deployment", "refactor", "docs"],
        )

        json_str = original.model_dump_json()
        restored = WeeklySummary.model_validate_json(json_str)

        assert restored.biggest_wins == original.biggest_wins
        assert restored.friction_points == original.friction_points
        assert restored.dominant_mood == original.dominant_mood
        assert restored.velocity == original.velocity
        assert restored.key_projects == original.key_projects
        assert restored.key_tags == original.key_tags

    def test_minimal_fields(self):
        """Schema should accept empty lists."""
        summary = WeeklySummary(
            biggest_wins=[],
            friction_points=[],
            dominant_mood="Neutral",
            velocity="No tasks this week.",
            key_projects=[],
            key_tags=[],
        )
        assert summary.dominant_mood == "Neutral"


# ---------------------------------------------------------------------------
# Database Summary Methods Tests
# ---------------------------------------------------------------------------


class TestDatabaseSummaries:
    """Tests for the Summary model persistence and queries."""

    def test_add_and_get_summaries(self, temp_db):
        """Round-trip: add a summary and retrieve it."""
        start = datetime(2026, 3, 30, 0, 0, 0)
        end = datetime(2026, 4, 5, 23, 59, 59)

        temp_db.add_summary(
            content='{"biggest_wins": ["test"]}',
            period_start=start,
            period_end=end,
            summary_type="weekly",
        )

        summaries = temp_db.get_summaries(summary_type="weekly", limit=4)
        assert len(summaries) == 1
        assert summaries[0].period_start == start
        assert summaries[0].period_end == end
        assert '"biggest_wins"' in summaries[0].content

    def test_summaries_ordered_by_period_end(self, temp_db):
        """Summaries should be returned in descending period_end order."""
        week1_start = datetime(2026, 3, 23, 0, 0, 0)
        week1_end = datetime(2026, 3, 29, 23, 59, 59)
        week2_start = datetime(2026, 3, 30, 0, 0, 0)
        week2_end = datetime(2026, 4, 5, 23, 59, 59)

        temp_db.add_summary(
            content='{"week": 1}',
            period_start=week1_start,
            period_end=week1_end,
        )
        temp_db.add_summary(
            content='{"week": 2}',
            period_start=week2_start,
            period_end=week2_end,
        )

        summaries = temp_db.get_summaries(limit=4)
        assert len(summaries) == 2
        assert summaries[0].period_end > summaries[1].period_end

    def test_get_latest_summary(self, temp_db):
        """get_latest_summary returns the single most recent record."""
        temp_db.add_summary(
            content='{"week": "old"}',
            period_start=datetime(2026, 3, 16),
            period_end=datetime(2026, 3, 22, 23, 59, 59),
        )
        temp_db.add_summary(
            content='{"week": "new"}',
            period_start=datetime(2026, 3, 23),
            period_end=datetime(2026, 3, 29, 23, 59, 59),
        )

        latest = temp_db.get_latest_summary()
        assert latest is not None
        assert '"new"' in latest.content

    def test_get_latest_summary_empty(self, temp_db):
        """Returns None when no summaries exist."""
        latest = temp_db.get_latest_summary()
        assert latest is None

    def test_summary_limit(self, temp_db):
        """Verify the limit parameter is respected."""
        base_date = datetime(2026, 1, 1)
        for i in range(6):
            temp_db.add_summary(
                content=f'{{"week": {i}}}',
                period_start=base_date + timedelta(days=i * 7),
                period_end=base_date + timedelta(days=i * 7 + 6, hours=23),
            )

        summaries = temp_db.get_summaries(limit=4)
        assert len(summaries) == 4


# ---------------------------------------------------------------------------
# Core Engine Tests
# ---------------------------------------------------------------------------


class TestCompressWeek:
    """Tests for the high-level compress_week orchestrator."""

    @patch("dwriter.ai.summarizer._summarize_text")
    def test_compress_week_standard_path(self, mock_summarize, temp_db):
        """Standard path with a small amount of text should call AI once."""
        from dwriter.ai.summarizer import compress_week
        from dwriter.config import AIConfig

        # Setup: Mock data and AI response
        temp_db.add_entry(content="Entry 1", created_at=datetime(2026, 3, 31))
        mock_summary = WeeklySummary(
            biggest_wins=["Test Win"],
            friction_points=[],
            dominant_mood="Neutral",
            velocity="Steady",
            key_projects=[],
            key_tags=[],
        )
        mock_summarize.return_value = mock_summary

        config = AIConfig(enabled=True, chat_model="gemma4:e4b", daemon_model="gemma4:e2b")
        start = datetime(2026, 3, 30)
        end = datetime(2026, 4, 5, 23, 59, 59)

        # Act
        result = compress_week(temp_db, config, start, end)

        # Assert
        assert result.biggest_wins == ["Test Win"]
        assert mock_summarize.call_count == 1
        # Verify persistence
        assert temp_db.get_latest_summary() is not None

    @patch("dwriter.ai.summarizer._summarize_text")
    def test_token_chunking_threshold(self, mock_summarize, temp_db):
        """Large text should trigger the two-pass split/merge strategy."""
        from dwriter.ai.summarizer import compress_week
        from dwriter.config import AIConfig

        # Setup: Seed a huge amount of entries to exceed 20k threshold
        # _TOKEN_CHUNK_THRESHOLD = 20_000
        content = "X" * 15_000
        temp_db.add_entry(content=content, created_at=datetime(2026, 3, 31))
        temp_db.add_entry(content=content, created_at=datetime(2026, 4, 3))

        mock_summary = WeeklySummary(
            biggest_wins=["Chunked Win"],
            friction_points=[],
            dominant_mood="Neutral",
            velocity="Steady",
            key_projects=[],
            key_tags=[],
        )
        # Mocking 3 calls: Part 1, Part 2, then the final Merge
        mock_summarize.return_value = mock_summary

        config = AIConfig(enabled=True, chat_model="gemma4:e4b", daemon_model="gemma4:e2b")
        start = datetime(2026, 3, 30)
        end = datetime(2026, 4, 5, 23, 59, 59)

        # Act
        compress_week(temp_db, config, start, end)

        # Assert: 3 calls expected for the chunking logic
        assert mock_summarize.call_count == 3
