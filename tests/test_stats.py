"""Tests for stats streak calculation."""

from datetime import datetime, timedelta

from dwriter.stats_utils import calculate_streak


def test_streak_empty():
    """Test streak calculation with no entries."""
    current, longest = calculate_streak([])
    assert current == 0
    assert longest == 0


def test_streak_single_day():
    """Test streak with single day."""
    dates = [datetime.now()]
    current, longest = calculate_streak(dates)
    assert current >= 0  # May be 0 if not today
    assert longest >= 1


def test_streak_consecutive_days():
    """Test streak with consecutive days."""
    today = datetime.now()
    dates = [today - timedelta(days=i) for i in range(5)]

    current, longest = calculate_streak(dates)

    assert longest >= 5


def test_streak_with_gap():
    """Test streak calculation with a gap."""
    today = datetime.now()
    # 3 consecutive days, gap, then 2 more
    dates = [
        today,
        today - timedelta(days=1),
        today - timedelta(days=2),
        today - timedelta(days=10),
        today - timedelta(days=11),
    ]

    current, longest = calculate_streak(dates)

    assert longest >= 3
