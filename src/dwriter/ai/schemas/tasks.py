"""AI Task Management Schemas for dwriter.

This module defines models for capturing task-related intents, including
single tasks, log entries, and project decompositions.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class AddTodoIntent(BaseModel):
    """Represents the intent to add a single task.

    Attributes:
        content: The core description of the task.
        priority: The urgency level of the task.
        project: Optional associated project name.
        tags: List of associated hashtags.
        due_date: Optional deadline for the task.
    """

    content: str = Field(description="Task description.")
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    project: str | None = Field(None, description="Project name.")
    tags: list[str] = Field(default_factory=list, description="Associated tags.")
    due_date: datetime | None = Field(None, description="Task deadline.")


class LogEntryIntent(BaseModel):
    """Represents the intent to record a journal entry.

    Attributes:
        content: The text content of the entry.
        project: Optional associated project name.
        tags: List of associated hashtags.
        created_at: Optional timestamp for the entry.
    """

    content: str = Field(description="Journal entry content.")
    project: str | None = Field(None, description="Project name.")
    tags: list[str] = Field(default_factory=list, description="Associated tags.")
    created_at: datetime | None = Field(None, description="Entry timestamp.")


class SubTask(BaseModel):
    """Represents a granular task within a project breakdown.

    Attributes:
        content: Description of the sub-task.
        priority: Task urgency level.
        estimated_days_out: Estimated lead time until the task is due.
    """

    content: str
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    estimated_days_out: int = Field(0, description="Estimated days until due.")


class ProjectBreakdownIntent(BaseModel):
    """Represents the intent to decompose a request into multiple tasks.

    Attributes:
        project_name: The overarching project name for all sub-tasks.
        tasks: List of sub-tasks to be added.
    """

    project_name: str = Field(description="The project name.")
    tasks: list[SubTask] = Field(description="List of constituent sub-tasks.")
