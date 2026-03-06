"""Interactive examples browser TUI using Textual."""
from __future__ import annotations

from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, MarkdownViewer, TabbedContent, TabPane


class ExamplesScreen(Screen[Any]):
    """The main interactive examples browser screen."""

    BINDINGS = [
        Binding("q,escape", "app.quit", "Quit", show=True),
        Binding("t", "toggle_toc", "ToC", show=True),
        Binding("?", "goto_help", "Help", show=True),
        Binding("1", "switch_tab(0)", "1st", show=False),
        Binding("2", "switch_tab(1)", "2nd", show=False),
        Binding("3", "switch_tab(2)", "3rd", show=False),
        Binding("4", "switch_tab(3)", "4th", show=False),
        Binding("5", "switch_tab(4)", "5th", show=False),
        Binding("6", "switch_tab(5)", "6th", show=False),
        Binding("7", "switch_tab(6)", "7th", show=False),
        Binding("8", "switch_tab(7)", "8th", show=False),
        Binding("9", "switch_tab(8)", "9th", show=False),
        Binding("tab", "next_tab", "Next Tab", show=False),
        Binding("c", "copy_command", "Copy", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._loaded_subtabs: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="logging"):
            category_config = [
                ("📝 Logging", "logging", ["basic", "tags", "project", "combined", "date"]),
                ("📋 Viewing", "viewing", ["today", "all"]),
                ("🤖 Standup", "standup", ["generate", "formats", "options"]),
                ("📊 Review", "review", ["default", "custom", "formats"]),
                ("✏️ Editing", "editing", ["interactive", "specific", "undo", "bulk"]),
                ("✅ Todos", "todos", ["board", "add", "priority", "list", "complete"]),
                ("⏱️ Timer", "timer", ["default", "custom", "tagged"]),
                ("🔍 Search", "search", ["tui", "fuzzy", "filter_project", "filter_tag", "type"]),
                ("📈 Stats", "stats", ["dashboard"]),
                ("⚙️ Config", "config", ["show", "edit", "reset", "path"]),
            ]
            for label, tab_id, subtabs in category_config:
                with TabPane(label, id=tab_id):
                    if len(subtabs) == 1:
                        # Single sub-tab - just show MarkdownViewer directly
                        yield MarkdownViewer(id=f"{tab_id}-{subtabs[0]}-viewer", show_table_of_contents=False)
                    else:
                        # Multiple sub-tabs - use nested tabs with unique IDs
                        nested_id = f"{tab_id}-nested"
                        with TabbedContent(initial=f"{tab_id}-{subtabs[0]}", id=nested_id):
                            for subtab_id in subtabs:
                                pane_id = f"{tab_id}-{subtab_id}"
                                display_name = subtab_id.replace("_", " ").title()
                                with TabPane(display_name, id=pane_id):
                                    yield MarkdownViewer(id=f"{pane_id}-viewer", show_table_of_contents=False)
        yield Footer()

    def on_mount(self) -> None:
        """Load the first tab's content on mount."""
        self._load_subtab_content("logging", "basic")

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Lazy-load markdown content when tab is activated."""
        if not event.pane.id:
            return
        
        # Only handle sub-tab activations (they have format: {category}-{subtab})
        # Outer tabs are single words like "logging", "todos", etc.
        parts = event.pane.id.split("-")
        if len(parts) < 2:
            return  # This is an outer tab, not a sub-tab
        
        # Extract category (first part) and subtab (rest joined)
        category = parts[0]
        subtab = "-".join(parts[1:])
        
        # Validate this is a known category
        valid_categories = ["logging", "viewing", "standup", "review", "editing",
                           "todos", "timer", "search", "stats", "config"]
        if category not in valid_categories:
            return
            
        self._load_subtab_content(category, subtab)

    def _load_subtab_content(self, category: str, subtab: str) -> None:
        """Load markdown content for a sub-tab if not already loaded."""
        subtab_id = f"{category}-{subtab}"
        if subtab_id in self._loaded_subtabs:
            return

        viewer = self.query_one(f"#{subtab_id}-viewer", MarkdownViewer)

        example_map = {
            "logging": {
                "basic": ("Basic Logging", 'dwriter add "fixed a bug"', "Add a simple entry:"),
                "tags": ("With Tags", 'dwriter add "bug fix" -t bug -t backend', "Add entries with tags:"),
                "project": ("With Project", 'dwriter add "refactored auth" -p backend', "Add entries with a project:"),
                "combined": ("Multiple Tags & Project", 'dwriter add "refactored database" -t refactor -t backend -p myapp', "Combine tags and projects:"),
                "date": ("With Date", 'dwriter add "Finished report" --date yesterday', "Add entries for a specific date:"),
            },
            "viewing": {
                "today": ("Today's Entries", "dwriter today", "Show all entries logged today:"),
                "all": ("All Entries", "dwriter", "Show all entries (default view):"),
            },
            "standup": {
                "generate": ("Generate Standup", "dwriter standup", "Create yesterday's summary (copies to clipboard):"),
                "formats": ("Formats", "dwriter standup --format slack", "Different output formats (slack, jira, markdown):"),
                "options": ("Options", "dwriter standup --with-todos", "Include pending tasks with --with-todos:"),
            },
            "review": {
                "default": ("Default Review", "dwriter review", "Review last 5 days:"),
                "custom": ("Custom Period", "dwriter review --days 7", "Review last 7 days:"),
                "formats": ("Output Formats", "dwriter review --format markdown", "Different output formats:"),
            },
            "editing": {
                "interactive": ("Interactive Edit", "dwriter edit", "Launch interactive edit TUI:"),
                "specific": ("Edit by ID", "dwriter edit --id 42", "Edit specific entry:"),
                "undo": ("Undo Last", "dwriter undo", "Delete last entry:"),
                "bulk": ("Bulk Delete", "dwriter delete --before 2025-01-01", "Bulk delete old entries:"),
            },
            "todos": {
                "board": ("Todo Board", "dwriter todo", "Launch interactive todo board:"),
                "add": ("Add Task", 'dwriter todo "write tests"', "Add a new task:"),
                "priority": ("With Priority", 'dwriter todo "fix bug" --priority urgent', "Add task with priority:"),
                "list": ("List Tasks", "dwriter todo list", "List pending tasks:"),
                "complete": ("Complete Task", "dwriter done 5", "Mark task complete (auto-logs):"),
            },
            "timer": {
                "default": ("Default Timer", "dwriter timer", "Start 25-minute timer (Pomodoro):"),
                "custom": ("Custom Duration", "dwriter timer 30", "Start custom duration timer:"),
                "tagged": ("With Tags", "dwriter timer 45 -t deepwork", "Timer with tags and project:"),
            },
            "search": {
                "tui": ("Search TUI", "dwriter search", "Launch interactive search:"),
                "fuzzy": ("Fuzzy Search", 'dwriter search "auth bug"', "Fuzzy search entries and todos:"),
                "filter_project": ("Filter by Project", 'dwriter search "refactor" -p my_project', "Filter by project:"),
                "filter_tag": ("Filter by Tag", 'dwriter search "cache" -t backend', "Filter by tag:"),
                "type": ("Search Type", 'dwriter search "cache" --type todo', "Search only todos:"),
            },
            "stats": {
                "dashboard": ("Dashboard", "dwriter stats", "Interactive dashboard with calendar, charts, and statistics:"),
            },
            "config": {
                "show": ("Show Config", "dwriter config show", "View current configuration:"),
                "edit": ("Edit Config", "dwriter config edit", "Edit configuration file:"),
                "reset": ("Reset Config", "dwriter config reset", "Reset to defaults:"),
                "path": ("Config Path", "dwriter config path", "Show configuration file path:"),
            },
        }

        category_examples = example_map.get(category, {})
        example_data = category_examples.get(subtab)
        if not example_data:
            return

        title, command, description = example_data
        header_title = f"{category.title()} - {title}"
        md_lines = [
            f"# {header_title}\n",
            "=" * len(header_title) + "\n\n",
            f"{description}\n\n",
            "## Command\n",
            f"```bash\n{command}\n```\n\n",
        ]

        # Add additional examples for context
        additional_examples = {
            "logging": {
                "tags": "\n## More Examples\n\n```bash\ndwriter add \"feature complete\" -t feature -t backend\ndwriter add \"meeting notes\" -t meeting\n```",
                "project": "\n## More Examples\n\n```bash\ndwriter add \"deployed to prod\" -p backend\ndwriter add \"design review\" -p frontend\n```",
                "date": "\n## More Examples\n\n```bash\ndwriter add \"sprint planning\" --date \"last Monday\"\ndwriter add \"code review\" --date \"3 days ago\"\n```",
            },
            "standup": {
                "formats": "\n## Available Formats\n\n```bash\ndwriter standup --format slack\ndwriter standup --format jira\ndwriter standup --format markdown\n```",
            },
            "review": {
                "formats": "\n## Available Formats\n\n```bash\ndwriter review --format markdown\ndwriter review --format plain\ndwriter review --format slack\n```",
            },
            "todos": {
                "priority": "\n## Priority Levels\n\n```bash\ndwriter todo \"urgent fix\" --priority urgent\ndwriter todo \"normal task\" --priority normal\ndwriter todo \"low priority\" --priority low\n```",
            },
        }

        if category in additional_examples and subtab in additional_examples[category]:
            md_lines.append(additional_examples[category][subtab] + "\n")

        viewer.document.update("".join(md_lines))
        self._loaded_subtabs.add(subtab_id)

    def action_switch_tab(self, index: int) -> None:
        """Switch to tab by index."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "viewing", "standup", "review", "editing",
                "todos", "timer", "search", "stats", "config"]
        if 0 <= index < len(tabs):
            tabbed.active = tabs[index]

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "viewing", "standup", "review", "editing",
                "todos", "timer", "search", "stats", "config"]
        current_idx = tabs.index(tabbed.active)
        next_idx = (current_idx + 1) % len(tabs)
        tabbed.active = tabs[next_idx]

    def action_goto_help(self) -> None:
        """Navigate to the help TUI."""
        from .help_tui import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_copy_command(self) -> None:
        """Copy the current code block to clipboard."""
        self.notify("Select a code block and use Ctrl+Shift+C to copy", timeout=3)

    def action_toggle_toc(self) -> None:
        """Toggle the Table of Contents sidebar."""
        tabbed = self.query_one(TabbedContent)
        # Find active sub-tab viewer
        active_category = tabbed.active
        subtab_map = {
            "logging": "basic", "viewing": "today", "standup": "generate",
            "review": "default", "editing": "interactive", "todos": "board",
            "timer": "default", "search": "tui", "stats": "dashboard", "config": "show",
        }
        subtab = subtab_map.get(active_category, "basic")
        try:
            viewer = self.query_one(f"#{active_category}-{subtab}-viewer", MarkdownViewer)
            viewer.show_table_of_contents = not viewer.show_table_of_contents
        except Exception:
            pass


class ExamplesApp(App[None]):
    """Standalone app for testing."""

    def on_mount(self) -> None:
        self.push_screen(ExamplesScreen())


if __name__ == "__main__":
    app = ExamplesApp()
    app.run()
