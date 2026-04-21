"""AI schemas for metadata and narrative extraction.

This module defines models for extracting structured metadata, including tags,
sentiment analysis, and productivity narratives from raw text content.
"""

from pydantic import BaseModel, Field


class TagExtraction(BaseModel):
    """Collection of tags extracted from raw text content.

    Attributes:
        tags: List of hashtags relevant to the source content.
    """

    tags: list[str] = Field(description="A list of relevant hashtags for the content.")


class BurnoutCheck(BaseModel):
    """Results of a burnout risk assessment derived from user input.

    Attributes:
        risk_score: Numerical risk assessment on a scale of 0 to 10.
        reasoning: Supporting justification for the risk score.
        recommendation: Actionable advice for mitigating identified risks.
    """

    risk_score: int = Field(ge=0, le=10)
    reasoning: str = Field(description="Explanation of the risk assessment.")
    recommendation: str = Field(description="Actionable suggestion for the user.")


class AITaskNarrative(BaseModel):
    """A conversational narrative reflecting user productivity patterns.

    Attributes:
        biggest_win: The primary accomplishment identified during the period.
        main_struggle: The primary challenge or blocker identified.
        suggested_focus: Strategic recommendation for future prioritization.
        summary: Concise wrap-up of the productivity analysis.
    """

    biggest_win: str = Field(description="The most significant achievement.")
    main_struggle: str = Field(description="The primary area of difficulty.")
    suggested_focus: str = Field(description="Recommended priority for next steps.")
    summary: str = Field(description="A brief conversational wrap-up.")


class EntryMetadata(BaseModel):
    """Structured metadata inferred from a journal entry.

    Attributes:
        implicit_mood: Single word describing emotional tone.
        life_domain: Category of the entry.
        energy_level: Inferred energy level from 1 to 10.
    """

    implicit_mood: str = Field(
        description="A single word describing the emotional tone, e.g., Stressed, Focused, Tired, Excited"  # noqa: E501
    )
    life_domain: str = Field(
        description="Categorize into: Health, Career, Social, Admin, Deep Work, or Leisure"  # noqa: E501
    )
    energy_level: int = Field(description="Inferred energy level from 1 to 10", ge=1, le=10)  # noqa: E501


class SemanticRecommendation(BaseModel):
    """Recommended project and tags based on semantic similarity to past entries.

    Attributes:
        project: Recommended project name (starting with &).
        tags: Recommended hashtags (starting with #).
    """

    project: str | None = Field(
        description="A single recommended project name, prefixed with '&'. Return null if no strong match."  # noqa: E501
    )
    tags: list[str] = Field(
        description="Up to two recommended hashtags, each prefixed with '#'."
    )


class ExtractedFact(BaseModel):
    """A durable fact or preference extracted from user input."""

    text: str = Field(description="The extracted fact statement.")
    category: str = Field(
        description="Must be one of: 'preference', 'pattern', 'goal', "
        "'constraint', 'context'"
    )


class FactBatch(BaseModel):
    """Collection of facts extracted from one or more entries."""

    facts: list[ExtractedFact] = Field(description="List of extracted facts.")
