"""Multi-step todo creation workflow for the omnibox."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from textual.widgets import Input

    from .app import DWriterApp

TodoStep = Literal["task", "tags", "priority", "due_date"]


class TodoInputState:
    """State tracker for multi-step todo input workflow."""

    def __init__(self) -> None:
        """Initialize the todo input state."""
        self.active: bool = False
        self.step: TodoStep = "task"
        self.content: str = ""
        self.tags: list[str] = []
        self.project: str = ""
        self.priority: str = "normal"
        self.due_date: str = ""


class TodoWorkflow:
    """Encapsulates the 4-step omnibox todo creation flow.

    Holds all state and logic for the guided todo wizard, keeping it out of
    the main app class. The workflow communicates back to the app via its
    public interface (``notify``, ``post_message``, ``run_worker``).
    """

    def __init__(self, app: DWriterApp) -> None:
        """Initialize the workflow with a reference to the parent app."""
        self._app = app
        self.state = TodoInputState()

    def start(self, value: str, message: Input.Submitted) -> None:
        """Start the multi-step todo creation workflow from an omnibox submission."""
        from .parsers import parse_todo_add

        parsed = parse_todo_add(value)
        self.state.active = True
        self.state.step = "tags"
        self.state.content = parsed.content
        self.state.tags = parsed.tags
        self.state.project = parsed.project or ""
        self.state.priority = parsed.priority
        message.input.value = ""
        self._app._update_omnibox_placeholder("todo")

    def handle_step(self, value: str, message: Input.Submitted) -> None:
        """Advance through a workflow step based on the current state."""
        step = self.state.step

        if step == "tags":
            if value:
                from .parsers import parse_todo_add

                parsed = parse_todo_add(value)
                for tag in parsed.tags:
                    if tag not in self.state.tags:
                        self.state.tags.append(tag)
                if parsed.project:
                    self.state.project = parsed.project
            self.state.step = "priority"
            message.input.value = ""
            self._app._update_omnibox_placeholder("todo")

        elif step == "priority":
            value_lower = value.lower().strip()
            if value_lower == "l":
                self.state.priority = "low"
            elif value_lower == "h":
                self.state.priority = "high"
            elif value_lower == "u":
                self.state.priority = "urgent"
            else:
                self.state.priority = "normal"
            self.state.step = "due_date"
            message.input.value = ""
            self._app._update_omnibox_placeholder("todo")

        elif step == "due_date":
            due_date = None
            if value and value.lower() != "none":
                due_date = self.parse_due_date(value)

            content = self.state.content
            priority = self.state.priority
            all_tags = list(self._app.ctx.config.defaults.tags) + self.state.tags
            project = self.state.project or self._app.ctx.config.defaults.project

            async def add_todo_worker() -> None:
                from .messages import TodoUpdated

                todo = self._app.ctx.db.add_todo(
                    content=content,
                    priority=priority,
                    tags=all_tags,
                    project=project,
                    due_date=due_date,
                )
                self._app.notify(f"Todo added: {content}")
                self._app.post_message(TodoUpdated(todo_id=todo.id, action="added"))

            self._app.run_worker(add_todo_worker())
            message.input.value = ""
            self.reset()

    def reset(self) -> None:
        """Reset workflow state to idle and refresh the omnibox placeholder."""
        self.state = TodoInputState()
        self._app._update_omnibox_placeholder("todo")

    def parse_due_date(self, due_str: str) -> Any:
        """Parse a natural-language due date string for todo creation."""
        from ..date_utils import parse_natural_date

        try:
            date_fmt = self._app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt)
            return parse_natural_date(due_str, prefer_future=True, format_hint=hint)
        except Exception:
            return None
