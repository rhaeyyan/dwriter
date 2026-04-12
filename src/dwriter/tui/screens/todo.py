"""Todo screen for dwriter TUI.

This module provides the todo board for task management, including
completion tracking, prioritization, and metadata editing.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext
    from ..app import DWriterApp

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
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

from ...database import Todo
from ..colors import (
    PROJECT,
    TAG,
    get_icon,
)
from ..messages import EntryAdded, TodoUpdated


class AddTodoForm(Vertical):
    """Inline form for rapid task addition directly from the board."""

    app: DWriterApp

    DEFAULT_CSS = """
    AddTodoForm {
        padding: 1 4;
        height: auto;
        background: $surface;
    }

    #add-form-title {
        text-style: bold;
        padding-bottom: 1;
        color: $primary;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-col {
        width: 1fr;
        height: auto;
    }

    #add-buttons {
        margin-top: 1;
        width: 100%;
        height: auto;
    }

    #add-buttons Button {
        width: 1fr;
    }

    Label {
        color: $text-muted;
        padding: 1 0 0 0;
    }

    Input {
        margin-bottom: 1;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
        background: transparent;
    }

    Input:focus {
        border: none;
        border-bottom: solid $accent;
        background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        """Composes the form fields."""
        yield Label("Quick Add Task", id="add-form-title")
        
        yield Label("Content:")
        yield Input(id="add-content", placeholder="What needs to be done?")

        with Horizontal(classes="form-row"):
            with Vertical(classes="form-col"):
                date_fmt = self.app.ctx.config.display.due_date_format
                yield Label("Due Date:")
                yield Input(id="add-date", placeholder=f"today, {date_fmt}, +5d...")
            with Vertical(classes="form-col"):
                yield Label("Time:")
                yield Input(id="add-time", placeholder="2pm, 14:30, +2h...")
        
        yield Label("Tags:")
        yield Input(id="add-tags", placeholder="work, personal, etc.")

        yield Label("Project:")
        yield Input(id="add-project", placeholder="Project name (optional)")

        with Horizontal(id="add-buttons"):
            yield Button("\\[ SAVE ]", id="add-save-btn", variant="primary")
            yield Button("\\[ SAVE AS REMINDER ]", id="add-reminder-btn", variant="error")
            yield Button("\\[ CANCEL ]", id="add-cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatches button press events."""
        if event.button.id == "add-save-btn":
            self.action_save(is_reminder=False)
        elif event.button.id == "add-reminder-btn":
            self.action_save(is_reminder=True)
        elif event.button.id == "add-cancel-btn":
            self.action_cancel()

    def action_cancel(self) -> None:
        """Cancels the add operation and returns to the pending list."""
        self.post_message(self.AddTodoCancel())

    def action_save(self, is_reminder: bool = False) -> None:
        """Assembles form data and emits a signal to the parent screen."""
        content = self.query_one("#add-content", Input).value.strip()
        if not content: return

        date_val = self.query_one("#add-date", Input).value.strip()
        time_val = self.query_one("#add-time", Input).value.strip()
        due_str = f"{date_val} {time_val}".strip() or None

        tags_raw = self.query_one("#add-tags", Input).value.strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
        project = self.query_one("#add-project", Input).value.strip() or None

        self.post_message(self.AddTodoSignal(content, due_str, tags, project, is_reminder))

    class AddTodoSignal(Message):
        """Signal emitted when a task is submitted via the form."""
        def __init__(self, content: str, due_str: str | None, tags: list[str], project: str|None, is_reminder: bool = False) -> None:
            super().__init__()
            self.content = content
            self.due_str = due_str
            self.tags = tags
            self.project = project
            self.is_reminder = is_reminder

    class AddTodoCancel(Message):
        """Signal emitted when the add operation is cancelled."""
        def __init__(self) -> None:
            super().__init__()


class TodoListItem(ListItem):
    """Custom list item for representing todo objects in a ListView."""

    app: DWriterApp

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initializes the todo list item.

        Args:
            todo (Todo): The database todo object.
            **kwargs (Any): Additional arguments passed to ListItem.
        """
        super().__init__(**kwargs)
        self.todo = todo


class EditTodoModal(ModalScreen):  # type: ignore[type-arg]
    """Modal dialog for modifying task attributes."""

    app: DWriterApp

    CSS = """
    EditTodoModal {
        align: center middle;
    }

    #edit-modal-container {
        width: 85%;
        max-width: 100;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: solid $primary;
        padding: 1 3;
        overflow-y: auto;
    }

    #edit-modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    #edit-content-label, #edit-date-label, #edit-time-label, #edit-tags-label, #edit-project-label {
        color: $text-muted;
        padding: 1 0 0 0;
    }

    #edit-input {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
    }

    #date-input, #time-input, #tags-input, #project-input {
        width: 100%;
        margin: 0 0 1 0;
        border: none;
        border-bottom: solid $primary;
        padding: 1 2 0 2;
    }

    .horizontal-row {
        height: 5;
        width: 100%;
    }

    .col {
        width: 1fr;
        height: auto;
    }

    #edit-buttons {
        align: center middle;
        padding: 1 0;
        height: 3;
        width: 100%;
    }

    Button {
        margin: 0 1;
    }

    #save-as-reminder-btn {
        background: $error;
        color: white;
    }

    #help-text {
        text-style: italic;
        color: $foreground 60%;
        padding: 0 0 1 0;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "save", "Save"),
    ]

    def __init__(self, todo: Todo, **kwargs: Any) -> None:
        """Initializes the edit modal.

        Args:
            todo (Todo): The todo object to modify.
            **kwargs (Any): Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.todo = todo
        self.result: tuple[str | None, str | None, list[str] | None, str | None, bool] = (
            None,
            None,
            None,
            None,
            False,
        )

    def compose(self) -> ComposeResult:
        """Composes the modal UI."""
        with Vertical(id="edit-modal-container"):
            yield Label(f"Edit Task #{self.todo.id}", id="edit-modal-title")

            yield Label("Content:", id="edit-content-label")
            yield Input(
                value=self.todo.content,
                id="edit-input",
                placeholder="Enter task content...",
            )

            date_fmt = self.app.ctx.config.display.due_date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            hint = fmt_map.get(date_fmt, "%Y-%m-%d")

            with Horizontal(classes="horizontal-row"):
                with Vertical(classes="col"):
                    yield Label("Due Date:", id="edit-date-label")
                    date_val = self.todo.due_date.strftime(hint) if self.todo.due_date else ""
                    yield Input(
                        value=date_val,
                        id="date-input",
                        placeholder=f"{date_fmt}, tomorrow, etc.",
                    )
                with Vertical(classes="col"):
                    yield Label("Time:", id="edit-time-label")
                    time_str = ""
                    if self.todo.due_date and (self.todo.due_date.hour != 0 or self.todo.due_date.minute != 0):
                        time_str = self.todo.due_date.strftime("%H:%M")
                    yield Input(
                        value=time_str,
                        id="time-input",
                        placeholder="2pm, 14:30, +2h, etc.",
                    )
            yield Label("Examples: tomorrow, Friday, 2pm, +15m", id="help-text")

            yield Label("Tags:", id="edit-tags-label")
            tags_str = ", ".join(self.todo.tag_names) if self.todo.tag_names else ""
            yield Input(value=tags_str, id="tags-input", placeholder="Comma-separated tags")

            yield Label("Project:", id="edit-project-label")
            yield Input(value=self.todo.project or "", id="project-input", placeholder="Project name (optional)")

            with Horizontal(id="edit-buttons"):
                yield Button("\\[ SAVE ]", id="save-btn", variant="primary")
                yield Button("\\[ SAVE AS REMINDER ]", id="save-as-reminder-btn", variant="error")
                yield Button("\\[ CANCEL ]", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Focuses the content input."""
        self.query_one("#edit-input", Input).focus()

    def action_save(self, is_reminder: bool = False) -> None:
        """Assembles data and dismisses the modal with the result."""
        content = self.query_one("#edit-input", Input).value.strip() or None
        date_val = self.query_one("#date-input", Input).value.strip()
        time_val = self.query_one("#time-input", Input).value.strip()
        due_date_str = f"{date_val} {time_val}".strip() or None

        tags_str = self.query_one("#tags-input", Input).value.strip() or None
        project = self.query_one("#project-input", Input).value.strip() or None
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else None

        self.result = (content, due_date_str, tags, project, is_reminder)
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        """Closes the modal without modifications."""
        self.result = (None, None, None, None, False)
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatches button press events."""
        if event.button.id == "save-btn": self.action_save(is_reminder=False)
        elif event.button.id == "save-as-reminder-btn": self.action_save(is_reminder=True)
        elif event.button.id == "cancel-btn": self.action_cancel()


def _wrap_todo_with_hanging_indent(text: str, indent: str) -> str:
    """Wrap text with a hanging indentation pattern for todo items.

    Args:
        text: The text content to wrap (may contain Rich markup).
        indent: The indentation string for the first line.

    Returns:
        The text wrapped with consistent hanging indentation.
    """
    tag_pattern = re.compile(r"\[/?[^]]*\]")
    visible_text = tag_pattern.sub("", text)
    wrap_width = 70
    words = visible_text.split()
    if not words:
        return f"{indent}{text}"

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

    indent_prefix = indent
    return (f"{indent_prefix}{lines[0]}\n" +
            "\n".join(f"{indent_prefix}{line}" for line in lines[1:]))


class TodoListView(ListView):
    """Component for displaying and sorting task collections."""

    def __init__(self, todos: list[Todo] | None = None, **kwargs: Any) -> None:
        """Initializes the todo list view.

        Args:
            todos (list[Todo], optional): Initial collection of tasks.
            **kwargs (Any): Additional arguments passed to ListView.
        """
        super().__init__(**kwargs)
        self._todos = todos or []
        self._loaded = False

    def _sort_todos(self, todos: list[Todo]) -> list[Todo]:
        """Sorts tasks based on priority, urgency, and completion status.

        The sorting strategy adheres to the configured 'todo_sorting_mode',
        prioritizing either priority level or due date. Active reminders
        are always hoisted to the top.

        Args:
            todos (list[Todo]): The collection of tasks to sort.

        Returns:
            list[Todo]: The sorted collection.
        """
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        sorting_mode = self.app.ctx.config.display.todo_sorting_mode

        def sort_key(todo: Todo) -> tuple[int, int, int, float]:
            if todo.status == "completed":
                completed_score = -int(todo.completed_at.timestamp()) if todo.completed_at else 0
                return (999, 0, 0, float(completed_score))

            is_active_reminder = 0 if (
                todo.priority == "urgent" and todo.due_date and 
                todo.due_date <= datetime.now() + timedelta(minutes=30)
            ) else 1

            priority_score = priority_order.get(todo.priority, 2)
            due_score = 9999
            if todo.due_date:
                due_date_only = todo.due_date.replace(hour=0, minute=0, second=0, microsecond=0)
                days_until = (due_date_only - today).days
                due_score = days_until - 1000 if days_until < 0 else days_until

            created_score = -todo.created_at.timestamp() if todo.created_at else 0.0

            if sorting_mode == "date_first":
                return (is_active_reminder, due_score, priority_score, created_score)
            return (is_active_reminder, priority_score, due_score, created_score)

        return sorted(todos, key=sort_key)

    def update_todos(self, todos: list[Todo]) -> None:
        """Refreshes the display with a new collection of tasks.

        Args:
            todos (list[Todo]): The tasks to display.
        """
        sorted_todos = self._sort_todos(todos)
        self._todos = sorted_todos
        self._loaded = True
        self.clear()
        for todo in sorted_todos:
            self.append_item(todo)

    def append_item(self, todo: Todo) -> None:
        """Appends a task to the view.

        Args:
            todo (Todo): The database task object.
        """
        label = self._format_todo(todo)
        list_item = TodoListItem(todo)
        list_item._add_child(Label(label, markup=True))
        self.append(list_item)

    def _format_todo(self, todo: Todo) -> str:
        """Generates markup for task display.

        Args:
            todo (Todo): The task object to format.

        Returns:
            str: Formatted markup string.
        """
        from ..colors import PRIORITY_URGENT, REMINDER_COLOR, get_weekday_color
        
        priority_map = {
            "urgent": f"[{PRIORITY_URGENT}]\\[Urgent][/]",
            "high": "[#FCBF49]\\[High][/]",
            "normal": "[white]\\[Normal][/]",
            "low": "[dim]\\[Low][/]",
        }
        pri_str = priority_map.get(todo.priority, "[white]\\[N][/]")

        if todo.status == "completed" and todo.completed_at:
            # Use format_entry_datetime helper for consistency, wrapping completed_at in a dummy Entry if needed
            # but simpler to just use the config here since we have it
            date_fmt_setting = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            strftime_fmt = fmt_map.get(date_fmt_setting, "%Y-%m-%d")
            d_str = f"[cyan]{todo.completed_at.strftime(strftime_fmt + ' %H:%M')}[/cyan]"
        elif todo.due_date:
            weekday = todo.due_date.weekday()
            wd_color = get_weekday_color(weekday)
            
            # Format as requested: [Tuesday 2026-04-07]
            date_fmt_setting = self.app.ctx.config.display.date_format
            fmt_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "MM/DD/YYYY": "%m/%d/%Y",
                "DD/MM/YYYY": "%d/%m/%Y",
            }
            strftime_fmt = fmt_map.get(date_fmt_setting, "%Y-%m-%d")
            date_str = todo.due_date.strftime(strftime_fmt)
            day_name = todo.due_date.strftime('%A')
            
            d_str = f"[{wd_color}]\\[{day_name} {date_str}][/]"
            
            # Add [due time, if applicable] - use $success to match logs
            if todo.due_date.hour != 0 or todo.due_date.minute != 0:
                use_24hr = self.app.ctx.config.display.clock_24hr
                t_fmt = "%H:%M" if use_24hr else "%I:%M %p"
                d_str += f" [$success]\\[{todo.due_date.strftime(t_fmt)}][/]"
        else:
            d_str = "[dim]\\[---][/]"

        safe_content = todo.content.replace("[", "\\[")
        
        # Split tags into Git context vs User defined
        user_tags = [t for t in todo.tag_names if not t.startswith("git-")]
        git_tags = [t for t in todo.tag_names if t.startswith("git-")]

        tags_parts = []
        if user_tags:
            tags_parts.append(f"[{TAG}]#{' #'.join(user_tags)}[/]")
        if git_tags:
            # Context tags (Git) are rendered in a muted, dim style
            tags_parts.append(f"[dim #8c92a6]#{' #'.join(git_tags)}[/]")
        
        tags_str = " ".join(tags_parts)
        project_str = f" [{PROJECT}]&{todo.project}[/]" if todo.project else ""

        is_active_reminder = (
            todo.status == "pending" and todo.priority == "urgent" and
            todo.due_date and todo.due_date <= datetime.now() + timedelta(minutes=30)
        )

        first_line = f"{d_str} {pri_str}  [dim]·[/]  {tags_str}{project_str}"

        # Hanging indentation for content: subsequent lines align with first word
        indent = "  "

        if todo.status == "completed":
            use_emojis = self.app.ctx.config.display.use_emojis
            check_icon = get_icon("check", use_emojis)
            content_text = f"{check_icon} {safe_content}"
            wrapped = _wrap_todo_with_hanging_indent(content_text, indent)
            return f"[dim]{first_line}\n{wrapped}[/]"
        if is_active_reminder:
            content_text = f"🔔 {safe_content}"
            wrapped = _wrap_todo_with_hanging_indent(content_text, indent)
            return f"[{REMINDER_COLOR}]{first_line}\n{wrapped}[/]"

        content_text = f"[bold white]{safe_content}[/]"
        wrapped = _wrap_todo_with_hanging_indent(safe_content, indent)
        return f"{first_line}\n[bold white]{wrapped}[/]"

    @property
    def selected_todo(self) -> Todo | None:
        """Retrieves the currently highlighted task."""
        if isinstance(self.highlighted_child, TodoListItem):
            return self.highlighted_child.todo
        return None


class TodoScreen(Container):
    """Primary interface for managing the task lifecycle."""

    app: DWriterApp

    DEFAULT_CSS = """
    TodoScreen {
        height: 1fr;
    }

    #todo-header-container {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        background: $panel;
        border: none;
        border-bottom: solid $primary;
    }

    #todo-title {
        text-style: bold;
        color: $foreground;
    }

    #todo-subtitle {
        color: $foreground 60%;
    }

    #todo-list-container {
        height: 1fr;
        margin: 0 2;
    }

    TodoListView {
        height: 1fr;
        border: solid $primary;
        background: $panel;
        padding: 0;
    }

    TodoListView:focus {
        border: solid $accent;
    }

    ListItem {
        height: auto;
        margin-bottom: 1;
        padding: 0 2;
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
        color: $foreground 60%;
        padding: 0 2;
    }

    TabbedContent {
        height: 1fr;
    }

    TabbedContent > TabPane {
        padding: 0;
    }

    #todo-tabs Tabs Tab#tab-add-pane {
        color: $success;
        text-style: bold;
        background: transparent;
        padding: 0 1;
        min-width: 0;
    }

    #todo-tabs Tabs Tab#tab-add-pane:hover {
        background: $success 20%;
        color: $success;
        text-style: bold;
    }

    #todo-tabs Tabs Tab#tab-add-pane.-active {
        background: $success;
        color: $background;
        text-style: bold;
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

    filter_status = reactive("pending")
    show_header = reactive(False)

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the todo screen.

        Args:
            ctx (AppContext): Application context.
            **kwargs (Any): Additional arguments passed to Container.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._all_todos: list[Todo] = []

    def compose(self) -> ComposeResult:
        """Composes the todo UI layout."""
        use_emojis = self.ctx.config.display.use_emojis
        with Vertical():
            with Container(id="todo-header-container"):
                yield Label(f"{get_icon('todo', use_emojis)} To-Do Board", id="todo-title")
                yield Label(
                    f"Space: Complete {get_icon('bullet', use_emojis)} e: Edit {get_icon('bullet', use_emojis)} +/-: Priority {get_icon('bullet', use_emojis)} "
                    f"d: Delete {get_icon('bullet', use_emojis)} 1/2/3: Tabs {get_icon('bullet', use_emojis)} h: Hide header {get_icon('bullet', use_emojis)} q: Quit",
                    id="todo-subtitle",
                )
            with TabbedContent(initial="pending-pane", id="todo-tabs"):
                with TabPane("\\[+]", id="add-pane"):
                    yield AddTodoForm()
                with TabPane(f"{get_icon('timer', use_emojis)} Pending (0)", id="pending-pane"):
                    yield TodoListView(id="todos")
                with TabPane(f"{get_icon('history', use_emojis)} Upcoming (0)", id="upcoming-pane"):
                    yield TodoListView(id="todos-upcoming")
                with TabPane(f"{get_icon('check', use_emojis)} Completed (0)", id="completed-pane"):
                    yield TodoListView(id="todos-completed")

    def watch_show_header(self, show: bool) -> None:
        """Updates header visibility based on reactive state."""
        try:
            header = self.query_one("#todo-header-container", Container)
            if header: header.display = show
        except Exception: pass

    def action_toggle_header(self) -> None:
        """Toggles the visibility of the board header."""
        self.show_header = not self.show_header

    def on_mount(self) -> None:
        """Performs initial data load and focuses the pending task list."""
        self._load_todos()
        self.query_one(TabbedContent).active = "pending-pane"
        active_view = self._get_active_list_view()
        if active_view: active_view.focus()

    def on_show(self) -> None:
        """Refreshes task data when the screen becomes visible."""
        self._load_todos()
        active_view = self._get_active_list_view()
        if active_view: active_view.focus()

    def watch_filter_status(self, status: str) -> None:
        """Updates the active tab and reloads data when the filter status changes."""
        tab_map = {"pending": "pending-pane", "completed": "completed-pane", "upcoming": "upcoming-pane"}
        tabbed = self.query_one(TabbedContent)
        tab_id = tab_map.get(status, "pending-pane")
        if tabbed.active != tab_id: tabbed.active = tab_id
        self._load_todos()

    def _get_active_list_view(self) -> TodoListView | None:
        """Retrieves the TodoListView component for the currently active tab."""
        active = self.query_one(TabbedContent).active
        if active == "pending-pane": return self.query_one("#todos", TodoListView)
        if active == "completed-pane": return self.query_one("#todos-completed", TodoListView)
        if active == "upcoming-pane": return self.query_one("#todos-upcoming", TodoListView)
        return None

    def _load_todos(self) -> None:
        """Loads task data from the database and refreshes all constituent lists."""
        self._all_todos = self.ctx.db.get_todos()
        self._update_all_lists()

    def on_add_todo_form_add_todo_signal(self, message: AddTodoForm.AddTodoSignal) -> None:
        """Handles task creation from the inline add form."""
        from ...date_utils import parse_natural_date
        try:
            due_date_format = self.ctx.config.display.due_date_format
            fmt_map = {"YYYY-MM-DD": "%Y-%m-%d", "MM/DD/YYYY": "%m/%d/%Y", "DD/MM/YYYY": "%d/%m/%Y"}
            hint = fmt_map.get(due_date_format)
            due_date = parse_natural_date(message.due_str, prefer_future=True, format_hint=hint) if message.due_str else None
            
            async def add_worker() -> None:
                task = self.ctx.db.add_todo(
                    content=message.content, due_date=due_date, tags=message.tags,
                    project=message.project, priority="urgent" if message.is_reminder else "normal",
                )
                self.notify(f"Added task: {task.content}")
                
                self._load_todos()
                self.post_message(TodoUpdated(todo_id=task.id, action="added"))

            self.run_worker(add_worker())
            
            form = self.query_one(AddTodoForm)
            for inp_id in ["#add-content", "#add-date", "#add-time", "#add-tags", "#add-project"]:
                form.query_one(inp_id, Input).value = ""
            
            self.query_one(TabbedContent).active = "pending-pane"
            self.query_one("#todos", TodoListView).focus()
        except Exception as e:
            self.notify(f"Error adding task: {e}", severity="error")

    def on_add_todo_form_add_todo_cancel(self, message: AddTodoForm.AddTodoCancel) -> None:
        """Handles cancellation from the inline add form."""
        self.query_one(TabbedContent).active = "pending-pane"
        active_view = self._get_active_list_view()
        if active_view: active_view.focus()

    def _get_upcoming_todos(self) -> list[Todo]:
        """Filters pending tasks due within the next 72 hours."""
        all_todos = self.ctx.db.get_all_todos()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        upcoming = [t for t in all_todos if t.status == "pending" and t.due_date and 0 <= (t.due_date.replace(hour=0, minute=0, second=0, microsecond=0) - today).days <= 2]
        
        pending_list = self.query("#todos").first(TodoListView)
        return pending_list._sort_todos(upcoming) if pending_list else upcoming

    def _update_all_lists(self) -> None:
        """Updates the content and item counts for all task tabs."""
        all_todos = self.ctx.db.get_all_todos()
        pending = [t for t in all_todos if t.status == "pending"]
        completed = [t for t in all_todos if t.status == "completed"]
        upcoming = self._get_upcoming_todos()

        self._update_tab_labels(len(pending), len(upcoming), len(completed))

        for pending_list in self.query("#todos").results(TodoListView): pending_list.update_todos(pending)
        for upcoming_list in self.query("#todos-upcoming").results(TodoListView): upcoming_list.update_todos(upcoming)
        for completed_list in self.query("#todos-completed").results(TodoListView): completed_list.update_todos(completed)

    def _update_tab_labels(self, pending_count: int, upcoming_count: int, completed_count: int) -> None:
        """Refreshes tab titles with updated item counts."""
        try:
            tabbed = self.query_one("#todo-tabs", TabbedContent)
            use_emojis = self.ctx.config.display.use_emojis
            
            p_tab = tabbed.get_tab("pending-pane")
            if p_tab: p_tab.label = f"{get_icon('timer', use_emojis)} Pending ({pending_count})"
            
            u_tab = tabbed.get_tab("upcoming-pane")
            if u_tab: u_tab.label = f"{get_icon('history', use_emojis)} Upcoming ({upcoming_count})"
            
            c_tab = tabbed.get_tab("completed-pane")
            if c_tab: c_tab.label = f"{get_icon('check_small', use_emojis)} Completed ({completed_count})"
            
            tabbed.refresh()
        except Exception: pass

    def _get_selected_todo(self) -> Todo | None:
        """Retrieves the task currently selected in the active view."""
        active_view = self._get_active_list_view()
        return active_view.selected_todo if active_view else None

    def action_cursor_down(self) -> None:
        """Moves selection to the next task in the active list."""
        view = self._get_active_list_view()
        if view: view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Moves selection to the previous task in the active list."""
        view = self._get_active_list_view()
        if view: view.action_cursor_up()

    def action_toggle_complete(self) -> None:
        """Toggles the completion status of the selected task.

        Tasks marked as complete are automatically logged to the journal.
        Reverting a task to pending removes the associated log entry.
        """
        todo = self._get_selected_todo()
        if todo is None: return

        new_status = "pending" if todo.status == "completed" else "completed"
        now = datetime.now()

        async def toggle_worker() -> None:
            self.ctx.db.update_todo(todo.id, status=new_status, completed_at=now if new_status == "completed" else None)

            if new_status == "completed":
                use_emojis = self.app.ctx.config.display.use_emojis
                entry = self.ctx.db.add_entry(
                    content=f"{get_icon('check', use_emojis)} {todo.content}",
                    tags=todo.tag_names, project=todo.project, created_at=now, todo_id=todo.id,
                )
                self.notify(f"Task #{todo.id} completed & logged!")
                self.post_message(EntryAdded(entry_id=entry.id, content=entry.content, created_at=entry.created_at))
            else:
                self.ctx.db.delete_entry_by_todo_id(todo.id)
                self.notify(f"Task #{todo.id} marked pending")

            self._load_todos()
            self.post_message(TodoUpdated(todo_id=todo.id, action="updated"))

        self.run_worker(toggle_worker())

    def action_edit(self) -> None:
        """Opens the edit modal for the selected task."""
        todo = self._get_selected_todo()
        if not todo: return

        def on_dismiss(result: Any) -> None:
            if result is None or result[0] is None: return
            content, due_str, tags, project, is_reminder = result
            due_date = self._parse_due_date(due_str) if due_str else None
            priority = "urgent" if is_reminder else todo.priority

            async def edit_worker() -> None:
                self.ctx.db.update_todo(
                    todo.id, content=content, due_date=due_date, tags=tags, 
                    project=project, priority=priority,
                    reminder_last_sent=None if is_reminder else todo.reminder_last_sent
                )
                self.notify(f"Task #{todo.id} updated")
                self._load_todos()
                self.post_message(TodoUpdated(todo_id=todo.id, action="updated"))

            self.run_worker(edit_worker())

        self.app.push_screen(EditTodoModal(todo), on_dismiss)

    def action_delete(self) -> None:
        """Permanently removes the selected task."""
        todo = self._get_selected_todo()
        if not todo: return
        
        async def delete_worker() -> None:
            self.ctx.db.delete_todo(todo.id)
            self.notify(f"Task #{todo.id} deleted")
            self._load_todos()
            self.post_message(TodoUpdated(todo_id=todo.id, action="deleted"))

        self.run_worker(delete_worker())

    def action_increase_priority(self) -> None:
        """Elevates the priority of the selected task."""
        todo = self._get_selected_todo()
        if not todo: return
        priorities = ["low", "normal", "high", "urgent"]
        idx = priorities.index(todo.priority) if todo.priority in priorities else 1
        new_priority = priorities[min(idx + 1, len(priorities) - 1)]
        
        async def priority_worker() -> None:
            self.ctx.db.update_todo(todo.id, priority=new_priority)
            self._load_todos()
        
        self.run_worker(priority_worker())

    def action_decrease_priority(self) -> None:
        """Lowers the priority of the selected task."""
        todo = self._get_selected_todo()
        if not todo: return
        priorities = ["low", "normal", "high", "urgent"]
        idx = priorities.index(todo.priority) if todo.priority in priorities else 1
        new_priority = priorities[max(idx - 1, 0)]

        async def priority_worker() -> None:
            self.ctx.db.update_todo(todo.id, priority=new_priority)
            self._load_todos()

        self.run_worker(priority_worker())

    def action_switch_tab_pending(self) -> None:
        """Activates the pending tasks tab."""
        self.filter_status = "pending"

    def action_switch_tab_upcoming(self) -> None:
        """Activates the upcoming tasks tab."""
        self.filter_status = "upcoming"

    def action_switch_tab_completed(self) -> None:
        """Activates the completed tasks tab."""
        self.filter_status = "completed"

    def action_next_tab(self) -> None:
        """Cycles to the next task tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["upcoming-pane", "pending-pane", "completed-pane"]
        idx = (tabs.index(tabbed.active) + 1) % len(tabs) if tabbed.active in tabs else 0
        self.filter_status = tabs[idx].replace("-pane", "")

    def _parse_due_date(self, due_str: str) -> datetime | None:
        """Parses a due date string with temporal awareness.

        Args:
            due_str (str): The date string to parse.

        Returns:
            datetime | None: Parsed datetime or None.
        """
        from ...date_utils import parse_natural_date
        try:
            fmt_map = {"YYYY-MM-DD": "%Y-%m-%d", "MM/DD/YYYY": "%m/%d/%Y", "DD/MM/YYYY": "%d/%m/%Y"}
            hint = fmt_map.get(self.app.ctx.config.display.due_date_format)
            return parse_natural_date(due_str, prefer_future=True, format_hint=hint)
        except ValueError: return None

    def on_todo_updated(self, message: TodoUpdated) -> None:
        """Refreshes data in response to TodoUpdated events."""
        self._load_todos()
