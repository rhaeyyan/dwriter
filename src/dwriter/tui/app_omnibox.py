"""Omnibox visibility and placeholder mixin for DWriterApp."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class OmniboxMixin:
    """Mixin providing omnibox focus, visibility, and placeholder logic."""

    def watch_permanent_omnibox(self, value: bool) -> None:
        """Update omnibox visibility when the permanent_omnibox setting changes."""
        try:
            self.query_one("#omnibox-container").set_class(not value, "hidden")  # type: ignore[attr-defined]
            self.query_one("#omnibox-footer").set_class(not value, "hidden")  # type: ignore[attr-defined]
        except Exception:
            pass
        self._sync_omnibox_visibility()  # type: ignore[attr-defined]

    def _sync_omnibox_visibility(self) -> None:
        """Central logic for omnibox visibility using CSS classes and focus management."""
        from .widgets.omnibox import Omnibox

        try:
            is_permanent = self.permanent_omnibox  # type: ignore[attr-defined]
            current_focused = self.focused  # type: ignore[attr-defined]
            is_omnibox_focused = (
                current_focused is not None
                and getattr(current_focused, "id", None) == "quick-add"
            )
            show = is_permanent or is_omnibox_focused

            container = self.query_one("#omnibox-container")  # type: ignore[attr-defined]
            footer = self.query_one("#omnibox-footer")  # type: ignore[attr-defined]
            omnibox = self.query_one("#quick-add", Omnibox)  # type: ignore[attr-defined]

            container.set_class(not show, "hidden")
            footer.set_class(not show, "hidden")

            if not is_permanent and not is_omnibox_focused:
                omnibox.can_focus = False
            else:
                omnibox.can_focus = True
        except Exception:
            pass

    def action_focus_omnibox(self) -> None:
        """Focus the quick-add input."""
        from .widgets.omnibox import Omnibox

        self.query_one("#omnibox-container").remove_class("hidden")  # type: ignore[attr-defined]
        self.query_one("#omnibox-footer").remove_class("hidden")  # type: ignore[attr-defined]
        omnibox = self.query_one("#quick-add", Omnibox)  # type: ignore[attr-defined]
        omnibox.can_focus = True
        omnibox.focus()
        self._sync_omnibox_visibility()

    def action_blur_omnibox(self) -> None:
        """Remove focus from the omnibox when pressing escape."""
        if self.focused is not None and self.focused.id == "quick-add":  # type: ignore[attr-defined]
            if self._todo_workflow.state.active:  # type: ignore[attr-defined]
                self._todo_workflow.reset()  # type: ignore[attr-defined]
                self.notify("Todo creation cancelled", timeout=1.5)  # type: ignore[attr-defined]
            self.set_focus(None)  # type: ignore[attr-defined]
            self._sync_omnibox_visibility()

    def _update_omnibox_placeholder(self, screen_name: str) -> None:
        """Update the omnibox placeholder and hint based on the current screen."""
        from textual.widgets import Label

        from .colors import get_icon
        from .widgets.omnibox import Omnibox

        use_emojis = self.ctx.config.display.use_emojis  # type: ignore[attr-defined]
        bullet = get_icon("bullet", use_emojis)
        try:
            omnibox = self.query_one("#quick-add", Omnibox)  # type: ignore[attr-defined]
            hint = self.query_one("#omnibox-hint", Label)  # type: ignore[attr-defined]

            if screen_name == "todo":
                if self._todo_workflow.state.active:  # type: ignore[attr-defined]
                    step = self._todo_workflow.state.step  # type: ignore[attr-defined]
                    if step == "task":
                        omnibox.placeholder = "Enter task description..."
                        hint.update(
                            f"Task text with optional #tag &project {bullet} 'q' to cancel"
                        )
                    elif step == "tags":
                        current_tags = (
                            ", ".join(self._todo_workflow.state.tags)  # type: ignore[attr-defined]
                            if self._todo_workflow.state.tags  # type: ignore[attr-defined]
                            else "none"
                        )
                        tags_info = f"Current: {current_tags}"
                        proj_info = (
                            f"Project: {self._todo_workflow.state.project}"  # type: ignore[attr-defined]
                            if self._todo_workflow.state.project  # type: ignore[attr-defined]
                            else ""
                        )
                        hint.update(
                            f"{tags_info} {proj_info} {bullet} "
                            "Add more #tag &project or Enter to skip"
                        )
                        omnibox.placeholder = (
                            "Add tags/project (or press Enter to skip)..."
                        )
                    elif step == "priority":
                        omnibox.placeholder = (
                            "Priority: L=Low, N=Normal, H=High, U=Urgent "
                            "(or Enter for Normal)"
                        )
                        hint.update(
                            f"Task: {self._todo_workflow.state.content[:40]}... {bullet} 'q' to cancel"  # type: ignore[attr-defined]
                        )
                    elif step == "due_date":
                        date_fmt = self.ctx.config.display.date_format  # type: ignore[attr-defined]
                        omnibox.placeholder = (
                            f"Due date: {date_fmt}, today, tomorrow, 5d, 2w, 3m "
                            "(or Enter for none)"
                        )
                        hint.update(
                            f"Priority: {self._todo_workflow.state.priority.upper()} {bullet} "  # type: ignore[attr-defined]
                            "'q' to cancel"
                        )
                else:
                    omnibox.placeholder = "Enter Task and press Enter to start multi-step add"
                    hint.update(
                        f"Enter Task and press Enter to start multi-step add {bullet} "
                        "'q' to cancel"
                    )
            elif screen_name == "timer":
                omnibox.placeholder = "Start timer... (use #tag &project MINUTES)"
                hint.update(
                    f"Press / to focus {bullet} Enter: #tag &project 15 starts 15min timer"
                )
            else:
                date_fmt = self.ctx.config.display.date_format  # type: ignore[attr-defined]
                omnibox.placeholder = (
                    f"#tag &project YOUR-ENTRY | #tag &project YOUR-ENTRY {date_fmt}"
                )
                hint.update(
                    f"#tag &project YOUR-ENTRY {bullet} #tag &project YOUR-ENTRY {date_fmt}"
                )
        except Exception:
            pass
