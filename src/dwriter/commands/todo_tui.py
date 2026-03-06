"""Interactive todo board TUI using Textual.

This module provides a real-time interface for managing tasks,
marking them complete, and editing/deleting.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
)

from ..database import Todo


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
        self.result: tuple[str | None, str | None, str | None, str | None] = (None, None, None, None)

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
                from textual.widgets import Button

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
        tags = None
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
                from textual.widgets import Button

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
            yield Label(
                "Separate tags with commas",
                id="edit-hint",
            )
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
            yield Label(
                f"Edit Project for Task #{self.todo.id}",
                id="edit-modal-title",
            )
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
        self._loaded = False  # Track if this view has been populated

    def update_todos(self, todos: list[Todo]) -> None:
        """Update the displayed todos.

        Args:
            todos: List of Todo objects to display.
        """
        self._todos = todos
        self._loaded = True
        self.clear()
        for todo in todos:
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
        """Format a todo for display.

        Args:
            todo: Todo object to format.

        Returns:
            Formatted string with markup.
        """
        priority_colors = {
            "urgent": "red",
            "high": "yellow",
            "normal": "white",
            "low": "dim",
        }
        color = priority_colors.get(todo.priority, "white")
        
        # Format due date (shown first) - standardized display
        due_str = ""
        if todo.due_date:
            due_date = todo.due_date
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            due_date_only = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_until = (due_date_only - today).days
            
            if days_until == 0:
                due_str = f"[bold yellow]TODAY[/bold yellow] | "
            elif days_until == 1:
                due_str = f"[yellow]TOMORROW[/yellow] | "
            elif days_until < 0:
                # Overdue - show as negative days in red
                due_str = f"[red]{days_until}d[/red] | "
            elif days_until <= 30:
                # Within a month - show as Xd in cyan
                due_str = f"[cyan]{days_until}d[/cyan] | "
            else:
                # More than a month - show as Xm in dim cyan
                months_until = days_until // 30
                due_str = f"[dim cyan]{months_until}m[/dim cyan] | "
        else:
            due_str = "     – | "  # Placeholder for tasks without due date
        
        # Format tags with default terminal color (no special styling)
        tags_str = ""
        if todo.tag_names:
            tags_display = ", ".join(todo.tag_names)
            tags_str = f" #{tags_display}"
        
        # Format projects with magenta/fuchsia color (#ff00ff)
        project_str = ""
        if todo.project:
            project_str = f" [#ff00ff]→ {todo.project}[/]"
        
        # Format priority label
        priority_label = todo.priority.upper()

        if todo.status == "completed":
            return (
                f"[dim]{due_str}"
                f"[{color}]{priority_label}[/{color}] "
                f"[strike]{todo.content}[/strike]{tags_str}{project_str}[/dim]"
            )
        else:
            # Task content in lime green (#00ff00)
            return (
                f"{due_str}"
                f"[{color}]{priority_label}[/{color}] "
                f"[#00ff00]{todo.content}[/]{tags_str}{project_str}"
            )

    @property
    def selected_todo(self) -> Todo | None:
        """Get the currently selected todo."""
        if self.highlighted_child is None:
            return None
        if isinstance(self.highlighted_child, TodoListItem):
            return self.highlighted_child.todo
        return None


class TodoApp(App):  # type: ignore[type-arg]
    """Interactive todo board application.

    Provides a real-time interface for managing tasks.

    Key bindings:
        a: Add new task
        j/k: Navigate up/down
        Space/Enter: Mark task as complete
        e: Edit task (content, due date, tags, project)
        d: Delete selected task
        +/-: Change priority
        1/2/3: Switch tabs (Pending/Completed/All)
        Tab: Cycle through tabs
        q/Esc: Quit
        ?: Help
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #header-container {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        background: $panel;
    }

    #title {
        text-style: bold;
        color: $text;
    }

    #subtitle {
        color: $text-muted;
    }

    #list-container {
        height: 1fr;
        margin: 0 2;
    }

    TodoListView {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    TodoListView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
    }

    Label {
        width: 100%;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 2;
    }

    .pending-count {
        color: $text;
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
        Binding("a", "add", "Add", show=True),
        Binding("+", "increase_priority", "Priority +"),
        Binding("-", "decrease_priority", "Priority -"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("?", "goto_help", "Help"),
        # Tab navigation
        Binding("1", "switch_tab_pending", "Pending", show=False),
        Binding("2", "switch_tab_completed", "Completed", show=False),
        Binding("3", "switch_tab_all", "All", show=False),
        Binding("tab", "next_tab", "Next Tab", show=False),
    ]

    # Reactive filter status - triggers UI update when changed
    filter_status = reactive("pending")

    def __init__(
        self,
        db: Any,
        console: Any,
        show_all: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the todo application.

        Args:
            db: Database instance for querying todos.
            console: Rich console instance.
            show_all: Whether to show all tasks including completed.
            **kwargs: Additional arguments passed to App.
        """
        super().__init__(**kwargs)
        self.db = db
        self.console = console
        self.show_all = show_all
        self._all_todos: list[Todo] = []
        # Set initial filter based on show_all flag
        if show_all:
            self.filter_status = "all"

    def compose(self) -> ComposeResult:
        """Compose the todo UI layout."""
        yield Header()
        with Vertical():
            with Container(id="header-container"):
                yield Label("📋 Todo Board", id="title")
                yield Label(
                    "a: Add | Space: Complete | e: Edit | +/-: Priority | "
                    "d: Delete | 1/2/3: Tabs | q/?: Quit/Help",
                    id="subtitle",
                )
            # Use TabbedContent for filter switching
            with TabbedContent(initial="pending-pane"):
                with TabPane("⏳ Pending", id="pending-pane"):
                    yield TodoListView(id="todos")
                with TabPane("✓ Completed", id="completed-pane"):
                    yield TodoListView(id="todos-completed")
                with TabPane("📋 All", id="all-pane"):
                    yield TodoListView(id="todos-all")
        yield Label("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load data and focus the list on mount."""
        # Set initial tab based on show_all flag
        tabbed = self.query_one(TabbedContent)
        if self.show_all:
            tabbed.active = "all-pane"
        else:
            tabbed.active = "pending-pane"
        self._load_todos()
        self._get_active_list_view().focus()

    def watch_filter_status(self, status: str) -> None:
        """Reactively update the todo list when filter changes."""
        # Map filter status to tab ID
        tab_map = {
            "pending": "pending-pane",
            "completed": "completed-pane",
            "all": "all-pane",
        }
        tabbed = self.query_one(TabbedContent)
        if tabbed.active != tab_map.get(status, "pending-pane"):
            tabbed.active = tab_map.get(status, "pending-pane")
        self._load_todos()
        self._update_status_bar()

    def _get_active_list_view(self) -> TodoListView:
        """Get the TodoListView for the currently active tab."""
        tabbed = self.query_one(TabbedContent)
        if tabbed.active == "pending-pane":
            return self.query_one("#todos", TodoListView)
        elif tabbed.active == "completed-pane":
            return self.query_one("#todos-completed", TodoListView)
        else:
            return self.query_one("#todos-all", TodoListView)

    def _get_status_for_active_tab(self) -> str | None:
        """Get the status filter for the active tab."""
        tabbed = self.query_one(TabbedContent)
        if tabbed.active == "pending-pane":
            return "pending"
        elif tabbed.active == "completed-pane":
            return "completed"
        else:
            return None  # Show all

    def _load_todos(self) -> None:
        """Load todos from the database based on active tab filter."""
        status_filter = self._get_status_for_active_tab()
        self._all_todos = self.db.get_todos(status=status_filter)
        self._update_all_lists()
        self._update_status_bar()

    def _update_all_lists(self) -> None:
        """Update all three list views (pending, completed, all)."""
        # Get all todos for populating all views
        all_todos = self.db.get_todos(status=None)
        pending_todos = [t for t in all_todos if t.status == "pending"]
        completed_todos = [t for t in all_todos if t.status == "completed"]
        
        # Update each list view
        try:
            pending_list = self.query_one("#todos", TodoListView)
            pending_list.update_todos(pending_todos)
        except Exception:
            pass
        
        try:
            completed_list = self.query_one("#todos-completed", TodoListView)
            completed_list.update_todos(completed_todos)
        except Exception:
            pass
        
        try:
            all_list = self.query_one("#todos-all", TodoListView)
            all_list.update_todos(all_todos)
        except Exception:
            pass

    def _update_list(self) -> None:
        """Update the active todo list view."""
        list_view = self._get_active_list_view()
        list_view.update_todos(self._all_todos)

    def _update_status_bar(self) -> None:
        """Update the status bar with counts."""
        tabbed = self.query_one(TabbedContent)

        # Get total counts from database
        all_todos = self.db.get_all_todos()
        total_pending = sum(1 for t in all_todos if t.status == "pending")
        total_completed = sum(1 for t in all_todos if t.status == "completed")

        status_bar = self.query_one("#status-bar", Label)

        if tabbed.active == "pending-pane":
            status_bar.update(
                f"⏳ Pending: {len(self._all_todos)} ({total_pending} total) | "
                f"✓ Completed: {total_completed} | "
                "a: Add | j/k: Navigate | space: Complete | +/-: Priority | "
                "e: Edit | d: Delete | 1/2/3: Tabs | q/?: Quit/Help"
            )
        elif tabbed.active == "completed-pane":
            status_bar.update(
                f"✓ Completed: {len(self._all_todos)} ({total_completed} total) | "
                f"⏳ Pending: {total_pending} | "
                "a: Add | j/k: Navigate | +/-: Priority | "
                "e: Edit | d: Delete | 1/2/3: Tabs | q/?: Quit/Help"
            )
        else:  # all-pane
            status_bar.update(
                f"📋 All: {len(self._all_todos)} "
                f"({total_pending} pending, {total_completed} completed) | "
                "a: Add | j/k: Navigate | space: Complete | +/-: Priority | "
                "e: Edit | d: Delete | 1/2/3: Tabs | q/?: Quit/Help"
            )

    def action_cursor_down(self) -> None:
        """Move cursor down in todo list."""
        list_view = self._get_active_list_view()
        list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in todo list."""
        list_view = self._get_active_list_view()
        list_view.action_cursor_up()

    def action_toggle_complete(self) -> None:
        """Mark the selected todo as complete or incomplete."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        try:
            if todo.status == "completed":
                # Mark as incomplete
                self.db.update_todo(
                    todo.id,
                    status="pending",
                    completed_at=None,
                )
                self.notify(f"⏳ Task #{todo.id} marked as pending", timeout=1.5)
            else:
                # Mark as complete
                self.db.update_todo(
                    todo.id,
                    status="completed",
                    completed_at=datetime.now(),
                )

                # Auto-log to journal
                entry_content = f"Completed: {todo.content}"
                self.db.add_entry(
                    content=entry_content,
                    tags=todo.tag_names,
                    project=todo.project,
                    created_at=datetime.now(),
                )

                self.notify(f"✅ Task #{todo.id} completed & logged!", timeout=2)

            # Refresh the list
            self._load_todos()

        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=3)

    def action_edit(self) -> None:
        """Edit the selected todo."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, str | None, list[str] | None, str | None]
        ) -> None:
            content, due_date_str, tags, project = result
            
            # Check if anything changed
            content_changed = content is not None and content != todo.content
            due_date_changed = due_date_str is not None
            tags_changed = tags is not None
            project_changed = project is not None and project != todo.project
            
            # Handle cancel (all None)
            if result == (None, None, None, None):
                return
            
            try:
                updates = {}
                notifications = []
                
                # Handle content update
                if content_changed:
                    updates["content"] = content
                    notifications.append("content updated")
                
                # Handle due date update
                if due_date_changed:
                    if due_date_str is None or due_date_str.strip() == "":
                        # Clear the due date
                        updates["due_date"] = None
                        notifications.append("due date cleared")
                    else:
                        # Parse and set new due date
                        from ..date_utils import parse_natural_date
                        try:
                            due_date = parse_natural_date(due_date_str)
                            updates["due_date"] = due_date
                            notifications.append(f"due: {due_date.strftime('%Y-%m-%d')}")
                        except ValueError as e:
                            self.notify(
                                f"Invalid date format: {e}",
                                severity="error",
                                timeout=3,
                            )
                            return
                
                # Handle tags update
                if tags_changed:
                    updates["tags"] = tags
                    if tags:
                        notifications.append(f"tags: {', '.join(tags)}")
                    else:
                        notifications.append("tags cleared")
                
                # Handle project update
                if project_changed:
                    updates["project"] = project if project else None
                    if project:
                        notifications.append(f"project: {project}")
                    else:
                        notifications.append("project cleared")
                
                # Apply updates if any
                if updates:
                    self.db.update_todo(todo.id, **updates)
                    self.notify(f"Task #{todo.id}: {'; '.join(notifications)}", timeout=2)
                    self._load_todos()

            except Exception as e:
                self.notify(
                    f"Error updating task: {e}",
                    severity="error",
                    timeout=3,
                )

        self.push_screen(EditTodoModal(todo), on_dismiss)

    def action_add(self) -> None:
        """Add a new todo task."""
        def on_dismiss(result: str | None) -> None:
            if result:
                try:
                    task = self.db.add_todo(
                        content=result,
                        priority="normal",
                        project=None,
                        tags=[],
                    )
                    self.notify(f"✅ Task #{task.id} added!", timeout=1.5)
                    self._load_todos()
                except Exception as e:
                    self.notify(
                        f"Error adding task: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(AddTodoModal(), on_dismiss)

    def action_increase_priority(self) -> None:
        """Increase the priority of the selected todo."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        if todo.status == "completed":
            self.notify(
                "Cannot change priority of completed task",
                severity="information",
                timeout=1.5,
            )
            return

        priority_order = ["low", "normal", "high", "urgent"]
        current_idx = priority_order.index(todo.priority)
        if current_idx < len(priority_order) - 1:
            new_priority = priority_order[current_idx + 1]
            try:
                self.db.update_todo(todo.id, priority=new_priority)
                self.notify(
                    f"Priority: {todo.priority} → {new_priority}",
                    timeout=1.5,
                )
                self._load_todos()
            except Exception as e:
                self.notify(
                    f"Error updating priority: {e}",
                    severity="error",
                    timeout=3,
                )
        else:
            self.notify(
                "Already at highest priority (urgent)",
                severity="information",
                timeout=1.5,
            )

    def action_decrease_priority(self) -> None:
        """Decrease the priority of the selected todo."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        if todo.status == "completed":
            self.notify(
                "Cannot change priority of completed task",
                severity="information",
                timeout=1.5,
            )
            return

        priority_order = ["low", "normal", "high", "urgent"]
        current_idx = priority_order.index(todo.priority)
        if current_idx > 0:
            new_priority = priority_order[current_idx - 1]
            try:
                self.db.update_todo(todo.id, priority=new_priority)
                self.notify(
                    f"Priority: {todo.priority} → {new_priority}",
                    timeout=1.5,
                )
                self._load_todos()
            except Exception as e:
                self.notify(
                    f"Error updating priority: {e}",
                    severity="error",
                    timeout=3,
                )
        else:
            self.notify(
                "Already at lowest priority (low)",
                severity="information",
                timeout=1.5,
            )

    def action_edit_tags(self) -> None:
        """Edit the selected todo's tags."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: list[str] | None) -> None:
            if result is not None and result != todo.tag_names:
                try:
                    self.db.update_todo(todo.id, tags=result)
                    self.notify(f"Task #{todo.id} tags updated", timeout=1.5)
                    self._load_todos()
                except Exception as e:
                    self.notify(
                        f"Error updating tags: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditTagsModal(todo), on_dismiss)

    def action_edit_project(self) -> None:
        """Edit the selected todo's project."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: str | None) -> None:
            if result is not None and result != todo.project:
                try:
                    self.db.update_todo(todo.id, project=result)
                    self.notify(f"Task #{todo.id} project updated", timeout=1.5)
                    self._load_todos()
                except Exception as e:
                    self.notify(
                        f"Error updating project: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditProjectModal(todo), on_dismiss)

    def action_delete(self) -> None:
        """Delete the selected todo."""
        list_view = self._get_active_list_view()
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(confirmed: bool) -> None:
            if confirmed:
                try:
                    self.db.delete_todo(todo.id)
                    self.notify(f"Task #{todo.id} deleted", timeout=1.5)
                    self._load_todos()
                except Exception as e:
                    self.notify(
                        f"Error deleting task: {e}",
                        severity="error",
                        timeout=3,
                    )

        # Show confirmation dialog
        self._show_delete_confirmation(todo.id, on_dismiss)

    def _show_delete_confirmation(
        self, todo_id: int, callback: Callable[[bool], None]
    ) -> None:
        """Show a delete confirmation dialog."""

        class ConfirmModal(ModalScreen):  # type: ignore[type-arg]
            """Confirmation dialog for deletion."""

            CSS = """
            ConfirmModal {
                align: center middle;
            }

            #confirm-container {
                width: 60;
                height: auto;
                background: $surface;
                border: thick $error;
                padding: 1 3;
            }

            #confirm-message {
                text-align: center;
                padding: 1 0;
            }

            #confirm-buttons {
                align: center middle;
                padding: 1 0;
            }
            """

            BINDINGS = [
                ("y", "confirm", "Yes"),
                ("n", "cancel", "No"),
                ("escape", "cancel", "Cancel"),
            ]

            def __init__(self, tid: int, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.todo_id = tid

            def compose(self) -> ComposeResult:
                with Container(id="confirm-container"):
                    yield Label(
                        f"Delete task #{self.todo_id}?",
                        id="confirm-message",
                    )
                    with Container(id="confirm-buttons"):
                        from textual.widgets import Button

                        yield Button("Yes", id="yes-btn", variant="error")
                        yield Button("No", id="no-btn", variant="default")

            def action_confirm(self) -> None:
                self.dismiss(True)

            def action_cancel(self) -> None:
                self.dismiss(False)

            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "yes-btn":
                    self.action_confirm()
                elif event.button.id == "no-btn":
                    self.action_cancel()

        self.push_screen(ConfirmModal(todo_id), callback)  # type: ignore[arg-type]

    def action_refresh(self) -> None:
        """Refresh the todo list."""
        self._load_todos()
        self.notify("List refreshed", timeout=1)

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["pending-pane", "completed-pane", "all-pane"]
        current_idx = tabs.index(tabbed.active)
        next_idx = (current_idx + 1) % len(tabs)
        tabbed.active = tabs[next_idx]
        status_map = {
            "pending-pane": "pending",
            "completed-pane": "completed",
            "all-pane": "all",
        }
        self.filter_status = status_map[tabs[next_idx]]

    def action_switch_tab_pending(self) -> None:
        """Switch to the Pending tab."""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = "pending-pane"
        self.filter_status = "pending"

    def action_switch_tab_completed(self) -> None:
        """Switch to the Completed tab."""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = "completed-pane"
        self.filter_status = "completed"

    def action_switch_tab_all(self) -> None:
        """Switch to the All tab."""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = "all-pane"
        self.filter_status = "all"

    def action_goto_help(self) -> None:
        """Navigate to the help TUI."""
        from .help_tui import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:  # type: ignore[override]
        """Quit the todo application."""
        self.exit()
