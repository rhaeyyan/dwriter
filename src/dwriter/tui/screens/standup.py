"""Standup & Review Screen for dwriter TUI."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

import pyperclip
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from ...ui_utils import format_entry_datetime
from ..colors import get_icon


class ExportFormatScreen(ModalScreen[str]):
    """Modal screen for selecting export format."""

    DEFAULT_CSS = """
    ExportFormatScreen { align: center middle; background: rgba(13, 15, 24, 0.85); }
    #export-container { width: 50; height: auto; border: solid $primary; background: $panel; padding: 1 2; }
    #export-title { text-align: center; text-style: bold; margin-bottom: 1; }
    #export-container Button { width: 100%; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="export-container"):
            yield Label(f"{get_icon('export', use_emojis)} Export As", id="export-title")
            yield Button(f"\\[ {get_icon('markdown', use_emojis)} MARKDOWN ]", id="export-markdown", variant="primary")
            yield Button(f"\\[ {get_icon('note', use_emojis)} PLAIN ]", id="export-plain", variant="default")
            yield Button(f"\\[ {get_icon('csv', use_emojis)} CSV ]", id="export-csv", variant="default")
            yield Button(f"\\[ {get_icon('json', use_emojis)} JSON ]", id="export-json", variant="default")
            yield Button("\\[ CANCEL ]", id="export-cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export-markdown":
            self.dismiss("markdown")
        elif event.button.id == "export-plain":
            self.dismiss("plain")
        elif event.button.id == "export-csv":
            self.dismiss("csv")
        elif event.button.id == "export-json":
            self.dismiss("json")
        elif event.button.id == "export-cancel":
            self.dismiss(None)


class RangeSelectionScreen(ModalScreen[tuple[datetime, datetime] | None]):
    """Modal screen for selecting a date range."""

    DEFAULT_CSS = """
    RangeSelectionScreen { align: center middle; background: rgba(13, 15, 24, 0.85); }
    #range-container { width: 50; height: auto; border: solid $primary; background: $panel; padding: 1 2; }
    #range-title { text-align: center; text-style: bold; margin-bottom: 1; }
    .range-inputs { height: auto; margin-bottom: 1; }
    #range-start, #range-end { width: 1fr; }
    #range-label { color: $text-muted; text-style: bold; content-align: center middle; padding-top: 1; margin: 0 1; }
    #range-footer { height: auto; align: center middle; }
    #range-footer Button { margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="range-container"):
            yield Label("Select Date Range", id="range-title")
            with Horizontal(classes="range-inputs"):
                yield Input(placeholder="YYYY-MM-DD", id="range-start")
                yield Label(" To ", id="range-label")
                yield Input(placeholder="YYYY-MM-DD", id="range-end")
            with Horizontal(id="range-footer"):
                yield Button("\\[ CANCEL ]", id="btn-cancel", variant="default")
                yield Button("\\[ ENTER ]", id="btn-enter", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-enter":
            self.action_submit()

    def action_submit(self) -> None:
        start_input = self.query_one("#range-start", Input).value
        end_input = self.query_one("#range-end", Input).value
        try:
            start_date = datetime.strptime(start_input.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_input.strip(), "%Y-%m-%d")
            self.dismiss((start_date, end_date))
        except ValueError:
            self.notify("Invalid date format. Use YYYY-MM-DD.", severity="error")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_submit()


class StandupScreen(ModalScreen[None]):
    """Unified modal screen for generating Daily Standups and Period Reviews."""

    DEFAULT_CSS = """
    StandupScreen { align: center middle; background: rgba(13, 15, 24, 0.85); }
    #unified-container { width: 100%; height: 100%; border: solid $primary; background: $panel; padding: 1 2; }

    #unified-header { height: 3; border-bottom: solid $primary; margin-bottom: 1; }
    .header-title { color: $text-muted; text-style: bold; }
    #btn-back { text-align: right; background: transparent; border: none; }
    .spacer { width: 1fr; }

    .controls { height: auto; min-height: 3; margin-bottom: 1; align: left middle; }
    .control-label { color: $text-muted; text-style: bold; content-align: center middle; margin-right: 1; height: 3; }

    .spacer { width: 1fr; }

    #btn-prev-day, #btn-next-day { margin-top: 1; height: 1; min-width: 4; padding: 0; }
    #daily-format { width: 25; }
    #weekly-period { width: 25; }
    #weekly-format { width: 20; }

    #daily-editor, #weekly-editor { height: 1fr; border: solid $success; background: #0d0f18; }
    #weekly-summary { height: 1; margin-top: 1; color: $text-muted; text-style: bold; content-align: center middle; }

    #unified-footer { height: auto; min-height: 3; margin-top: 1; align: center middle; }
    #unified-footer Button { margin: 0 1; }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close", show=False),
        Binding("ctrl+b", "save_file", "Save", show=False),
        Binding("ctrl+y", "copy_to_clipboard", "Copy", show=False),
        Binding("ctrl+t", "toggle_todos", "Todos", show=False),
    ]

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

        self.daily_date = datetime.now() - timedelta(days=1)
        self.daily_include_todos = True
        self.weekly_days = 7
        self.weekly_range: tuple[datetime, datetime] | None = None

    def compose(self) -> ComposeResult:
        use_emojis = self.ctx.config.display.use_emojis
        with Container(id="unified-container"):
            with Horizontal(id="unified-header"):
                yield Label(f"{get_icon('todo', use_emojis)} Standup & Review", classes="header-title")
                yield Static(classes="spacer")
                yield Button("\\[ BACK (ESC) ]", id="btn-back", variant="default")

            with TabbedContent(id="tabs"):
                with TabPane(f"{get_icon('history', use_emojis)} Daily Standup", id="daily-tab"):
                    with Horizontal(classes="controls"):
                        yield Button(get_icon("arrow_left", use_emojis), id="btn-prev-day", variant="primary")
                        yield Label(
                            " Yesterday ",
                            id="daily-date-label",
                            classes="control-label",
                        )
                        yield Button(get_icon("arrow_right", use_emojis), id="btn-next-day", variant="primary")
                        yield Static(classes="spacer")
                        yield Label("Format: ", classes="control-label")
                        yield Select(
                            [
                                ("Markdown", "markdown"),
                                ("Plain-txt", "plain-txt"),
                                ("Slack", "slack"),
                                ("Jira", "jira"),
                                ("Bullets", "bullets"),
                            ],
                            value="markdown",
                            id="daily-format",
                            allow_blank=False,
                        )
                    yield TextArea(
                        id="daily-editor", show_line_numbers=True, read_only=True
                    )

                with TabPane(f"{get_icon('csv', use_emojis)} Period Review", id="weekly-tab"):
                    with Horizontal(classes="controls"):
                        yield Label("Period: ", classes="control-label")
                        yield Select(
                            [
                                ("Last 7 Days", 7),
                                ("Last 14 Days", 14),
                                ("Last 30 Days", 30),
                                ("Range", -1),
                            ],
                            value=7,
                            id="weekly-period",
                            allow_blank=False,
                        )
                        yield Static(classes="spacer")
                        yield Label("Format: ", classes="control-label")
                        yield Select(
                            [
                                ("Markdown", "markdown"),
                                ("Plain-txt", "plain-txt"),
                                ("Slack", "slack"),
                                ("Jira", "jira"),
                                ("Bullets", "bullets"),
                            ],
                            value="markdown",
                            id="weekly-format",
                            allow_blank=False,
                        )
                    yield TextArea(
                        id="weekly-editor", show_line_numbers=True, read_only=True
                    )
                    yield Label(
                        "─── Summary ─────────────────────────────────────",
                        id="weekly-summary",
                    )

            with Horizontal(id="unified-footer"):
                yield Button(f"\\[ {get_icon('check', use_emojis)} TODOS (^T) ]", id="btn-todos")
                yield Button(f"\\[ {get_icon('copy', use_emojis)} COPY ]", id="btn-copy", variant="success")
                yield Button(f"\\[ {get_icon('export', use_emojis)} EXPORT ]", id="btn-save", variant="primary")

    async def on_mount(self) -> None:
        """Initialize standup screen."""
        self._update_daily_date_label()
        self._generate_daily_report()
        self._generate_weekly_report()

        # Use suspend to temporarily exit alt screen and resize
        def _do_resize() -> None:
            import sys

            sys.stdout.write("\033[8;42;116t")
            sys.stdout.flush()

        try:
            async with self.app.suspend():
                _do_resize()
        except Exception:
            # Fallback: try direct write if suspend fails
            import sys

            sys.stdout.write("\033[8;42;116t")
            sys.stdout.flush()

    def on_unmount(self) -> None:
        """Resize terminal back when standup screen closes."""
        import sys

        sys.stdout.write("\033[8;42;82t")
        sys.stdout.flush()

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        todos_btn = self.query_one("#btn-todos", Button)
        if event.pane.id == "daily-tab":
            todos_btn.display = "block"
            todos_btn.label = (
                "\\[ HIDE TODOS ]" if self.daily_include_todos else "\\[ SHOW TODOS ]"
            )
        else:
            todos_btn.display = "none"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-prev-day":
            self.daily_date -= timedelta(days=1)
            self._update_daily_date_label()
            self._generate_daily_report()
        elif event.button.id == "btn-next-day":
            if self.daily_date.date() < datetime.now().date():
                self.daily_date += timedelta(days=1)
                self._update_daily_date_label()
                self._generate_daily_report()
        elif event.button.id == "btn-copy":
            self.action_copy_to_clipboard()
        elif event.button.id == "btn-save":
            self._open_export_dialog()
        elif event.button.id == "btn-todos":
            self.action_toggle_todos()
        elif event.button.id == "btn-back":
            self.app.pop_screen()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "daily-format":
            self._generate_daily_report()
        elif event.select.id == "weekly-period":
            if event.value == -1:
                def on_range_selected(date_range: tuple[datetime, datetime] | None) -> None:
                    if date_range:
                        self.weekly_range = date_range
                        self.weekly_days = -1
                        self._generate_weekly_report()
                        self.query_one("#weekly-editor").focus()
                    else:
                        # Revert selection on cancel
                        self.query_one("#weekly-period", Select).value = self.weekly_days if self.weekly_days != -1 else 7
                
                self.app.push_screen(RangeSelectionScreen(), on_range_selected)
            else:
                self.weekly_range = None
                if isinstance(event.value, int):
                    self.weekly_days = event.value
                    self._generate_weekly_report()
        elif event.select.id == "weekly-format":
            self._generate_weekly_report()


    def action_toggle_todos(self) -> None:
        active_pane = self.query_one(TabbedContent).active
        if active_pane == "daily-tab":
            self.daily_include_todos = not self.daily_include_todos
            self._generate_daily_report()
            todos_btn = self.query_one("#btn-todos", Button)
            todos_btn.label = (
                "\\[ HIDE TODOS ]" if self.daily_include_todos else "\\[ SHOW TODOS ]"
            )
            self.notify(
                f"Todos {'included' if self.daily_include_todos else 'excluded'}."
            )

    def action_copy_to_clipboard(self) -> None:
        active_pane = self.query_one(TabbedContent).active
        editor_id = "#daily-editor" if active_pane == "daily-tab" else "#weekly-editor"
        text = self.query_one(editor_id, TextArea).text
        if text:
            try:
                pyperclip.copy(text)
                self.notify("📋 Copied to clipboard!", severity="information")
            except Exception as e:
                self.notify(f"Copy failed: {e}", severity="error")

    def _open_export_dialog(self) -> None:
        """Open the export format selection dialog."""

        def on_format_selected(format: str | None) -> None:
            if format:
                self._export_content(format)

        self.app.push_screen(ExportFormatScreen(), on_format_selected)

    def _export_content(self, format: str) -> None:
        """Export content in the selected format."""
        active_pane = self.query_one(TabbedContent).active
        editor_id = "#daily-editor" if active_pane == "daily-tab" else "#weekly-editor"
        text = self.query_one(editor_id, TextArea).text

        if not text:
            self.notify("No content to export.", severity="warning")
            return

        try:
            # Save exports to 'dwriter-exports' to avoid confusion with the tool's source code
            doc_dir = Path.home() / "Documents" / "dwriter-exports"
            doc_dir.mkdir(parents=True, exist_ok=True)

            if active_pane == "daily-tab":
                base_name = f"standup-{self.daily_date.strftime('%Y-%m-%d')}"
            else:
                if self.weekly_range:
                    s_str = self.weekly_range[0].strftime('%Y-%m-%d')
                    e_str = self.weekly_range[1].strftime('%Y-%m-%d')
                    base_name = f"review-{s_str}-to-{e_str}"
                else:
                    base_name = (
                        f"review-{self.weekly_days}d-{datetime.now().strftime('%Y-%m-%d')}"
                    )

            if format == "markdown":
                path = doc_dir / f"{base_name}.md"
                with open(path, "w") as f:
                    f.write(text)
                self.notify(f"📄 Exported to {path}", severity="information")

            elif format == "plain":
                path = doc_dir / f"{base_name}.txt"
                # Convert markdown to plain text (simple conversion)
                plain_text = self._convert_to_plain_text(text)
                with open(path, "w") as f:
                    f.write(plain_text)
                self.notify(f"📄 Exported to {path}", severity="information")

            elif format == "csv":
                path = doc_dir / f"{base_name}.csv"
                self._export_to_csv(path)

            elif format == "json":
                path = doc_dir / f"{base_name}.json"
                self._export_to_json(path)

        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    def _convert_to_plain_text(self, markdown_text: str) -> str:
        """Simple markdown to plain text conversion."""
        lines = markdown_text.split("\n")
        plain_lines = []
        for line in lines:
            # Remove markdown formatting
            line = line.replace("###", "").replace("##", "").replace("#", "")
            line = line.replace("**", "").replace("*", "")
            line = line.replace("`", "")
            # Clean up extra spaces
            line = line.strip()
            plain_lines.append(line)
        return "\n".join(plain_lines)

    def _export_to_csv(self, path: Path) -> None:
        """Export raw entry data to CSV, ignoring all markdown formatting."""
        import csv

        # Get the date range based on active tab
        active_pane = self.query_one(TabbedContent).active

        if active_pane == "daily-tab":
            target_d = self.daily_date.date()
            entries = [
                e
                for e in self.ctx.db.get_all_entries()
                if e.created_at.date() == target_d
            ]
        else:
            if self.weekly_range:
                start_date = self.weekly_range[0]
                end_date = self.weekly_range[1]
                entries = [
                    e for e in self.ctx.db.get_all_entries() if start_date.date() <= e.created_at.date() <= end_date.date()
                ]
            else:
                start_date = datetime.now() - timedelta(days=self.weekly_days)
                entries = [
                    e for e in self.ctx.db.get_all_entries() if e.created_at >= start_date
                ]
            entries.sort(key=lambda x: x.created_at, reverse=True)

        if not entries:
            self.notify("No entries to export.", severity="warning")
            return

        # Write to CSV with clean data (no markdown formatting)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Date", "Time", "Content", "Project", "Tags"])

            for e in entries:
                # Clean content by removing emoji prefixes
                clean_content = e.content.lstrip("✅⏱️ ")
                # Get project (or empty string)
                project = e.project if e.project else ""
                # Get tags as space-separated list (or empty string)
                tags = " ".join(e.tag_names) if e.tag_names else ""

                _, time_str = format_entry_datetime(e)

                writer.writerow(
                    [
                        e.created_at.strftime("%Y-%m-%d"),
                        time_str or "",
                        clean_content,
                        project,
                        tags,
                    ]
                )

        self.notify(f"📊 CSV exported to {path}", severity="information")

    def _export_to_json(self, path: Path) -> None:
        """Export raw entry data to JSON."""
        import json

        # Get the date range based on active tab
        active_pane = self.query_one(TabbedContent).active

        if active_pane == "daily-tab":
            target_d = self.daily_date.date()
            entries = [
                e
                for e in self.ctx.db.get_all_entries()
                if e.created_at.date() == target_d
            ]
        else:
            if self.weekly_range:
                start_date = self.weekly_range[0]
                end_date = self.weekly_range[1]
                entries = [
                    e for e in self.ctx.db.get_all_entries() if start_date.date() <= e.created_at.date() <= end_date.date()
                ]
            else:
                start_date = datetime.now() - timedelta(days=self.weekly_days)
                entries = [
                    e for e in self.ctx.db.get_all_entries() if e.created_at >= start_date
                ]
            entries.sort(key=lambda x: x.created_at, reverse=True)

        if not entries:
            self.notify("No entries to export.", severity="warning")
            return

        data = []
        for e in entries:
            _, time_str = format_entry_datetime(e)
            data.append(
                {
                    "date": e.created_at.strftime("%Y-%m-%d"),
                    "time": time_str or "",
                    "content": e.content.lstrip("✅⏱️ "),
                    "project": e.project or "",
                    "tags": e.tag_names,
                }
            )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.notify(f"📦 JSON exported to {path}", severity="information")

    def action_save_file(self) -> None:
        """Legacy action - now opens export dialog."""
        self._open_export_dialog()

    def _update_daily_date_label(self) -> None:
        rel = (
            "Yesterday"
            if self.daily_date.date() == (datetime.now() - timedelta(days=1)).date()
            else "Past"
        )
        self.query_one("#daily-date-label", Label).update(
            f" {rel} ({self.daily_date.strftime('%Y-%m-%d')}) "
        )

    def _generate_daily_report(self) -> None:
        try:
            target_d = self.daily_date.date()
            all_entries = self.ctx.db.get_all_entries()
            entries = [e for e in all_entries if e.created_at.date() == target_d]
            pending_todos = [
                t for t in self.ctx.db.get_all_todos() if t.status == "pending"
            ]
            format_val = self.query_one("#daily-format", Select).value

            lines = []
            if format_val == "markdown":
                lines.append(f"### Standup: {self.daily_date.strftime('%Y-%m-%d')}")
                lines.append("\n**What I did:**")
                if not entries:
                    lines.append("- No entries logged.")
                for e in entries:
                    _, time_str = format_entry_datetime(e)
                    time_prefix = f"{time_str} - " if time_str else ""
                    
                    proj = f" `{e.project}`" if e.project else ""
                    tags = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                    clean_content = e.content.lstrip("✅⏱️ ")
                    lines.append(f"- {time_prefix}{clean_content}{proj}{tags}")
                if self.daily_include_todos:
                    lines.append("\n**Plan for today:**")
                    if not pending_todos:
                        lines.append("- Clear schedule.")
                    for t in pending_todos[:5]:
                        clean_content = t.content.lstrip("✅⏱️ ")
                        lines.append(f"- [ ] {clean_content}")

            elif format_val == "plain-txt":
                lines.append(f"Standup: {self.daily_date.strftime('%Y-%m-%d')}")
                lines.append("\nCompleted:")
                if not entries:
                    lines.append("  Nothing logged.")
                for e in entries:
                    _, time_str = format_entry_datetime(e)
                    time_prefix = f"{time_str} - " if time_str else ""
                    
                    p_str = f" ({e.project})" if e.project else ""
                    t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                    clean_content = e.content.lstrip("✅⏱️ ")
                    lines.append(
                        f"  {time_prefix}{clean_content}{p_str}{t_str}"
                    )
                if self.daily_include_todos:
                    lines.append("\nPlan for today:")
                    for t in pending_todos[:5]:
                        clean_content = t.content.lstrip("✅⏱️ ")
                        lines.append(f"  - {clean_content}")

            elif format_val == "slack":
                lines.append(f"*Update ({self.daily_date.strftime('%m/%d')})*")
                lines.append("\n*Completed:*")
                if not entries:
                    lines.append("• Nothing logged.")
                for e in entries:
                    _, time_str = format_entry_datetime(e)
                    time_prefix = f"{time_str} - " if time_str else ""
                    
                    p_str = f" ({e.project})" if e.project else ""
                    t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                    clean_content = e.content.lstrip("✅⏱️ ")
                    lines.append(f"• {time_prefix}{clean_content}{p_str}{t_str}")
                if self.daily_include_todos:
                    lines.append("\n*Today:*")
                    for t in pending_todos[:5]:
                        clean_content = t.content.lstrip("✅⏱️ ")
                        lines.append(f"• {clean_content}")

            elif format_val == "jira":
                lines.append(f"h3. Standup: {self.daily_date.strftime('%Y-%m-%d')}")
                lines.append("\nh4. What I did:")
                if not entries:
                    lines.append("* No entries logged.")
                for e in entries:
                    _, time_str = format_entry_datetime(e)
                    time_prefix = f"{time_str} - " if time_str else ""
                    
                    p_str = f" ({e.project})" if e.project else ""
                    t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                    clean_content = e.content.lstrip("✅⏱️ ")
                    lines.append(
                        f"* {time_prefix}{clean_content}{p_str}{t_str}"
                    )
                if self.daily_include_todos:
                    lines.append("\nh4. Plan for today:")
                    if not pending_todos:
                        lines.append("* Clear schedule.")
                    for t in pending_todos[:5]:
                        clean_content = t.content.lstrip("✅⏱️ ")
                        lines.append(f"* {clean_content}")

            elif format_val == "bullets":
                if not entries:
                    lines.append("* No entries logged.")
                for e in entries:
                    p_str = f" {e.project}" if e.project else ""
                    t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                    clean_content = e.content.lstrip("✅⏱️ ")
                    lines.append(f"* {clean_content}{p_str}{t_str}")

            self.query_one("#daily-editor", TextArea).text = "\n".join(lines)
        except Exception:
            pass

    def _generate_weekly_report(self) -> None:
        try:
            if self.weekly_range:
                start_date = self.weekly_range[0]
                end_date = self.weekly_range[1]
                entries = [
                    e for e in self.ctx.db.get_all_entries() if start_date.date() <= e.created_at.date() <= end_date.date()
                ]
            else:
                now = datetime.now()
                start_date = now - timedelta(days=self.weekly_days)
                entries = [
                    e for e in self.ctx.db.get_all_entries() if e.created_at >= start_date
                ]
            
            entries.sort(key=lambda x: x.created_at, reverse=True)

            grouped, tags_set, projects_set = {}, set(), set()
            for e in entries:
                d_str = e.created_at.strftime("%A, %Y-%m-%d")
                if d_str not in grouped:
                    grouped[d_str] = []
                grouped[d_str].append(e)
                for t in e.tag_names:
                    tags_set.add(t)
                if e.project:
                    projects_set.add(e.project)

            use_emojis = self.ctx.config.display.use_emojis
            note_icon = get_icon("note", use_emojis)
            tag_icon = get_icon("tag", use_emojis)
            folder_icon = get_icon("folder", use_emojis)
            self.query_one("#weekly-summary", Label).update(
                f"─── Summary: {note_icon} {len(entries)} entries | {tag_icon} {len(tags_set)} tags | {folder_icon} {len(projects_set)} projects ───"
            )

            format_val = self.query_one("#weekly-format", Select).value
            lines = []

            if format_val == "markdown":
                if self.weekly_range:
                    s_str = self.weekly_range[0].strftime('%Y-%m-%d')
                    e_str = self.weekly_range[1].strftime('%Y-%m-%d')
                    lines.append(f"# Review: {s_str} to {e_str}\n")
                else:
                    lines.append(f"# Review: Last {self.weekly_days} Days\n")
                if not grouped:
                    lines.append("No activity.")
                for d_str, day_entries in grouped.items():
                    lines.append(f"## {d_str}")
                    for e in day_entries:
                        _, time_str = format_entry_datetime(e)
                        time_prefix = f"{time_str} - " if time_str else ""
                        
                        proj = f" `{e.project}`" if e.project else ""
                        tags = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                        clean_content = e.content.lstrip("✅⏱️ ")
                        lines.append(f"- {time_prefix}{clean_content}{proj}{tags}")
                    lines.append("")

            elif format_val == "plain-txt":
                if self.weekly_range:
                    s_str = self.weekly_range[0].strftime('%Y-%m-%d')
                    e_str = self.weekly_range[1].strftime('%Y-%m-%d')
                    lines.append(f"Review: {s_str} to {e_str}")
                else:
                    lines.append(f"Review: Last {self.weekly_days} Days")
                lines.append("-" * 40)
                if not grouped:
                    lines.append("No activity.")
                for d_str, day_entries in grouped.items():
                    lines.append(f"\n[{d_str}]")
                    for e in day_entries:
                        _, time_str = format_entry_datetime(e)
                        time_prefix = f"{time_str} - " if time_str else ""
                        
                        p_str = f" ({e.project})" if e.project else ""
                        t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                        clean_content = e.content.lstrip("✅⏱️ ")
                        lines.append(
                            f"• {time_prefix}{clean_content}{p_str}{t_str}"
                        )

            elif format_val == "slack":
                if self.weekly_range:
                    s_str = self.weekly_range[0].strftime('%Y-%m-%d')
                    e_str = self.weekly_range[1].strftime('%Y-%m-%d')
                    lines.append(f"*Review: {s_str} to {e_str}*")
                else:
                    lines.append(f"*Review: Last {self.weekly_days} Days*")
                lines.append("")
                if not grouped:
                    lines.append("No activity.")
                for d_str, day_entries in grouped.items():
                    lines.append(f"*{d_str}*")
                    for e in day_entries:
                        _, time_str = format_entry_datetime(e)
                        time_prefix = f"{time_str} - " if time_str else ""
                        
                        p_str = f" {e.project}" if e.project else ""
                        t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                        clean_content = e.content.lstrip("✅⏱️ ")
                        lines.append(
                            f"• {time_prefix}{clean_content}{p_str}{t_str}"
                        )
                    lines.append("")

            elif format_val == "jira":
                if self.weekly_range:
                    s_str = self.weekly_range[0].strftime('%Y-%m-%d')
                    e_str = self.weekly_range[1].strftime('%Y-%m-%d')
                    lines.append(f"h1. Review: {s_str} to {e_str}\n")
                else:
                    lines.append(f"h1. Review: Last {self.weekly_days} Days\n")
                if not grouped:
                    lines.append("No activity.")
                for d_str, day_entries in grouped.items():
                    lines.append(f"h2. {d_str}")
                    for e in day_entries:
                        _, time_str = format_entry_datetime(e)
                        time_prefix = f"{time_str} - " if time_str else ""
                        
                        p_str = f" &{e.project}" if e.project else ""
                        t_str = f" ({', '.join(f'#{t}' for t in e.tag_names)})" if e.tag_names else ""
                        clean_content = e.content.lstrip("✅⏱️ ")
                        lines.append(
                            f"* {time_prefix}{clean_content}{p_str}{t_str}"
                        )
                    lines.append("")

            elif format_val == "bullets":
                if not grouped:
                    lines.append("* No activity.")
                for d_str, day_entries in grouped.items():
                    lines.append(f"* {d_str}")
                    for e in day_entries:
                        _, time_str = format_entry_datetime(e)
                        time_prefix = f"{time_str} - " if time_str else ""
                        
                        p_str = f" &{e.project}" if e.project else ""
                        t_str = f" ({', '.join(f'#{t}' for t in e.tag_names)})" if e.tag_names else ""
                        clean_content = e.content.lstrip("✅⏱️ ")
                        lines.append(
                            f"  * {time_prefix}{clean_content}{p_str}{t_str}"
                        )

            self.query_one("#weekly-editor", TextArea).text = "\n".join(lines)
        except Exception:
            pass
