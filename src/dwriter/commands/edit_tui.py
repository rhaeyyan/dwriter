"""Interactive edit TUI using Textual.

This module provides a real-time interface for editing and deleting
journal entries.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

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
    TextArea,
)

from ..database import Entry


class EntryListItem(ListItem):
    """Custom list item for journal entries."""

    def __init__(self, entry: Entry, **kwargs: Any) -> None:
        """Initialize the entry list item.

        Args:
            entry: Entry object to display.
            **kwargs: Additional arguments passed to ListItem.
        """
        super().__init__(**kwargs)
        self.entry = entry


class EditEntryModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing an entry's content."""

    CSS = """
    EditEntryModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 90;
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
        height: 8;
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

    def __init__(self, entry: Entry, **kwargs: Any) -> None:
        """Initialize the edit modal.

        Args:
            entry: Entry object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry = entry
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Entry #{self.entry.id}", id="edit-modal-title")
            text_area = TextArea(
                text=self.entry.content,
                id="edit-input",
            )
            text_area.show_line_numbers = False
            yield text_area
            with Container(id="edit-buttons"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#edit-input", TextArea).focus()

    def action_save(self) -> None:
        """Save the edited content."""
        text_area = self.query_one("#edit-input", TextArea)
        self.result = text_area.text.strip()
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


class EditTagsModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for editing an entry's tags."""

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

    def __init__(self, entry: Entry, **kwargs: Any) -> None:
        """Initialize the edit tags modal.

        Args:
            entry: Entry object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry = entry
        self.result: list[str] | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(f"Edit Tags for Entry #{self.entry.id}", id="edit-modal-title")
            yield Input(
                value=", ".join(self.entry.tag_names),
                id="edit-input",
                placeholder="tag1, tag2, tag3",
            )
            yield Label(
                "Separate tags with commas (without #)",
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
    """Modal dialog for editing an entry's project."""

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

    def __init__(self, entry: Entry, **kwargs: Any) -> None:
        """Initialize the edit project modal.

        Args:
            entry: Entry object to edit.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry = entry
        self.result: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container(id="edit-modal-container"):
            yield Label(
                f"Edit Project for Entry #{self.entry.id}",
                id="edit-modal-title",
            )
            yield Input(
                value=self.entry.project or "",
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


class EntryListView(ListView):
    """ListView for displaying journal entries."""

    def __init__(self, entries: list[Entry] | None = None, **kwargs: Any) -> None:
        """Initialize the entry list view.

        Args:
            entries: Optional list of Entry objects to display.
            **kwargs: Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._entries = entries or []

    def update_entries(self, entries: list[Entry]) -> None:
        """Update the displayed entries.

        Args:
            entries: List of Entry objects to display.
        """
        self._entries = entries
        self.clear()
        for entry in entries:
            self.append_item(entry)

    def append_item(self, entry: Entry) -> None:
        """Append a single entry to the list.

        Args:
            entry: Entry object to display.
        """
        label = self._format_entry(entry)
        list_item = EntryListItem(entry)
        list_item._add_child(Label(label, markup=True))
        self.append(list_item)

    def _format_entry(self, entry: Entry) -> str:
        """Format an entry for display.

        Args:
            entry: Entry object to format.

        Returns:
            Formatted string with markup.
        """
        time_str = entry.created_at.strftime("%I:%M %p")
        tags_str = ""
        if entry.tag_names:
            tags_str = f" [yellow]#{' #'.join(entry.tag_names)}[/yellow]"
        project_str = f" [purple]{entry.project}[/purple]" if entry.project else ""

        return (
            f"[magenta][{entry.id}][/magenta] "
            f"[dim]{time_str}[/dim] | "
            f"{entry.content}{tags_str}{project_str}"
        )

    @property
    def selected_entry(self) -> Entry | None:
        """Get the currently selected entry."""
        if self.highlighted_child is None:
            return None
        if isinstance(self.highlighted_child, EntryListItem):
            return self.highlighted_child.entry
        return None


class EditApp(App):  # type: ignore[type-arg]
    """Interactive edit application.

    Provides a real-time interface for editing and deleting entries.

    Key bindings:
        j/k: Navigate up/down
        e: Edit entry content
        t: Edit tags
        p: Edit project
        d: Delete entry
        Enter: Edit content (shortcut)
        Escape/q: Quit
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

    #date-label {
        color: $accent;
        text-style: bold;
    }

    #list-container {
        height: 1fr;
        margin: 0 2;
    }

    EntryListView {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    EntryListView:focus {
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
        ("e", "edit_content", "Edit"),
        ("t", "edit_tags", "Tags"),
        ("p", "edit_project", "Project"),
        ("d", "delete", "Delete"),
        ("enter", "edit_content", "Edit"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(
        self,
        db: Any,
        console: Any,
        date: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the edit application.

        Args:
            db: Database instance for querying entries.
            console: Rich console instance.
            date: Optional date to filter entries (defaults to today).
            **kwargs: Additional arguments passed to App.
        """
        super().__init__(**kwargs)
        self.db = db
        self.console = console
        self.edit_date = date or datetime.now()
        self._all_entries: list[Entry] = []

    def compose(self) -> ComposeResult:
        """Compose the edit UI layout."""
        yield Header()
        with Vertical():
            with Container(id="header-container"):
                yield Label("✏️ Edit Entries", id="title")
                date_str = self.edit_date.strftime("%Y-%m-%d")
                yield Label(f"Date: {date_str}", id="date-label")
                yield Label(
                    "e: Edit | t: Tags | p: Project | d: Delete | q: Quit",
                    id="subtitle",
                )
            with Container(id="list-container"):
                yield EntryListView(id="entries")
        yield Label("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load data and focus the list on mount."""
        self._load_entries()
        self.query_one(EntryListView).focus()

    def _load_entries(self) -> None:
        """Load entries from the database."""
        self._all_entries = self.db.get_entries_by_date(self.edit_date)
        self._update_list()
        self._update_status_bar()

    def _update_list(self) -> None:
        """Update the entry list view."""
        list_view = self.query_one(EntryListView)
        list_view.update_entries(self._all_entries)

    def _update_status_bar(self) -> None:
        """Update the status bar with entry count."""
        count = len(self._all_entries)
        status_bar = self.query_one("#status-bar", Label)
        if count == 0:
            status_bar.update(
                "No entries for this date | "
                "j/k: Navigate | e: Edit | t: Tags | p: Project | "
                "d: Delete | r: Refresh | q: Quit"
            )
        else:
            status_bar.update(
                f"Showing {count} entrie{'s' if count > 1 else ''} | "
                "j/k: Navigate | e: Edit | t: Tags | p: Project | "
                "d: Delete | r: Refresh | q: Quit"
            )

    def action_cursor_down(self) -> None:
        """Move cursor down in entry list."""
        list_view = self.query_one(EntryListView)
        list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in entry list."""
        list_view = self.query_one(EntryListView)
        list_view.action_cursor_up()

    def action_edit_content(self) -> None:
        """Edit the selected entry's content."""
        list_view = self.query_one(EntryListView)
        entry = list_view.selected_entry

        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: str | None) -> None:
            if result is not None and result != entry.content:
                try:
                    if not result:
                        self.notify(
                            "Content cannot be empty. Use 'd' to delete.",
                            severity="warning",
                            timeout=2,
                        )
                        return
                    self.db.update_entry(entry.id, content=result)
                    self.notify(f"Entry #{entry.id} updated", timeout=1.5)
                    self._load_entries()
                except Exception as e:
                    self.notify(
                        f"Error updating entry: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditEntryModal(entry), on_dismiss)

    def action_edit_tags(self) -> None:
        """Edit the selected entry's tags."""
        list_view = self.query_one(EntryListView)
        entry = list_view.selected_entry

        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: list[str] | None) -> None:
            if result is not None and result != entry.tag_names:
                try:
                    self.db.update_entry(entry.id, tags=result)
                    self.notify(f"Entry #{entry.id} tags updated", timeout=1.5)
                    self._load_entries()
                except Exception as e:
                    self.notify(
                        f"Error updating tags: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditTagsModal(entry), on_dismiss)

    def action_edit_project(self) -> None:
        """Edit the selected entry's project."""
        list_view = self.query_one(EntryListView)
        entry = list_view.selected_entry

        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(result: str | None) -> None:
            if result is not None and result != entry.project:
                try:
                    self.db.update_entry(entry.id, project=result)
                    self.notify(f"Entry #{entry.id} project updated", timeout=1.5)
                    self._load_entries()
                except Exception as e:
                    self.notify(
                        f"Error updating project: {e}",
                        severity="error",
                        timeout=3,
                    )

        self.push_screen(EditProjectModal(entry), on_dismiss)

    def action_delete(self) -> None:
        """Delete the selected entry."""
        list_view = self.query_one(EntryListView)
        entry = list_view.selected_entry

        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        def on_dismiss(confirmed: bool) -> None:
            if confirmed:
                try:
                    self.db.delete_entry(entry.id)
                    self.notify(f"Entry #{entry.id} deleted", timeout=1.5)
                    self._load_entries()
                except Exception as e:
                    self.notify(
                        f"Error deleting entry: {e}",
                        severity="error",
                        timeout=3,
                    )

        self._show_delete_confirmation(entry.id, on_dismiss)

    def _show_delete_confirmation(
        self, entry_id: int, callback: Callable[[bool], None]
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

            def __init__(self, eid: int, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.entry_id = eid

            def compose(self) -> ComposeResult:
                with Container(id="confirm-container"):
                    yield Label(
                        f"Delete entry #{self.entry_id}?",
                        id="confirm-message",
                    )
                    with Container(id="confirm-buttons"):
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

        self.push_screen(ConfirmModal(entry_id), callback)  # type: ignore[arg-type]

    def action_refresh(self) -> None:
        """Refresh the entry list."""
        self._load_entries()
        self.notify("List refreshed", timeout=1)

    def action_quit(self) -> None:  # type: ignore[override]
        """Quit the edit application."""
        self.exit()
