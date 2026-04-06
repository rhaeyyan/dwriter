"""Parser for omnibox quick-add input.

This module provides parsing logic for the global quick-add input bar,
extracting content, tags, and projects from user input.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal


@dataclass
class ParsedEntry:
    """Represents a parsed quick-add command for journal entries.

    Attributes:
        content: The cleaned content text with tags and projects removed.
        tags: List of tag names extracted from #tag patterns.
        project: Project name extracted from &project patterns, or None.
        created_at: Optional datetime for the entry (parsed from date suffixes).
    """

    content: str
    tags: list[str] = field(default_factory=list)
    project: str | None = None
    created_at: datetime | None = None


@dataclass
class ParsedTodo:
    """Represents a parsed todo quick-add command.

    Attributes:
        content: The cleaned content text with metadata removed.
        tags: List of tag names extracted from #tag patterns.
        project: Project name extracted from &project patterns, or None.
        priority: Priority level (urgent, high, normal, low).
        due_date: Due date string if specified with @due:date.
    """

    content: str
    tags: list[str] = field(default_factory=list)
    project: str | None = None
    priority: Literal["urgent", "high", "normal", "low"] = "normal"
    due_date: str | None = None


@dataclass
class ParsedTimer:
    """Represents a parsed timer command.

    Format: "#tag1 #tag2 &project 15" or just "15" for minutes

    Attributes:
        minutes: Timer duration in minutes.
        tags: List of tag names extracted from #tag patterns.
        project: Project name extracted from &project patterns, or None.
        content: Optional content/description for the session log.
    """

    minutes: int
    tags: list[str] = field(default_factory=list)
    project: str | None = None
    content: str | None = None


def parse_quick_add(raw_input: str, date_format: str = "YYYY-MM-DD") -> ParsedEntry:
    """Parse an omnibox string into content, tags, and project.

    Format: "Completed the auth flow #backend #security &core-engine"

    Date suffixes:
        -yesterday, -2 days ago, -last Friday, -2024-01-15
        Or standalone: 2024-01-15

    Args:
        raw_input: Raw input string from the omnibox.
        date_format: User's preferred date format (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY).

    Returns:
        ParsedEntry with extracted content, tags, project, and optional datetime.
    """
    # Extract tags (words prefixed with #)
    tags: list[str] = re.findall(r"#([\w:-]+)", raw_input)

    # Extract project (text prefixed with &)
    projects: list[str] = re.findall(r"&([\w:-]+)", raw_input)

    # Extract date suffixes
    created_at: datetime | None = None

    # Mapping for strftime/strptime
    fmt_map = {
        "YYYY-MM-DD": "%Y-%m-%d",
        "MM/DD/YYYY": "%m/%d/%Y",
        "DD/MM/YYYY": "%d/%m/%Y",
    }
    hint = fmt_map.get(date_format, "%Y-%m-%d")

    # Construct regex for absolute dates based on format
    # YYYY-MM-DD: \d{4}-\d{2}-\d{2}
    # MM/DD/YYYY: \d{2}/\d{2}/\d{4}
    # DD/MM/YYYY: \d{2}/\d{2}/\d{4}
    abs_date_pattern = r"\d{4}-\d{2}-\d{2}"
    if date_format in ("MM/DD/YYYY", "DD/MM/YYYY"):
        abs_date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"

    # Match hyphen-prefixed date patterns
    date_regex = (
        rf"\s+-(yesterday|today|\d+d|\d+w|\d+\s*days?\s*ago|\d+\s*weeks?\s*ago|"
        rf"last\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
        rf"{abs_date_pattern})"
    )
    date_match = re.search(date_regex, raw_input, re.IGNORECASE)
    if date_match:
        date_str = date_match.group(1)
        created_at = _parse_date_suffix(date_str, hint)
    else:
        # Check for standalone absolute dates
        date_match = re.search(rf"\b({abs_date_pattern})\b", raw_input)
        if date_match:
            date_str = date_match.group(1)
            created_at = _parse_date_suffix(date_str, hint)

    # Clean the input: remove tags, project blocks, and date suffix
    clean_text = raw_input
    # Remove date suffixes first
    clean_text = re.sub(
        rf"\s+-(yesterday|today|\d+d|\d+w|\d+\s*days?\s*ago|\d+\s*weeks?\s*ago|last\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)|{abs_date_pattern})",
        "",
        clean_text,
        flags=re.IGNORECASE,
    )
    clean_text = re.sub(rf"\b{abs_date_pattern}\b", "", clean_text)
    # Then remove tags and projects (&)
    clean_text = re.sub(r"#[\w:-]+", "", clean_text)
    clean_text = re.sub(r"&[\w:-]+", "", clean_text)

    # Normalize whitespace
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return ParsedEntry(
        content=clean_text,
        tags=tags,
        project=projects[0] if projects else None,
        created_at=created_at,
    )


def _parse_date_suffix(date_str: str, format_hint: str = "%Y-%m-%d") -> datetime | None:
    """Parse a date suffix string.

    Args:
        date_str: Date string (e.g., "yesterday", "2 days ago", "2024-01-15").
        format_hint: Standard format string to try first.

    Returns:
        Parsed datetime or None.
    """
    date_str = date_str.lower().strip()

    # Try hinted format first
    try:
        return datetime.strptime(date_str, format_hint).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    except ValueError:
        pass

    # Try fallback standard format if different
    if format_hint != "%Y-%m-%d":
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        except ValueError:
            pass

    now = datetime.now()

    # Handle "yesterday"
    if date_str == "yesterday":
        return (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Handle "today"
    if date_str == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle short forms: "2d" (2 days ago), "2w" (2 weeks ago)
    days_match = re.match(r"(\d+)d$", date_str)
    if days_match:
        days = int(days_match.group(1))
        return (now - timedelta(days=days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    weeks_match = re.match(r"(\d+)w$", date_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return (now - timedelta(weeks=weeks)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Handle "X days ago"
    days_ago_match = re.match(r"(\d+)\s*days?\s*ago", date_str)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        return (now - timedelta(days=days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Handle "X weeks ago"
    weeks_ago_match = re.match(r"(\d+)\s*weeks?\s*ago", date_str)
    if weeks_ago_match:
        weeks = int(weeks_ago_match.group(1))
        return (now - timedelta(weeks=weeks)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Handle "last Monday", "last Friday", etc.
    weekday_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    if date_str.startswith("last "):
        day_name = date_str[5:]
        if day_name in weekday_map:
            target_weekday = weekday_map[day_name]
            days_back = (now.weekday() - target_weekday) % 7
            if days_back == 0:
                days_back = 7  # Go to previous week
            return (now - timedelta(days=days_back)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

    return None


def parse_todo_add(raw_input: str) -> ParsedTodo:
    """Parse an omnibox string for todo creation.

    Format: "Write unit tests #testing &backend !high @due:tomorrow"

    Special syntax:
        !urgent, !high, !normal, !low - Set priority
        @due:DATE - Set due date (e.g., @due:tomorrow, @due:2024-01-15, @due:+3d)

    Args:
        raw_input: Raw input string from the omnibox.

    Returns:
        ParsedTodo with extracted content, tags, project, priority, and due date.
    """
    # Extract priority (e.g., !urgent, !high, !normal, !low)
    priority_match = re.search(r"!(urgent|high|normal|low)\b", raw_input, re.IGNORECASE)
    priority: Literal["urgent", "high", "normal", "low"] = "normal"
    if priority_match:
        priority_str = priority_match.group(1).lower()
        if priority_str in ("urgent", "high", "normal", "low"):
            priority = priority_str  # type: ignore[assignment]

    # Extract due date (e.g., @due:tomorrow, @due:2024-01-15, @due:+3d)
    due_match = re.search(r"@due:(\S+)", raw_input)
    due_date: str | None = None
    if due_match:
        due_date = due_match.group(1)

    # Extract tags (words prefixed with #)
    tags: list[str] = re.findall(r"#([\w:-]+)", raw_input)

    # Extract project (text prefixed with &)
    projects: list[str] = re.findall(r"&([\w:-]+)", raw_input)

    # Clean the input: remove all special syntax
    clean_text = re.sub(
        r"!(urgent|high|normal|low)\b", "", raw_input, flags=re.IGNORECASE
    )
    clean_text = re.sub(r"@due:\S+", "", clean_text)
    clean_text = re.sub(r"#[\w:-]+", "", clean_text)
    clean_text = re.sub(r"&[\w:-]+", "", clean_text)

    # Normalize whitespace
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return ParsedTodo(
        content=clean_text,
        tags=tags,
        project=projects[0] if projects else None,
        priority=priority,
        due_date=due_date,
    )


def parse_timer(raw_input: str) -> ParsedTimer | None:
    """Parse an omnibox string for timer start command.

    Format: "#tag1 #tag2 $project 15" or just "15" for minutes
    The timer command is detected when the input contains a standalone number
    (representing minutes) along with optional tags and project.

    IMPORTANT: Date patterns (YYYY-MM-DD) are NOT timer commands.

    Args:
        raw_input: Raw input string from the omnibox.

    Returns:
        ParsedTimer with extracted minutes, tags, and project, or None if
        not a timer command.
    """
    # Skip if input contains a date pattern - those are journal entries, not timers
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", raw_input):
        return None

    # Look for a standalone number (minutes) in the input
    # It must be surrounded by whitespace or string boundaries
    minutes_match = re.search(r"(?:^|\s)(\d{1,3})(?=\s|$)", raw_input.strip())

    if not minutes_match:
        return None

    minutes = int(minutes_match.group(1))

    # Validate it's a reasonable timer duration (1-999 minutes)
    if minutes < 1 or minutes > 999:
        return None

    # Extract tags (words prefixed with #)
    tags: list[str] = re.findall(r"#([\w:-]+)", raw_input)

    # Extract project (text prefixed with &)
    projects: list[str] = re.findall(r"&([\w:-]+)", raw_input)

    # Extract content (everything except tags, projects, and the minutes number)
    clean_text = re.sub(r"#[\w:-]+", "", raw_input)
    clean_text = re.sub(r"&[\w:-]+", "", clean_text)
    clean_text = re.sub(r"(?:^|\s)\d{1,3}(?=\s|$)", " ", clean_text, count=1)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return ParsedTimer(
        minutes=minutes,
        tags=tags,
        project=projects[0] if projects else None,
        content=clean_text if clean_text else None,
    )
