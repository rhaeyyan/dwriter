"""Unified color schema for dwriter TUI.

This module provides consistent color definitions used across all TUI components
for a cohesive visual experience.

Color Scheme:
    - Due dates: Yellow (today/tomorrow), Red (overdue), Cyan (future)
    - Tags: Yellow (#tag format)
    - Projects: Magenta/Fuchsia (→ project format)
    - Priority: Red (urgent), Yellow (high), White (normal), Dim (low)
    - Entries/Todos: Green (active content), Dim (completed)
    - Status: Green (running), Yellow (paused), Accent (finished)
"""

from __future__ import annotations

# Due date colors
DUE_TODAY = "bold yellow"
DUE_TOMORROW = "yellow"
DUE_OVERDUE = "red"
DUE_SOON = "cyan"  # Within 30 days
DUE_LATER = "dim cyan"  # More than 30 days
DUE_NONE = "dim"  # No due date

# Tag colors
TAG = "yellow"

# Project colors
PROJECT = "#ff00ff"  # Magenta/fuchsia

# Priority colors
PRIORITY_URGENT = "red"
PRIORITY_HIGH = "yellow"
PRIORITY_NORMAL = "white"
PRIORITY_LOW = "dim"

# Content colors
CONTENT_ACTIVE = "#00ff00"  # Bright green for active items
CONTENT_COMPLETED = "dim"  # Dimmed for completed items

# Status colors
STATUS_RUNNING = "green"
STATUS_PAUSED = "warning"  # Yellow/orange
STATUS_FINISHED = "accent"

# Progress bar gradient (green → yellow → orange → red)
PROGRESS_COLORS = [
    "#00ff00",  # Green (0-25%)
    "#7fff00",  # Green-yellow (25-50%)
    "#ffff00",  # Yellow (50-75%)
    "#ffa500",  # Orange (75-85%)
    "#ff0000",  # Red (85-100%)
]

# UI element colors
UI_BORDER = "$primary"
UI_BORDER_FOCUS = "$accent"
UI_PANEL = "$panel"
UI_SURFACE = "$surface"
UI_TEXT = "$foreground"
UI_TEXT_MUTED = "$text-muted"
UI_SUCCESS = "$success"
UI_WARNING = "$warning"
UI_ERROR = "$error"
UI_INFO = "$info"


def get_priority_color(priority: str) -> str:
    """Get the color for a priority level.

    Args:
        priority: Priority string (urgent, high, normal, low).

    Returns:
        Color string.
    """
    colors = {
        "urgent": PRIORITY_URGENT,
        "high": PRIORITY_HIGH,
        "normal": PRIORITY_NORMAL,
        "low": PRIORITY_LOW,
    }
    return colors.get(priority, PRIORITY_NORMAL)


def get_due_date_style(days_until: int) -> tuple[str, str]:
    """Get the style for a due date based on days until due.

    Args:
        days_until: Number of days until due (negative if overdue).

    Returns:
        Tuple of (style, label) for formatting.
    """
    if days_until == 0:
        return DUE_TODAY, "TODAY"
    elif days_until == 1:
        return DUE_TOMORROW, "TOMORROW"
    elif days_until < 0:
        return DUE_OVERDUE, f"{days_until}d"
    elif days_until <= 30:
        return DUE_SOON, f"{days_until}d"
    else:
        months = days_until // 30
        return DUE_LATER, f"{months}m"


def get_progress_color(progress: float) -> str:
    """Get the color for a progress percentage.

    Args:
        progress: Progress from 0.0 (start) to 1.0 (complete).

    Returns:
        Hex color string.
    """
    if progress < 0.25:
        return PROGRESS_COLORS[0]
    elif progress < 0.5:
        return PROGRESS_COLORS[1]
    elif progress < 0.75:
        return PROGRESS_COLORS[2]
    elif progress < 0.85:
        return PROGRESS_COLORS[3]
    else:
        return PROGRESS_COLORS[4]


def format_due_date_display(days_until: int) -> str:
    """Format a due date for display with appropriate styling.

    Args:
        days_until: Number of days until due (negative if overdue).

    Returns:
        Formatted string with markup.
    """
    style, label = get_due_date_style(days_until)
    return f"[{style}]{label}[/{style}]"
