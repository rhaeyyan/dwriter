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
        self._loaded_tabs: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="logging"):
            # Create tabs for each category
            categories = [
                ("📝 Logging", "logging"),
                ("📋 Viewing", "viewing"),
                ("🤖 Standup", "standup"),
                ("📊 Review", "review"),
                ("✏️ Editing", "editing"),
                ("✅ Todos", "todos"),
                ("⏱️ Focus", "focus"),
                ("🔍 Search", "search"),
                ("📈 Stats", "stats"),
                ("⚙️ Config", "config"),
            ]
            for category, tab_id in categories:
                with TabPane(category, id=tab_id):
                    yield MarkdownViewer(id=f"{tab_id}-viewer", show_table_of_contents=True)
        yield Footer()

    def on_mount(self) -> None:
        """Load the first tab's content on mount."""
        self._load_tab_content("logging")

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Lazy-load markdown content when tab is activated."""
        if event.pane.id:
            self._load_tab_content(event.pane.id)

    def _load_tab_content(self, tab_id: str) -> None:
        """Load markdown content for a tab if not already loaded."""
        if tab_id in self._loaded_tabs:
            return
        
        viewer = self.query_one(f"#{tab_id}-viewer", MarkdownViewer)
        
        # Get examples for this category
        category_map = {
            "logging": self._get_logging_examples,
            "viewing": self._get_viewing_examples,
            "standup": self._get_standup_examples,
            "review": self._get_review_examples,
            "editing": self._get_editing_examples,
            "todos": self._get_todos_examples,
            "focus": self._get_focus_examples,
            "search": self._get_search_examples,
            "stats": self._get_stats_examples,
            "config": self._get_config_examples,
        }
        
        get_examples = category_map.get(tab_id)
        if not get_examples:
            return
        
        examples = get_examples()
        
        # Build markdown
        md_lines = [f"# {tab_id.title()} Examples\n\n"]
        for title, markdown, _ in examples:
            md_lines.append(f"## {title}\n\n")
            md_lines.append(f"{markdown}\n\n")
        
        viewer.document.update("".join(md_lines))
        self._loaded_tabs.add(tab_id)

    def action_switch_tab(self, index: int) -> None:
        """Switch to tab by index."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "viewing", "standup", "review", "editing",
                "todos", "focus", "search", "stats", "config"]
        if 0 <= index < len(tabs):
            tabbed.active = tabs[index]

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "viewing", "standup", "review", "editing",
                "todos", "focus", "search", "stats", "config"]
        current_idx = tabs.index(tabbed.active)
        next_idx = (current_idx + 1) % len(tabs)
        tabbed.active = tabs[next_idx]

    def _get_logging_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Basic Logging", "Add a simple entry:", 'dwriter add "fixed a bug"'),
            ("With Tags", "Add entries with tags using `-t`:\n\n```bash\ndwriter add \"bug fix\" -t bug -t backend\n```", 'dwriter add "bug fix" -t bug -t backend'),
            ("With Project", "Add entries with a project using `-p`:\n\n```bash\ndwriter add \"refactored auth\" -p backend\n```", 'dwriter add "refactored auth" -p backend'),
            ("Multiple Tags & Project", "Combine tags and projects:\n\n```bash\ndwriter add \"refactored database\" -t refactor -t backend -p myapp\n```", 'dwriter add "refactored database" -t refactor -t backend -p myapp'),
            ("With Date", "Add entries for a specific date:\n\n```bash\ndwriter add \"Finished report\" --date yesterday\ndwriter add \"Meeting notes\" --date \"last Friday\"\n```", 'dwriter add "Finished report" --date yesterday'),
        ]

    def _get_viewing_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Today's Entries", "Show all entries logged today:\n\n```bash\ndwriter today\n```", "dwriter today"),
            ("All Entries", "Show all entries (default view):\n\n```bash\ndwriter\n```", "dwriter"),
        ]

    def _get_standup_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Generate Standup", "Create yesterday's summary (copies to clipboard):\n\n```bash\ndwriter standup\n```", "dwriter standup"),
            ("Slack Format", "```bash\ndwriter standup --format slack\n```", "dwriter standup --format slack"),
            ("Jira Format", "```bash\ndwriter standup --format jira\n```", "dwriter standup --format jira"),
            ("Markdown Format", "```bash\ndwriter standup --format markdown\n```", "dwriter standup --format markdown"),
            ("No Copy", "```bash\ndwriter standup --no-copy\n```", "dwriter standup --no-copy"),
            ("Include Pending Tasks", "```bash\ndwriter standup --with-todos\n```", "dwriter standup --with-todos"),
        ]

    def _get_review_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Review Last 5 Days", "```bash\ndwriter review\n```", "dwriter review"),
            ("Review Last 7 Days", "```bash\ndwriter review --days 7\n```", "dwriter review --days 7"),
            ("Markdown Format", "```bash\ndwriter review --format markdown\n```", "dwriter review --format markdown"),
            ("Plain Format", "```bash\ndwriter review --format plain\n```", "dwriter review --format plain"),
            ("Slack Format", "```bash\ndwriter review --format slack\n```", "dwriter review --format slack"),
        ]

    def _get_editing_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Edit Entries", "Launch interactive edit TUI:\n\n```bash\ndwriter edit\n```", "dwriter edit"),
            ("Edit Specific Entry", "```bash\ndwriter edit --id 42\n```", "dwriter edit --id 42"),
            ("Search and Edit", "```bash\ndwriter edit --search \"redis cache\"\n```", 'dwriter edit --search "redis cache"'),
            ("Undo Last Entry", "```bash\ndwriter undo\n```", "dwriter undo"),
            ("Bulk Delete", "```bash\ndwriter delete --before 2025-01-01\n```", "dwriter delete --before 2025-01-01"),
        ]

    def _get_todos_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Interactive Todo Board", "```bash\ndwriter todo\n```", "dwriter todo"),
            ("Add Task", "```bash\ndwriter todo \"write tests\"\n```", 'dwriter todo "write tests"'),
            ("With Priority", "```bash\ndwriter todo \"fix bug\" --priority urgent\n```", 'dwriter todo "fix bug" --priority urgent'),
            ("With Tags & Project", "```bash\ndwriter todo \"fix bug\" --priority urgent -t bug -p backend\n```", 'dwriter todo "fix bug" --priority urgent -t bug -p backend'),
            ("List Tasks", "```bash\ndwriter todo list\n```", "dwriter todo list"),
            ("Complete Task", "```bash\ndwriter done 5\n```", "dwriter done 5"),
        ]

    def _get_focus_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Focus Timer (Pomodoro)", "Start a 25-minute timer:\n\n```bash\ndwriter focus\n```", "dwriter focus"),
            ("Custom Duration", "```bash\ndwriter focus 30\ndwriter focus 45\n```", "dwriter focus 30"),
            ("With Tags & Project", "```bash\ndwriter focus 45 -t deepwork -p backend\n```", "dwriter focus 45 -t deepwork -p backend"),
        ]

    def _get_search_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Interactive Search TUI", "```bash\ndwriter search\n```", "dwriter search"),
            ("Fuzzy Search", "```bash\ndwriter search \"auth bug\"\n```", 'dwriter search "auth bug"'),
            ("Filter by Project", "```bash\ndwriter search \"refactor\" -p my_project\n```", 'dwriter search "refactor" -p my_project'),
            ("Filter by Tags", "```bash\ndwriter search \"cache\" -t backend\n```", 'dwriter search "cache" -t backend'),
            ("Search Type", "```bash\ndwriter search \"cache\" --type todo\n```", 'dwriter search "cache" --type todo'),
        ]

    def _get_stats_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Statistics Dashboard", "Interactive dashboard with:\n- GitHub-style contribution calendar\n- Weekly activity chart\n- Statistics summary\n- Top tags\n\n```bash\ndwriter stats\n```", "dwriter stats"),
        ]

    def _get_config_examples(self) -> list[tuple[str, str, str]]:
        return [
            ("Show Configuration", "```bash\ndwriter config show\n```", "dwriter config show"),
            ("Edit Configuration", "```bash\ndwriter config edit\n```", "dwriter config edit"),
            ("Reset Configuration", "```bash\ndwriter config reset\n```", "dwriter config reset"),
            ("Configuration Path", "```bash\ndwriter config path\n```", "dwriter config path"),
        ]

    def action_copy_command(self) -> None:
        """Copy the current code block to clipboard."""
        # MarkdownViewer handles code block copying natively via Ctrl+Shift+C
        self.notify("Select a code block and use Ctrl+Shift+C to copy", timeout=3)

    def action_toggle_toc(self) -> None:
        """Toggle the Table of Contents sidebar."""
        tabbed = self.query_one(TabbedContent)
        viewer = self.query_one(f"#{tabbed.active}-viewer", MarkdownViewer)
        viewer.show_table_of_contents = not viewer.show_table_of_contents


class ExamplesApp(App[None]):
    """Standalone app for testing."""

    def on_mount(self) -> None:
        self.push_screen(ExamplesScreen())


if __name__ == "__main__":
    app = ExamplesApp()
    app.run()
