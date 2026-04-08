"""Fuzzy search utilities using RapidFuzz.

This module provides fuzzy matching capabilities for searching
journal entries and to-do tasks.
"""

import math
from typing import Any

from rapidfuzz import fuzz, process


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculates the cosine similarity between two vectors.

    Args:
        vec1 (list[float]): The first vector.
        vec2 (list[float]): The second vector.

    Returns:
        float: The cosine similarity score (-1.0 to 1.0).
    """
    if not vec1 or not vec2:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def search_items(
    query: str,
    items: list[Any],
    limit: int = 10,
    threshold: int = 60,
) -> list[tuple[Any, float]]:
    """Search a list of Entry or Todo objects using fuzzy matching.

    Args:
        query: The search query string.
        items: List of Entry or Todo objects to search.
        limit: Maximum number of results to return.
        threshold: Minimum score cutoff (0-100).

    Returns:
        List of tuples containing (item, score) sorted by score descending.
    """
    if not items:
        return []

    # Build searchable text for each item
    choices = {}
    for item in items:
        tag_text = " ".join(item.tag_names)
        project_text = item.project or ""
        searchable_text = f"{item.content} {tag_text} {project_text}"
        choices[item.id] = searchable_text

    # Extract top results using WRatio for partial matches
    results = process.extract(
        query,
        choices,
        scorer=fuzz.WRatio,
        limit=limit,
        score_cutoff=threshold,
    )

    # Map back to original objects
    # RapidFuzz 3.x returns (choice_value, score, metadata) tuples
    matched_items = []
    for _, score, item_id in results:
        original_item = next(i for i in items if i.id == item_id)
        matched_items.append((original_item, score))

    return matched_items


def find_best_match(
    query: str,
    items: list[Any],
    threshold: int = 75,
) -> tuple[Any, float] | None:
    """Find the single best matching item for a query.

    Args:
        query: The search query string.
        items: List of Entry or Todo objects to search.
        threshold: Minimum score cutoff (0-100).

    Returns:
        Tuple of (item, score) for the best match, or None if no match found.
    """
    results = search_items(query, items, limit=1, threshold=threshold)
    return results[0] if results else None


def find_multiple_matches(
    query: str,
    items: list[Any],
    limit: int = 5,
    threshold: int = 60,
) -> list[tuple[Any, float]]:
    """Find multiple matching items for interactive selection.

    Args:
        query: The search query string.
        items: List of Entry or Todo objects to search.
        limit: Maximum number of results to return.
        threshold: Minimum score cutoff (0-100).

    Returns:
        List of tuples containing (item, score) sorted by score descending.
    """
    return search_items(query, items, limit=limit, threshold=threshold)
