"""Interactive todo board TUI using Textual.

This module provides a real-time interface for managing tasks,
marking them complete, and editing/deleting.
"""

from datetime import datetime
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
)

from ..database import Todo


class TodoListItem(ListItem):
    """Custom list item for todo tasks."""

    def __init__(self, todo: Todo, **kwargs):
        """Initialize the todo list item.

        Args:
            todo: Todo object to display.
            **kwargs: Additional arguments passed to ListItem.
        """
        super().__init__(**kwargs)
        self.todo = todo


class EditTodoModal(ModalScreen):
    """Modal dialog for editing a todo."""

    CSS = """
    EditTodoModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 80;
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
        height: 5;
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
        ("enter", "save", "Save"),
    ]

    def __init__(self, todo: Todo, **kwargs):
        """Initialize the edit modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Task #{self.todo.id}", id="edit-modal-title")
            yield Input(
                value=self.todo.content,
                id="edit-input",
                placeholder="Enter task content...",
            )
            with Container(id="edit-buttons"):
                from textual.widgets import Button

                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        """Save the edited content."""
        input_widget = self.query_one("#edit-input", Input)
        self.result = input_widget.value.strip()
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditTagsModal(ModalScreen):
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

    def __init__(self, todo: Todo, **kwargs):
        """Initialize the edit tags modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: Optional[List[str]] = None

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

    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditProjectModal(ModalScreen):
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

    def __init__(self, todo: Todo, **kwargs):
        """Initialize the edit project modal.

        Args:
            todo: Todo object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: Optional[str] = None

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

    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class TodoListView(ListView):
    """ListView for displaying todo tasks."""

    def __init__(self, todos: List[Todo] = None, **kwargs):
        """Initialize the todo list view.

        Args:
            todos: Optional list of Todo objects to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._todos = todos or []

    def update_todos(self, todos: List[Todo]) -> None:
        """Update the displayed todos.

        Args:
            todos: List of Todo objects to display.
        """
        self._todos = todos
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
        tags_str = f" [dim]#{', '.join(todo.tag_names)}[/dim]" if todo.tag_names else ""
        project_str = f" [dim]{todo.project}[/dim]" if todo.project else ""

        if todo.status == "completed":
            return (
                f"[dim][cyan][{todo.id}][/cyan] "
                f"[{color}]✓[/{color}] "
                f"[strike]{todo.content}[/strike]{tags_str}{project_str}[/dim]"
            )
        else:
            return (
                f"[cyan][{todo.id}][/cyan] "
                f"[{color}]{todo.priority.upper()}[/{color}] "
                f"{todo.content}{tags_str}{project_str}"
            )

    @property
    def selected_todo(self) -> Optional[Todo]:
        """Get the currently selected todo."""
        if self.highlighted_child is None:
            return None
        if isinstance(self.highlighted_child, TodoListItem):
            return self.highlighted_child.todo
        return None


class TodoApp(App):
    """Interactive todo board application.

    Provides a real-time interface for managing tasks.

    Key bindings:
        j/k: Navigate up/down
        Space: Mark task as complete
        e: Edit selected task
        d: Delete selected task
        Enter: Toggle complete status
        Escape/q: Quit
        /: Focus search/filter (future)
        r: Refresh list
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
    """

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("space", "toggle_complete", "Complete"),
        ("e", "edit", "Edit"),
        ("d", "delete", "Delete"),
        ("enter", "toggle_complete", "Toggle"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("+", "increase_priority", "Priority +"),
        ("-", "decrease_priority", "Priority -"),
        ("t", "edit_tags", "Tags"),
        ("p", "edit_project", "Project"),
    ]

    def __init__(
        self,
        db,
        console,
        show_all: bool = False,
        **kwargs,
    ):
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
        self._all_todos: List[Todo] = []

    def compose(self) -> ComposeResult:
        """Compose the todo UI layout."""
        yield Header()
        with Vertical():
            with Container(id="header-container"):
                yield Label("📋 Todo Board", id="title")
                yield Label(
                    "Space: Complete | e: Edit | +/-: Priority | "
                    "t: Tags | p: Project | d: Delete | q: Quit",
                    id="subtitle",
                )
            with Container(id="list-container"):
                yield TodoListView(id="todos")
        yield Label("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load data and focus the list on mount."""
        self._load_todos()
        self.query_one(TodoListView).focus()

    def _load_todos(self) -> None:
        """Load todos from the database."""
        status_filter = None if self.show_all else "pending"
        self._all_todos = self.db.get_todos(status=status_filter)
        self._update_list()
        self._update_status_bar()

    def _update_list(self) -> None:
        """Update the todo list view."""
        list_view = self.query_one(TodoListView)
        list_view.update_todos(self._all_todos)

    def _update_status_bar(self) -> None:
        """Update the status bar with counts."""
        pending_count = sum(1 for t in self._all_todos if t.status == "pending")
        completed_count = sum(1 for t in self._all_todos if t.status == "completed")
        total = len(self._all_todos)

        status_bar = self.query_one("#status-bar", Label)
        if self.show_all:
            status_bar.update(
                f"Showing {total} tasks | "
                f"[class=pending-count]{pending_count} pending[/] | "
                f"[class=completed-count]{completed_count} completed[/] | "
                "j/k: Navigate | space: Complete | +/-: Priority | "
                "e: Edit | t: Tags | p: Project | d: Delete | r: Refresh | q: Quit"
            )
        else:
            status_bar.update(
                f"Showing {pending_count} pending tasks | "
                "j/k: Navigate | space: Complete | +/-: Priority | "
                "e: Edit | t: Tags | p: Project | d: Delete | r: Refresh | q: Quit"
            )

    def action_cursor_down(self) -> None:
        """Move cursor down in todo list."""
        list_view = self.query_one(TodoListView)
        list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in todo list."""
        list_view = self.query_one(TodoListView)
        list_view.action_cursor_up()

    def action_toggle_complete(self) -> None:
        """Mark the selected todo as complete."""
        list_view = self.query_one(TodoListView)
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        if todo.status == "completed":
            self.notify(
                "Task is already completed",
                severity="information",
                timeout=1.5,
            )
            return

        try:
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
            self.notify(f"Error completing task: {e}", severity="error", timeout=3)

    def action_edit(self) -> None:
        """Edit the selected todo."""
        list_view = self.query_one(TodoListView)
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: Optional[str]) -> None:
            if result is not None and result != todo.content:
                try:
                    self.db.update_todo(todo.id, content=result)
                    self.notify(f"Task #{todo.id} updated", timeout=1.5)
                    self._load_todos()
                except Exception as e:
                    self.notify(
                        f"Error updating task: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditTodoModal(todo), on_dismiss)

    def action_increase_priority(self) -> None:
        """Increase the priority of the selected todo."""
        list_view = self.query_one(TodoListView)
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
        list_view = self.query_one(TodoListView)
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
        list_view = self.query_one(TodoListView)
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: Optional[List[str]]) -> None:
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
        list_view = self.query_one(TodoListView)
        todo = list_view.selected_todo

        if todo is None:
            self.notify("No task selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: Optional[str]) -> None:
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
        list_view = self.query_one(TodoListView)
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

    def _show_delete_confirmation(self, todo_id: int, callback) -> None:
        """Show a delete confirmation dialog."""

        class ConfirmModal(ModalScreen):
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

            def __init__(self, tid: int, **kwargs):
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

            def on_button_pressed(self, event) -> None:
                if event.button.id == "yes-btn":
                    self.action_confirm()
                elif event.button.id == "no-btn":
                    self.action_cancel()

        self.push_screen(ConfirmModal(todo_id), callback)

    def action_refresh(self) -> None:
        """Refresh the todo list."""
        self._load_todos()
        self.notify("List refreshed", timeout=1)

    def action_quit(self) -> None:
        """Quit the todo application."""
        self.exit()
