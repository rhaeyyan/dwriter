"""Todo screen for dwriter TUI.

This module provides the todo board for managing tasks,
marking them complete, and editing/deleting.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext
    from ..app import DWriterApp

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
)

from ...database import Todo
from ..colors import (
    DUE_OVERDUE,
    DUE_SOON,
    DUE_TODAY,
    DUE_TOMORROW,
    PROJECT,
    TAG,
    get_icon,
)
from ..messages import EntryAdded, TodoUpdated


class AddTodoForm(Vertical):
    """A form for quickly adding a new todo directly from the board."""

    app: DWriterApp

    DEFAULT_CSS = """
    AddTodoForm {
        padding: 1 4;
        height: auto;
        background: $surface;
    }

    #add-form-title {
        text-style: bold;
        padding-bottom: 1;
        color: $primary;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-col {
        width: 1fr;
        height: auto;
    }

    #add-buttons {
        margin-top: 1;
        width: 100%;
        height: auto;
    }

    #add-buttons Button {
        width: 1fr;
    }

    Label {
        text-style: bold;
        padding: 1 0 0 0;
    }

    Input {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the form fields."""
        yield Label("Quick Add Task", id="add-form-title")
        
        yield Label("Content:")
        yield Input(id="add-content", placeholder="What needs to be done?")

        with Horizontal(classes="form-row"):
            with Vertical(classes="form-col"):
                date_fmt = self.app.ctx.config.display.due_date_format
                yield Label("Due Date:")
                yield Input(id="add-date", placeholder=f"today, {date_fmt}, +5d...")
            with Vertical(classes="form-col"):
                yield Label("Time:")
                yield Input(id="add-time", placeholder="2pm, 14:30, +2h...")
        
        yield Label("Tags:")
        yield Input(id="add-tags", placeholder="work, personal, etc.")

        yield Label("Project:")
        yield Input(id="add-project", placeholder="Project name (optional)")

        with Horizontal(id="add-buttons"):
            yield Button("\\[ SAVE ]", id="add-save-btn", variant="primary")
            yield Button("\\[ SAVE AS REMINDER ]", id="add-reminder-btn", variant="error")
            yield Button("\\[ CANCEL ]", id="add-cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle save button press."""
        if event.button.id == "add-save-btn":
            self.action_save(is_reminder=False)
        elif event.button.id == "add-reminder-btn":
            self.action_save(is_reminder=True)
        elif event.button.id == "add-cancel-btn":
            self.action_cancel()

    def action_cancel(self) -> None:
        """Cancel and return to pending list."""
        self.post_message(self.AddTodoCancel())

    def action_save(self, is_reminder: bool = False) -> None:
        """Save the new task and emit a message to parent."""
        content_input = self.query_one("#add-content", Input)
        date_input = self.query_one("#add-date", Input)
        time_input = self.query_one("#add-time", Input)
        tags_input = self.query_one("#add-tags", Input)
        project_input = self.query_one("#add-project", Input)

        content = content_input.value.strip()
        if not content:
            return

        # Combine date and time
        date_val = date_input.value.strip()
        time_val = time_input.value.strip()
        due_str = None
        if date_val and time_val:
            due_str = f"{date_val} {time_val}"
        elif date_val:
            due_str = date_val
        elif time_val:
            due_str = time_val

        tags_raw = tags_input.value.strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
        project = project_input.value.strip() or None

        # Post the message to the screen
        self.post_message(self.AddTodoSignal(content, due_str, tags, project, is_reminder))

    class AddTodoSignal(Message):
        """Message sent when a todo is successfully added from the form."""
        def __init__(self, content: str, due_str: str | None, tags: list[str], project: str|None, is_reminder: bool = False) -> None:
            super().__init__()
            self.content = content
            self.due_str = due_str
            self.tags = tags
            self.project = project
            self.is_reminder = is_reminder

    class AddTodoCancel(Message):
        """Signal to cancel add and go back."""
        def __init__(self) -> None:
            super().__init__()


class TodoListItem(ListItem):
    """Custom list item for todo tasks."""

    app: DWriterApp

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initialize the todo list item.

        Args:
            todo: Todo object to display.
            **kwargs: Additional arguments passed to ListItem.
        """
        super().__init__(**kwargs)
        self.todo = todo


class EditTodoModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing a todo."""

    app: DWriterApp

    CSS = """
    EditTodoModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 85%;
        max-width: 100;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: solid $primary;
        padding: 1 3;
        overflow-y: auto;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-content-label, #edit-date-label, #edit-time-label, #edit-tags-label, #edit-project-label {
        text-style: bold;
        padding: 1 0 0 0;
    }

    #edit-input {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
    }

    #date-input, #time-input, #tags-input, #project-input {
        width: 100%;
        margin: 0 0 1 0;
    }

    .horizontal-row {
        height: 5;
        width: 100%;
    }

    .col {
        width: 1fr;
        height: auto;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
        height: 3;
        width: 100%;
    }

    Button {
        margin: 0 1;
    }

    #save-as-reminder-btn {
        background: $error;
        color: white;
    }

    #help-text {
        text-style: italic;
        color: $foreground 60%;
        padding: 0 0 1 0;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "save", "Save"),
    ]

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initialize the edit modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        # Result: (content, due_date_str, tags, project, is_reminder)
        self.result: tuple[str | None, str | None, list[str] | None, str | None, bool] = (
            None,
            None,
            None,
            None,
            False,
        )

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Vertical(id="edit-modal-container"):
            yield Label(f"Edit Task #{self.todo.id}", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(
                value=self.todo.content,
                id="edit-input",
                placeholder="Enter task content...",
            )

            # Date and Time fields side-by-side
            date_fmt = self.app.ctx.config.display.due_date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt, "%Y-%m-%d")

            with Horizontal(classes="horizontal-row"):
                with Vertical(classes="col"):
                    yield Label("Due Date:", id="edit-date-label")
                    date_val = ""
                    if self.todo.due_date:
                        date_val = self.todo.due_date.strftime(hint)
                    yield Input(
                        value=date_val,
                        id="date-input",
                        placeholder=f"{date_fmt}, tomorrow, etc.",
                    )
                with Vertical(classes="col"):
                    yield Label("Time:", id="edit-time-label")
                    time_str = ""
                    if self.todo.due_date and (self.todo.due_date.hour != 0 or self.todo.due_date.minute != 0):
                        time_str = self.todo.due_date.strftime("%H:%M")
                    yield Input(
                        value=time_str,
                        id="time-input",
                        placeholder="2pm, 14:30, +2h, etc.",
                    )
            yield Label(
                "Examples: tomorrow, Friday, 2pm, +15m, in 1 hour",
                id="help-text",
            )

            # Tags field
            yield Label("Tags:", id="edit-tags-label")
            tags_str = ", ".join(self.todo.tag_names) if self.todo.tag_names else ""
            yield Input(
                value=tags_str,
                id="tags-input",
                placeholder="Comma-separated tags (e.g., work, urgent)",
            )

            # Project field
            yield Label("Project:", id="edit-project-label")
            yield Input(
                value=self.todo.project or "",
                id="project-input",
                placeholder="Project name (optional)",
            )

            with Horizontal(id="edit-buttons"):
                yield Button("\\[ SAVE ]", id="save-btn", variant="primary")
                yield Button("\\[ SAVE AS REMINDER ]", id="save-as-reminder-btn", variant="error")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the content input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self, is_reminder: bool = False) -> None:
        """Save the edited content, due date, tags, and project."""
        content_widget = self.query_one("#edit-input", Input)
        date_widget = self.query_one("#date-input", Input)
        time_widget = self.query_one("#time-input", Input)
        tags_widget = self.query_one("#tags-input", Input)
        project_widget = self.query_one("#project-input", Input)

        content = content_widget.value.strip() or None
        
        # Combine date and time
        date_val = date_widget.value.strip()
        time_val = time_widget.value.strip()
        
        due_date_str = None
        if date_val and time_val:
            due_date_str = f"{date_val} {time_val}"
        elif date_val:
            due_date_str = date_val
        elif time_val:
            due_date_str = time_val

        tags_str = tags_widget.value.strip() or None
        project = project_widget.value.strip() or None

        # Parse tags from comma-separated string
        tags: list[str] | None = None
        if tags_str is not None:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        self.result = (content, due_date_str, tags, project, is_reminder)
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.result = (None, None, None, None, False)
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save(is_reminder=False)
        elif event.button.id == "save-as-reminder-btn":
            self.action_save(is_reminder=True)
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class AddTodoModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for adding a new todo."""

    CSS = """
    AddTodoModal {
        align: center middle;
    }

    #add-modal-container {
        width: 80;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 3;
    }

    #add-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #add-input {
        width: 100%;
        height: 5;
        margin: 1 0;
    }

    #add-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "save", "Save"),
    ]

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the add modal.

        Args:
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="add-modal-container"):
            yield Label(f"{get_icon('plus', use_emojis)} Add New Task", id="add-modal-title")
            yield Input(
                value="",
                id="add-input",
                placeholder="Enter task content...",
            )
            with Container(id="add-buttons"):
                yield Button("\\[ ADD ]", id="add-btn", variant="primary")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#add-input", Input).focus()

    def action_save(self) -> None:
        """Save the new task."""
        input_widget = self.query_one("#add-input", Input)
        self.result = input_widget.value.strip()
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel adding."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditTagsModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing a todo's tags."""

    CSS = """
    EditTagsModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 70;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 3;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-input {
        width: 100%;
        margin: 1 0;
    }

    #edit-hint {
        color: $foreground 60%;
        padding: 0 0 1 0;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initialize the edit tags modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: list[str] | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Tags for Task #{self.todo.id}", id="edit-modal-title")
            yield Input(
                value=", ".join(self.todo.tag_names),
                id="edit-input",
                placeholder="tag1, tag2, tag3",
            )
            yield Label("Separate tags with commas", id="edit-hint")
            with Container(id="edit-buttons"):
                yield Button("\\[ SAVE ]", id="save-btn", variant="primary")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Save the edited tags."""
        input_widget = self.query_one("#edit-input", Input)
        value = input_widget.value.strip()
        if value:
            self.result = [t.strip() for t in value.split(",") if t.strip()]
        else:
            self.result = []
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditProjectModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing a todo's project."""

    CSS = """
    EditProjectModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 70;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 3;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-input {
        width: 100%;
        margin: 1 0;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initialize the edit project modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Project for Task #{self.todo.id}", id="edit-modal-title")
            yield Input(
                value=self.todo.project or "",
                id="edit-input",
                placeholder="Project name (optional)",
            )
            with Container(id="edit-buttons"):
                yield Button("\\[ SAVE ]", id="save-btn", variant="primary")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Save the edited project."""
        input_widget = self.query_one("#edit-input", Input)
        self.result = input_widget.value.strip() or None
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class TodoListView(ListView):
    """ListView for displaying todo tasks."""

    def __init__(self, todos: list[Todo] | None = None, **kwargs: Any) -> None:
        """Initialize the todo list view.

        Args:
            todos: Optional list of Todo objects to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._todos = todos or []
        self._loaded = False

    def _sort_todos(self, todos: list[Todo]) -> list[Todo]:
        """Sort todos by priority and due date based on user configuration.

        Sorting order for pending todos (priority_first):
        1. Priority (urgent → high → normal → low)
        2. Due date urgency (overdue → today → tomorrow → soonest → no date)
        3. Creation date (newest first)

        Sorting order for pending todos (date_first):
        1. Due date urgency (overdue → today → tomorrow → soonest → no date)
        2. Priority (urgent → high → normal → low)
        3. Creation date (newest first)

        Sorting order for completed todos:
        1. Completion date (most recent first)

        Args:
            todos: List of Todo objects to sort.

        Returns:
            Sorted list of Todo objects.
        """
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        sorting_mode = self.app.ctx.config.display.todo_sorting_mode

        def sort_key(todo: Todo) -> tuple[int, int, int, float]:
            # For completed todos, sort by completion date (most recent first)
            if todo.status == "completed":
                completed_score = (
                    -int(todo.completed_at.timestamp()) if todo.completed_at else 0
                )
                # Put all completed todos after pending ones
                return (999, 0, 0, float(completed_score))

            # Active reminder score (0 if active, 1 otherwise)
            is_active_reminder = 1
            if (
                todo.priority == "urgent"
                and todo.due_date
                and todo.due_date <= datetime.now() + timedelta(minutes=30)
            ):
                is_active_reminder = 0

            # Priority score (lower is higher priority)
            priority_score = priority_order.get(todo.priority, 2)

            # Due date score (lower is more urgent)
            due_score = 9999  # Default for no due date
            if todo.due_date:
                due_date_only = todo.due_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                days_until = (due_date_only - today).days
                if days_until < 0:
                    due_score = days_until - 1000
                elif days_until == 0:
                    due_score = 0
                elif days_until == 1:
                    due_score = 1
                else:
                    due_score = days_until

            # Creation date score (negative so newer comes first)
            created_score = -todo.created_at.timestamp() if todo.created_at else 0.0

            if sorting_mode == "date_first":
                # Chronological first, then priority
                return (is_active_reminder, due_score, priority_score, created_score)
            else:
                # Priority first (default), then chronological
                return (is_active_reminder, priority_score, due_score, created_score)

        return sorted(todos, key=sort_key)

    def update_todos(self, todos: list[Todo]) -> None:
        """Update the displayed todos.

        Args:
            todos: List of Todo objects to display.
        """
        # Sort todos by priority and due date
        sorted_todos = self._sort_todos(todos)
        self._todos = sorted_todos
        self._loaded = True
        self.clear()
        for todo in sorted_todos:
            self.append_item(todo)

    def append_item(self, todo: Todo) -> None:
        """Append a single todo to the list.

        Args:
            todo: Todo object to display.
        """
        label = self._format_todo(todo)
        list_item = TodoListItem(todo)
        list_item._add_child(Label(label, markup=True))
        self.append(list_item)

    def _format_todo(self, todo: Todo) -> str:
        """Format a todo for display with configurable date format.

        Args:
            todo: Todo object to format.

        Returns:
            Formatted string with markup.
        """
        # Spelled out priority tags - explicit closing tags
        priority_map = {
            "urgent": "[bold red]\\[Urgent][/bold red]",
            "high": "[#FA5053]\\[High][/#FA5053]",
            "normal": "[white]\\[Normal][/white]",
            "low": "[dim]\\[Low][/dim]",
        }
        pri_str = priority_map.get(todo.priority, "[white]\\[N][/white]")

        d_str = "[dim]\\[---][/dim]"
        due_date_format = self.app.ctx.config.display.due_date_format

        # If completed, swap the due-date block for the exact timestamp
        if todo.status == "completed" and todo.completed_at:
            dt_str = todo.completed_at.strftime("%m-%d %H:%M")
            d_str = f"[cyan]{dt_str}[/cyan]"
        elif todo.due_date:
            if due_date_format == "relative":
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                due_only = todo.due_date.replace(hour=0, minute=0, second=0, microsecond=0)
                days = (due_only - today).days
                if days < 0:
                    d_str = f"[{DUE_OVERDUE}]Overdue[/{DUE_OVERDUE}]"
                elif days == 0:
                    d_str = f"[{DUE_TODAY}]Today[/{DUE_TODAY}]"
                elif days == 1:
                    d_str = f"[{DUE_TOMORROW}]Tomorrow[/{DUE_TOMORROW}]"
                elif days <= 9:
                    d_str = f"[{DUE_SOON}]{days}d[/{DUE_SOON}]"
                elif days <= 99:
                    d_str = f"[{DUE_SOON}]{days}d[/{DUE_SOON}]"
                else:
                    d_str = f"[{DUE_SOON}]99+[/{DUE_SOON}]"
            else:
                # Absolute date formats with day of week coloring
                DAY_COLORS = {
                    "Monday": "#6A9FE8",
                    "Tuesday": "#56C8C8",
                    "Wednesday": "#72C472",
                    "Thursday": "#E8A84A",
                    "Friday": "#B57FE8",
                    "Saturday": "#E87FA0",
                    "Sunday": "#E86060",
                }
                day_name = todo.due_date.strftime("%A")
                day_color = DAY_COLORS.get(day_name, "#FFFFFF")

                # Mapping our config keys to strftime formats
                fmt_map = {
                    "YYYY-MM-DD": "%Y-%m-%d",
                    "MM/DD/YYYY": "%m/%d/%Y",
                    "DD/MM/YYYY": "%d/%m/%Y",
                }
                base_fmt = fmt_map.get(due_date_format, "%Y-%m-%d")
                formatted_date = todo.due_date.strftime(f"%A, {base_fmt}")
                d_str = f"[{day_color}]\\[{formatted_date}][/{day_color}]"

        # ESCAPE USER CONTENT! This stops user-typed brackets from crashing the app.
        safe_content = todo.content.replace("[", "\\[")
        safe_project = todo.project.replace("[", "\\[") if todo.project else ""

        # Format tags and project on first line
        tags_str = (
            f"[{TAG}]#{' #'.join(todo.tag_names)}[/{TAG}]" if todo.tag_names else ""
        )
        project_str = (
            f" [{PROJECT}]&{safe_project}[/{PROJECT}]" if safe_project else ""
        )

        # Format: Due date priority | #tags : Project on first line, content on second line
        first_line = f"{d_str} {pri_str} | {tags_str}{project_str}"

        # Determine if this is an active reminder for highlighting
        is_active_reminder = (
            todo.status == "pending"
            and todo.priority == "urgent"
            and todo.due_date
            and todo.due_date <= datetime.now() + timedelta(minutes=30)
        )

        # Content on second line with reduced indentation - add check emoji for completed todos
        if todo.status == "completed":
            use_emojis = self.app.ctx.config.display.use_emojis
            check_icon = get_icon("check", use_emojis)
            return f"[dim]{first_line}\n  {check_icon} {safe_content}[/dim]"

        if is_active_reminder:
            # Ruby/Cyberpunk alert style: bold red on dark background with pulsing feel
            return f"[bold #FF0000]{first_line}\n  🔔 {safe_content}[/bold #FF0000]"

        return f"{first_line}\n  [bold white]{safe_content}[/bold white]"

    @property
    def selected_todo(self) -> Todo | None:
        """Get the currently selected todo."""
        if self.highlighted_child is None:
            return None
        if isinstance(self.highlighted_child, TodoListItem):
            return self.highlighted_child.todo
        return None


class TodoScreen(Container):
    """Todo board screen."""

    app: DWriterApp

    DEFAULT_CSS = """
    TodoScreen {
        height: 1fr;
    }

    #todo-header-container {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        background: $panel;
        border: solid $secondary;
    }

    #todo-title {
        text-style: bold;
        color: $foreground;
    }

    #todo-subtitle {
        color: $foreground 60%;
    }

    #todo-list-container {
        height: 1fr;
        margin: 0 2;
    }

    TodoListView {
        height: 1fr;
        border: solid $secondary;
        background: $panel;
        padding: 0;
    }

    TodoListView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
        margin-bottom: 1;
        padding: 0;
    }

    Label {
        width: 100%;
        padding: 0;
        margin: 0;
    }

    #todo-status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $foreground 60%;
        padding: 0 2;
    }

    .pending-count {
        color: $foreground;
    }

    .completed-count {
        color: $success;
    }

    TabbedContent {
        height: 1fr;
    }

    TabbedContent > TabPane {
        padding: 0;
    }

    /* Use Textual's auto-generated ID for the tab to guarantee maximum CSS specificity */
    #todo-tabs #tab-add-pane {
        color: $success;
        text-style: bold;
        background: transparent;
        padding: 0 1;
        min-width: 0;
    }

    #todo-tabs #tab-add-pane:hover {
        background: $success 20%;
        color: $success;
        text-style: bold;
    }

    #todo-tabs #tab-add-pane.-active {
        background: $success;
        color: $background;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("space", "toggle_complete", "Complete"),
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
        Binding("enter", "toggle_complete", "Toggle"),
        Binding("+", "increase_priority", "Priority +"),
        Binding("-", "decrease_priority", "Priority -"),
        Binding("1", "switch_tab_pending", "Pending", show=False),
        Binding("2", "switch_tab_upcoming", "Upcoming", show=False),
        Binding("3", "switch_tab_completed", "Completed", show=False),
        Binding("tab", "next_tab", "Next Tab", show=False),
        Binding("h", "toggle_header", "Toggle Header"),
    ]

    # Reactive filter status - triggers UI update when changed
    filter_status = reactive("pending")
    show_header = reactive(False)

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initialize the todo screen.

        Args:
            ctx: Application context with database and configuration.
            **kwargs: Additional arguments passed to Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._all_todos: list[Todo] = []

    def compose(self) -> ComposeResult:
        """Compose the todo UI layout."""
        use_emojis = self.ctx.config.display.use_emojis
        with Vertical():
            with Container(id="todo-header-container"):
                yield Label(f"{get_icon('todo', use_emojis)} To-Do Board", id="todo-title")
                yield Label(
                    f"Space: Complete {get_icon('bullet', use_emojis)} e: Edit {get_icon('bullet', use_emojis)} +/-: Priority {get_icon('bullet', use_emojis)} "
                    f"d: Delete {get_icon('bullet', use_emojis)} 1/2/3: Tabs {get_icon('bullet', use_emojis)} h: Hide header {get_icon('bullet', use_emojis)} q: Quit",
                    id="todo-subtitle",
                )
            # Use TabbedContent for filter switching with dynamic counts
            with TabbedContent(initial="pending-pane", id="todo-tabs"):
                with TabPane("\\[+]", id="add-pane"):
                    yield AddTodoForm()
                with TabPane(f"{get_icon('timer', use_emojis)} Pending (0)", id="pending-pane"):
                    yield TodoListView(id="todos")
                with TabPane(f"{get_icon('history', use_emojis)} Upcoming (0)", id="upcoming-pane"):
                    yield TodoListView(id="todos-upcoming")
                with TabPane(f"{get_icon('check', use_emojis)} Completed (0)", id="completed-pane"):
                    yield TodoListView(id="todos-completed")

    def watch_show_header(self, show: bool) -> None:
        """Reactively show/hide the header container."""
        try:
            header = self.query_one("#todo-header-container", Container)
            if header:
                header.display = show
        except Exception:
            pass

    def action_toggle_header(self) -> None:
        """Toggle the header visibility."""
        self.show_header = not self.show_header

    def on_mount(self) -> None:
        """Load data and focus the list on mount."""
        # Set initial header visibility
        try:
            header = self.query_one("#todo-header-container", Container)
            if header:
                header.display = self.show_header
        except Exception:
            pass

        tabbed = self.query_one(TabbedContent)
        # Re-map focus logic to avoid add-pane for initial list focus
        tabbed.active = "pending-pane"
        self._load_todos()
        active_view = self._get_active_list_view()
        if active_view is not None:
            active_view.focus()
        else:
            # If no active list view (e.g. on add form), focus the first input
            try:
                self.query_one("#add-content", Input).focus()
            except Exception:
                pass

    def on_show(self) -> None:
        """Refresh data when the todo screen becomes visible."""
        self._load_todos()
        active_view = self._get_active_list_view()
        if active_view:
            active_view.focus()

    def watch_filter_status(self, status: str) -> None:
        """Reactively update the todo list when filter changes.

        Args:
            status: New filter status.
        """
        tab_map = {
            "pending": "pending-pane",
            "completed": "completed-pane",
            "all": "all-pane",
        }
        tabbed = self.query_one(TabbedContent)
        if tabbed.active != tab_map.get(status, "pending-pane"):
            tabbed.active = tab_map.get(status, "pending-pane")
        self._load_todos()

    def _get_active_list_view(self) -> TodoListView | None:
        """Get the TodoListView for the currently active tab."""
        tabbed = self.query_one(TabbedContent)
        if tabbed.active == "pending-pane":
            return self.query_one("#todos", TodoListView)
        elif tabbed.active == "completed-pane":
            return self.query_one("#todos-completed", TodoListView)
        elif tabbed.active == "upcoming-pane":
            return self.query_one("#todos-upcoming", TodoListView)
        return None

    def _get_status_for_active_tab(self) -> str | None:
        """Get the status filter for the active tab."""
        tabbed = self.query_one(TabbedContent)
        if tabbed.active == "pending-pane":
            return "pending"
        elif tabbed.active == "completed-pane":
            return "completed"
        else:
            return None

    def _load_todos(self) -> None:
        """Load todos from database and update all lists."""
        # We always load all todos to update the counts in the tab labels
        self._all_todos = self.ctx.db.get_todos()
        self._update_all_lists()

    def on_add_todo_form_add_todo_signal(self, message: AddTodoForm.AddTodoSignal) -> None:
        """Handle signal from AddTodoForm to create a new task."""
        from ...date_utils import parse_natural_date
        
        try:
            due_date_format = self.ctx.config.display.due_date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(due_date_format)
            due_date = parse_natural_date(message.due_str, prefer_future=True, format_hint=hint) if message.due_str else None
            task = self.ctx.db.add_todo(
                content=message.content,
                due_date=due_date,
                tags=message.tags,
                project=message.project,
                priority="urgent" if message.is_reminder else "normal",
            )
            self.notify(f"Added task: {task.content}")
            
            # Clear the form fields
            form = self.query_one(AddTodoForm)
            form.query_one("#add-content", Input).value = ""
            form.query_one("#add-date", Input).value = ""
            form.query_one("#add-time", Input).value = ""
            form.query_one("#add-tags", Input).value = ""
            form.query_one("#add-project", Input).value = ""
            
            # Refresh lists to show the new task in Pending/Upcoming
            self._load_todos()
            
            # Switch back to the Pending tab to show the new task
            self.query_one(TabbedContent).active = "pending-pane"
            self.query_one("#todos", TodoListView).focus()
            
        except Exception as e:
            self.notify(f"Error adding task: {e}", variant="error")

    def on_add_todo_form_add_todo_cancel(self, message: AddTodoForm.AddTodoCancel) -> None:
        """Handle cancel signal from AddTodoForm."""
        self.query_one(TabbedContent).active = "pending-pane"
        active_view = self._get_active_list_view()
        if active_view:
            active_view.focus()

    def _get_upcoming_todos(self) -> list[Todo]:
        """Get todos due today, tomorrow, and in the next 2 days.

        Returns:
            List of todos due within the next 3 days (0, 1, 2 days from now).
        """
        all_todos = self.ctx.db.get_all_todos()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        upcoming = []
        for todo in all_todos:
            if todo.due_date and todo.status == "pending":
                due_only = todo.due_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                days = (due_only - today).days
                # Include today (0), tomorrow (1), and next 2 days (2)
                if 0 <= days <= 2:
                    upcoming.append(todo)

        # Use the pending list view to sort if available, otherwise just return
        pending_list = self.query("#todos").first(TodoListView)
        if pending_list:
            return pending_list._sort_todos(upcoming)
        return upcoming

    def _update_all_lists(self) -> None:
        """Update all list views (pending, upcoming, completed)."""
        all_todos = self.ctx.db.get_all_todos()
        pending_todos = [t for t in all_todos if t.status == "pending"]
        completed_todos = [t for t in all_todos if t.status == "completed"]
        upcoming_todos = self._get_upcoming_todos()

        # Update tab labels with counts
        self._update_tab_labels(
            len(pending_todos), len(upcoming_todos), len(completed_todos)
        )

        # Use query() instead of query_one() to safely handle deferred tabs
        # TabbedContent uses deferred rendering - tabs aren't mounted until clicked
        for pending_list in self.query("#todos").results(TodoListView):
            pending_list.update_todos(pending_todos)

        for upcoming_list in self.query("#todos-upcoming").results(TodoListView):
            upcoming_list.update_todos(upcoming_todos)

        for completed_list in self.query("#todos-completed").results(TodoListView):
            completed_list.update_todos(completed_todos)

        # Also update the cached list with sorted pending todos
        pending_list = self.query("#todos").first(TodoListView)
        if pending_list:
            self._all_todos = pending_list._sort_todos(pending_todos)
        else:
            self._all_todos = pending_todos

    def _update_tab_labels(
        self, pending_count: int, upcoming_count: int, completed_count: int
    ) -> None:
        """Update tab labels with item counts.

        Args:
            pending_count: Number of pending todos.
            upcoming_count: Number of upcoming todos (due within 3 days).
            completed_count: Number of completed todos.
        """
        try:
            tabbed = self.query_one("#todo-tabs", TabbedContent)
            # Use get_tab() to get the Tab object and update its label
            use_emojis = self.ctx.config.display.use_emojis
            pending_tab = tabbed.get_tab("pending-pane")
            if pending_tab:
                pending_tab.label = f"{get_icon('timer', use_emojis)} Pending ({pending_count})"

            upcoming_tab = tabbed.get_tab("upcoming-pane")
            if upcoming_tab:
                upcoming_tab.label = f"{get_icon('history', use_emojis)} Upcoming ({upcoming_count})"

            completed_tab = tabbed.get_tab("completed-pane")
            if completed_tab:
                completed_tab.label = f"{get_icon('check_small', use_emojis)} Completed ({completed_count})"

            # Refresh the tabbed widget to ensure labels are redrawn
            tabbed.refresh()
        except Exception:
            # If tab update fails, just pass - counts will show next time
            pass

    def _update_list(self) -> None:
        """Update the active todo list view."""
        list_view = self._get_active_list_view()
        if list_view is not None:
            list_view.update_todos(self._all_todos)

    def _get_selected_todo(self) -> Todo | None:
        """Get the currently selected todo."""
        list_view = self._get_active_list_view()
        if list_view is not None:
            return list_view.selected_todo
        return None

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        list_view = self._get_active_list_view()
        if list_view is not None:
            list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        list_view = self._get_active_list_view()
        if list_view is not None:
            list_view.action_cursor_up()

    def action_toggle_complete(self) -> None:
        """Toggle the selected task as complete.

        When a todo is completed, it is logged as an entry with the completion
        date serving as the entry date. The journal entry is linked to the todo
        for synced state (un-completing or deleting the todo removes the log).
        """
        todo = self._get_selected_todo()
        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        new_status = "pending" if todo.status == "completed" else "completed"
        now = datetime.now()

        # Update the To-Do item status in the database
        self.ctx.db.update_todo(
            todo.id,
            status=new_status,
            completed_at=now if new_status == "completed" else None,
        )

        if new_status == "completed":
            # Log completion to journal with a link back to the todo
            use_emojis = self.ctx.config.display.use_emojis
            check_icon = get_icon("check", use_emojis)
            entry = self.ctx.db.add_entry(
                content=f"{check_icon} {todo.content}",
                tags=todo.tag_names,
                project=todo.project,
                created_at=now,
                todo_id=todo.id,
            )
            self.notify(f"Task #{todo.id} completed & logged to journal!", timeout=1.5)
            # Post EntryAdded message so Logs screen updates reactively
            self.post_message(
                EntryAdded(
                    entry_id=entry.id,
                    content=entry.content,
                    created_at=entry.created_at,
                )
            )
        else:
            # Remove the journal entry linked to this todo
            self.ctx.db.delete_entry_by_todo_id(todo.id)
            self.notify(f"Task #{todo.id} marked pending & log removed", timeout=1.5)

        self._load_todos()
        self.post_message(TodoUpdated(todo_id=todo.id, action="updated"))

    def action_edit(self) -> None:
        """Edit the selected todo."""
        active_view = self._get_active_list_view()
        if active_view is None:
            return
            
        todo = active_view.selected_todo
        if not todo:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, str | None, list[str] | None, str | None, bool] | None,
        ) -> None:
            if result is None:
                return
            content, due_date_str, tags, project, is_reminder = result
            if content is None:
                return

            # Parse due date
            due_date: datetime | None = None
            if due_date_str:
                due_date = self._parse_due_date(due_date_str)

            # If "Save as Reminder" was clicked, force priority to urgent
            priority = todo.priority
            if is_reminder:
                priority = "urgent"

            self.ctx.db.update_todo(
                todo.id,
                content=content,
                due_date=due_date,
                tags=tags,
                project=project,
                priority=priority,
                reminder_last_sent=None if is_reminder else todo.reminder_last_sent,
            )
            self.notify(f"Task #{todo.id} updated", timeout=1.5)
            self._load_todos()
            self.post_message(TodoUpdated(todo_id=todo.id, action="updated"))

        self.app.push_screen(EditTodoModal(todo), on_dismiss)

    def action_delete(self) -> None:
        """Delete the selected task."""
        active_view = self._get_active_list_view()
        if active_view is None:
            return
            
        todo = active_view.selected_todo
        if not todo:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        self.ctx.db.delete_todo(todo.id)
        self.notify(f"Task #{todo.id} deleted", timeout=1.5)
        self._load_todos()
        self.post_message(TodoUpdated(todo_id=todo.id, action="deleted"))

    def action_increase_priority(self) -> None:
        """Increase priority of selected todo."""
        active_view = self._get_active_list_view()
        if active_view is None:
            return
            
        todo = active_view.selected_todo
        if not todo:
            return

        priorities = ["low", "normal", "high", "urgent"]
        current_idx = priorities.index(todo.priority) if todo.priority in priorities else 1
        new_idx = min(current_idx + 1, len(priorities) - 1)

        self.ctx.db.update_todo(todo.id, priority=priorities[new_idx])
        self.notify(f"Priority: {priorities[new_idx]}", timeout=1)
        self._load_todos()

    def action_decrease_priority(self) -> None:
        """Decrease priority of selected todo."""
        active_view = self._get_active_list_view()
        if active_view is None:
            return
            
        todo = active_view.selected_todo
        if not todo:
            return

        priorities = ["low", "normal", "high", "urgent"]
        current_idx = priorities.index(todo.priority) if todo.priority in priorities else 1
        new_idx = max(current_idx - 1, 0)

        self.ctx.db.update_todo(todo.id, priority=priorities[new_idx])
        self.notify(f"Priority: {priorities[new_idx]}", timeout=1)
        self._load_todos()

    def action_switch_tab_pending(self) -> None:
        """Switch to pending tab."""
        self.filter_status = "pending"

    def action_switch_tab_upcoming(self) -> None:
        """Switch to upcoming tab."""
        self.filter_status = "upcoming"

    def action_switch_tab_completed(self) -> None:
        """Switch to completed tab."""
        self.filter_status = "completed"

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["upcoming-pane", "pending-pane", "completed-pane"]
        current = tabs.index(tabbed.active) if tabbed.active in tabs else 0
        next_idx = (current + 1) % len(tabs)
        tab_map = {
            "upcoming-pane": "upcoming",
            "pending-pane": "pending",
            "completed-pane": "completed",
        }
        self.filter_status = tab_map.get(tabs[next_idx], "upcoming")

    def _parse_due_date(self, due_str: str) -> datetime | None:
        """Parse a due date string using the central date_utils parser.

        Args:
            due_str: Due date string (e.g., "2024-01-15", "tomorrow", "2pm").

        Returns:
            Parsed datetime or None.
        """
        from ...date_utils import parse_natural_date
        try:
            # Use configuration to hint at preferred input format
            due_date_format = self.app.ctx.config.display.due_date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(due_date_format)
            
            # Prefer future for TUI-based todo editing
            return parse_natural_date(due_str, prefer_future=True, format_hint=hint)
        except ValueError:
            return None

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Handle TodoUpdated messages from other screens.

        Args:
            message: TodoUpdated message.
        """
        # Refresh the todo list when todos are updated elsewhere
        self._load_todos()
