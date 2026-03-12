"""Todo screen for dwriter TUI.

This module provides the todo board for managing tasks,
marking them complete, and editing/deleting.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
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

from ...cli import AppContext
from ...database import Todo
from ..messages import EntryAdded, TodoUpdated


class TodoListItem(ListItem):
    """Custom list item for todo tasks."""

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

    CSS = """
    EditTodoModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 90;
        height: auto;
        max-height: 90;
        background: $surface;
        border: thick $primary;
        padding: 1 3;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-content-label, #edit-due-label, #edit-tags-label, #edit-project-label {
        text-style: bold;
        padding: 1 0 0 0;
    }

    #edit-input {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
    }

    #due-input, #tags-input, #project-input {
        width: 100%;
        margin: 0 0 1 0;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }

    #help-text {
        text-style: italic;
        color: $text-muted;
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
        self.result: tuple[str | None, str | None, list[str] | None, str | None] = (
            None,
            None,
            None,
            None,
        )

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Task #{self.todo.id}", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(
                value=self.todo.content,
                id="edit-input",
                placeholder="Enter task content...",
            )

            # Due date field
            yield Label("Due Date:", id="edit-due-label")
            due_date_str = ""
            if self.todo.due_date:
                due_date_str = self.todo.due_date.strftime("%Y-%m-%d")
            yield Input(
                value=due_date_str,
                id="due-input",
                placeholder="YYYY-MM-DD, tomorrow, +5d, +1w, etc.",
            )
            yield Label(
                "Examples: 2024-01-15, tomorrow, +5d, +1w, +1m, 3 days",
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

            with Container(id="edit-buttons"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the content input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Save the edited content, due date, tags, and project."""
        content_widget = self.query_one("#edit-input", Input)
        due_widget = self.query_one("#due-input", Input)
        tags_widget = self.query_one("#tags-input", Input)
        project_widget = self.query_one("#project-input", Input)

        content = content_widget.value.strip() or None
        due_date_str = due_widget.value.strip() or None
        tags_str = tags_widget.value.strip() or None
        project = project_widget.value.strip() or None

        # Parse tags from comma-separated string
        tags: list[str] | None = None
        if tags_str is not None:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        self.result = (content, due_date_str, tags, project)
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.result = (None, None, None, None)
        self.dismiss(self.result)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
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
        border: thick $primary;
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
        with Container(id="add-modal-container"):
            yield Label("➕ Add New Task", id="add-modal-title")
            yield Input(
                value="",
                id="add-input",
                placeholder="Enter task content...",
            )
            with Container(id="add-buttons"):
                yield Button("Add", id="add-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

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
        border: thick $primary;
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
        color: $text-muted;
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
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

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
        border: thick $primary;
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
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

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

    @staticmethod
    def _sort_todos(todos: list[Todo]) -> list[Todo]:
        """Sort todos by priority and due date.

        Sorting order for pending todos:
        1. Priority (urgent → high → normal → low)
        2. Due date urgency (overdue → today → tomorrow → soonest → no date)
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

        def sort_key(todo: Todo) -> tuple[int, int, float, float]:
            # For completed todos, sort by completion date (most recent first)
            if todo.status == "completed":
                completed_score = (
                    -todo.completed_at.timestamp() if todo.completed_at else 0.0
                )
                # Put all completed todos after pending ones with a high priority score
                return (999, 0, completed_score, 0.0)

            # Priority score (lower is higher priority)
            priority_score = priority_order.get(todo.priority, 2)

            # Due date score (lower is more urgent)
            # OVERDUE items should appear ABOVE TODAY items
            due_score = 9999  # Default for no due date
            if todo.due_date:
                due_date_only = todo.due_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                days_until = (due_date_only - today).days
                if days_until < 0:
                    # Overdue: sort by most overdue first (most negative)
                    # Give overdue items a very low score so they appear first
                    due_score = days_until - 1000
                elif days_until == 0:
                    # Due today
                    due_score = 0
                elif days_until == 1:
                    # Due tomorrow
                    due_score = 1
                else:
                    # Due later: sort by soonest first
                    due_score = days_until

            # Creation date score (negative so newer comes first)
            created_score = -todo.created_at.timestamp() if todo.created_at else 0.0

            return (priority_score, due_score, created_score, 0.0)

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
        """Format a todo for display with ultra-compact metadata for 75-column terminals.

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

        # If completed, swap the due-date block for the exact timestamp
        if todo.status == "completed" and todo.completed_at:
            dt_str = todo.completed_at.strftime("%m-%d %H:%M")
            d_str = f"[cyan]{dt_str}[/cyan]"
        elif todo.due_date:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            due_only = todo.due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days = (due_only - today).days
            if days < 0:
                d_str = "[red]Overdue[/red]"
            elif days == 0:
                d_str = "[orange]Today[/orange]"
            elif days == 1:
                d_str = "[yellow]Tomorrow[/yellow]"
            elif days <= 9:
                d_str = f"[cyan]{days}d[/cyan]"
            elif days <= 99:
                d_str = f"[cyan]{days}d[/cyan]"
            else:
                d_str = "[cyan]99+[/cyan]"

        # ESCAPE USER CONTENT! This stops user-typed brackets from crashing the app.
        safe_content = todo.content.replace("[", "\\[")
        safe_project = todo.project.replace("[", "\\[") if todo.project else ""

        # Format tags and project on first line
        tags_str = (
            f"[yellow]#{' #'.join(todo.tag_names)}[/yellow]" if todo.tag_names else ""
        )
        project_str = (
            f"[cyan] : [/cyan][magenta]{safe_project}[/magenta]" if safe_project else ""
        )

        # Format: Due date priority | #tags : Project on first line, content on second line
        first_line = f"{d_str} {pri_str} | {tags_str}{project_str}"

        # Content on second line with reduced indentation - add check emoji for completed todos
        if todo.status == "completed":
            return f"[dim]{first_line}\n  ✅ {safe_content}[/dim]"

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
    """Todo board screen for managing tasks.

    Provides a real-time interface for managing tasks with:
    - Tabbed view for Pending/Completed/All tasks
    - Add, edit, complete, and delete operations
    - Priority management
    - Due date tracking with visual indicators

    Key bindings:
        a: Add new task
        j/k: Navigate up/down
        Space/Enter: Mark task as complete
        e: Edit task
        d: Delete selected task
        +/-: Change priority
        1/2/3: Switch tabs
    """

    DEFAULT_CSS = """
    TodoScreen {
        height: 1fr;
    }

    #todo-header-container {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        background: $panel;
    }

    #todo-title {
        text-style: bold;
        color: $foreground;
    }

    #todo-subtitle {
        color: $text-muted;
    }

    #todo-list-container {
        height: 1fr;
        margin: 0 2;
    }

    TodoListView {
        height: 1fr;
        border: solid $primary;
        padding: 0;
    }

    TodoListView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
        margin: 0;
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
        color: $text-muted;
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
        with Vertical():
            with Container(id="todo-header-container"):
                yield Label("📋 To-Do Board", id="todo-title")
                yield Label(
                    "Space: Complete | e: Edit | +/-: Priority | "
                    "d: Delete | 1/2/3: Tabs | h: Hide header | q: Quit",
                    id="todo-subtitle",
                )
            # Use TabbedContent for filter switching with dynamic counts
            with TabbedContent(initial="upcoming-pane", id="todo-tabs"):
                with TabPane("📅 Upcoming (0)", id="upcoming-pane"):
                    yield TodoListView(id="todos-upcoming")
                with TabPane("⏳ Pending (0)", id="pending-pane"):
                    yield TodoListView(id="todos")
                with TabPane("✅ Completed (0)", id="completed-pane"):
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
        tabbed.active = "pending-pane"
        self._load_todos()
        self._get_active_list_view().focus()

    def on_show(self) -> None:
        """Refresh data when the todo screen becomes visible."""
        self._load_todos()
        self._get_active_list_view().focus()

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

    def _get_active_list_view(self) -> TodoListView:
        """Get the TodoListView for the currently active tab."""
        tabbed = self.query_one(TabbedContent)
        if tabbed.active == "pending-pane":
            return self.query_one("#todos", TodoListView)
        elif tabbed.active == "completed-pane":
            return self.query_one("#todos-completed", TodoListView)
        else:
            # upcoming-pane
            return self.query_one("#todos-upcoming", TodoListView)

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
        """Load todos from the database based on active tab filter."""
        status_filter = self._get_status_for_active_tab()
        self._all_todos = self.ctx.db.get_todos(status=status_filter)
        self._update_all_lists()

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
        return TodoListView._sort_todos(upcoming)

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
        self._all_todos = TodoListView._sort_todos(pending_todos)

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
            pending_tab = tabbed.get_tab("pending-pane")
            if pending_tab:
                pending_tab.label = f"⏳ Pending ({pending_count})"

            upcoming_tab = tabbed.get_tab("upcoming-pane")
            if upcoming_tab:
                upcoming_tab.label = f"📅 Upcoming ({upcoming_count})"

            completed_tab = tabbed.get_tab("completed-pane")
            if completed_tab:
                completed_tab.label = f"✓ Completed ({completed_count})"

            # Refresh the tabbed widget to ensure labels are redrawn
            tabbed.refresh()
        except Exception:
            # If tab update fails, just pass - counts will show next time
            pass

    def _update_list(self) -> None:
        """Update the active todo list view."""
        list_view = self._get_active_list_view()
        list_view.update_todos(self._all_todos)

    def _get_selected_todo(self) -> Todo | None:
        """Get the currently selected todo."""
        list_view = self._get_active_list_view()
        return list_view.selected_todo

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        list_view = self._get_active_list_view()
        list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        list_view = self._get_active_list_view()
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
            entry = self.ctx.db.add_entry(
                content=f"✅ {todo.content}",
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
        """Edit the selected task."""
        todo = self._get_selected_todo()
        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, str | None, list[str] | None, str | None] | None,
        ) -> None:
            if result is None:
                return
            content, due_date_str, tags, project = result
            if content is None:
                return

            # Parse due date
            due_date: datetime | None = None
            if due_date_str:
                due_date = self._parse_due_date(due_date_str)

            self.ctx.db.update_todo(
                todo.id,
                content=content,
                due_date=due_date,
                tags=tags,
                project=project,
            )
            self.notify(f"Task #{todo.id} updated", timeout=1.5)
            self._load_todos()
            self.post_message(TodoUpdated(todo_id=todo.id, action="updated"))

        self.app.push_screen(EditTodoModal(todo), on_dismiss)

    def action_delete(self) -> None:
        """Delete the selected task."""
        todo = self._get_selected_todo()
        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        self.ctx.db.delete_todo(todo.id)
        self.notify(f"Task #{todo.id} deleted", timeout=1.5)
        self._load_todos()
        self.post_message(TodoUpdated(todo_id=todo.id, action="deleted"))

    def action_increase_priority(self) -> None:
        """Increase the priority of the selected task."""
        todo = self._get_selected_todo()
        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        priorities = ["low", "normal", "high", "urgent"]
        current_idx = (
            priorities.index(todo.priority) if todo.priority in priorities else 1
        )
        new_idx = min(current_idx + 1, len(priorities) - 1)

        self.ctx.db.update_todo(todo.id, priority=priorities[new_idx])
        self.notify(f"Priority: {priorities[new_idx]}", timeout=1)
        self._load_todos()

    def action_decrease_priority(self) -> None:
        """Decrease the priority of the selected task."""
        todo = self._get_selected_todo()
        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        priorities = ["low", "normal", "high", "urgent"]
        current_idx = (
            priorities.index(todo.priority) if todo.priority in priorities else 1
        )
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
        """Parse a due date string.

        Args:
            due_str: Due date string (e.g., "2024-01-15", "tomorrow", "+5d").

        Returns:
            Parsed datetime or None.
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Try parsing as date
        try:
            return datetime.strptime(due_str, "%Y-%m-%d")
        except ValueError:
            pass

        # Handle relative dates
        due_str_lower = due_str.lower().strip()

        if due_str_lower == "tomorrow":
            return today + timedelta(days=1)
        elif due_str_lower == "today":
            return today
        elif due_str_lower.endswith("d"):
            try:
                days = int(due_str_lower[:-1])
                return today + timedelta(days=days)
            except ValueError:
                pass
        elif due_str_lower.endswith("w"):
            try:
                weeks = int(due_str_lower[:-1])
                return today + timedelta(weeks=weeks)
            except ValueError:
                pass
        elif due_str_lower.endswith("m"):
            try:
                months = int(due_str_lower[:-1])
                # Approximate month as 30 days
                return today + timedelta(days=months * 30)
            except ValueError:
                pass
        elif "day" in due_str_lower:
            try:
                days = int(due_str_lower.split()[0])
                return today + timedelta(days=days)
            except ValueError:
                pass

        return None

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Handle TodoUpdated messages from other screens.

        Args:
            message: TodoUpdated message.
        """
        # Refresh the todo list when todos are updated elsewhere
        self._load_todos()
