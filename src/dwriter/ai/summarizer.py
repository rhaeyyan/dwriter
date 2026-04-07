"""Summarization engine for long-term activity archival.

This module processes weekly activity into structured summaries using the
Instructor framework and a local or remote AI model. These summaries facilitate
efficient historical retrieval and context restoration in the TUI.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..config import AIConfig
    from ..database import Database


class WeeklySummary(BaseModel):
    """Structured weekly retrospective data for persistent storage.

    Attributes:
        biggest_wins: Major accomplishments or completed tasks.
        friction_points: Recurring blockers or areas of struggle.
        dominant_mood: Single-word sentiment analysis of the week's entries.
        velocity: Descriptive summary of task throughput.
        key_projects: Projects that received significant attention.
        key_tags: Frequently used tags during the period.
    """

    biggest_wins: list[str] = Field(
        description="Top 3 accomplishments or completed tasks this week."
    )
    friction_points: list[str] = Field(
        description="Top 3 recurring blockers, abandoned tasks, or areas of struggle."
    )
    dominant_mood: str = Field(
        description="Sentiment summary (e.g., 'Focused', 'Scattered', 'Energized')."
    )
    velocity: str = Field(
        description="Summary of task throughput for the week."
    )
    key_projects: list[str] = Field(
        description="Project names with the highest activity."
    )
    key_tags: list[str] = Field(
        description="Most frequent tags used during the week."
    )


# Maximum character count threshold for triggering recursive chunked summarization
_TOKEN_CHUNK_THRESHOLD = 20_000


def get_week_bounds(
    reference: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Calculates the start and end boundaries for a specific week.

    The window extends from Monday at 00:00:00 to Sunday at 23:59:59. If no
    reference date is provided, the function defaults to the most recently
    completed Monday-Sunday cycle.

    Args:
        reference: A date within the target week. Defaults to None.

    Returns:
        A tuple containing the start and end datetime objects for the week.
    """
    if reference is None:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
    else:
        ref = reference.replace(hour=0, minute=0, second=0, microsecond=0)
        days_since_monday = ref.weekday()
        last_monday = ref - timedelta(days=days_since_monday)

    period_start = last_monday
    period_end = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return period_start, period_end


def _build_raw_text(db: Database, start: datetime, end: datetime) -> str:
    """Aggregates journal entries and tasks within a date range into a text block.

    Args:
        db: Database instance for data retrieval.
        start: The beginning of the target period.
        end: The end of the target period.

    Returns:
        A formatted string containing consolidated activity data.
    """
    entries = db.get_entries_in_range(start, end)
    todos = db.get_all_todos()
    week_todos = [t for t in todos if start <= t.created_at <= end]

    lines: list[str] = []
    lines.append("=== JOURNAL ENTRIES ===")
    for e in entries:
        tags = ", ".join(f"#{t}" for t in e.tag_names)
        project = f" &{e.project}" if e.project else ""
        lines.append(
            f"[{e.created_at.strftime('%Y-%m-%d %H:%M')}]{project} {e.content} {tags}"
        )

    lines.append("\n=== TASKS ===")
    for t in week_todos:
        status = "DONE" if t.status == "completed" else "PENDING"
        project = f" &{t.project}" if t.project else ""
        lines.append(f"[{status}][{t.priority.upper()}]{project} {t.content}")

    return "\n".join(lines)


def _summarize_text(
    raw_text: str, config: AIConfig
) -> WeeklySummary:
    """Executes a structured summarization pass on the provided text.

    Args:
        raw_text: The activity data to be summarized.
        config: AI configuration settings.

    Returns:
        A structured WeeklySummary object.
    """
    from ..ai.engine import get_ai_client, get_system_prompt

    client = get_ai_client(config)
    system = get_system_prompt(
        "Summarize the user's weekly activity into a data-driven "
        "structured retrospective. Use & for projects and # for tags."
    )

    return client.chat.completions.create(
        model=config.model,
        response_model=WeeklySummary,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": raw_text},
        ],
        max_retries=2,
    )


def compress_week(
    db: Database,
    config: AIConfig,
    period_start: datetime,
    period_end: datetime,
) -> WeeklySummary:
    """Generates and persists a structured weekly activity summary.

    If the raw activity data exceeds the character threshold, the function
    employs a recursive chunking strategy: splitting the period, summarizing
    each half, and merging the results in a final refinement pass.

    Args:
        db: Database instance.
        config: AI configuration.
        period_start: Start of the target week.
        period_end: End of the target week.

    Returns:
        The completed WeeklySummary object.
    """
    raw_text = _build_raw_text(db, period_start, period_end)

    if len(raw_text) > _TOKEN_CHUNK_THRESHOLD:
        midpoint = period_start + timedelta(days=3, hours=23, minutes=59, seconds=59)
        first_half = _build_raw_text(db, period_start, midpoint)
        second_half = _build_raw_text(
            db, midpoint + timedelta(seconds=1), period_end
        )

        summary_a = _summarize_text(first_half, config)
        summary_b = _summarize_text(second_half, config)

        merge_text = (
            "Consolidate these two partial summaries into a unified weekly retrospective.\n\n"
            f"PART 1 (Mon-Wed):\n{summary_a.model_dump_json()}\n\n"
            f"PART 2 (Thu-Sun):\n{summary_b.model_dump_json()}"
        )
        summary = _summarize_text(merge_text, config)
    else:
        summary = _summarize_text(raw_text, config)

    db.add_summary(
        content=summary.model_dump_json(),
        period_start=period_start,
        period_end=period_end,
        summary_type="weekly",
    )

    return summary
