"""Embedding generation and hybrid semantic search for the 2nd-Brain.

Extracted from ``engine.py`` to keep that module under the architectural
600-line ceiling (FRAMEWORK File-Size Ceiling Guard). This module owns the
embedding endpoint and the ``search_semantic`` agentic tool implementation.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from openai import OpenAI

from dwriter.config import AIConfig

if TYPE_CHECKING:
    from dwriter.graph import GraphProjector


def get_embedding(text: str, config: AIConfig) -> list[float]:
    """Generates a vector embedding for the given text using the Ollama API.

    Args:
        text (str): The source text to embed.
        config (AIConfig): The AI configuration settings.

    Returns:
        list[float]: The generated embedding vector.
    """
    client = OpenAI(base_url=config.base_url, api_key="ollama")
    response = client.embeddings.create(model="nomic-embed-text", input=text)
    return response.data[0].embedding


def search_semantic(
    query: str,
    config: AIConfig,
    projector: GraphProjector | None = None,
) -> str:
    """Hybrid semantic + FTS search over journal entries.

    Generates a query embedding, then fuses ANN vector results with FTS results
    via Reciprocal Rank Fusion. Returns entries that are conceptually related to
    the query even when exact keywords don't match.

    Args:
        query (str): Natural language search query.
        config (AIConfig): AI configuration (needed for embedding endpoint).
        projector (GraphProjector | None): Reuse an open graph connection when
            provided; otherwise a short-lived projector is opened for this call.

    Returns:
        str: JSON array of matching entries, or an error message.
    """
    try:
        from dwriter.graph import GraphProjector, hybrid_search_entries

        embedding = get_embedding(query, config)
        if projector is None:
            projector = GraphProjector()
        results = hybrid_search_entries(query, embedding, projector)
        if not results:
            return "No semantically matching entries found."
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"Error in semantic search: {e}"
