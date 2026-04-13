"""Proactive AI logic for background processing of entries."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext
    from ..database import Entry

import instructor
import openai

from .engine import get_embedding, get_semantic_recommendation
from .permissions import PermissionEnforcer, permission_mode_from_str


def process_proactive_tagging(ctx: AppContext, entry: Entry) -> None:
    """Runs the proactive AI pipeline for a new entry with graceful degradation."""
    if not ctx.config.ai.enabled:
        return

    # Update app state if running in TUI
    app = getattr(ctx, "app", None)
    if app:
        app.is_processing = True

    try:
        # 1. Generate embedding if missing
        if not entry.embedding:
            try:
                embedding = get_embedding(entry.content, ctx.config.ai)
                ctx.db.update_entry(entry.id, embedding=embedding)
            except (openai.APITimeoutError, openai.APIConnectionError):
                logging.warning("Ollama timeout/connection error during embedding generation.")  # noqa: E501
                return
        else:
            import json
            embedding = json.loads(entry.embedding.decode("utf-8"))

        # 2. Search for similar entries
        similar_entries = ctx.db.search_similar_entries(embedding, limit=5)
        similar_entries = [e for e in similar_entries if e.id != entry.id]

        if not similar_entries:
            return

        # 3. Generate recommendations
        if len(entry.content) < 10:
            return

        enforcer = PermissionEnforcer(
            mode=permission_mode_from_str(ctx.config.ai.features.permission_mode)
        )
        permission = enforcer.check("proactive_tagging")
        if not permission.allowed:
            logging.warning("Proactive tagging blocked by Security Mode: %s", permission.reason)  # noqa: E501
            return

        try:
            recommendation = get_semantic_recommendation(
                entry.content, similar_entries, ctx.config.ai
            )
        except (instructor.InstructorRetryException, openai.APITimeoutError):  # type: ignore[attr-defined]
            logging.warning("AI recommendation failed due to validation or timeout.")
            return

        if not recommendation or (not recommendation.project and not recommendation.tags):  # noqa: E501
            return

        # 4. Trigger TUI notification
        _trigger_tui_recommendation(ctx, entry, recommendation)

    except Exception as e:
        logging.error(f"Proactive AI unexpected error: {e}")
    finally:
        if app:
            app.is_processing = False


def _trigger_tui_recommendation(ctx: AppContext, entry: Entry, recommendation: Any) -> None:  # noqa: E501
    """Helper to signal the TUI about a new recommendation."""
    # This will be implemented by the TUI Architect.
    # For now, we'll post a message if we can find the app.
    import sys
    # A bit hacky but works for reaching the Textual App from a background thread
    # if it was started in the same process.
    for module in sys.modules.values():
        if hasattr(module, "DWriterApp"):
            # This is not quite right, we need the INSTANCE.
            pass

    # Better: AppContext could store a reference to the app.
    if hasattr(ctx, "app") and ctx.app:
        from .messages import SemanticRecommendationReady
        ctx.app.post_message(SemanticRecommendationReady(
            entry_id=entry.id,
            project=recommendation.project,
            tags=recommendation.tags
        ))
