"""Graph-backed search functions for journal entries and todos."""

from __future__ import annotations

from typing import Any

from .projector import GraphProjector


def search_graph_journal(
    query: str,
    projector: GraphProjector,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """FTS search over Entry nodes in the graph index."""
    return projector.search_fts(query, "Entry", "entry_fts_idx", limit)


def search_graph_todos(
    query: str,
    projector: GraphProjector,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """FTS search over Todo nodes in the graph index."""
    return projector.search_fts(query, "Todo", "todo_fts_idx", limit)
