"""Graph-backed search functions for journal entries and todos."""

from __future__ import annotations

from typing import Any

from ..search_utils import rrf_fuse
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


def search_graph_facts(
    query: str,
    projector: GraphProjector,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """FTS search over Fact nodes in the graph index."""
    return projector.search_facts_fts(query, limit)


def hybrid_search_entries(
    query: str,
    query_embedding: list[float],
    projector: GraphProjector,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Hybrid search over Entry nodes fusing FTS and ANN vector results via RRF.

    Returns up to `limit` entries ranked by combined relevance. Entries without
    embeddings can still appear via FTS; entries without FTS hits can appear via
    vector similarity.
    """
    fts_rows = projector.search_fts(query, "Entry", "entry_fts_idx", limit)
    vec_rows = projector.search_vector(query_embedding, limit)

    fts_ids = [r["uuid"] for r in fts_rows]
    vec_ids = [r["uuid"] for r in vec_rows]
    fused_ids = rrf_fuse([fts_ids, vec_ids])[:limit]

    # FTS rows carry a `score`, vector rows carry a `distance` — the two are not
    # comparable, so we drop both and expose the fused `rank` (1 = best) as the
    # single relevance signal. This keeps every returned row on one schema.
    by_uuid: dict[str, dict[str, Any]] = {}
    for row in fts_rows + vec_rows:
        by_uuid.setdefault(row["uuid"], row)

    fused: list[dict[str, Any]] = []
    for rank, uid in enumerate(fused_ids, start=1):
        hit = by_uuid.get(uid)
        if hit is None:
            continue
        fused.append(
            {
                "uuid": uid,
                "content": hit.get("content", ""),
                "project": hit.get("project", ""),
                "rank": rank,
            }
        )
    return fused
