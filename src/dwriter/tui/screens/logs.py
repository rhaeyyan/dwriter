"""Logs screen for viewing and managing journal entries."""

from __future__ import annotations

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
from ...search_utils import search_items
from ..colors import PROJECT, TAG, get_icon


class QuickAddEntryModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for rapid journal entry creation."""

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
        color: $text-muted;
        padding: 1 0 0 0;
    }

    #edit-input, #tags-input, #project-input {
        width: 100%;
        border: none;
        border-bottom: solid $primary;
        margin: 0 0 1 0;
        padding: 1 2 0 2;
    }

    .datetime-container {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
    }

    #date-input {
        width: 60%;
        margin-right: 1;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
    }

    #time-input {
        width: 1fr;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
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
        """Initializes the quick add modal."""
        super().__init__(**kwargs)
        self.result: tuple[
            str | None, list[str] | None, str | None, datetime | None
        ] = (None, None, None, None)

    def compose(self) -> ComposeResult:
        """Composes the modal layout."""
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
        """Focuses the content input on mount."""
        self.query_one("#edit-input", Input).focus()

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parses a date string using configured date format hints.

        Args:
            date_str (str): The date string to parse.

        Returns:
            datetime | None: The parsed datetime or None if parsing fails.
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
        """Parses a time string in 12 or 24-hour formats.

        Args:
            time_str (str): The time string to parse.

        Returns:
            datetime | None: A datetime object with the parsed time for the current day.
        """
        time_str = time_str.strip().upper()
        for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
            try:
                parsed = datetime.strptime(time_str, fmt)
                return datetime.now().replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
            except ValueError:
                pass
        return None

    def action_save(self) -> None:
        """Executes the save operation."""
        self._do_save()

    def action_save_and_exit(self) -> None:
        """Executes the save operation and closes the modal."""
        self._do_save()

    def _do_save(self) -> None:
        """Assembles input data and dismisses the modal with the result."""
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
        """Dismisses the modal without saving."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatches button press events to corresponding actions."""
        if event.button.id == "save-exit-btn": self.action_save_and_exit()
        elif event.button.id == "cancel-btn": self.action_cancel()


class EditEntryModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for modifying existing journal entries."""

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
        color: $text-muted;
        padding: 1 0 0 0;
    }

    #edit-input, #tags-input, #project-input {
        width: 100%;
        border: none;
        border-bottom: solid $primary;
        margin: 0 0 1 0;
        padding: 1 2 0 2;
    }

    .datetime-container {
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
    }

    #date-input {
        width: 60%;
        margin-right: 1;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
    }

    #time-input {
        width: 1fr;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
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
        """Initializes the edit modal.

        Args:
            entry (Entry): The database entry object to modify.
            **kwargs (Any): Additional arguments passed to ModalScreen.
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
        """Composes the modal UI components."""
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="edit-modal-container"):
            yield Button(f"{get_icon('save', use_emojis)} Save & Exit", id="save-exit-btn", variant="success")
            yield Label(f"{get_icon('edit', use_emojis)} Edit Entry #{self.entry.id}", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(
                value=self.entry.content,
                id="edit-input",
                placeholder="Entry content...",
            )

            yield Label("Tags:", id="edit-tags-label")
            tags_str = ", ".join(self.entry.tag_names) if self.entry.tag_names else ""
            yield Input(
                value=tags_str,
                id="tags-input",
                placeholder="Comma-separated tags",
            )

            yield Label("Project:", id="edit-project-label")
            yield Input(
                value=self.entry.project or "",
                id="project-input",
                placeholder="Project name (optional)",
            )

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
                    time_str = ""
                else:
                    time_str = dt.strftime("%I:%M %p") if dt else ""
                yield Input(
                    value=time_str,
                    id="time-input",
                    placeholder="HH:MM AM/PM",
                    disabled=lock_mode,
                )

            yield Label(
                "Date: yesterday, 2 days ago, last Friday | Time: 2:30 PM, 14:30",
                id="help-text",
            )

            with Container(id="edit-buttons"):
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focuses the primary content input."""
        self.query_one("#edit-input", Input).focus()

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parses a date string with configuration-based format hints.

        Args:
            date_str (str): The date string to parse.

        Returns:
            datetime | None: Parsed datetime or None.
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
        """Parses a time string in 12 or 24-hour format.

        Args:
            time_str (str): The time string to parse.

        Returns:
            datetime | None: Parsed time as a datetime object for the current day.
        """
        time_str = time_str.strip().upper()
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
        """Executes the save operation."""
        self._do_save()

    def action_save_and_exit(self) -> None:
        """Executes the save operation and closes the modal."""
        self._do_save()

    def _do_save(self) -> None:
        """Assembles data from inputs and dismisses the modal."""
        content = self.query_one("#edit-input", Input).value.strip() or None
        date_str = self.query_one("#date-input", Input).value.strip() or None
        time_str = self.query_one("#time-input", Input).value.strip() or None
        tags_str = self.query_one("#tags-input", Input).value.strip() or None
        project = self.query_one("#project-input", Input).value.strip() or None

        created_at: datetime | None = None
        if date_str:
            parsed_date = self._parse_date(date_str)
            if parsed_date is None:
                self.notify("Invalid date format", severity="error", timeout=2)
                return

            if time_str:
                parsed_time = self._parse_time(time_str)
                if parsed_time is None:
                    self.notify("Invalid time format", severity="error", timeout=2)
                    return
                created_at = parsed_date.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                )
            else:
                created_at = parsed_date.replace(hour=0, minute=0)
        elif time_str:
            created_at = self._parse_time(time_str)

        tags: list[str] | None = None
        if tags_str is not None:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        self.result = (content, tags, project, created_at)
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Closes the modal without modifications."""
        self.result = (None, None, None, None)
        self.dismiss(self.result)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button interaction events."""
        if event.button.id == "save-btn": self.action_save()
        elif event.button.id == "cancel-btn": self.action_cancel()
        elif event.button.id == "save-exit-btn": self.action_save_and_exit()


class DeleteConfirmModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for confirming the permanent deletion of an entry."""

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
        """Initializes the confirmation modal.

        Args:
            entry_id (int): The identifier of the entry to be deleted.
            entry_content (str): Content preview for the confirmation message.
            **kwargs (Any): Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.entry_id = entry_id
        self.entry_content = entry_content
        self.result: int | None = None

    def compose(self) -> ComposeResult:
        """Composes the modal layout."""
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
        """Confirms deletion and dismisses the modal with the entry identifier."""
        self.result = self.entry_id
        self.dismiss(self.entry_id)

    def action_cancel(self) -> None:
        """Cancels deletion and dismisses the modal."""
        self.result = None
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button interaction events."""
        if event.button.id == "delete-btn": self.action_confirm()
        elif event.button.id == "cancel-btn": self.action_cancel()


def _wrap_with_hanging_indent(text: str, indent: str) -> str:
    """Wrap text with a hanging indentation pattern.

    The first line starts with the given indent, and all subsequent
    lines are padded with the same indent so they align vertically
    with the first word of the first line.

    Args:
        text: The text content to wrap.
        indent: The indentation string for the first line (e.g. "  ").

    Returns:
        The text wrapped with consistent hanging indentation.
    """
    # Strip Rich markup tags to compute visible width for wrapping
    import re
    tag_pattern = re.compile(r"\[/?[^]]*\]")
    visible_text = tag_pattern.sub("", text)
    # Use a reasonable terminal width for wrapping
    wrap_width = 70
    words = visible_text.split()
    if not words:
        return f"{indent}{text}"

    # We build lines manually, accounting for markup length vs visible length
    lines: list[str] = []
    current_line_words: list[str] = []
    current_visible_len = 0

    for word in words:
        word_visible_len = len(tag_pattern.sub("", word))
        if current_visible_len + len(current_line_words) + word_visible_len <= wrap_width:
            current_line_words.append(word)
            current_visible_len += word_visible_len
        else:
            lines.append(" ".join(current_line_words))
            current_line_words = [word]
            current_visible_len = word_visible_len

    if current_line_words:
        lines.append(" ".join(current_line_words))

    # Now we need to re-insert markup. For simplicity, we join with the indent
    # and let Textual's native wrapping handle the rest. The key is the indent.
    indent_prefix = indent
    return (f"{indent_prefix}{lines[0]}\n" +
            "\n".join(f"{indent_prefix}{line}" for line in lines[1:]))


class LogsResultsView(ListView):
    """Component for displaying and interacting with a collection of journal entries."""

    def __init__(
        self, items: list[tuple[Entry, float]] | None = None, **kwargs: Any
    ) -> None:
        """Initializes the logs view.

        Args:
            items (list[tuple[Entry, float]], optional): Initial collection of entries.
            **kwargs (Any): Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._items = items or []

    def update_items(self, items: list[tuple[Entry, float]]) -> None:
        """Replaces the current collection of entries and refreshes the display.

        Args:
            items (list[tuple[Entry, float]]): The new collection of entries.
        """
        self._items = items
        self.clear()
        for entry, score in items:
            self.append_item(entry, score)

    def append_item(self, entry: Entry, score: float | None = None) -> None:
        """Appends a single entry to the view.

        Args:
            entry (Entry): The database entry object.
            score (float, optional): Match relevance score for search results.
        """
        label = self._format_entry(entry, score)
        list_item = ListItem(Label(label, markup=True))
        list_item.item_data = {"item": entry, "score": score, "type": "entry"}  # type: ignore[attr-defined]
        self.append(list_item)

    def _format_entry(self, entry: Entry, score: float | None = None) -> str:
        """Formats an entry into a markup string for UI presentation.

        Args:
            entry (Entry): The database entry object.
            score (float, optional): Match relevance score.

        Returns:
            str: The formatted markup string.
        """
        from ...ui_utils import format_entry_datetime

        date_str, time_str = format_entry_datetime(entry, self.app.ctx.config)
        content = entry.content
        
        use_emojis = self.app.ctx.config.display.use_emojis
        check_icon = get_icon("check", use_emojis)
        timer_icon = get_icon("timer", use_emojis)
        
        # Replace legacy ASCII markers with theme-aware icons
        if content.startswith("✅ "): content = content.replace("✅ ", f"{check_icon} ", 1)
        elif content.startswith("✓ "): content = content.replace("✓ ", f"{check_icon} ", 1)
        if "⏱️" in content: content = content.replace("⏱️", timer_icon)

        # Split tags into Git context vs User defined
        user_tags = [t for t in entry.tag_names if not t.startswith("git-")]
        git_tags = [t for t in entry.tag_names if t.startswith("git-")]

        tags_parts = []
        if user_tags:
            tags_parts.append(f"[{TAG}]#{' #'.join(user_tags)}[/]")
        if git_tags:
            # Context tags (Git) are rendered in a muted, dim style
            tags_parts.append(f"[dim #8c92a6]#{' #'.join(git_tags)}[/]")
        
        tags_str = " ".join(tags_parts)
        project_str = f" [{PROJECT}]&{entry.project}[/]" if entry.project else ""

        score_str = ""
        if score is not None:
            score_color = "green" if score >= 90 else "yellow" if score >= 75 else "dim"
            score_str = f" [{score_color}]({int(score)}%)[/]"

        theme = getattr(self.app, "theme_variables", {})
        time_hex = theme.get("success", "#73E6CB")
        color_tag = time_hex if time_hex.startswith("#") else f"#{time_hex}"
        
        datetime_str = f"[cyan]{date_str}[/]"
        if time_str:
            datetime_str = f"[cyan]{date_str}[/] [{color_tag}]{time_str}[/]"

        first_line = f"{datetime_str}  [dim]·[/]  {tags_str}{project_str}{score_str}"

        if not content:
            return first_line

        # Hanging indentation: subsequent lines align with the first word of content.
        # The prefix on the first line is: "{first_line}\n  "
        # We calculate the indent width as the visible length of "{first_line}  " 
        # and use that to pad subsequent lines.
        # For Rich markup, we count the raw string length minus markup tags.
        # A simpler approach: use a fixed indent that matches the "  " prefix
        # but with hanging wrap applied via textwrap.
        indent = "  "
        wrapped_content = _wrap_with_hanging_indent(content, indent)
        return f"{first_line}\n{wrapped_content}"


class LogsScreen(Container):
    """Primary interface for browsing, searching, and managing journal entries."""

    DEFAULT_CSS = """
    LogsScreen {
        height: 1fr;
        background: $background;
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
        margin: 0;
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
        border: none;
        border-bottom: solid $primary;
        margin: 0 1;
        padding: 1 2 0 2;
    }

    #search-input:focus {
        border: none;
        border-bottom: solid $accent;
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
        border: solid $primary;
        background: $panel;
        padding: 0;
    }

    LogsResultsView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
        margin: 0;
        padding: 1 2;
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
        """Initializes the logs screen.

        Args:
            ctx (AppContext): Application context.
            **kwargs (Any): Additional arguments passed to Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._all_entries: list[Entry] = []
        self._page_size = 50
        self._offset = 0
        self._has_more = True

    def compose(self) -> ComposeResult:
        """Composes the logs UI layout."""
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
        """Retrieves entries from the database using a paginated strategy.
        
        Args:
            reset (bool): If True, resets pagination state and clears current results.
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
        """Loads initial dataset and focuses the results view."""
        self._load_data(reset=True)
        self._display_recent_entries()
        self.query_one("#logs-results", LogsResultsView).focus()

    def on_show(self) -> None:
        """Refreshes the dataset when the screen is shown."""
        self._load_data(reset=True)
        self._display_recent_entries()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handles changes in the search input to filter entries.

        Args:
            event (Input.Changed): The input change event.
        """
        if event.input.id == "search-input":
            query = event.value.strip()
            self.query_one("#btn-load-more").display = not bool(query)
            self._perform_search(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button interaction events."""
        if event.button.id == "btn-standup":
            from .standup import StandupScreen
            self.app.push_screen(StandupScreen(self.ctx))
        elif event.button.id == "btn-quick-add": self.action_quick_add()
        elif event.button.id == "btn-load-more": self.action_load_more()

    def action_load_more(self) -> None:
        """Retrieves and appends the next page of entries."""
        if not self._has_more: return
        self._load_data(reset=False)
        self._display_recent_entries(append=True)

    def _perform_search(self, query: str) -> None:
        """Executes a fuzzy search against loaded entries.

        Args:
            query (str): The search query.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        query = query.strip()

        if not query:
            self._display_recent_entries()
            return

        results_view.clear()
        matched_entries = search_items(query, self._all_entries, limit=50, threshold=50)

        for entry, score in matched_entries:
            results_view.append_item(entry, score)

        self._update_status_bar(len(matched_entries), is_search=True)

    def _display_recent_entries(self, append: bool = False) -> None:
        """Updates the UI with the current collection of loaded entries.

        Args:
            append (bool): If True, appends the latest page instead of clearing.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        
        if not append:
            results_view.clear()
            entries_to_show = self._all_entries
        else:
            entries_to_show = self._all_entries[-self._page_size:]

        for entry in entries_to_show:
            results_view.append_item(entry, score=None)

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
        """Updates the status bar with result metrics.

        Args:
            count (int): Number of entries displayed.
            is_search (bool): Indicates if the results are from a search query.
        """
        use_emojis = self.ctx.config.display.use_emojis
        bullet = get_icon("bullet", use_emojis)
        label = f"Found {count} matches" if is_search else f"Showing {count} recent entries"
        self.query_one("#logs-status-bar", Label).update(
            f"{label}  {bullet}  j/k: Navigate  {bullet}  e: Edit  {bullet}  d: Delete  {bullet}  t: Tags  {bullet}  p: Project  {bullet}  /: Search  {bullet}  q: Quit"
        )

    def _get_selected_entry(self) -> Entry | None:
        """Retrieves the entry currently highlighted in the results view.

        Returns:
            Entry | None: The selected entry or None if no selection exists.
        """
        results_view = self.query_one("#logs-results", LogsResultsView)
        if results_view.highlighted_child is None: return None
        item_data = results_view.highlighted_child.item_data  # type: ignore[attr-defined]
        return item_data.get("item") if item_data else None

    def action_cursor_down(self) -> None:
        """Moves focus to the next item in the results list."""
        self.query_one("#logs-results", LogsResultsView).action_cursor_down()

    def action_cursor_up(self) -> None:
        """Moves focus to the previous item in the results list."""
        self.query_one("#logs-results", LogsResultsView).action_cursor_up()

    def action_focus_search(self) -> None:
        """Transfers focus to the search input field."""
        self.query_one("#search-input", Input).focus()

    def action_select(self) -> None:
        """Copies the content of the selected entry to the system clipboard."""
        entry = self._get_selected_entry()
        if entry is None:
            self.notify("No entry selected", severity="warning", timeout=1.5)
            return

        try:
            import pyperclip
            pyperclip.copy(entry.content)
            self.notify(f"Copied: {entry.content[:50]}...", timeout=2)
        except Exception:
            self.notify(f"Content: {entry.content}", timeout=3)

    def action_edit_content(self) -> None:
        """Opens the edit modal for the selected entry."""
        entry = self._get_selected_entry()
        if entry is None: return

        def on_dismiss(result: Any) -> None:
            if result is None or result[0] is None: return
            content, tags, project, created_at = result
            
            async def edit_worker() -> None:
                self.ctx.db.update_entry(entry.id, content=content, tags=tags, project=project, created_at=created_at)
                self.notify(f"Entry #{entry.id} updated")
                self._load_data()
                self._display_recent_entries()

            self.run_worker(edit_worker())

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_delete_entry(self) -> None:
        """Confirms and executes deletion of the selected entry."""
        entry = self._get_selected_entry()
        if entry is None: return

        def on_dismiss(result: int | None) -> None:
            if result is not None:
                async def delete_worker() -> None:
                    self.ctx.db.delete_entry(result)
                    self.notify(f"Entry #{result} deleted")
                    self._load_data()
                    self._display_recent_entries()

                self.run_worker(delete_worker())

        self.app.push_screen(DeleteConfirmModal(entry.id, entry.content), on_dismiss)

    def action_edit_tags(self) -> None:
        """Opens the edit modal specifically for modifying tags."""
        entry = self._get_selected_entry()
        if entry is None: return

        def on_dismiss(result: Any) -> None:
            if result is None or result[1] is None: return
            
            async def tags_worker() -> None:
                self.ctx.db.update_entry(entry.id, tags=result[1])
                self.notify(f"Entry #{entry.id} tags updated")
                self._load_data()
                self._display_recent_entries()

            self.run_worker(tags_worker())

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_edit_project(self) -> None:
        """Opens the edit modal specifically for modifying the project."""
        entry = self._get_selected_entry()
        if entry is None: return

        def on_dismiss(result: Any) -> None:
            if result is None or result[2] is None: return
            
            async def project_worker() -> None:
                self.ctx.db.update_entry(entry.id, project=result[2])
                self.notify(f"Entry #{entry.id} project updated")
                self._load_data()
                self._display_recent_entries()

            self.run_worker(project_worker())

        self.app.push_screen(EditEntryModal(entry), on_dismiss)

    def action_quick_add(self) -> None:
        """Opens the modal for creating a new journal entry."""
        def on_dismiss(result: Any) -> None:
            if result is None or result[0] is None: return
            content, tags, project, created_at = result
            
            async def add_worker() -> None:
                self.ctx.db.add_entry(content=content, tags=tags, project=project, created_at=created_at)
                self.notify("New entry added")
                self._load_data()
                self._display_recent_entries()

            self.run_worker(add_worker())

        self.app.push_screen(QuickAddEntryModal(), on_dismiss)

    def on_entry_added(self, message: Any) -> None:
        """Responds to EntryAdded events by refreshing the view."""
        self._load_data()
        self._display_recent_entries()
