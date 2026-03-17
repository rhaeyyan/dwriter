"""Natural language date parsing utilities for dwriter.

This module provides functions to parse natural language date expressions
like "yesterday", "last Friday", "3 days ago", etc.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_natural_date(date_str: str) -> datetime:
    """Parse a natural language date string into a datetime object.

    Args:
        date_str: A natural language date expression like "yesterday",
            "last Friday", "3 days ago", "today", etc.

    Returns:
        A datetime object representing the parsed date.

    Raises:
        ValueError: If the date string cannot be parsed.

    Examples:
        >>> parse_natural_date("yesterday")
        datetime(2024, 1, 15, 0, 0, 0)  # (assuming today is 2024-01-16)

        >>> parse_natural_date("last Friday")
        datetime(2024, 1, 12, 0, 0, 0)  # (assuming today is 2024-01-16)

        >>> parse_natural_date("3 days ago")
        datetime(2024, 1, 13, 0, 0, 0)  # (assuming today is 2024-01-16)

        >>> parse_natural_date("+5d")
        datetime(2024, 1, 21, 0, 0, 0)  # (assuming today is 2024-01-16)

        >>> parse_natural_date("tomorrow")
        datetime(2024, 1, 17, 0, 0, 0)  # (assuming today is 2024-01-16)
    """
    date_str = date_str.strip().lower()

    # Handle "today"
    if date_str == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "yesterday"
    if date_str == "yesterday":
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "tomorrow"
    if date_str == "tomorrow":
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "+Nd" shorthand pattern for future dates (e.g., "+3d", "+5d", "+10d")
    future_days_match = re.match(r"^\+(\d+)d$", date_str)
    if future_days_match:
        days = int(future_days_match.group(1))
        date = datetime.now() + timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "+Nw" shorthand pattern for future weeks (e.g., "+2w", "+1w")
    future_weeks_match = re.match(r"^\+(\d+)w$", date_str)
    if future_weeks_match:
        weeks = int(future_weeks_match.group(1))
        date = datetime.now() + timedelta(weeks=weeks)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "+Nm" shorthand pattern for future months (e.g., "+1m", "+3m")
    # Note: Uses approximate 30-day months
    future_months_match = re.match(r"^\+(\d+)m$", date_str)
    if future_months_match:
        months = int(future_months_match.group(1))
        # Approximate months as 30 days each
        days = months * 30
        date = datetime.now() + timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "N days" pattern for future dates (e.g., "3 days", "1 day")
    future_days_pattern = re.match(r"^(\d+)\s*days?$", date_str)
    if future_days_pattern:
        days = int(future_days_pattern.group(1))
        date = datetime.now() + timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "N weeks" pattern for future dates (e.g., "2 weeks", "1 week")
    future_weeks_pattern = re.match(r"^(\d+)\s*weeks?$", date_str)
    if future_weeks_pattern:
        weeks = int(future_weeks_pattern.group(1))
        date = datetime.now() + timedelta(weeks=weeks)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "N days ago" pattern (e.g., "3 days ago", "1 day ago")
    days_ago_match = re.match(r"^(\d+)\s*days?\s*ago$", date_str)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        date = datetime.now() - timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "N weeks ago" pattern (e.g., "2 weeks ago", "1 week ago")
    weeks_ago_match = re.match(r"^(\d+)\s*weeks?\s*ago$", date_str)
    if weeks_ago_match:
        weeks = int(weeks_ago_match.group(1))
        date = datetime.now() - timedelta(weeks=weeks)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "-Nd" shorthand pattern (e.g., "-3d", "-5d", "-10d")
    shorthand_match = re.match(r"^-(\d+)d$", date_str)
    if shorthand_match:
        days = int(shorthand_match.group(1))
        date = datetime.now() - timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "-Nw" shorthand pattern for weeks (e.g., "-5w", "-2w")
    weeks_shorthand_match = re.match(r"^-(\d+)w$", date_str)
    if weeks_shorthand_match:
        weeks = int(weeks_shorthand_match.group(1))
        date = datetime.now() - timedelta(weeks=weeks)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "-Nm" shorthand pattern for months (e.g., "-1m", "-3m")
    # Note: Uses approximate 30-day months
    months_shorthand_match = re.match(r"^-(\d+)m$", date_str)
    if months_shorthand_match:
        months = int(months_shorthand_match.group(1))
        # Approximate months as 30 days each
        days = months * 30
        date = datetime.now() - timedelta(days=days)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "last <weekday>" pattern (e.g., "last Friday", "last Monday")
    weekdays = {
        "monday": 0,
        "mon": 0,
        "tuesday": 1,
        "tue": 1,
        "wednesday": 2,
        "wed": 2,
        "thursday": 3,
        "thu": 3,
        "friday": 4,
        "fri": 4,
        "saturday": 5,
        "sat": 5,
        "sunday": 6,
        "sun": 6,
    }

    last_weekday_match = re.match(r"^last\s+(\w+)$", date_str)
    if last_weekday_match:
        weekday_name = last_weekday_match.group(1).lower()
        if weekday_name in weekdays:
            target_weekday = weekdays[weekday_name]
            today = datetime.now()
            days_back = (today.weekday() - target_weekday) % 7
            # If today is the same weekday, go back 7 days
            if days_back == 0:
                days_back = 7
            date = today - timedelta(days=days_back)
            return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "<weekday>" pattern (e.g., "Friday", "Monday")
    # This refers to the most recent occurrence of that weekday
    if date_str in weekdays:
        target_weekday = weekdays[date_str]
        today = datetime.now()
        days_back = (today.weekday() - target_weekday) % 7
        # If today is the same weekday, interpret as today
        if days_back == 0:
            return today.replace(hour=0, minute=0, second=0, microsecond=0)
        date = today - timedelta(days=days_back)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle standard date formats
    date_formats = [
        "%Y-%m-%d",  # 2024-01-15
        "%Y/%m/%d",  # 2024/01/15
        "%d-%m-%Y",  # 15-01-2024
        "%d/%m/%Y",  # 15/01/2024
        "%m-%d-%Y",  # 01-15-2024
        "%m/%d/%Y",  # 01/15/2024
        "%B %d, %Y",  # January 15, 2024
        "%b %d, %Y",  # Jan 15, 2024
        "%d %B %Y",  # 15 January 2024
        "%d %b %Y",  # 15 Jan 2024
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            continue

    raise ValueError(
        f"Unable to parse date: '{date_str}'. "
        "Supported formats: 'today', 'yesterday', 'tomorrow', "
        "'N days ago', 'N weeks ago', '-Nd' (e.g., '-3d'), "
        "'-Nw' (e.g., '-5w'), '-Nm' (e.g., '-1m'), "
        "'+Nd' (e.g., '+5d'), '+Nw' (e.g., '+2w'), '+Nm' (e.g., '+1m'), "
        "'N days', 'N weeks', "
        "'last <weekday>', '<weekday>', "
        "or standard dates (YYYY-MM-DD, MM/DD/YYYY, etc.)"
    )


def parse_date_or_default(date_str: Optional[str]) -> datetime:
    """Parse a date string or return current datetime if None.

    Args:
        date_str: A natural language date expression or None.

    Returns:
        A datetime object. If date_str is None, returns current datetime.
    """
    if date_str is None:
        return datetime.now()

    return parse_natural_date(date_str)
