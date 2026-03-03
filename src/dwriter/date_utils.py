"""Natural language date parsing utilities for Day Writer.

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
    """
    date_str = date_str.strip().lower()

    # Handle "today"
    if date_str == "today":
        return datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Handle "yesterday"
    if date_str == "yesterday":
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle "tomorrow"
    if date_str == "tomorrow":
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

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
        "'N days ago', 'N weeks ago', 'last <weekday>', '<weekday>', "
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
