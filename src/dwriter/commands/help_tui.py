"""Interactive help TUI using Textual with dynamic Click introspection."""
from __future__ import annotations

from typing import Any

import click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    MarkdownViewer,
    TabbedContent,
    TabPane,
)


class CommandInfo:
    """Holds metadata about a Click command."""

    def __init__(
        self,
        name: str,
        short_help: str,
        full_help: str,
        usage: str,
    ) -> None:
        self.name = name
        self.short_help = short_help
        self.full_help = full_help
        self.usage = usage


class ClickIntrospector:
    """Extract command metadata from Click app for TUI display."""

    def __init__(self, cli_group: click.Group) -> None:
        self.cli = cli_group

    def get_commands(self) -> dict[str, CommandInfo]:
        """Extract all commands with their help text."""
        ctx = click.Context(self.cli)
        commands = {}

        for cmd_name in self.cli.list_commands(ctx):
            cmd = self.cli.get_command(ctx, cmd_name)
            if cmd is None:
                continue

            short_help = cmd.short_help or ""
            full_help = cmd.get_help(ctx)

            usage_parts = [f"dwriter {cmd_name}"]
            for param in cmd.params:
                if isinstance(param, click.Argument):
                    usage_parts.append(f"<{param.name}>")
                elif isinstance(param, click.Option):
                    opt = "/".join(param.opts)
                    if param.metavar:
                        opt += f" <{param.metavar}>"
                    usage_parts.append(f"[{opt}]")

            usage = " ".join(usage_parts)

            commands[cmd_name] = CommandInfo(
                name=cmd_name,
                short_help=short_help,
                full_help=full_help,
                usage=usage,
            )

        return commands

    def get_command_categories(self) -> dict[str, list[str]]:
        """Group commands by category."""
        return {
            "Logging": ["add", "today", "undo"],
            "Todos": ["todo", "done"],
            "Reports": ["standup", "review", "stats"],
            "Editing": ["edit", "delete"],
            "Search": ["search"],
            "Focus": ["focus"],
            "Config": ["config"],
            "Help": ["examples", "help"],
        }


def _get_cli_app() -> click.Group:
    """Get the main CLI app."""
    try:
        from ..cli import main as cli_app
        return cli_app
    except ImportError:
        import sys
        from pathlib import Path
        src_path = str(Path(__file__).parent.parent.parent)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from dwriter.cli import main as cli_app
        return cli_app


class HelpScreen(Screen[Any]):
    """The main interactive help browser screen."""

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
        Binding("tab", "next_tab", "Next Tab", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cli_app = _get_cli_app()
        self.introspector = ClickIntrospector(self.cli_app)
        self.commands_data = self.introspector.get_commands()
        self.categories_data = self.introspector.get_command_categories()
        self._loaded_tabs: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="logging"):
            # Create a tab for each category
            category_ids = {
                "Logging": "logging",
                "Todos": "todos",
                "Reports": "reports",
                "Editing": "editing",
                "Search": "search",
                "Focus": "focus",
                "Config": "config",
                "Help": "help",
            }
            for category, tab_id in category_ids.items():
                if category in self.categories_data:
                    with TabPane(f"📋 {category}" if category != "Help" else "❓ Help", id=tab_id):
                        # Lazy-load: MarkdownViewer starts empty
                        yield MarkdownViewer(id=f"{tab_id}-viewer", show_table_of_contents=True)
        yield Footer()

    def on_mount(self) -> None:
        """Load the first tab's content on mount."""
        # Load the initial tab's content
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
        
        # Build markdown for this category
        md_lines = ["# dwriter Command Reference\n\n"]
        
        # Get commands for this tab
        category_name = {"logging": "Logging", "todos": "Todos", "reports": "Reports",
                        "editing": "Editing", "search": "Search", "focus": "Focus",
                        "config": "Config", "help": "Help"}[tab_id]
        
        cmd_names = self.categories_data.get(category_name, [])
        
        for cmd_name in cmd_names:
            if cmd_name in self.commands_data:
                cmd = self.commands_data[cmd_name]
                md_lines.append(f"## `{cmd.name}`\n")
                md_lines.append(f"> {cmd.short_help}\n\n")
                md_lines.append("**Usage:**\n")
                md_lines.append(f"```bash\n{cmd.usage}\n```\n\n")
                md_lines.append("**Details:**\n")
                md_lines.append(f"{cmd.full_help}\n\n")
                md_lines.append("---\n")

        viewer.document.update("\n".join(md_lines))
        self._loaded_tabs.add(tab_id)

    def action_switch_tab(self, index: int) -> None:
        """Switch to tab by index."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "todos", "reports", "editing", "search", "focus", "config", "help"]
        if 0 <= index < len(tabs):
            tabbed.active = tabs[index]

    def action_next_tab(self) -> None:
        """Cycle to the next tab."""
        tabbed = self.query_one(TabbedContent)
        tabs = ["logging", "todos", "reports", "editing", "search", "focus", "config", "help"]
        current_idx = tabs.index(tabbed.active)
        next_idx = (current_idx + 1) % len(tabs)
        tabbed.active = tabs[next_idx]

    def action_toggle_toc(self) -> None:
        """Toggle the Table of Contents sidebar."""
        tabbed = self.query_one(TabbedContent)
        viewer = self.query_one(f"#{tabbed.active}-viewer", MarkdownViewer)
        viewer.show_table_of_contents = not viewer.show_table_of_contents


class HelpApp(App[None]):
    """Standalone app for testing."""

    def on_mount(self) -> None:
        self.push_screen(HelpScreen())


if __name__ == "__main__":
    app = HelpApp()
    app.run()
