"""Search screen for dwriter TUI.

This module provides fuzzy search across journal entries and todos.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Header, Input, Label, ListItem, ListView

from ...database import Entry, Todo
from ...search_utils import search_items
from ..colors import (
    DUE_LATER,
    DUE_OVERDUE,
    DUE_SOON,
    DUE_TODAY,
    DUE_TOMORROW,
    PROJECT,
    TAG,
    get_icon,
)


class EntryResultsView(ListView):
    """ListView for displaying entry and todo search results."""

    def __init__(
        self, items: list[tuple[Entry | Todo, float]] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the entry results view.

        Args:
            items: Optional list of (entry, score) tuples to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: list[tuple[Entry | Todo, float]]) -> None:
        """Update the displayed items.

        Args:
            items: List of (entry, score) tuples to display.
        """
        self._items = items
        self.clear()
        for item, score in items:
            if isinstance(item, Entry):
                self.append_item(item, score)
            else:
                self.append_todo(item, score)

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

    def append_todo(self, todo: Todo, score: float) -> None:
        """Append a single todo to the list.

        Args:
            todo: Todo object to display.
            score: Match score (0-100).
        """
        label = self._format_todo(todo, score)
        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": todo, "score": score, "type": "todo"}  # type: ignore[attr-defined]
        self.append(list_item)

    def _format_entry(self, entry: Entry, score: float) -> str:
        """Format an entry for display.

        Args:
            entry: Entry object to format.
            score: Match score.

        Returns:
            Formatted string with markup.
        """
        from ...ui_utils import format_entry_datetime

        date_str, time_str = format_entry_datetime(entry)
        score_color = self._get_score_color(score)
        tags_str = ""
        if entry.tag_names:
            tags_str = f" [{TAG}]#{' #'.join(entry.tag_names)}[/{TAG}]"
        project_str = (
            f" [{PROJECT}]&{entry.project}[/{PROJECT}]" if entry.project else ""
        )

        # Hide ID, uniform format (no magenta ID)
        if time_str is None:
            return (
                f"[dim]{date_str}[/dim] | "
                f"{entry.content}{tags_str}{project_str} "
                f"[{score_color}]({int(score)}%)[/{score_color}]"
            )
        else:
            return (
                f"[dim]{date_str} {time_str}[/dim] | "
                f"{entry.content}{tags_str}{project_str} "
                f"[{score_color}]({int(score)}%)[/{score_color}]"
            )

    def _format_todo(self, todo: Todo, score: float) -> str:
        """Format a todo for display with ultra-compact metadata for 75-column terminals.

        Args:
            todo: Todo object to format.
            score: Match score.

        Returns:
            Formatted string with markup.
        """
        # Spelled out priority tags - explicit closing tags
        priority_map = {
            "urgent": "[red]\\[Urgent][/red]",
            "high": "[yellow]\\[High][/yellow]",
            "normal": "[white]\\[Normal][/white]",
            "low": "[dim]\\[Low][/dim]",
        }
        pri_str = priority_map.get(todo.priority, "[white]\\[N][/white]")

        score_color = "green" if score >= 90 else "yellow" if score >= 75 else "dim"

        d_str = "[dim]\\[---][/dim]"

        # Apply the exact same timestamp logic here
        if todo.status == "completed" and todo.completed_at:
            dt_str = todo.completed_at.strftime("%m-%d %H:%M")
            d_str = f"[cyan]{dt_str}[/cyan]"
        elif todo.due_date:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            due_only = todo.due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days = (due_only - today).days
            if days < 0:
                d_str = f"[{DUE_OVERDUE}]\\[OVD][/{DUE_OVERDUE}]"
            elif days == 0:
                d_str = f"[{DUE_TODAY}]\\[TDY][/{DUE_TODAY}]"
            elif days == 1:
                d_str = f"[{DUE_TOMORROW}]\\[TMR][/{DUE_TOMORROW}]"
            elif days <= 9:
                d_str = f"[{DUE_SOON}]\\[{days}d][/{DUE_SOON}]"
            elif days <= 99:
                d_str = f"[{DUE_SOON}]\\[{days}d][/{DUE_SOON}]"
            else:
                d_str = f"[{DUE_SOON}]\\[99+][/{DUE_SOON}]"

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

        score_str = f"[{score_color}]({int(score)}%)[/{score_color}]"

        # Format: Due date priority | #tags : Project on first line, content on second line
        first_line = f"{d_str} {pri_str} | {tags_str}{project_str} {score_str}"

        # Content on second line with indentation - add check emoji for completed todos
        if todo.status == "completed":
            use_emojis = self.app.ctx.config.display.use_emojis
            check_icon = get_icon("check", use_emojis)
            return f"[dim]{first_line}\n    {check_icon} {safe_content}[/dim]"

        return f"{first_line}\n    [bold white]{safe_content}[/bold white]"

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


class SearchScreen(Container):
    """Search screen for entries and todos."""

    DEFAULT_CSS = """
    SearchScreen {
        height: 1fr;
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

    EntryResultsView {
        height: 1fr;
        border: solid #45475a;
        padding: 1;
    }

    EntryResultsView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
    }

    Label {
        width: 100%;
    }

    #search-status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $foreground 60%;
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
    ]

    def __init__(
        self,
        ctx: AppContext,
        **kwargs: Any,
    ) -> None:
        """Initialize the search screen.

        Args:
            ctx: Application context with database and configuration.
            **kwargs: Additional arguments passed to Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._all_entries: list[Entry] = []
        self._all_todos: list[Todo] = []
        self._search_mode: str = "all"  # "all", "log", or "todo"

    def compose(self) -> ComposeResult:
        """Compose the search UI layout."""
        yield Header()
        use_emojis = self.ctx.config.display.use_emojis
        with Vertical():
            with Container(id="search-container"):
                yield Input(
                    placeholder="Type to search... (/log for entries, /todo for todos)",
                    id="search-input",
                )
            with Container(id="results-container"):
                # Single unified results view
                yield EntryResultsView(id="entries-results")
        yield Label(
            f"j/k: Navigate  {get_icon('bullet', use_emojis)}  Enter: Select  {get_icon('bullet', use_emojis)}  /: Search  {get_icon('bullet', use_emojis)}  e: Edit  {get_icon('bullet', use_emojis)}  t: Tags  {get_icon('bullet', use_emojis)}  p: Project  {get_icon('bullet', use_emojis)}  +/-: Priority  {get_icon('bullet', use_emojis)}  ?: Help",
            id="search-status-bar",
        )

    def on_mount(self) -> None:
        """Load data and focus the search input on mount."""
        self._load_data()
        self.query_one("#search-input", Input).focus()

    def _load_data(self) -> None:
        """Load entries and todos from the database."""
        self._all_entries = self.ctx.db.get_all_entries()
        self._all_todos = self.ctx.db.get_all_todos()

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
        entries_view.clear()

        # Parse search mode from query
        query = query.strip()
        if query.startswith("/log "):
            self._search_mode = "log"
            query = query[5:]  # Remove "/log " prefix
        elif query.startswith("/todo "):
            self._search_mode = "todo"
            query = query[6:]  # Remove "/todo " prefix
        else:
            self._search_mode = "all"

        if not query.strip():
            self._update_status_bar(0, 0)
            return

        # Search based on mode
        matched_entries = []
        matched_todos = []

        if self._search_mode in ("all", "log"):
            matched_entries = search_items(
                query, self._all_entries, limit=50, threshold=50
            )

        if self._search_mode in ("all", "todo"):
            # Only search pending todos - completed todos appear as journal entries
            pending_todos = [t for t in self._all_todos if t.status == "pending"]
            matched_todos = search_items(query, pending_todos, limit=50, threshold=50)

        # Display results based on mode
        if self._search_mode == "todo":
            # Show todos in the entries view (reuse it)
            for todo, score in matched_todos:
                entries_view.append_todo(todo, score)
        else:
            # Show entries (or mixed results in "all" mode)
            for entry, score in matched_entries:
                entries_view.append_item(entry, score)
            # In "all" mode, also show todos
            if self._search_mode == "all":
                for todo, score in matched_todos:
                    entries_view.append_todo(todo, score)

        self._update_status_bar(len(matched_entries), len(matched_todos))

    def _update_status_bar(self, entry_count: int, todo_count: int) -> None:
        """Update the status bar with result counts.

        Args:
            entry_count: Number of matched entries.
            todo_count: Number of matched todos.
        """
        total = entry_count + todo_count
        self.query_one("#search-status-bar", Label).update(
            f"Found {total} matches ({entry_count} entries, {todo_count} todos) | "
            "j/k: Navigate | Enter: Select | /: Search | q: Quit"
        )

    def _get_active_view(self) -> EntryResultsView:
        """Get the currently active results view based on focus."""
        focused = self.focused  # type: ignore[attr-defined]
        if isinstance(focused, EntryResultsView):
            return focused

        # Default to entries view
        return self.query_one("#entries-results", EntryResultsView)

    def _get_selected_item(
        self,
    ) -> tuple[Entry | Todo | None, str | None]:
        """Get currently selected item and its type.

        Returns:
            Tuple of (item, item_type) or (None, None).
        """
        results_view = self._get_active_view()
        if results_view.highlighted_child is None:
            return None, None
        item_data = results_view.highlighted_child.item_data  # type: ignore[attr-defined]
        if not item_data:
            return None, None
        return item_data["item"], item_data["type"]

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
        item, item_type = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        content = item.content
        try:
            import pyperclip

            pyperclip.copy(content)
            self.notify(f"Copied: {content[:50]}...", timeout=2)
        except Exception:
            self.notify(f"Content: {content}", timeout=3)

    def action_edit_content(self) -> None:
        """Edit content of selected item."""
        item, item_type = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        # Placeholder - full implementation would show edit modal
        self.notify("Edit content - coming soon", timeout=1.5)

    def action_edit_tags(self) -> None:
        """Edit tags of selected item."""
        item, item_type = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        # Placeholder
        self.notify("Edit tags - coming soon", timeout=1.5)

    def action_edit_project(self) -> None:
        """Edit project of selected item."""
        item, item_type = self._get_selected_item()
        if item is None:
            self.notify("No item selected", severity="warning", timeout=1.5)
            return

        # Placeholder
        self.notify("Edit project - coming soon", timeout=1.5)

    def action_increase_priority(self) -> None:
        """Increase priority of selected todo."""
        item, item_type = self._get_selected_item()
        if item is None or item_type != "todo":
            self.notify(
                "Select a todo to change priority", severity="warning", timeout=1.5
            )
            return

        # Placeholder
        self.notify("Priority change - coming soon", timeout=1.5)

    def action_decrease_priority(self) -> None:
        """Decrease priority of selected todo."""
        item, item_type = self._get_selected_item()
        if item is None or item_type != "todo":
            self.notify(
                "Select a todo to change priority", severity="warning", timeout=1.5
            )
            return

        # Placeholder
        self.notify("Priority change - coming soon", timeout=1.5)
