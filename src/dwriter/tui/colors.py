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

from rich.text import Text

# Due date colors
DUE_TODAY = "bold #fab387"
DUE_TOMORROW = "#fab387"
DUE_OVERDUE = "red"
DUE_SOON = "cyan"  # Within 30 days
DUE_LATER = "dim cyan"  # More than 30 days
DUE_NONE = "dim"  # No due date

# Tag colors
TAG = "bold #e5ff00"  # Neon yellow

# Project colors
PROJECT = "bold #ff00ff"  # Magenta/fuchsia

# Priority colors
PRIORITY_URGENT = "red"
PRIORITY_HIGH = "yellow"
PRIORITY_NORMAL = "white"
PRIORITY_LOW = "dim"

# Content colors
CONTENT_ACTIVE = "#00e5ff"  # Bright cyan for active items
CONTENT_COMPLETED = "dim"  # Dimmed for completed items

# Status colors
STATUS_RUNNING = "green"
STATUS_PAUSED = "warning"  # Yellow/orange
STATUS_FINISHED = "accent"

# Border colors (btop-style: muted borders, bright data)
BORDER_MUTED = "#45475a"  # Dim border for panels at rest
BORDER_ACTIVE = "#00e5ff"  # Accent border for focused panels
PANEL_HEADER = "#00e5ff"  # Section header color inside panels

# Block bar gradient (8-step smooth for ▏▎▍▌▋▊▉█ bars)
BLOCK_GRADIENT = [
    "#00e5ff",  # Cyan
    "#00ffcc",  # Teal-cyan
    "#39ff14",  # Neon green
    "#ccff00",  # Neon green-yellow
    "#e5ff00",  # Neon yellow
    "#ffea00",  # Bright yellow
    "#ff7b00",  # Neon orange
    "#ff003c",  # Neon red
]

