"""Logs screen for viewing journal entries."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Header, Input, Label, ListItem, ListView

from ...database import Entry
from ..colors import PROJECT, TAG, get_icon
from ...search_utils import search_items


class QuickAddEntryModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for adding a new journal entry."""

    CSS = """
    QuickAddEntryModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 80;
        height: auto;
        max-height: 40;
        background: $surface;
        border: solid $success;
        padding: 1 2;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-content-label, #edit-tags-label, #edit-project-label, #edit-datetime-label {
        text-style: bold;
        padding: 1 0 0 0;
    }

    #edit-input, #tags-input, #project-input {
        width: 100%;
        margin: 0 0 1 0;
    }

    .datetime-container {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
    }

    #date-input {
        width: 60%;
        margin-right: 1;
    }

    #time-input {
        width: 1fr;
    }

    #help-text {
        color: $text-muted;
        padding: 0 0 1 0;
        text-style: italic;
    }

    #save-exit-btn {
        dock: top;
        width: auto;
        margin: 0 1;
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
        ("ctrl+s", "save_and_exit", "Save & Exit"),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.result: tuple[
            str | None, list[str] | None, str | None, datetime | None
        ] = (None, None, None, None)

    def compose(self) -> ComposeResult:
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="edit-modal-container"):
            yield Button(f"{get_icon('save', use_emojis)} Save & Exit", id="save-exit-btn", variant="success")
            yield Label(f"{get_icon('plus', use_emojis)} Quick Add Entry", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(id="edit-input", placeholder="What's happening?")

            yield Label("Tags:", id="edit-tags-label")
            yield Input(id="tags-input", placeholder="work, personal, etc.")

            yield Label("Project:", id="edit-project-label")
            yield Input(id="project-input", placeholder="Project name (optional)")

            lock_mode = self.app.ctx.config.display.lock_mode
            date_fmt = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt, "%Y-%m-%d")
            
            yield Label("Date and Time:", id="edit-datetime-label")
            with Horizontal(classes="datetime-container"):
                yield Input(value=datetime.now().strftime(hint), id="date-input", placeholder=date_fmt)
                yield Input(value=datetime.now().strftime("%I:%M %p"), id="time-input", placeholder="HH:MM AM/PM")

            yield Label(f"Date: yesterday, today, {date_fmt} | Time: 2pm, 14:30", id="help-text")

            with Container(id="edit-buttons"):
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def _parse_date(self, date_str: str) -> datetime | None:
        from ...date_utils import parse_natural_date
        try:
            date_fmt = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt)
            return parse_natural_date(date_str, format_hint=hint)
        except ValueError:
            return None

    def _parse_time(self, time_str: str) -> datetime | None:
        time_str = time_str.strip().upper()
        for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
            try:
                parsed = datetime.strptime(time_str, fmt)
                return datetime.now().replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
            except ValueError:
                pass
        return None

    def action_save(self) -> None: self._do_save()
    def action_save_and_exit(self) -> None: self._do_save()

    def _do_save(self) -> None:
        content = self.query_one("#edit-input", Input).value.strip() or None
        date_str = self.query_one("#date-input", Input).value.strip() or None
        time_str = self.query_one("#time-input", Input).value.strip() or None
        tags_str = self.query_one("#tags-input", Input).value.strip() or None
        project = self.query_one("#project-input", Input).value.strip() or None

        created_at: datetime | None = None
        if date_str:
            parsed_date = self._parse_date(date_str)
            if parsed_date:
                if time_str:
                    parsed_time = self._parse_time(time_str)
                    if parsed_time:
                        created_at = parsed_date.replace(hour=parsed_time.hour, minute=parsed_time.minute)
                else:
                    created_at = parsed_date.replace(hour=0, minute=0)

        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else None
        self.result = (content, tags, project, created_at)
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-exit-btn": self.action_save_and_exit()
        elif event.button.id == "cancel-btn": self.action_cancel()


class EditEntryModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing a journal entry."""

    CSS = """
    EditEntryModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 80;
        height: auto;
        max-height: 40;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-content-label, #edit-tags-label, #edit-project-label, #edit-datetime-label {
        text-style: bold;
        padding: 1 0 0 0;
    }

    #edit-input, #tags-input, #project-input {
        width: 100%;
        margin: 0 0 1 0;
    }

    .datetime-container {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
    }

    #date-input {
        width: 60%;
        margin-right: 1;
    }

    #time-input {
        width: 1fr;
    }

    #help-text {
        color: $text-muted;
        padding: 0 0 1 0;
        text-style: italic;
    }

    #save-exit-btn {
        dock: top;
        width: auto;
        margin: 0 1;
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
        ("ctrl+s", "save_and_exit", "Save & Exit"),
    ]

    def __init__(
        self,
        entry: Entry,
        **kwargs: Any,
    ) -> None:
        """Initialize the edit modal.

        Args:
            entry: Entry object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry = entry
        self.result: tuple[
            str | None, list[str] | None, str | None, datetime | None
        ] = (
            None,
            None,
            None,
            None,
        )

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="edit-modal-container"):
            # Save & Exit button in top-right corner
            yield Button(f"{get_icon('save', use_emojis)} Save & Exit", id="save-exit-btn", variant="success")

            yield Label(f"{get_icon('edit', use_emojis)} Edit Entry #{self.entry.id}", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(
                value=self.entry.content,
                id="edit-input",
                placeholder="Entry content...",
            )

            # Tags field
            yield Label("Tags:", id="edit-tags-label")
            tags_str = ", ".join(self.entry.tag_names) if self.entry.tag_names else ""
            yield Input(
                value=tags_str,
                id="tags-input",
                placeholder="Comma-separated tags (e.g., work, urgent)",
            )

            # Project field
            yield Label("Project:", id="edit-project-label")
            yield Input(
                value=self.entry.project or "",
                id="project-input",
                placeholder="Project name (optional)",
            )

            # Date and Time fields on the same line
            lock_mode = self.app.ctx.config.display.lock_mode
            date_fmt = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt, "%Y-%m-%d")

            yield Label(
                "Date and Time:" + (" [yellow](Locked)[/]" if lock_mode else ""),
                id="edit-datetime-label"
            )
            with Horizontal(classes="datetime-container"):
                date_val = (
                    self.entry.created_at.strftime(hint)
                    if self.entry.created_at
                    else ""
                )
                yield Input(
                    value=date_val,
                    id="date-input",
                    placeholder=date_fmt,
                    disabled=lock_mode,
                )

                dt = self.entry.created_at
                if dt and dt.hour == 0 and dt.minute == 0 and dt.second == 0:
                    time_str = ""  # Leave blank for midnight times
                else:
                    time_str = dt.strftime("%I:%M %p") if dt else ""
                yield Input(
                    value=time_str,
                    id="time-input",
                    placeholder="HH:MM AM/PM",
                    disabled=lock_mode,
                )

            yield Label(
                "Date: yesterday, 2 days ago, last Friday | Time: 2:30 PM, 14:30 (or leave blank)",
                id="help-text",
            )

            with Container(id="edit-buttons"):
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the content input on mount."""
        self.query_one("#edit-input", Input).focus()

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse a date string using the central date_utils parser.

        Args:
            date_str: Date string in various formats.

        Returns:
            Parsed datetime or None.
        """
        from ...date_utils import parse_natural_date

        try:
            date_fmt = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt)
            return parse_natural_date(date_str, format_hint=hint)
        except ValueError:
            return None

    def _parse_time(self, time_str: str) -> datetime | None:
        """Parse a time string in 12 or 24-hour format.

        Args:
            time_str: Time string (e.g., "02:30 PM", "14:30", "2:30pm").

        Returns:
            Parsed datetime with today's date or None.
        """
        time_str = time_str.strip().upper()

        # Try 12-hour format: HH:MM AM/PM
        for fmt in ["%I:%M %p", "%I:%M%p", "%I:%M %P", "%I:%M%P"]:
            try:
                parsed = datetime.strptime(time_str, fmt)
                return datetime.now().replace(
                    hour=parsed.hour,
                    minute=parsed.minute,
                    second=0,
                    microsecond=0,
                )
            except ValueError:
                pass

        # Try 24-hour format: HH:MM
        try:
            parsed = datetime.strptime(time_str, "%H:%M")
            return datetime.now().replace(
                hour=parsed.hour,
                minute=parsed.minute,
                second=0,
                microsecond=0,
            )
        except ValueError:
            pass

        return None

    def action_save(self) -> None:
        """Save the edited content, tags, project, and datetime."""
        self._do_save()

    def action_save_and_exit(self) -> None:
        """Save and exit the modal."""
        self._do_save()

    def _do_save(self) -> None:
        """Perform the save operation."""
        content_widget = self.query_one("#edit-input", Input)
        date_widget = self.query_one("#date-input", Input)
        time_widget = self.query_one("#time-input", Input)
        tags_widget = self.query_one("#tags-input", Input)
        project_widget = self.query_one("#project-input", Input)

        content = content_widget.value.strip() or None
        date_str = date_widget.value.strip() or None
        time_str = time_widget.value.strip() or None
        tags_str = tags_widget.value.strip() or None
        project = project_widget.value.strip() or None

        # Parse date and time
        created_at: datetime | None = None

        if date_str:
            parsed_date = self._parse_date(date_str)
            if parsed_date is None:
                self.notify(
                    "Invalid date format. Use YYYY-MM-DD", severity="error", timeout=2
                )
                return

            # Parse time if provided (time is optional)
            if time_str:
                parsed_time = self._parse_time(time_str)
                if parsed_time is None:
                    self.notify(
                        "Invalid time format. Use HH:MM AM/PM",
                        severity="error",
                        timeout=2,
                    )
                    return
                # Combine date and time
                created_at = parsed_date.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                )
            else:
                # Use date only (midnight) - time is optional
                created_at = parsed_date.replace(hour=0, minute=0)
        elif time_str:
            # Time only without date - use today
            parsed_time = self._parse_time(time_str)
            if parsed_time:
                created_at = parsed_time

        # Parse tags from comma-separated string
        tags: list[str] | None = None
        if tags_str is not None:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        self.result = (content, tags, project, created_at)
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
        elif event.button.id == "save-exit-btn":
            self.action_save_and_exit()


class DeleteConfirmModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for confirming entry deletion."""

    CSS = """
    DeleteConfirmModal {
        align: center middle;
    }

    #delete-modal-container {
        width: 50;
        height: auto;
        min-height: 8;
        background: $surface;
        border: solid $error;
        padding: 0 2;
    }

    #delete-modal-title {
        text-align: center;
        text-style: bold;
        color: $error;
        padding: 0;
        margin-top: 1;
    }

    #delete-modal-content {
        text-align: center;
        padding: 0;
        margin: 1 0;
        color: $text-muted;
    }

    #delete-buttons {
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def __init__(
        self,
        entry_id: int,
        entry_content: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the delete confirm modal.

        Args:
            entry_id: ID of the entry to delete.
            entry_content: Preview of entry content.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry_id = entry_id
        self.entry_content = entry_content
        self.result: int | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="delete-modal-container"):
            yield Label(f"{get_icon('warning', use_emojis)} Delete Entry?", id="delete-modal-title")
            yield Label(
                f'"{self.entry_content[:50]}{"..." if len(self.entry_content) > 50 else ""}"',
                id="delete-modal-content",
            )
            with Container(id="delete-buttons"):
                yield Button("\\[ DELETE ]", id="delete-btn", variant="error")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def action_confirm(self) -> None:
        """Confirm deletion."""
        self.result = self.entry_id
        self.dismiss(self.entry_id)

    def action_cancel(self) -> None:
        """Cancel deletion."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "delete-btn":
            self.action_confirm()
        elif event.button.id == "cancel-btn":
            self.action_cancel()


class LogsResultsView(ListView):
    """ListView for displaying journal entry search results."""

    def __init__(
        self, items: list[tuple[Entry, float]] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the logs results view.

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

    def append_item(self, entry: Entry, score: float | None = None) -> None:
        """Append a single entry to the list.

        Args:
            entry: Entry object to display.
            score: Optional match score (0-100) for search results.
        """
        label = self._format_entry(entry, score)
        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": entry, "score": score, "type": "entry"}  # type: ignore[attr-defined]
        self.append(list_item)

    def _format_entry(self, entry: Entry, score: float | None = None) -> str:
        """Format an entry for display.

        Args:
            entry: Entry object to format.
            score: Optional match score for search results.

        Returns:
            Formatted string with markup.
        """
        from ...ui_utils import format_entry_datetime

        date_str, time_str = format_entry_datetime(entry, self.app.ctx.config)

        # Clean up content - remove check emoji/mark from completed todos
        content = entry.content
        
        use_emojis = self.app.ctx.config.display.use_emojis
        check_icon = get_icon("check", use_emojis)
        timer_icon = get_icon("timer", use_emojis)
        
        if content.startswith("✅ "):
            content = content.replace("✅ ", f"{check_icon} ", 1)
        elif content.startswith("✓ "):
            content = content.replace("✓ ", f"{check_icon} ", 1)
        
        # Ensure timer session icon is correct
        if "⏱️" in content:
            content = content.replace("⏱️", timer_icon)

        # Format tags and project on first line
        tags_str = (
            f"[{TAG}]#{' #'.join(entry.tag_names)}[/{TAG}]" if entry.tag_names else ""
        )
        project_str = (
            f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
            if entry.project
            else ""
        )

        # Add score if this is a search result
        score_str = ""
        if score is not None:
            score_color = "green" if score >= 90 else "yellow" if score >= 75 else "dim"
            score_str = f" [{score_color}]({int(score)}%)[/{score_color}]"

        # Format: date time | #tags : Project on first line, content on second line
        theme = getattr(self.app, "theme_variables", {})
        time_hex = theme.get("success", "#73E6CB")
        # Ensure time_hex doesn't have double # and use universal closing tag
        color_tag = time_hex if time_hex.startswith("#") else f"#{time_hex}"
        
        datetime_str = f"[cyan]{date_str}[/cyan]"
        if time_str:
            datetime_str = f"[cyan]{date_str}[/cyan] [{color_tag}]{time_str}[/]"
        else:
            datetime_str = f"[cyan]{date_str}[/cyan]"

        first_line = f"{datetime_str} | {tags_str}{project_str}{score_str}"

        if content:
            return f"{first_line}\n  {content}"
        else:
            return first_line


class LogsScreen(Container):
    """Logs screen for viewing and searching journal entries."""

    DEFAULT_CSS = """
    LogsScreen {
        height: 1fr;
        background: $surface;
    }

    #search-container {
        height: auto;
        margin: 0 2 1 2;
        padding: 0;
    }

    #search-container Horizontal {
        height: auto;
        align: left middle;
    }

    #btn-standup, #btn-quick-add {
        width: auto;
        min-width: 0;
        height: 1;
        min-height: 1;
        background: transparent;
        border: none;
        padding: 0;
        margin: 1 0 0 0;
        content-align: center middle;
        text-style: bold;
    }

    #btn-standup {
        color: $primary;
    }

    #btn-quick-add {
        color: $success;
    }

    #btn-quick-add:hover {
        background: $success 20%;
        text-style: bold;
    }

    #btn-standup:hover {
        background: $surface;
        text-style: bold;
    }

    #search-input {
        width: 1fr;
        border: solid $secondary;
        margin: 0 1;
    }

    #search-input:focus {
        border: solid $accent;
    }

    #results-container {
        height: 1fr;
        margin: 0 2;
    }

    #load-more-container {
        height: 3;
        align: center middle;
        background: $panel;
        border-top: solid $primary;
    }

    #btn-load-more {
        width: 30;
    }

    LogsResultsView {
        height: 1fr;
        border: solid #45475a;
        background: $panel;
        padding: 0;
    }

    LogsResultsView:focus {
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

    #logs-status-bar {
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
        Binding("e", "edit_content", "Edit"),
        Binding("d", "delete_entry", "Delete"),
        Binding("t", "edit_tags", "Tags"),
        Binding("p", "edit_project", "Project"),
    ]

    def __init__(
        self,
        ctx: AppContext,
        **kwargs: Any,
    ) -> None:
        """Initialize the logs screen.

        Args:
            ctx: Application context with database and configuration.
            **kwargs: Additional arguments passed to Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._all_entries: list[Entry] = []
        self._page_size = 50
        self._offset = 0
        self._has_more = True

    def compose(self) -> ComposeResult:
        """Compose the logs UI layout."""
        from textual.containers import Horizontal

        yield Header()
        use_emojis = self.ctx.config.display.use_emojis
        with Vertical():
            with Container(id="search-container"):
                with Horizontal():
                    yield Button("\\[+]", id="btn-quick-add", variant="success")
                    yield Input(
                        placeholder="Search logs to edit/delete",
                        id="search-input",
                    )
                    yield Button("\\[ STAND-UP ]", id="btn-standup", variant="primary")
            with Container(id="results-container"):
                yield LogsResultsView(id="logs-results")
                with Horizontal(id="load-more-container"):
                    yield Button("\\[ LOAD MORE ]", id="btn-load-more", variant="default")
        yield Label(
            f"j/k: Navigate  {get_icon('bullet', use_emojis)}  Enter: Select  {get_icon('bullet', use_emojis)}  e: Edit  {get_icon('bullet', use_emojis)}  d: Delete  {get_icon('bullet', use_emojis)}  t: Tags  {get_icon('bullet', use_emojis)}  p: Project  {get_icon('bullet', use_emojis)}  q: Quit",
            id="logs-status-bar",
        )

    def _load_data(self, reset: bool = True) -> None:
        """Load entries from the database using pagination.
        
        Args:
            reset: If True, reset offset and clear current list.
        """
        if reset:
            self._offset = 0
            self._has_more = True
            self._all_entries = []

        if not self._has_more:
            return

        new_entries = self.ctx.db.get_entries_paginated(
            limit=self._page_size, offset=self._offset
        )
        
        if len(new_entries) < self._page_size:
            self._has_more = False
        
        self._all_entries.extend(new_entries)
        self._offset += len(new_entries)

    def on_mount(self) -> None:
        """Load data and display recent entries on mount."""
        self._load_data(reset=True)
        self._display_recent_entries()
        self.query_one("#logs-results", LogsResultsView).focus()

    def on_show(self) -> None:
        """Refresh data when the logs screen becomes visible."""
        self._load_data(reset=True)
        self._display_recent_entries()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes.

        Args:
            event: Input change event containing the query.
        """
        if event.input.id == "search-input":
            query = event.value.strip()
            # Hide load more during search
            self.query_one("#btn-load-more").display = not bool(query)
            self._perform_search(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "btn-standup":
            from .standup import StandupScreen

            self.app.push_screen(StandupScreen(self.ctx))
        elif event.button.id == "btn-quick-add":
            self.action_quick_add()
        elif event.button.id == "btn-load-more":
            self.action_load_more()

    def action_load_more(self) -> None:
        """Load the next page of entries."""
        if not self._has_more:
            return
            
        self._load_data(reset=False)
        self._display_recent_entries(append=True)

    def _perform_search(self, query: str) -> None:
        """Execute fuzzy search and update results.

        Args:
            query: Search query string.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        
        query = query.strip()

        if not query:
            # Show recent entries when search is empty
            self._display_recent_entries()
            return

        results_view.clear()
        
        # Search across the entries loaded in the current session.
        # Note: Large databases may eventually require FTS5 or background fetching.
        matched_entries = search_items(query, self._all_entries, limit=50, threshold=50)

        # Display results
        for entry, score in matched_entries:
            results_view.append_item(entry, score)

        self._update_status_bar(len(matched_entries), is_search=True)

    def _display_recent_entries(self, append: bool = False) -> None:
        """Display the entries from the loaded cache.

        Args:
            append: If True, only append new entries instead of clearing.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        
        if not append:
            results_view.clear()
            entries_to_show = self._all_entries
        else:
            # Only append the most recent batch
            entries_to_show = self._all_entries[-self._page_size:]

        for entry in entries_to_show:
            results_view.append_item(entry, score=None)

        # Update button visibility
        load_more_btn = self.query_one("#btn-load-more")
        load_more_btn.display = self._has_more
        if not self._has_more:
            load_more_btn.label = "No more entries"
            load_more_btn.disabled = True
        else:
            load_more_btn.label = "Load More"
            load_more_btn.disabled = False

        self._update_status_bar(len(self._all_entries), is_search=False)

    def _update_status_bar(self, count: int, is_search: bool) -> None:
        """Update the status bar with result counts.

        Args:
            count: Number of displayed entries.
            is_search: Whether this is a search result or recent entries view.
        """
        use_emojis = self.ctx.config.display.use_emojis
        bullet = get_icon("bullet", use_emojis)
        if is_search:
            self.query_one("#logs-status-bar", Label).update(
                f"Found {count} matches  {bullet}  "
                f"j/k: Navigate  {bullet}  e: Edit  {bullet}  d: Delete  {bullet}  t: Tags  {bullet}  p: Project  {bullet}  /: Search  {bullet}  q: Quit"
            )
        else:
            self.query_one("#logs-status-bar", Label).update(
                f"Showing {count} recent entries  {bullet}  "
                f"j/k: Navigate  {bullet}  e: Edit  {bullet}  d: Delete  {bullet}  t: Tags  {bullet}  p: Project  {bullet}  /: Search  {bullet}  q: Quit"
            )

    def _get_selected_entry(self) -> Entry | None:
        """Get the currently selected entry.

        Returns:
            Selected Entry or None.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        if results_view.highlighted_child is None:
            return None
        item_data = results_view.highlighted_child.item_data  # type: ignore[attr-defined]
        if not item_data:
            return None
        return item_data["item"]

    def action_cursor_down(self) -> None:
        """Move cursor down in results list."""
        results_view = self.query_one("#logs-results", LogsResultsView)
        results_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in results list."""
        results_view = self.query_one("#logs-results", LogsResultsView)
        results_view.action_cursor_up()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_select(self) -> None:
        """Select the highlighted item and copy its content."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        content = entry.content
        try:
            import pyperclip

            pyperclip.copy(content)
            self.notify(f"Copied: {content[:50]}...", timeout=2)
        except Exception:
            self.notify(f"Content: {content}", timeout=3)

    def action_edit_content(self) -> None:
        """Edit content of selected entry."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, list[str] | None, str | None, datetime | None]
            | None,
        ) -> None:
            if result is None:
                return
            content, tags, project, created_at = result
            if content is None:
                return

            self.ctx.db.update_entry(
                entry.id,
                content=content,
                tags=tags,
                project=project,
                created_at=created_at,
            )
            self.notify(f"Entry #{entry.id} updated", timeout=1.5)
            self._load_data()
            self._display_recent_entries()

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_delete_entry(self) -> None:
        """Delete selected entry."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: int | None) -> None:
            if result is not None:
                self.ctx.db.delete_entry(result)
                self.notify(f"Entry #{result} deleted", timeout=1.5)
                self._load_data()
                self._display_recent_entries()

        self.app.push_screen(
            DeleteConfirmModal(entry.id, entry.content),
            on_dismiss,
        )

    def action_edit_tags(self) -> None:
        """Edit tags of selected entry."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, list[str] | None, str | None] | None,
        ) -> None:
            if result is None:
                return
            content, tags, project = result
            if tags is None:
                return

            self.ctx.db.update_entry(
                entry.id,
                tags=tags,
            )
            self.notify(f"Entry #{entry.id} tags updated", timeout=1.5)
            self._load_data()
            self._display_recent_entries()

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_edit_project(self) -> None:
        """Edit project of selected entry."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(
            result: tuple[str | None, list[str] | None, str | None] | None,
        ) -> None:
            if result is None:
                return
            content, tags, project = result
            if project is None:
                return

            self.ctx.db.update_entry(
                entry.id,
                project=project,
            )
            self.notify(f"Entry #{entry.id} project updated", timeout=1.5)
            self._load_data()
            self._display_recent_entries()

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_quick_add(self) -> None:
        """Open modal to add a new journal entry."""
        def on_dismiss(
            result: tuple[str | None, list[str] | None, str | None, datetime | None]
            | None,
        ) -> None:
            if result is None:
                return
            content, tags, project, created_at = result
            if content is None:
                return

            self.ctx.db.add_entry(
                content=content,
                tags=tags,
                project=project,
                created_at=created_at,
            )
            self.notify("New entry added", timeout=1.5)
            self._load_data()
            self._display_recent_entries()

        self.app.push_screen(QuickAddEntryModal(), on_dismiss)

    def on_entry_added(self, message: Any) -> None:
        """Handle EntryAdded messages from other screens.

        Args:
            message: EntryAdded message.
        """
        # Refresh the logs when entries are added elsewhere
        self._load_data()
        self._display_recent_entries()
