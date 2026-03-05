"""Interactive search TUI using Textual.

This module provides a real-time fuzzy search interface for
journal entries and to-do tasks.
"""

from typing import Any, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView

from ..database import Entry, Todo
from ..search_utils import search_items


class SearchResultsView(ListView):
    """ListView for displaying search results."""

    def __init__(self, items: List[Any] = None, **kwargs):
        """Initialize the search results view.

        Args:
            items: Optional list of (item, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: List[Any]) -> None:
        """Update the displayed items.

        Args:
            items: List of (item, score) tuples to display.
        """
        self._items = items
        self.clear()
        for item, score in items:
            self.append_item(item, score)

    def append_item(self, item: Any, score: float) -> None:
        """Append a single item to the list.

        Args:
            item: Entry or Todo object to display.
            score: Match score (0-100).
        """
        if isinstance(item, Entry):
            label = self._format_entry(item, score)
        elif isinstance(item, Todo):
            label = self._format_todo(item, score)
        else:
            label = f"Unknown item type: {item}"

        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": item, "score": score}
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
        tags_str = f" [dim]#{', '.join(todo.tag_names)}[/dim]" if todo.tag_names else ""
        project_str = f" [dim]{todo.project}[/dim]" if todo.project else ""

        status_prefix = "[dim][strike]" if todo.status == "completed" else ""
        status_suffix = "[/strike][/dim]" if todo.status == "completed" else ""

        return (
            f"{status_prefix}[cyan][{todo.id}][/cyan] "
            f"[{color}]{todo.priority.upper()}[/{color}] "
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

    SearchResultsView {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    SearchResultsView:focus {
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

    .highlight {
        color: $accent;
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
                yield SearchResultsView(id="results")
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
        results_view = self.query_one("#results", SearchResultsView)
        results_view.clear()

        if not query.strip():
            return

        # Search entries
        if self.search_type in ["all", "entry"]:
            matched_entries = search_items(
                query, self._all_entries, limit=50, threshold=50
            )
            for entry, score in matched_entries:
                results_view.append_item(entry, score)

        # Search todos
        if self.search_type in ["all", "todo"]:
            matched_todos = search_items(
                query, self._all_todos, limit=50, threshold=50
            )
            for todo, score in matched_todos:
                results_view.append_item(todo, score)

        # Update status bar with result count
        total = len(matched_entries) + len(matched_todos) if query.strip() else 0
        type_label = (
            "Entries + Todos"
            if self.search_type == "all"
            else f"{self.search_type.capitalize()}s"
        )
        self.query_one("#status-bar", Label).update(
            f"Found {total} matches in {type_label} | "
            f"j/k: Navigate | Enter: Select | /: Search | n: Toggle type | q: Quit"
        )

    def action_cursor_down(self) -> None:
        """Move cursor down in results list."""
        results_view = self.query_one("#results", SearchResultsView)
        results_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in results list."""
        results_view = self.query_one("#results", SearchResultsView)
        results_view.action_cursor_up()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_select(self) -> None:
        """Select the highlighted item and copy its content."""
        results_view = self.query_one("#results", SearchResultsView)
        if results_view.highlighted_child is None:
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
