"""AI Triage Schemas for dwriter.

This module defines models for bulk task management and anti-procrastination
interventions.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class BulkSnoozeIntent(BaseModel):
    """Represents the intent to bulk-update task due dates.

    Attributes:
        target_tasks: The specific subset of tasks to snooze.
        snooze_until: The new target deadline.
        reasoning: Technical justification for the snooze action.
    """

    target_tasks: Literal["all_overdue", "low_priority"]
    snooze_until: datetime
    reasoning: str = Field(description="Justification for the bulk update.")


class TaskIntervention(BaseModel):
    """Represents a strategic intervention for a stale task.

    Attributes:
        task_id: Unique identifier for the target task.
        user_friendly_callout: Observation regarding the task status.
        suggested_micro_task: A low-effort initial step for the task.
        recommend_delete: Whether deletion is advised for the task.
    """

    task_id: int
    user_friendly_callout: str = Field(description="Observation about task status.")
    suggested_micro_task: str = Field(description="Minimal initial action.")
    recommend_delete: bool = Field(False)


class TriageReview(BaseModel):
    """Represents a collection of task interventions for review.

    Attributes:
        interventions: List of suggested task interventions.
    """

    interventions: list[TaskIntervention]
