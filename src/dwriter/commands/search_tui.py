"""Interactive search TUI using Textual.

This module provides a real-time fuzzy search interface for
journal entries and to-do tasks.
"""

from __future__ import annotations

from typing import Any

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
    Static,
)

from ..database import Entry, Todo
from ..search_utils import search_items


class EditContentModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing content."""

    CSS = """
    EditContentModal {
        align: center middle;
    }

    #modal-container {
        width: 90;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 3;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-input {
        width: 100%;
        height: 6;
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

    def __init__(
        self, content: str, title: str = "Edit Content", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.title_text = title
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(self.title_text, id="modal-title")
            yield Input(
                value=self.content,
                id="edit-input",
                placeholder="Enter content...",
            )
            with Container(id="edit-buttons"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        input_widget = self.query_one("#edit-input", Input)
        self.result = input_widget.value.strip()
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditTagsModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing tags."""

    CSS = """
    EditTagsModal {
        align: center middle;
    }

    #modal-container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 3;
    }

    #modal-title {
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

    def __init__(
        self, tags: list[str], title: str = "Edit Tags", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.tags = tags
        self.title_text = title
        self.result: list[str] | None = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(self.title_text, id="modal-title")
            yield Input(
                value=", ".join(self.tags),
                id="edit-input",
                placeholder="tag1, tag2, tag3",
            )
            yield Label("Separate tags with commas", id="edit-hint")
            with Container(id="edit-buttons"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        input_widget = self.query_one("#edit-input", Input)
        value = input_widget.value.strip()
        if value:
            self.result = [t.strip() for t in value.split(",") if t.strip()]
        else:
            self.result = []
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EditProjectModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing project."""

    CSS = """
    EditProjectModal {
        align: center middle;
    }

    #modal-container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 3;
    }

    #modal-title {
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

    def __init__(
        self, project: str | None, title: str = "Edit Project", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.project = project
        self.title_text = title
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(self.title_text, id="modal-title")
            yield Input(
                value=self.project or "",
                id="edit-input",
                placeholder="Project name (optional)",
            )
            with Container(id="edit-buttons"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def action_save(self) -> None:
        input_widget = self.query_one("#edit-input", Input)
        self.result = input_widget.value.strip() or None
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class EntryResultsView(ListView):
    """ListView for displaying entry search results."""

    def __init__(
        self, items: list[tuple[Entry, float]] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the entry results view.

        Args:
            items: Optional list of (entry, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: list[tuple[Entry, float]]) -> None:
        """Update the displayed items.

        Args:
            items: List of (entry, score) tuples to display.
        """
        self._items = items
        self.clear()
        for entry, score in items:
            self.append_item(entry, score)

    def append_item(self, entry: Entry, score: float) -> None:
        """Append a single entry to the list.

        Args:
            entry: Entry object to display.
            score: Match score (0-100).
        """
        label = self._format_entry(entry, score)
        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": entry, "score": score, "type": "entry"}  # type: ignore[attr-defined]
        self.append(list_item)

    def _format_entry(self, entry: Entry, score: float) -> str:
        """Format an entry for display.

        Args:
            entry: Entry object to format.
            score: Match score.

        Returns:
            Formatted string with markup.
        """
        from ..ui_utils import format_entry_datetime
        date_str, time_str = format_entry_datetime(entry)
        score_color = self._get_score_color(score)
        tags_str = ""
        if entry.tag_names:
            tags_str = f" [yellow]#{' #'.join(entry.tag_names)}[/yellow]"
        project_str = f" [purple]{entry.project}[/purple]" if entry.project else ""

        # Display with or without time based on whether it's a past date
        if time_str is None:
            return (
                f"[magenta][{entry.id}][/magenta] "
                f"[dim]{date_str}[/dim] | "
                f"{entry.content}{tags_str}{project_str} "
                f"[{score_color}]({int(score)}%)[/{score_color}]"
            )
        else:
            return (
                f"[magenta][{entry.id}][/magenta] "
                f"[dim]{date_str} {time_str}[/dim] | "
                f"{entry.content}{tags_str}{project_str} "
                f"[{score_color}]({int(score)}%)[/{score_color}]"
            )

    def _get_score_color(self, score: float) -> str:
        """Get the color for a match score.

        Args:
            score: Match score (0-100).

        Returns:
            Color name string.
        """
        if score >= 90:
            return "green"
        elif score >= 75:
            return "yellow"
        else:
            return "dim"


class TodoResultsView(ListView):
    """ListView for displaying todo search results."""

    def __init__(
        self, items: list[tuple[Todo, float]] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the todo results view.

        Args:
            items: Optional list of (todo, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: list[tuple[Todo, float]]) -> None:
        """Update the displayed items.

        Args:
            items: List of (todo, score) tuples to display.
        """
        self._items = items
        self.clear()
        for todo, score in items:
            self.append_item(todo, score)

    def append_item(self, todo: Todo, score: float) -> None:
        """Append a single todo to the list.

        Args:
            todo: Todo object to display.
            score: Match score (0-100).
        """
        label = self._format_todo(todo, score)
        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": todo, "score": score, "type": "todo"}  # type: ignore[attr-defined]
        self.append(list_item)

    def _format_todo(self, todo: Todo, score: float) -> str:
        """Format a todo for display.

        Args:
            todo: Todo object to format.
            score: Match score.

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
        score_color = self._get_score_color(score)
        # Match entry formatting: yellow tags, purple project
        if todo.tag_names:
            tags_str = f" [yellow]#{' #'.join(todo.tag_names)}[/yellow]"
        else:
            tags_str = ""
        if todo.project:
            project_str = f" [purple]{todo.project}[/purple]"
        else:
            project_str = ""

        status_prefix = "[dim][strike]" if todo.status == "completed" else ""
        status_suffix = "[/strike][/dim]" if todo.status == "completed" else ""

        return (
            f"{status_prefix}[cyan][{todo.id}][/cyan] "
            f"[{color}]{todo.priority.upper()}[/{color}] | "
            f"{todo.content}{tags_str}{project_str} "
            f"[{score_color}]({int(score)}%)[/{score_color}]{status_suffix}"
        )

    def _get_score_color(self, score: float) -> str:
        """Get the color for a match score.

        Args:
            score: Match score (0-100).

        Returns:
            Color name string.
        """
        if score >= 90:
            return "green"
        elif score >= 75:
            return "yellow"
        else:
            return "dim"


class SearchApp(App):  # type: ignore[type-arg]
    """Interactive search application.

    Provides real-time fuzzy search across journal entries and to-dos.

    Key bindings:
        j/k: Navigate up/down
        Enter: Select highlighted item (copy content)
        Escape/q: Quit
        /: Focus search input
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #search-container {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        background: $panel;
    }

    #search-input {
        width: 100%;
    }

    #results-container {
        height: 1fr;
        margin: 0 2;
    }

    #entries-section, #todos-section {
        height: 1fr;
        margin: 0 0 1 0;
    }

    .section-header {
        text-style: bold;
        padding: 0 0 0 1;
        background: $panel;
    }

    .entries-header {
        color: $accent;
    }

    .todos-header {
        color: $success;
    }

    EntryResultsView, TodoResultsView {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    EntryResultsView:focus, TodoResultsView:focus {
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
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("enter", "select", "Select"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("/", "focus_search", "Search"),
        Binding("ctrl+n", "toggle_type", "Toggle Type"),
        Binding("e", "edit_content", "Edit"),
        Binding("t", "edit_tags", "Tags"),
        Binding("p", "edit_project", "Project"),
        Binding("+", "increase_priority", "Priority +"),
        Binding("-", "decrease_priority", "Priority -"),
        Binding("?", "goto_help", "Help", show=True),
    ]

    search_type = reactive("all")

    def __init__(
        self,
        db: Any,
        console: Any,
        project: str | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the search application.

        Args:
            db: Database instance for querying entries and todos.
            console: Rich console instance.
            project: Optional project filter.
            tags: Optional list of tag filters.
            **kwargs: Additional arguments passed to App.
        """
        super().__init__(**kwargs)
        self.db = db
        self.console = console
        self.project = project
        self.tags = tags or []
        self._all_entries: list[Entry] = []
        self._all_todos: list[Todo] = []
        self._focused_section = "entries"

    def compose(self) -> ComposeResult:
        """Compose the search UI layout."""
        yield Header()
        with Vertical():
            with Container(id="search-container"):
                yield Input(
                    placeholder="Type to search entries and todos...",
                    id="search-input",
                )
            with Container(id="results-container"):
                # Entries section
                with Container(id="entries-section"):
                    yield Static("📝 ENTRIES", classes="section-header entries-header")
                    yield EntryResultsView(id="entries-results")
                # Todos section
                with Container(id="todos-section"):
                    yield Static("✅ TO-DOS", classes="section-header todos-header")
                    yield TodoResultsView(id="todos-results")
        yield Label(
            "j/k: Navigate | Enter: Select | /: Search | n: Toggle type | q: Quit",
            id="status-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load data and focus the search input on mount."""
        self._load_data()
        self.query_one("#search-input", Input).focus()

    def _load_data(self) -> None:
        """Load entries and todos from the database."""
        self._all_entries = self.db.get_all_entries(
            project=self.project if self.project else None,
            tags=self.tags if self.tags else None,
        )
        self._all_todos = self.db.get_all_todos(
            project=self.project if self.project else None,
            tags=self.tags if self.tags else None,
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes.

        Args:
            event: Input change event containing the query.
        """
        if event.input.id == "search-input":
            self._perform_search(event.value)

    def _perform_search(self, query: str) -> None:
        """Execute fuzzy search and update results.

        Args:
            query: Search query string.
        """
        entries_view = self.query_one("#entries-results", EntryResultsView)
        todos_view = self.query_one("#todos-results", TodoResultsView)
        entries_view.clear()
        todos_view.clear()

        if not query.strip():
            self._update_status_bar(0, 0)
            return

        # Search entries
        matched_entries = []
        if self.search_type in ["all", "entry"]:
            matched_entries = search_items(
                query, self._all_entries, limit=50, threshold=50
            )
            for entry, score in matched_entries:
                entries_view.append_item(entry, score)

        # Search todos
        matched_todos = []
        if self.search_type in ["all", "todo"]:
            matched_todos = search_items(
                query, self._all_todos, limit=50, threshold=50
            )
            for todo, score in matched_todos:
                todos_view.append_item(todo, score)

        self._update_status_bar(len(matched_entries), len(matched_todos))

    def _update_status_bar(self, entry_count: int, todo_count: int) -> None:
        """Update the status bar with result counts.

        Args:
            entry_count: Number of matched entries.
            todo_count: Number of matched todos.
        """
        total = entry_count + todo_count
        type_label = (
            "Entries + Todos"
            if self.search_type == "all"
            else f"{self.search_type.capitalize()}s"
        )
        self.query_one("#status-bar", Label).update(
            f"Found {total} matches ({entry_count} entries, {todo_count} todos) | "
            f"Type: {type_label} | "
            "j/k: Navigate | Enter: Select | e: Edit | t: Tags | p: Project | "
            "+/-: Priority | /: Search | n: Toggle | q: Quit"
        )

    def _get_active_view(self) -> EntryResultsView | TodoResultsView:
        """Get the currently active results view based on focus or search type."""
        # Check which view is actually focused
        focused = self.focused
        if isinstance(focused, (EntryResultsView, TodoResultsView)):
            return focused

        # Fallback to search_type-based selection
        if self.search_type == "entry":
            return self.query_one("#entries-results", EntryResultsView)
        elif self.search_type == "todo":
            return self.query_one("#todos-results", TodoResultsView)
        else:
            # For "all" mode, prefer entries view if it has items, otherwise todos
            entries_view = self.query_one("#entries-results", EntryResultsView)
            if entries_view._items:
                return entries_view
            return self.query_one("#todos-results", TodoResultsView)

    def action_cursor_down(self) -> None:
        """Move cursor down in results list."""
        results_view = self._get_active_view()
        results_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in results list."""
        results_view = self._get_active_view()
        results_view.action_cursor_up()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_select(self) -> None:
        """Select the highlighted item and copy its content."""
        results_view = self._get_active_view()
        if results_view.highlighted_child is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        item_data = results_view.highlighted_child.item_data  # type: ignore[attr-defined]
        if item_data:
            content = item_data["item"].content
            try:
                import pyperclip
                pyperclip.copy(content)
                self.notify(f"Copied: {content[:50]}...", timeout=2)
            except Exception:
                self.notify(f"Content: {content}", timeout=3)

    def _get_selected_item(
        self,
    ) -> tuple[
        Entry | Todo | None,
        str | None,
        EntryResultsView | TodoResultsView | None,
    ]:
        """Get currently selected item and its type."""
        results_view = self._get_active_view()
        if results_view.highlighted_child is None:
            return None, None, None
        item_data = results_view.highlighted_child.item_data  # type: ignore[attr-defined]
        if not item_data:
            return None, None, None
        return item_data["item"], item_data["type"], results_view

    def action_edit_content(self) -> None:
        """Edit content of selected item."""
        item, item_type, _ = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: str | None) -> None:
            if result is not None and result != item.content:
                try:
                    if not result:
                        self.notify(
                            "Content cannot be empty",
                            severity="warning",
                            timeout=2,
                        )
                        return
                    if item_type == "entry":
                        self.db.update_entry(item.id, content=result)
                    else:
                        self.db.update_todo(item.id, content=result)
                    self.notify(
                        f"{item_type.title()} #{item.id} updated",  # type: ignore[union-attr]
                        timeout=1.5,
                    )
                    search_input = self.query_one("#search-input", Input)
                    self._perform_search(search_input.value)
                except Exception as e:
                    self.notify(
                        f"Error updating: {e}",
                        severity="error",
                        timeout=3,
                    )

        if item_type == "entry":
            title = f"Edit Entry #{item.id}"
        elif item_type == "todo":
            title = f"Edit Task #{item.id}"
        else:
            return
        self.push_screen(EditContentModal(item.content, title), on_dismiss)

    def action_edit_tags(self) -> None:
        """Edit tags of selected item."""
        item, item_type, _ = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: list[str] | None) -> None:
            if result is not None and result != item.tag_names:
                try:
                    if item_type == "entry":
                        self.db.update_entry(item.id, tags=result)
                    else:
                        self.db.update_todo(item.id, tags=result)
                    msg = f"{item_type.title()} #{item.id} tags updated"  # type: ignore[union-attr]
                    self.notify(msg, timeout=1.5)
                    search_input = self.query_one("#search-input", Input)
                    self._perform_search(search_input.value)
                except Exception as e:
                    self.notify(
                        f"Error updating tags: {e}",
                        severity="error",
                        timeout=3,
                    )

        if item_type == "entry":
            title = f"Edit Entry #{item.id} Tags"
        elif item_type == "todo":
            title = f"Edit Task #{item.id} Tags"
        else:
            return
        self.push_screen(EditTagsModal(item.tag_names, title), on_dismiss)

    def action_edit_project(self) -> None:
        """Edit project of selected item."""
        item, item_type, _ = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: str | None) -> None:
            if result is not None and result != item.project:
                try:
                    if item_type == "entry":
                        self.db.update_entry(item.id, project=result)
                    else:
                        self.db.update_todo(item.id, project=result)
                    msg = f"{item_type.title()} #{item.id} project updated"  # type: ignore[union-attr]
                    self.notify(msg, timeout=1.5)
                    search_input = self.query_one("#search-input", Input)
                    self._perform_search(search_input.value)
                except Exception as e:
                    self.notify(
                        f"Error updating project: {e}",
                        severity="error",
                        timeout=3,
                    )

        if item_type == "entry":
            title = f"Edit Entry #{item.id} Project"
        elif item_type == "todo":
            title = f"Edit Task #{item.id} Project"
        else:
            return
        self.push_screen(EditProjectModal(item.project, title), on_dismiss)

    def action_increase_priority(self) -> None:
        """Increase priority of selected todo."""
        item, item_type, _ = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return
        if item_type != "todo":
            self.notify(
                "Priority only applies to todos",
                severity="information",
                timeout=1.5,
            )
            return
        if item.status == "completed":  # type: ignore[union-attr]
            self.notify(
                "Cannot change priority of completed task",
                severity="information",
                timeout=1.5,
            )
            return

        priority_order = ["low", "normal", "high", "urgent"]
        current_idx = priority_order.index(item.priority)  # type: ignore[union-attr]
        if current_idx < len(priority_order) - 1:
            new_priority = priority_order[current_idx + 1]
            try:
                self.db.update_todo(item.id, priority=new_priority)
                msg = f"Priority: {item.priority} → {new_priority}"  # type: ignore[union-attr]
                self.notify(msg, timeout=1.5)
                search_input = self.query_one("#search-input", Input)
                self._perform_search(search_input.value)
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
        """Decrease priority of selected todo."""
        item, item_type, _ = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return
        if item_type != "todo":
            self.notify(
                "Priority only applies to todos",
                severity="information",
                timeout=1.5,
            )
            return
        if item.status == "completed":  # type: ignore[union-attr]
            self.notify(
                "Cannot change priority of completed task",
                severity="information",
                timeout=1.5,
            )
            return

        priority_order = ["low", "normal", "high", "urgent"]
        current_idx = priority_order.index(item.priority)  # type: ignore[union-attr]
        if current_idx > 0:
            new_priority = priority_order[current_idx - 1]
            try:
                self.db.update_todo(item.id, priority=new_priority)
                msg = f"Priority: {item.priority} → {new_priority}"  # type: ignore[union-attr]
                self.notify(msg, timeout=1.5)
                search_input = self.query_one("#search-input", Input)
                self._perform_search(search_input.value)
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

    def action_quit(self) -> None:  # type: ignore[override]
        """Quit the search application."""
        self.exit()

    def action_toggle_type(self) -> None:
        """Toggle between search types (all/entry/todo)."""
        types = ["all", "entry", "todo"]
        current_idx = types.index(self.search_type)
        next_idx = (current_idx + 1) % len(types)
        self.search_type = types[next_idx]

        # Re-run search with new type
        search_input = self.query_one("#search-input", Input)
        self._perform_search(search_input.value)

    def action_goto_help(self) -> None:
        """Navigate to the help TUI."""
        from .help_tui import HelpScreen
        self.app.push_screen(HelpScreen())

    def watch_search_type(self, value: str) -> None:
        """Handle search type changes.

        Args:
            value: New search type value.
        """
        type_labels = {
            "all": "Entries + Todos",
            "entry": "Entries Only",
            "todo": "Todos Only",
        }
        self.notify(f"Searching: {type_labels[value]}", timeout=1.5)
