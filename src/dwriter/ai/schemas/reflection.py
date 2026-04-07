"""AI schemas for reflection and context restoration.

This module defines models for generating personalized journaling prompts
and providing automated workflow context restoration.
"""

from pydantic import BaseModel, Field


class ReflectionPrompt(BaseModel):
    """Structured representation of a personalized journaling prompt.

    Attributes:
        prompt_text: The primary question or prompt text for the user.
        recurring_themes: Key themes identified from recent activity.
    """

    prompt_text: str = Field(description="The journaling question for the user.")
    recurring_themes: list[str] = Field(
        description="Identified themes from recent activity."
    )


class ContextRestore(BaseModel):
    """Summary of user activity to facilitate workflow resumption.

    Attributes:
        summary_of_last_known_state: A concise summary of the user's recent actions.
        urgent_pending_items: High-priority tasks requiring immediate attention.
    """

    summary_of_last_known_state: str = Field(
        description="Summary of the user's previous state."
    )
    urgent_pending_items: list[str] = Field(
        description="High-priority tasks for immediate focus."
    )
