"""Natural language date parsing utilities for dwriter.

This module provides functions to parse natural language date expressions
like "yesterday", "last Friday", "3 days ago", etc.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_natural_date(
    date_str: str, prefer_future: bool = False, format_hint: Optional[str] = None
) -> datetime:
    """Parse a natural language date string into a datetime object.

    Args:
        date_str: A natural language date expression like "yesterday",
            "last Friday", "3 days ago", "today", etc.
        prefer_future: If True, ambiguous dates (like "Friday") will prefer
            future occurrences.
        format_hint: Optional format string to try first (e.g., "%m/%d/%Y").

    Returns:
        A datetime object representing the parsed date.

    Raises:
        ValueError: If the date string cannot be parsed.
    """
    date_str = date_str.strip().lower()

    if format_hint:
        try:
            return datetime.strptime(date_str, format_hint)
        except ValueError:
            pass

    # Special handling for "at" prefix
    if date_str.startswith("at "):
        date_str = date_str[3:].strip()

    now = datetime.now()
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle relative offsets first: +Nh, +Nm (e.g., +2h, +30m)
    rel_time_match = re.match(r"^\+(?P<value>\d+)(?P<unit>[hm])$", date_str)
    if rel_time_match:
        value = int(rel_time_match.group("value"))
        unit = rel_time_match.group("unit")
        if unit == "h":
            return now + timedelta(hours=value)
        else:
            return now + timedelta(minutes=value)

    # Handle "in N mins/hours"
    in_rel_match = re.match(
        r"^in\s+(?P<value>\d+)\s*(?P<unit>min|mins|minute|minutes|hour|hours)$",
        date_str,
    )
    if in_rel_match:
        value = int(in_rel_match.group("value"))
        unit = in_rel_match.group("unit")
        if unit.startswith("h"):
            return now + timedelta(hours=value)
        else:
            return now + timedelta(minutes=value)

    # Handle absolute times (e.g., "3pm", "14:00", "2:30pm")
    time_match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", date_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)

        if meridiem == "pm" and hour < 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0

        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # If the time has already passed today, and it's a bare time
        # (not part of a combined pattern), assume tomorrow if prefer_future
        # is set or if it's just a time like "2pm"
        if target < now:
            target += timedelta(days=1)
        return target

    # Weekday mapping
    weekdays = {
        "monday": 0, "mon": 0, "tuesday": 1, "tue": 1,
        "wednesday": 2, "wed": 2, "thursday": 3, "thu": 3,
        "friday": 4, "fri": 4, "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6,
    }

    # Handle combined patterns like "tomorrow 2pm" or "Friday at 3"
    day_patterns = (
        r"(?P<day>today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun|last\s+\w+)"
    )
    time_patterns = r"(?P<time>\d{1,2}(?::\d{2})?\s*(?P<meridiem>am|pm)?)"
    combined_match = re.match(
        rf"^{day_patterns}(?:\s+(?:at\s+)?{time_patterns})?$", date_str
    )
    if combined_match:
        day_str = combined_match.group("day")
        time_part = combined_match.group("time")

        # Get base date
        if day_str == "today":
            base_date = today_midnight
        elif day_str == "tomorrow":
            base_date = today_midnight + timedelta(days=1)
        elif day_str == "yesterday":
            base_date = today_midnight - timedelta(days=1)
        elif day_str.startswith("last "):
            wd_name = day_str[5:].strip()
            target_wd = weekdays.get(wd_name)
            if target_wd is not None:
                days_back = (now.weekday() - target_wd) % 7
                if days_back == 0:
                    days_back = 7
                base_date = today_midnight - timedelta(days=days_back)
            else:
                raise ValueError(f"Unable to parse date: '{date_str}'")
        elif day_str in weekdays:
            target_wd = weekdays[day_str]
            if prefer_future:
                days_ahead = (target_wd - now.weekday()) % 7
                base_date = today_midnight + timedelta(days=days_ahead)
            else:
                days_back = (now.weekday() - target_wd) % 7
                base_date = today_midnight - timedelta(days=days_back)
        else:
            base_date = today_midnight

        if time_part:
            # Parse time and apply to base_date
            time_dt = parse_natural_date(time_part)
            return base_date.replace(hour=time_dt.hour, minute=time_dt.minute)
        return base_date

    # Simple patterns
    if date_str == "today":
        return today_midnight
    if date_str == "yesterday":
        return today_midnight - timedelta(days=1)
    if date_str == "tomorrow":
        return today_midnight + timedelta(days=1)

    # Shorthands
    future_match = re.match(r"^\+(?P<val>\d+)(?P<unit>d|w|mo)$", date_str)
    if future_match:
        val = int(future_match.group("val"))
        unit = future_match.group("unit")
        if unit == "d":
            return today_midnight + timedelta(days=val)
        if unit == "w":
            return today_midnight + timedelta(weeks=val)
        if unit == "mo":
            return today_midnight + timedelta(days=val * 30)

    past_match = re.match(r"^-(?P<val>\d+)(?P<unit>d|w|mo)$", date_str)
    if past_match:
        val = int(past_match.group("val"))
        unit = past_match.group("unit")
        if unit == "d":
            return today_midnight - timedelta(days=val)
        if unit == "w":
            return today_midnight - timedelta(weeks=val)
        if unit == "mo":
            return today_midnight - timedelta(days=val * 30)

    # N days/weeks [ago]
    ago_match = re.match(
        r"^(?P<val>\d+)\s+(?P<unit>day|days|week|weeks)(?P<ago>\s+ago)?$", date_str
    )
    if ago_match:
        val = int(ago_match.group("val"))
        unit = ago_match.group("unit")
        is_past = ago_match.group("ago") is not None
        delta = (
            timedelta(days=val) if unit.startswith("day") else timedelta(weeks=val)
        )
        if is_past:
            return today_midnight - delta
        return today_midnight + delta

    # Weekdays alone
    if date_str in weekdays:
        target_wd = weekdays[date_str]
        if prefer_future:
            days_ahead = (target_wd - now.weekday()) % 7
            return today_midnight + timedelta(days=days_ahead)
        else:
            days_back = (now.weekday() - target_wd) % 7
            return today_midnight - timedelta(days=days_back)

    # Standard formats
    date_formats = [
        "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
        "%m-%d-%Y", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y",
        "%d %B %Y", "%d %b %Y", "%Y-%m-%d %H:%M",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: '{date_str}'")


def parse_date_or_default(
    date_str: Optional[str], format_hint: Optional[str] = None
) -> datetime:
    """Parse a date string or return current datetime if None.

    Args:
        date_str: A natural language date expression or None.
        format_hint: Optional format string to try first (e.g., "%m/%d/%Y").

    Returns:
        A datetime object. If date_str is None, returns current datetime.
    """
    if date_str is None:
        return datetime.now()

    return parse_natural_date(date_str, format_hint=format_hint)
