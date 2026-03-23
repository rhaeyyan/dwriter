"""Help screen for dwriter TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
from ..colors import PROJECT, TAG, get_icon


class HelpScreen(Screen):  # type: ignore[type-arg]
    """Help screen for dwriter TUI."""

    CSS = """
    HelpScreen {
        background: $surface;
    }

    #help-container {
        height: 1fr;
        padding: 1 2;
    }

    #help-tabs {
        height: 1fr;
    }

    #help-tabs TabPane {
        padding: 1 2;
    }

    .help-section {
        height: auto;
        margin: 0 0 1 0;
    }

    .help-title {
        text-style: bold;
        color: $foreground;
        padding: 0 0 1 0;
    }

    .help-subtitle {
        color: $foreground 60%;
        padding: 0 0 1 0;
    }

    .help-command {
        color: $foreground;
        padding: 0 0 0 2;
    }

    .help-key {
        color: $accent;
        text-style: bold;
    }

    .help-example {
        color: $foreground 60%;
        padding: 0 0 0 4;
    }

    .help-divider {
        height: 1;
        background: $primary;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "quit", "Close"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Prev Tab"),
        Binding("1", "show_tab('overview')", "Overview", show=False),
        Binding("2", "show_tab('navigation')", "Navigation", show=False),
        Binding("3", "show_tab('omnibox')", "Omnibox", show=False),
        Binding("4", "show_tab('dashboard')", "Dashboard", show=False),
        Binding("5", "show_tab('todo')", "Todo", show=False),
        Binding("6", "show_tab('timer')", "Timer", show=False),
        Binding("7", "show_tab('search')", "Search", show=False),
        Binding("8", "show_tab('shortcuts')", "Shortcuts", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen layout."""
        yield Header()

        use_emojis = self.app.ctx.config.display.use_emojis
        with Container(id="help-container"):
            with TabbedContent(initial="overview", id="help-tabs"):
                # Tab 1: Overview
                with TabPane(f"{get_icon('overview', use_emojis)} Overview", id="overview"):
                    yield Static(self._get_overview_content(), markup=True)

                # Tab 2: Navigation
                with TabPane(f"{get_icon('navigation', use_emojis)} Navigation", id="navigation"):
                    yield Static(self._get_navigation_content(), markup=True)

                # Tab 3: Omnibox
                with TabPane(f"{get_icon('context', use_emojis)} Omnibox", id="omnibox"):
                    yield Static(self._get_omnibox_content(), markup=True)

                # Tab 4: Dashboard
                with TabPane(f"{get_icon('csv', use_emojis)} Dashboard", id="dashboard"):
                    yield Static(self._get_dashboard_content(), markup=True)

                # Tab 5: Todo
                with TabPane(f"{get_icon('todo', use_emojis)} Todo", id="todo"):
                    yield Static(self._get_todo_content(), markup=True)

                # Tab 6: Timer
                with TabPane(f"{get_icon('timer', use_emojis)} Timer", id="timer"):
                    yield Static(self._get_timer_content(), markup=True)

                # Tab 7: Search & Logs
                with TabPane(f"{get_icon('search', use_emojis)} Search/Logs", id="search"):
                    yield Static(self._get_search_content(), markup=True)

                # Tab 8: Shortcuts
                with TabPane(f"{get_icon('shortcuts', use_emojis)} Shortcuts", id="shortcuts"):
                    yield Static(self._get_shortcuts_content(), markup=True)

        yield Footer()

    def _get_overview_content(self) -> str:
        """Get overview tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Welcome to dwriter {get_icon('note', use_emojis)}[/bold]

[dim]A minimalist terminal journal for capturing work without breaking your flow.[/dim]

[bold #cba6f7]Quick Capture (Headless CLI):[/bold #cba6f7]
  [cyan]dwriter add "message"[/cyan]       → Log an entry
  [cyan]dwriter todo "task"[/cyan]         → Add a task
  [cyan]dwriter timer 25[/cyan]            → Start a focus session
  [cyan]dwriter standup[/cyan]             → Yesterday's summary
  [cyan]dwriter stats[/cyan]               → Performance summary

[bold #cba6f7]Unified Dashboard (TUI):[/bold #cba6f7]
  [cyan]dwriter[/cyan]                    → Launch the dashboard
  [#89dceb]1[/#89dceb] → {get_icon('dashboard', use_emojis)} Statistics & Activity Maps
  [#89dceb]2[/#89dceb] → {get_icon('logs', use_emojis)} History & Logs
  [#89dceb]3[/#89dceb] → {get_icon('todo', use_emojis)} Task Board
  [#89dceb]4[/#89dceb] → {get_icon('timer', use_emojis)} Focus Timer

[bold #cba6f7]Omnibox Syntax (press / to focus):[/bold #cba6f7]
  [{TAG}]#tag[/{TAG}]               → Categorize by tag
  [{PROJECT}]&project[/{PROJECT}]           → Assign to project
  [#89dceb]25[/#89dceb]                → Specify timer duration

[dim]Press Tab to navigate help topics. Press q to close.[/dim]
"""

    def _get_navigation_content(self) -> str:
        """Get navigation tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Navigation & Global Keys {get_icon('navigation', use_emojis)}[/bold]

[bold #cba6f7]Global Commands:[/bold #cba6f7]
  [cyan]/[/cyan]              → Focus the quick-add bar (Omnibox)
  [cyan]Ctrl+P[/cyan]         → Open the command palette
  [cyan]q[/cyan] or [cyan]Esc[/cyan]     → Close current screen or modal
  [cyan]?[/cyan]              → Open this help screen
  [#89dceb]1-4[/#89dceb]            → Quick-switch between dashboard views

[bold #cba6f7]List & Form Controls:[/bold #cba6f7]
  [cyan]j[/cyan] / [cyan]k[/cyan] or [cyan]↑[/cyan] / [cyan]↓[/cyan] → Navigate through lists
  [cyan]Enter[/cyan]          → Select, activate, or confirm
  [cyan]Tab[/cyan]            → Move to the next field or button
  [cyan]Shift+Tab[/cyan]      → Move to the previous field or button

[bold #cba6f7]Sidebar Navigation:[/bold #cba6f7]
  Use [cyan]j/k[/cyan] to highlight options and [cyan]Enter[/cyan] to select.

[dim]The footer bar at the bottom displays context-specific keys for each screen.[/dim]
"""

    def _get_omnibox_content(self) -> str:
        """Get omnibox tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Omnibox Syntax {get_icon('context', use_emojis)}[/bold]

[dim]The Omnibox is the input bar at the top of the screen. Press [cyan]/[/cyan] to focus.[/dim]

[bold #cba6f7]Journal Entries:[/bold #cba6f7]
  Format: [{TAG}]#tag[/{TAG}] [{PROJECT}]&project[/{PROJECT}] entry text
  Example: [{TAG}]#refactor[/{TAG}] [{PROJECT}]&engine[/{PROJECT}] fixed database deadlock

[bold #cba6f7]Task Management (Todo):[/bold #cba6f7]
  From the [bold]Todo Board[/bold], entering text into the Omnibox starts a
  multi-step workflow to define priority and due dates.

[bold #cba6f7]Focus Timer:[/bold #cba6f7]
  Format: [{TAG}]#tag[/{TAG}] [{PROJECT}]&project[/{PROJECT}] [#89dceb]MINUTES[/#89dceb]
  Example: [{TAG}]#deepwork[/{TAG}] [#89dceb]25[/#89dceb]
  Example: [{TAG}]#meeting[/{TAG}] [{PROJECT}]&team[/{PROJECT}] [#89dceb]60[/#89dceb]

[bold #cba6f7]Metadata Syntax:[/bold #cba6f7]
  [{TAG}]#tag[/{TAG}]         → Labels for categorization (e.g., #bug, #docs)
  [{PROJECT}]&project[/{PROJECT}]     → Project or client context (e.g., &internal)
  [#89dceb]NUMBER[/#89dceb]       → Focus session duration in minutes

[dim]Tip: Press 'q' at any time during a multi-step workflow to cancel.[/dim]
"""
        # fmt: on

    def _get_dashboard_content(self) -> str:
        """Get dashboard tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Dashboard & Analytics {get_icon('csv', use_emojis)}[/bold]

[dim]A visual summary of your productivity trends and behavioral insights.[/dim]

[bold #cba6f7]Visualizations:[/bold #cba6f7]
  → [bold]Pulse Panel (45-Day Heatmap):[/bold] A dense, rolling sparkline at the top
    of the dashboard showing your activity volume over the last 45 days.
  → [bold]Activity Calendar:[/bold] A GitHub-style heatmap showing your logging
    consistency over the past year.
  → [bold]Streak & Record:[/bold] Real-time tracking of your current and all-time 
    longest logging streaks.

[bold #cba6f7]Two-Cents (Behavioral Insights):[/bold #cba6f7]
  [dim]The dashboard automatically analyzes your patterns to provide context.[/dim]

  → [bold]Active Focus:[/bold] Highlights the tags and projects that have 
    occupied most of your time over the last 30 days.
  → [bold]High Focus Ratio:[/bold] Identifies when you are successfully 
    maintaining deep work sessions.
  → [bold]Project Fragmentation:[/bold] Alerts you when frequent context 
    switching between too many projects may be impacting your throughput.
  → [bold]Task Staleness:[/bold] Flags pending tasks that have been sitting 
    unattended for more than 14 days.

[bold #cba6f7]Controls & Actions:[/bold #cba6f7]
  [cyan]c[/cyan]              → Copy Performance Report (Markdown format)
  [cyan]r[/cyan]              → Refresh all analytics data
  [cyan]Tab[/cyan]            → Cycle focus between the Pulse Panel and Calendar

[dim]Tip: Use the 'c' key to instantly generate a Markdown report of your 
    KPIs—perfect for weekly reviews or personal auditing.[/dim]
"""
        # fmt: on

    def _get_todo_content(self) -> str:
        """Get todo tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Task Management (Todo) {get_icon('todo', use_emojis)}[/bold]

[dim]Manage pending tasks and automatically log them to your journal upon completion.[/dim]

[bold #cba6f7]Board Navigation:[/bold #cba6f7]
  [cyan]j / k[/cyan]          → Navigate through the task list
  [cyan]Space / Enter[/cyan]   → Mark as done (this auto-logs the task to your journal)
  [cyan]e[/cyan]              → Edit task details (content, due date, tags, project)
  [cyan]d[/cyan]              → Delete task
  [cyan]+ / -[/cyan]          → Adjust priority level
  [cyan]1 / 2 / 3[/cyan]      → Switch between [Pending], [Upcoming], and [Completed] tabs

[bold #cba6f7]Priority Indicators:[/bold #cba6f7]
  [red]\\[U][/red] Urgent    [yellow]\\[H][/yellow] High    [white]\\[N][/white] Normal    [dim]\\[L][/dim] Low

[bold #cba6f7]Due Date Indicators:[/bold #cba6f7]
  [red]\\[OVD][/red] → Overdue      [bold #fab387]\\[TDY][/bold #fab387] → Due today      [#89dceb]\\[5d][/#89dceb] → Days remaining

[dim]Note: Completed tasks appear in your journal history with a checkmark icon.[/dim]
"""
        # fmt: on

    def _get_timer_content(self) -> str:
        """Get timer tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Focus Timer {get_icon('timer', use_emojis)}[/bold]

[dim]Run timed focus sessions that prompted a journal entry upon completion.[/dim]

[bold #cba6f7]Session Controls:[/bold #cba6f7]
  [cyan]Space[/cyan]          → Start or Pause the countdown
  [cyan]+ / -[/cyan]          → Add or subtract 5 minutes from the duration
  [cyan]Enter[/cyan]          → Finish early and trigger the log prompt
  [cyan]q / Esc[/cyan]       → Exit the timer (prompts to log current progress)

[bold #cba6f7]Workflow:[/bold #cba6f7]
  1. Start timer from Omnibox or Timer screen.
  2. When finished, a modal appears to capture what you accomplished.
  3. Tags and projects are automatically inherited from the timer session.
"""
        # fmt: on

    def _get_search_content(self) -> str:
        """Get search tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Search & History {get_icon('search', use_emojis)}[/bold]

[dim]Locate past entries or tasks using fuzzy matching.[/dim]

[bold #cba6f7]Search View:[/bold #cba6f7]
  [cyan]j / k[/cyan]          → Navigate results
  [cyan]Enter[/cyan]          → Select a result to copy its content to the clipboard
  [cyan]/[/cyan]              → Focus the search input field
  [cyan]Ctrl+N[/cyan]         → Toggle between searching [All], [Entries], or [Tasks]

[bold #cba6f7]History (Logs) View:[/bold #cba6f7]
  [cyan]j / k[/cyan]          → Navigate chronological history
  [cyan]e / Enter[/cyan]      → Edit the selected log entry
  [cyan]d[/cyan]              → Delete the entry
  [cyan]t / p[/cyan]          → Quickly edit tags (#) or project (&) metadata
  [cyan]r[/cyan]              → Refresh the list

[dim]Tip: Search is typo-tolerant. Pressing Enter on any result copies it for easy sharing.[/dim]
"""

    def _get_shortcuts_content(self) -> str:
        """Get shortcuts reference tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Keyboard Reference {get_icon('shortcuts', use_emojis)}[/bold]

[bold #cba6f7]Global Navigation:[/bold #cba6f7]
  [cyan]/[/cyan]              → Focus Omnibox
  [cyan]Ctrl+P[/cyan]         → Command Palette
  [cyan]?[/cyan]              → Open Help
  [#89dceb]1-4[/#89dceb]            → Switch Dashboard views

[bold #cba6f7]Log Management:[/bold #cba6f7]
  [cyan]e / Enter[/cyan]      → Edit entry
  [cyan]d[/cyan]              → Delete entry
  [cyan]t / p[/cyan]          → Quick-edit metadata

[bold #cba6f7]Task Management:[/bold #cba6f7]
  [cyan]Space / Enter[/cyan]   → Mark as Done
  [cyan]+ / -[/cyan]          → Change Priority

[bold #cba6f7]Focus Timer:[/bold #cba6f7]
  [cyan]Space[/cyan]          → Start/Pause
  [cyan]+ / -[/cyan]          → Adjust Time

[dim]Most actions can be initiated via the Omnibox for a keyboard-first workflow.[/dim]
"""

    def action_quit(self) -> None:
        """Close the help screen."""
        self.dismiss()

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        try:
            tabbed = self.query_one("#help-tabs", TabbedContent)
            tabs = [
                "overview",
                "navigation",
                "omnibox",
                "dashboard",
                "todo",
                "timer",
                "search",
                "shortcuts",
            ]
            current = tabbed.active
            current_idx = tabs.index(current) if current in tabs else 0
            next_idx = (current_idx + 1) % len(tabs)
            tabbed.active = tabs[next_idx]
        except Exception:
            pass

    def action_prev_tab(self) -> None:
        """Switch to previous tab."""
        try:
            tabbed = self.query_one("#help-tabs", TabbedContent)
            tabs = [
                "overview",
                "navigation",
                "omnibox",
                "dashboard",
                "todo",
                "timer",
                "search",
                "shortcuts",
            ]
            current = tabbed.active
            current_idx = tabs.index(current) if current in tabs else 0
            prev_idx = (current_idx - 1) % len(tabs)
            tabbed.active = tabs[prev_idx]
        except Exception:
            pass

    def action_show_tab(self, tab_name: str) -> None:
        """Switch to a specific tab.

        Args:
            tab_name: Name of the tab to show.
        """
        try:
            tabbed = self.query_one("#help-tabs", TabbedContent)
            tabbed.active = tab_name
        except Exception:
            pass
