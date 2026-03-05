"""Interactive search TUI using Textual.

This module provides a real-time fuzzy search interface for
journal entries and to-do tasks.
"""

from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

from ..database import Entry, Todo
from ..search_utils import search_items


class EntryResultsView(ListView):
    """ListView for displaying entry search results."""

    def __init__(self, items: List[tuple] = None, **kwargs):
        """Initialize the entry results view.

        Args:
            items: Optional list of (entry, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: List[tuple]) -> None:
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
        list_item.item_data = {"item": entry, "score": score, "type": "entry"}
        self.append(list_item)

    def _format_entry(self, entry: Entry, score: float) -> str:
        """Format an entry for display.

        Args:
            entry: Entry object to format.
            score: Match score.

        Returns:
            Formatted string with markup.
        """
        date_str = entry.created_at.strftime("%Y-%m-%d")
        time_str = entry.created_at.strftime("%I:%M %p")
        score_color = self._get_score_color(score)
        tags_str = ""
        if entry.tag_names:
            tags_str = f" [yellow]#{' #'.join(entry.tag_names)}[/yellow]"
        project_str = f" [purple]{entry.project}[/purple]" if entry.project else ""

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

    def __init__(self, items: List[tuple] = None, **kwargs):
        """Initialize the todo results view.

        Args:
            items: Optional list of (todo, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: List[tuple]) -> None:
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
        list_item.item_data = {"item": todo, "score": score, "type": "todo"}
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


class SearchApp(App):
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
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("enter", "select", "Select"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("ctrl+n", "toggle_type", "Toggle Type"),
    ]

    search_type = reactive("all")

    def __init__(
        self,
        db,
        console,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ):
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
        self._all_entries = []
        self._all_todos = []
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
            f"j/k: Navigate | Enter: Select | /: Search | n: Toggle | q: Quit"
        )

    def _get_active_view(self):
        """Get the currently active results view based on search type."""
        if self.search_type == "entry":
            return self.query_one("#entries-results", EntryResultsView)
        elif self.search_type == "todo":
            return self.query_one("#todos-results", TodoResultsView)
        else:
            # For "all" mode, prefer entries view if it has items, otherwise todos
            entries_view = self.query_one("#entries-results", EntryResultsView)
            if entries_view.child_count > 0:
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

        item_data = results_view.highlighted_child.item_data
        if item_data:
            content = item_data["item"].content

            # Copy to clipboard
            try:
                import pyperclip

                pyperclip.copy(content)
                self.notify(f"Copied: {content[:50]}...", timeout=2)
            except Exception:
                self.notify(f"Content: {content}", timeout=3)

    def action_quit(self) -> None:
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
