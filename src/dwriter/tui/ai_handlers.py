"""AI recommendation event handlers mixin for DWriterApp."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .messages import EntryAdded, SemanticRecommendationReady
from .widgets.omnibox import Omnibox

if TYPE_CHECKING:
    pass


class AIHandlersMixin:
    """Mixin providing AI recommendation handling methods for DWriterApp."""

    def on_semantic_recommendation_ready(self, message: SemanticRecommendationReady) -> None:
        """Handle proactive AI recommendations."""
        self.pending_recommendation = message  # type: ignore[attr-defined]

        parts = []
        if message.project:
            parts.append(f"&{message.project}")
        if message.tags:
            parts.extend([f"#{t}" for t in message.tags])

        suggested = " ".join(parts)

        # Update Omnibox ghost text
        try:
            omnibox = self.query_one("#quick-add", Omnibox)  # type: ignore[attr-defined]
            omnibox.ghost_text = suggested
        except Exception:
            pass

        self.notify(  # type: ignore[attr-defined]
            f"AI Suggests: {suggested}. Press [Tab] to accept tokens or [Ctrl+A] for all.",
            title="✨ Smart Suggestion",
            severity="information",
            timeout=10
        )

    def action_apply_recommendation(self) -> None:
        """Apply the pending AI recommendation."""
        if not self.pending_recommendation:  # type: ignore[attr-defined]
            self.notify("No pending recommendations.")  # type: ignore[attr-defined]
            return

        message = self.pending_recommendation  # type: ignore[attr-defined]
        self.pending_recommendation = None  # type: ignore[attr-defined]

        # Clear ghost text
        try:
            omnibox = self.query_one("#quick-add", Omnibox)  # type: ignore[attr-defined]
            omnibox.ghost_text = ""
        except Exception:
            pass

        async def apply_worker() -> None:
            try:
                # Get existing entry to merge tags
                entry = self.ctx.db.get_entry(message.entry_id)  # type: ignore[attr-defined]

                proj_name = message.project.lstrip("&") if message.project else None
                tag_names = [t.lstrip("#") for t in message.tags]

                new_tags = list(set(entry.tag_names + tag_names))

                self.ctx.db.update_entry(  # type: ignore[attr-defined]
                    message.entry_id,
                    project=proj_name or entry.project,
                    tags=new_tags
                )
                self.notify("Recommendations applied!")  # type: ignore[attr-defined]
                # Trigger refresh
                self.post_message(EntryAdded(  # type: ignore[attr-defined]
                    entry_id=message.entry_id,
                    content=entry.content,
                    created_at=entry.created_at
                ))
            except Exception as e:
                self.notify(f"Failed to apply recommendation: {e}", severity="error")  # type: ignore[attr-defined]

        self.run_worker(apply_worker())  # type: ignore[attr-defined]
