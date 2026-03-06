"""Tests for natural language date parsing utilities."""

from datetime import datetime, timedelta

import pytest

from dwriter.date_utils import parse_date_or_default, parse_natural_date


class TestParseNaturalDate:
    """Tests for parse_natural_date function."""

    def test_today(self):
        """Test parsing 'today'."""
        result = parse_natural_date("today")
        expected = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_natural_date("yesterday")
        expected = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_natural_date("tomorrow")
        expected = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_days_ago_singular(self):
        """Test parsing '1 day ago'."""
        result = parse_natural_date("1 day ago")
        expected = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_days_ago_plural(self):
        """Test parsing '3 days ago'."""
        result = parse_natural_date("3 days ago")
        expected = (datetime.now() - timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_days_ago_with_spaces(self):
        """Test parsing '5  days ago' with extra spaces."""
        result = parse_natural_date("5  days ago")
        expected = (datetime.now() - timedelta(days=5)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_weeks_ago_singular(self):
        """Test parsing '1 week ago'."""
        result = parse_natural_date("1 week ago")
        expected = (datetime.now() - timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_weeks_ago_plural(self):
        """Test parsing '2 weeks ago'."""
        result = parse_natural_date("2 weeks ago")
        expected = (datetime.now() - timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_last_monday(self):
        """Test parsing 'last Monday'."""
        result = parse_natural_date("last Monday")
        today = datetime.now()
        # Find last Monday
        days_back = (today.weekday() - 0) % 7
        if days_back == 0:
            days_back = 7
        expected = (today - timedelta(days=days_back)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected
        assert result.weekday() == 0  # Monday

    def test_last_friday(self):
        """Test parsing 'last Friday'."""
        result = parse_natural_date("last Friday")
        today = datetime.now()
        # Find last Friday
        days_back = (today.weekday() - 4) % 7
        if days_back == 0:
            days_back = 7
        expected = (today - timedelta(days=days_back)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected
        assert result.weekday() == 4  # Friday

    def test_last_friday_abbreviated(self):
        """Test parsing 'last Fri'."""
        result = parse_natural_date("last Fri")
        today = datetime.now()
        # Find last Friday
        days_back = (today.weekday() - 4) % 7
        if days_back == 0:
            days_back = 7
        expected = (today - timedelta(days=days_back)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected
        assert result.weekday() == 4  # Friday

    def test_weekday_monday(self):
        """Test parsing 'Monday' (most recent Monday)."""
        result = parse_natural_date("Monday")
        today = datetime.now()
        days_back = (today.weekday() - 0) % 7
        # If today is Monday, should return today
        if days_back == 0:
            expected = today.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expected = (today - timedelta(days=days_back)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        assert result == expected

    def test_weekday_friday(self):
        """Test parsing 'Friday'."""
        result = parse_natural_date("Friday")
        today = datetime.now()
        days_back = (today.weekday() - 4) % 7
        if days_back == 0:
            expected = today.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expected = (today - timedelta(days=days_back)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        assert result == expected

    def test_weekday_abbreviated(self):
        """Test parsing abbreviated weekday 'Mon'."""
        result = parse_natural_date("Mon")
        today = datetime.now()
        days_back = (today.weekday() - 0) % 7
        if days_back == 0:
            expected = today.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expected = (today - timedelta(days=days_back)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        assert result == expected

    def test_iso_format(self):
        """Test parsing ISO format date '2024-01-15'."""
        result = parse_natural_date("2024-01-15")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_slash_format(self):
        """Test parsing US format '01/15/2024'."""
        result = parse_natural_date("01/15/2024")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_european_format(self):
        """Test parsing European format '15/01/2024'."""
        result = parse_natural_date("15/01/2024")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_long_month_format(self):
        """Test parsing 'January 15, 2024'."""
        result = parse_natural_date("January 15, 2024")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_short_month_format(self):
        """Test parsing 'Jan 15, 2024'."""
        result = parse_natural_date("Jan 15, 2024")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_day_month_year_format(self):
        """Test parsing '15 January 2024'."""
        result = parse_natural_date("15 January 2024")
        expected = datetime(2024, 1, 15, 0, 0, 0, 0)
        assert result == expected

    def test_case_insensitive(self):
        """Test that parsing is case insensitive."""
        result1 = parse_natural_date("Yesterday")
        result2 = parse_natural_date("YESTERDAY")
        result3 = parse_natural_date("yesterday")
        expected = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result1 == expected
        assert result2 == expected
        assert result3 == expected

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        result1 = parse_natural_date("  yesterday  ")
        result2 = parse_natural_date("yesterday")
        expected = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result1 == expected
        assert result2 == expected

    def test_invalid_date_raises_error(self):
        """Test that invalid dates raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_natural_date("invalid date")
        assert "Unable to parse date" in str(exc_info.value)

    def test_invalid_weekday(self):
        """Test that invalid weekday raises ValueError."""
        with pytest.raises(ValueError):
            parse_natural_date("last Someday")


class TestParseDateOrDefault:
    """Tests for parse_date_or_default function."""

    def test_none_returns_current_datetime(self):
        """Test that None returns current datetime."""
        result = parse_date_or_default(None)
        # Just check it's close to now (within a second)
        assert abs((result - datetime.now()).total_seconds()) < 1

    def test_valid_date_string(self):
        """Test parsing a valid date string."""
        result = parse_date_or_default("yesterday")
        expected = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_today_string(self):
        """Test parsing 'today'."""
        result = parse_date_or_default("today")
        expected = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected


class TestFutureDates:
    """Tests for future date parsing."""

    def test_tomorrow_explicit(self):
        """Test parsing 'tomorrow'."""
        result = parse_natural_date("tomorrow")
        expected = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_plus_days_shorthand(self):
        """Test parsing '+5d' shorthand."""
        result = parse_natural_date("+5d")
        expected = (datetime.now() + timedelta(days=5)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_plus_days_shorthand_singular(self):
        """Test parsing '+1d' shorthand."""
        result = parse_natural_date("+1d")
        expected = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_plus_weeks_shorthand(self):
        """Test parsing '+2w' shorthand."""
        result = parse_natural_date("+2w")
        expected = (datetime.now() + timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_plus_weeks_shorthand_singular(self):
        """Test parsing '+1w' shorthand."""
        result = parse_natural_date("+1w")
        expected = (datetime.now() + timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_plus_months_shorthand(self):
        """Test parsing '+3m' shorthand (approximate 30-day months)."""
        result = parse_natural_date("+3m")
        expected = (datetime.now() + timedelta(days=90)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_future_days_explicit(self):
        """Test parsing '3 days'."""
        result = parse_natural_date("3 days")
        expected = (datetime.now() + timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_future_days_explicit_singular(self):
        """Test parsing '1 day'."""
        result = parse_natural_date("1 day")
        expected = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_future_weeks_explicit(self):
        """Test parsing '2 weeks'."""
        result = parse_natural_date("2 weeks")
        expected = (datetime.now() + timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected

    def test_future_weeks_explicit_singular(self):
        """Test parsing '1 week'."""
        result = parse_natural_date("1 week")
        expected = (datetime.now() + timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result == expected