# Progress bar gradient (green → yellow → orange → red)
PROGRESS_COLORS = [
    "#00e5ff",  # Cyan (0-25%)
    "#ccff00",  # Neon green-yellow (25-40%)
    "#ffea00",  # Yellow (40-60%)
    "#ff7b00",  # Orange (60-75%)
    "#ff003c",  # Red (75-100%)
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

# Block characters for progress bars (btop-style sub-cell resolution)
_BLOCK_CHARS = " ▏▎▍▌▋▊▉█"

# Icon Mapping for consistency and fallback support
_ICONS = {
    "dashboard": ("🏠", "D"),
    "logs": ("📓", "L"),
    "todo": ("📋", "T"),
    "timer": ("⏱️", "M"),
    "history": ("📅", "H"),
    "glance": ("✨", "G"),
    "streak": ("🔥", "S"),
    "context": ("🔄", "C"),
    "friction": ("⚙️", "F"),
    "workload": ("⚡", "W"),
    "check": ("✅", "v"),
    "check_small": ("✓", "v"),
    "plus": ("➕", "+"),
    "warning": ("⚠️", "!"),
    "edit": ("✏️", "E"),
    "search": ("🔍", "Q"),
    "clock": ("🕒", "C"),
    "save": ("💾", "S"),
    "export": ("📤", "X"),
    "markdown": ("📄", "M"),
    "csv": ("📊", "C"),
    "json": ("📦", "J"),
    "standup": ("🎤", "S"),
    "question": ("❓", "?"),
    "tips": ("💡", "i"),
    "bullet": ("•", "*"),
    "navigation": ("🧭", "N"),
    "overview": ("📖", "O"),
    "shortcuts": ("⌨️", "K"),
    "clear": ("↺", "R"),
    "pause": ("⏸", "P"),
    "play": ("▶", ">"),
    "arrow_left": ("←", "<"),
    "arrow_right": ("→", ">"),
    "tag": ("🏷️", "#"),
    "folder": ("📁", "/"),
    "note": ("📝", "N"),
    "configure": ("⚙️", "C"),
}


def get_icon(name: str, use_emojis: bool = True) -> str:
    """Get an icon string with optional emoji fallback.

    Args:
        name: Name of the icon to retrieve.
        use_emojis: Whether to return the emoji or ASCII fallback.

    Returns:
        The requested icon string.
    """
    icon_tuple = _ICONS.get(name, ("", ""))
    return icon_tuple[0] if use_emojis else icon_tuple[1]


def render_block_bar(
    value: float,
    max_val: float,
    width: int = 20,
    color: str | None = None,
    gradient: bool = True,
    use_emojis: bool = True,
) -> str:
    """Render a btop-style block-character progress bar with gradient.

    Uses sub-cell resolution characters ▏▎▍▌▋▊▉█ for smooth fill,
    with optional gradient coloring from green → red.

    Args:
        value: Current value.
        max_val: Maximum value for normalization.
        width: Bar width in characters.
        color: Single color override (disables gradient).
        gradient: Whether to use gradient coloring.
        use_emojis: Whether to use Unicode block characters or ASCII.

    Returns:
        Rich markup string for the progress bar.
    """
    empty_char = "─" if use_emojis else "-"
    if max_val <= 0:
        return f"[#313244]{empty_char * width}[/]"

    ratio = min(value / max_val, 1.0)
    fill_exact = ratio * width
    full_blocks = int(fill_exact)
    fractional = fill_exact - full_blocks
    frac_index = int(fractional * 8)
    empty = width - full_blocks - (1 if frac_index > 0 else 0)

    # Pick color based on ratio
    if color:
        bar_color = color
    elif gradient:
        # Map ratio to gradient
        idx = min(int(ratio * (len(PROGRESS_COLORS) - 1)), len(PROGRESS_COLORS) - 1)
        bar_color = PROGRESS_COLORS[idx]
    else:
        bar_color = "#a6e3a1"

    parts = []
    if full_blocks > 0:
        parts.append(f"[{bar_color}]{'█' * full_blocks if use_emojis else '#' * full_blocks}[/]")
    if frac_index > 0 and use_emojis:
        parts.append(f"[{bar_color}]{_BLOCK_CHARS[frac_index]}[/]")
    elif frac_index > 0:
        parts.append(f"[{bar_color}]#[/]")

    if empty > 0:
        parts.append(f"[#313244]{empty_char * empty}[/]")

    return "".join(parts)


def render_block_bar_rich(
    value: float,
    max_val: float,
    width: int = 20,
    color: str | None = None,
    gradient: bool = True,
    use_emojis: bool = True,
) -> Text:
    """Render a btop-style block bar as a Rich Text object.

    Same as render_block_bar but returns a Rich Text object for use
    in Static widget updates.

    Args:
        value: Current value.
        max_val: Maximum value for normalization.
        width: Bar width in characters.
        color: Single color override.
        gradient: Whether to use gradient coloring.
        use_emojis: Whether to use Unicode block characters or ASCII.

    Returns:
        Rich Text object with styled progress bar.
    """
    empty_char = "─" if use_emojis else "-"
    if max_val <= 0:
        text = Text()
        text.append(empty_char * width, style="#313244")
        return text

    ratio = min(value / max_val, 1.0)
    fill_exact = ratio * width
    full_blocks = int(fill_exact)
    fractional = fill_exact - full_blocks
    frac_index = int(fractional * 8)
    empty = width - full_blocks - (1 if frac_index > 0 else 0)

    if color:
        bar_color = color
    elif gradient:
        idx = min(int(ratio * (len(PROGRESS_COLORS) - 1)), len(PROGRESS_COLORS) - 1)
        bar_color = PROGRESS_COLORS[idx]
    else:
        bar_color = "#a6e3a1"

    text = Text()
    if full_blocks > 0:
        text.append("█" * full_blocks if use_emojis else "#" * full_blocks, style=bar_color)
    if frac_index > 0 and use_emojis:
        text.append(_BLOCK_CHARS[frac_index], style=bar_color)
    elif frac_index > 0:
        text.append("#", style=bar_color)

    if empty > 0:
        text.append(empty_char * empty, style="#313244")

    return text


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
