"""Core AI schemas for structured intent representation.

This module defines the foundational Pydantic models used to represent
structured user intents and parameters extracted from natural language.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class UserIntent(BaseModel):
    """Unified intent model for representing AI-driven actions and parameters.

    Attributes:
        action: The specific operation to execute (e.g., 'add_todo', 'query').
        content: The primary text content associated with the intent.
        priority: The urgency level for task-related intents.
        project: Optional identifier for project association.
        tags: List of associated hashtags for categorization.
        due_date: Optional deadline for tasks.
        target: The data domain for query operations (e.g., 'entries', 'todos').
        date_range_start: Beginning of the temporal filter.
        date_range_end: End of the temporal filter.
        status: Filter for task completion state.
        summarize: If True, returns a condensed summary of results.
    """

    action: str
    content: str | None = None
    priority: str = "normal"
    project: str | None = None
    tags: list[str] = Field(default_factory=list)
    due_date: datetime | None = None

    target: str | None = None
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    status: str | None = None
    summarize: bool = Field(default=False)
