"""Command palette provider for dwriter.

This module provides the Provider implementation that populates
Textual's CommandPalette with dwriter-specific commands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.command import Hit, Hits, Provider

if TYPE_CHECKING:
    pass


class DWriterCommands(Provider):
    """Command provider for dwriter operations.

    This provider integrates dwriter's CLI commands into Textual's
    CommandPalette, making features discoverable via Ctrl+P.

    Usage:
        Press Ctrl+P in the TUI, then type command names like:
        - "standup" - Generate yesterday's standup
        - "review" - Review last N days
        - "stats" - View statistics dashboard
    """

    async def search(self, query: str) -> Hits:
        """Search for commands matching the query.

        Args:
            query: The search query from the command palette.

        Yields:
            Hit objects for matching commands.
        """
        matcher = self.matcher(query)

        commands = [
            (
                "standup",
                "Generate standup report",
                "Copy yesterday's entries formatted for standup meetings",
                self._run_standup,
            ),
            (
                "review",
                "Review last N days",
                "Generate a review of entries from the last N days",
                self._run_review,
            ),
            (
                "stats",
                "View statistics dashboard",
                "Open the statistics dashboard",
                self._run_stats,
            ),
            (
                "export",
                "Export entries to file",
                "Export entries to a file",
                self._run_export,
            ),
        ]

        for name, _, help_text, callback in commands:
            if matcher.match(name):
                yield Hit(
                    matcher.match(name),
                    matcher.highlight(name),
                    callback,
                    help=help_text,
                )

    async def _run_standup(self) -> None:
        """Open the standup screen for generating and editing standup reports."""
        from .app import DWriterApp
        from .screens.standup import StandupScreen

        app = self.screen.app
        if not isinstance(app, DWriterApp):
            return

        # Push the standup screen
        app.push_screen(StandupScreen(app.ctx))

    async def _run_review(self) -> None:
        """Open the unified Standup & Review modal."""
        from .app import DWriterApp
        from .screens.standup import StandupScreen

        app = self.screen.app
        if not isinstance(app, DWriterApp):
            return

        # Push the unified standup screen (contains both Daily and Period Review)
        app.push_screen(StandupScreen(app.ctx))

    async def _run_stats(self) -> None:
        """Open the statistics dashboard."""
        from .app import DWriterApp

        app = self.screen.app
        if not isinstance(app, DWriterApp):
            return
        # Navigate to dashboard screen
        app.mount_screen("dashboard")
        app.notify("Dashboard opened", timeout=1.5)

    async def _run_export(self) -> None:
        """Export entries to a file."""
        from .app import DWriterApp

        app = self.screen.app
        if not isinstance(app, DWriterApp):
            return
        app.notify("Export command - coming soon", timeout=1.5)
