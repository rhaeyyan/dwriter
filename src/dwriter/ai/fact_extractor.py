"""Fact extraction module for the Closed Learning Loop."""

import uuid
from typing import Any

from dwriter.ai.schemas.extraction import ExtractedFact, FactBatch
from dwriter.config import AIConfig
from dwriter.graph.projector import GraphProjector


def extract_facts(entries: list[Any], config: AIConfig) -> list[ExtractedFact]:
    """Extracts durable facts from journal entries.

    Args:
        entries: List of Entry objects.
        config: AI configuration.

    Returns:
        List of ExtractedFact objects.
    """
    from dwriter.ai.engine import get_ai_client

    if not entries:
        return []

    client = get_ai_client(config)

    context_parts = []
    for entry in entries:
        context_parts.append(f"Entry ID {entry.uuid}: {entry.content}")

    context_str = "\n\n".join(context_parts)

    system_msg = (
        "You are an analytical extractor for a 2nd-Brain system. "
        "Extract only durable, reusable facts (preferences, recurring patterns, "
        "stated goals, hard constraints, and contextual background). "
        "Explicitly exclude transient state like today's mood or one-off events. "
        "Return the facts according to the schema."
    )

    user_msg = f"### ENTRIES:\n{context_str}"

    try:
        batch = client.chat.completions.create(
            model=config.daemon_model,
            response_model=FactBatch,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        return batch.facts  # type: ignore[no-any-return]
    except Exception:
        return []


def project_extracted_facts(
    facts: list[ExtractedFact], source_entry_uuid: str, projector: GraphProjector
) -> None:
    """Projects a list of facts into the LadybugDB graph index.

    Args:
        facts: List of facts to project.
        source_entry_uuid: The UUID of the entry these facts came from.
        projector: The GraphProjector instance.
    """
    from datetime import datetime

    extracted_at = datetime.now().isoformat()

    for fact in facts:
        fact_uuid = str(uuid.uuid4())
        projector.project_fact(
            uuid=fact_uuid,
            text=fact.text,
            category=fact.category,
            extracted_at=extracted_at,
            source_entry_uuid=source_entry_uuid,
        )
