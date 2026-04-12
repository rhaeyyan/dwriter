"""Headless standup data assembly and formatting service.

This module is AI-free and branch-portable. It owns the shared logic for
fetching standup data from the database and rendering it in various output
formats. Both the CLI command and future consumers should call this service
rather than duplicating the fetch/format logic.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..database import Database

from ..tui.colors import PROJECT, TAG

# ---------------------------------------------------------------------------
# Format functions
# ---------------------------------------------------------------------------

def format_standup_bullets(entries: Any) -> str:
    """Format entries as bullet points."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] - {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'[{TAG}]#[/]{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_slack(entries: Any) -> str:
    """Format entries for Slack."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] • {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_jira(entries: Any) -> str:
    """Format entries for Jira."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] * {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_markdown(entries: Any) -> str:
    """Format entries as Markdown."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] - {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_todos(todos: Any, output_format: str) -> str:
    """Format pending todos based on the selected output format."""
    lines = []
    for todo in todos:
        if output_format == "slack":
            bullet = "•"
        elif output_format == "jira":
            bullet = "*"
        elif output_format == "markdown":
            bullet = "- [ ]"
        else:
            bullet = "-"

        line = f"{bullet} {todo.content}"

        if todo.tag_names:
            if output_format == "bullets":
                tags_list = ", ".join(f"[{TAG}]#{tag}[/{TAG}]" for tag in todo.tag_names)
            else:
                tags_list = ", ".join(f"#{tag}" for tag in todo.tag_names)
            line += f" ({tags_list})"

        if todo.project:
            if output_format in ["bullets", "markdown"]:
                line += f" [{PROJECT}]&{todo.project}[/{PROJECT}]"
            else:
                line += f" &{todo.project}"

        lines.append(line)
    return "\n".join(lines)


FORMATTERS = {
    "bullets": format_standup_bullets,
    "slack": format_standup_slack,
    "jira": format_standup_jira,
    "markdown": format_standup_markdown,
}


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------

def fetch_standup_data(
    db: Database,
    date: datetime,
    with_todos: bool = False,
) -> tuple[list[Any], list[Any]]:
    """Fetch standup entries and optionally pending todos for a given date.

    Args:
        db: Database instance.
        date: The target date (typically yesterday).
        with_todos: Whether to also fetch pending todos.

    Returns:
        A tuple of (entries, pending_todos). ``pending_todos`` is empty when
        ``with_todos`` is False.
    """
    entries = db.get_entries_by_date(date)
    pending_todos = db.get_todos(status="pending") if with_todos else []
    return entries, pending_todos


def build_standup_text(
    entries: list[Any],
    pending_todos: list[Any],
    output_format: str,
    date: datetime,
    with_todos: bool = False,
    with_weekly: bool = False,
    db: Database | None = None,
) -> str:
    """Assemble the full standup output string.

    Args:
        entries: Journal entries for the standup date.
        pending_todos: Pending todo tasks (used when ``with_todos`` is True).
        output_format: One of 'bullets', 'slack', 'jira', 'markdown'.
        date: The standup date (used for the header).
        with_todos: Append a 'Plan for Today' section.
        with_weekly: Append a 7-day Analytical Engine wrap-up.
        db: Database instance (required when ``with_weekly`` is True).

    Returns:
        The formatted standup string, ready for clipboard or display.
    """
    formatter = FORMATTERS.get(output_format, format_standup_bullets)
    standup_text = formatter(entries) if entries else ""

    header = f"Yesterday's Standup ({date.strftime('%Y-%m-%d')})"
    output = f"{header}\n{standup_text}" if standup_text else header

    if with_todos:
        if pending_todos:
            todo_header = "\n\nPlan for Today:"
            if output_format in ["slack", "jira"]:
                todo_header = f"\n\n*{todo_header.strip()}*"
            elif output_format == "markdown":
                todo_header = f"\n\n### {todo_header.strip()}"
            output += f"{todo_header}\n{format_todos(pending_todos, output_format)}"
        else:
            output += "\n\nPlan for Today:\n(No pending tasks)"

    if with_weekly:
        from ..analytics import AnalyticsEngine, InsightGenerator

        assert db is not None, "db is required when with_weekly=True"
        engine = AnalyticsEngine(db)
        insight_gen = InsightGenerator(engine)
        wrapup = insight_gen.generate_weekly_wrapup()

        wrapup_header = "\n\n7-Day Weekly Pulse:"
        if output_format in ["slack", "jira"]:
            wrapup_header = f"\n\n*{wrapup_header.strip()}*"
        elif output_format == "markdown":
            wrapup_header = f"\n\n### {wrapup_header.strip()}"

        clean_wrapup = ["- " + re.sub(r"\[.*?\]", "", n) for n in wrapup]
        output += f"{wrapup_header}\n" + "\n".join(clean_wrapup)

    return output
