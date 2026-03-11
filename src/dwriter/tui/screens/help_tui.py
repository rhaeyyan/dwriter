"""Help screen for dwriter TUI.

This module provides a comprehensive help screen with tabbed navigation
showing all available commands, keybindings, and usage examples.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane


class HelpScreen(Screen):  # type: ignore[type-arg]
    """Help screen for dwriter TUI.

    Provides comprehensive help with tabbed navigation for:
    - Overview & Quick Start
    - Navigation & Global Keys
    - Omnibox Commands
    - Dashboard Features
    - Todo Board
    - Timer
    - Search & Logs
    - Keyboard Shortcuts Reference
    """

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
        color: $text-muted;
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
        color: $text-muted;
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

        with Container(id="help-container"):
            with TabbedContent(initial="overview", id="help-tabs"):
                # Tab 1: Overview
                with TabPane("📖 Overview", id="overview"):
                    yield Static(self._get_overview_content(), markup=True)

                # Tab 2: Navigation
                with TabPane("🧭 Navigation", id="navigation"):
                    yield Static(self._get_navigation_content(), markup=True)

                # Tab 3: Omnibox
                with TabPane("⚡ Omnibox", id="omnibox"):
                    yield Static(self._get_omnibox_content(), markup=True)

                # Tab 4: Dashboard
                with TabPane("📊 Dashboard", id="dashboard"):
                    yield Static(self._get_dashboard_content(), markup=True)

                # Tab 5: Todo
                with TabPane("📋 Todo", id="todo"):
                    yield Static(self._get_todo_content(), markup=True)

                # Tab 6: Timer
                with TabPane("⏱️ Timer", id="timer"):
                    yield Static(self._get_timer_content(), markup=True)

                # Tab 7: Search & Logs
                with TabPane("🔍 Search/Logs", id="search"):
                    yield Static(self._get_search_content(), markup=True)

                # Tab 8: Shortcuts
                with TabPane("⌨️ Shortcuts", id="shortcuts"):
                    yield Static(self._get_shortcuts_content(), markup=True)

        yield Footer()

    def _get_overview_content(self) -> str:
        """Get overview tab content."""
        return """
[bold]Welcome to dwriter! 📝[/bold]

[dim]A low-friction terminal journaling tool for developers.[/dim]

[bold cyan]Quick Start:[/bold cyan]
  [cyan]dwriter[/cyan]                    → Launch TUI
  [cyan]dwriter add "message"[/cyan]       → Quick log entry
  [cyan]dwriter todo "task"[/cyan]         → Add a todo
  [cyan]dwriter search "query"[/cyan]      → Fuzzy search
  [cyan]dwriter standup[/cyan]             → Yesterday's summary
  [cyan]dwriter timer 25[/cyan]            → Start 25min timer
  [cyan]dwriter stats[/cyan]               → View dashboard
  [cyan]dwriter edit[/cyan]                → Edit entries
  [cyan]dwriter help[/cyan]                → This help screen

[bold cyan]Omnibox Syntax (press / to focus):[/bold cyan]
  [green]#tag[/green]               → Add tags (e.g., [green]#bug[/green], [green]#feature[/green])
  [magenta]&project[/magenta]           → Add project (e.g., [magenta]&backend[/magenta])
  [yellow]15[/yellow]                → Timer minutes (e.g., [yellow]25[/yellow])

[bold cyan]Examples:[/bold cyan]
  [green]#bug[/green] [magenta]&backend[/magenta] Fixed login issue
  [green]#work[/green] [magenta]&frontend[/magenta] Implement new feature
  [green]#deepwork[/green] [magenta]&research[/magenta] [yellow]25[/yellow] (25min timer)
  [green]#meeting[/green] [magenta]&team[/magenta] Weekly standup notes

[bold cyan]TUI Screens:[/bold cyan]
  [cyan]1[/cyan] → Dashboard (stats, calendar, activity)
  [cyan]2[/cyan] → Logs (journal entries)
  [cyan]3[/cyan] → Todo Board (task management)
  [cyan]4[/cyan] → Timer (pomodoro sessions)

[dim]Press Tab to navigate between help topics[/dim]
[dim]Press q or Esc to close[/dim]
"""

    def _get_navigation_content(self) -> str:
        """Get navigation tab content."""
        return """
[bold]TUI Navigation 🧭[/bold]

[bold cyan]Global Keys (work everywhere):[/bold cyan]
  [cyan]/[/cyan]              → Focus omnibox (quick-add bar at top)
  [cyan]Ctrl+P[/cyan]         → Open command palette
  [cyan]q[/cyan] or [cyan]Esc[/cyan]     → Quit current screen / Close modal
  [cyan]?[/cyan]              → Open this help screen
  [cyan]1-4[/cyan]            → Switch between main screens

[bold cyan]Screen Navigation:[/bold cyan]
  [cyan]1[/cyan]              → 🏠 Dashboard (statistics & calendar)
  [cyan]2[/cyan]              → 📓 Logs (journal entries view)
  [cyan]3[/cyan]              → 📋 Todo Board (task management)
  [cyan]4[/cyan]              → ⏱️ Timer (pomodoro sessions)

  [cyan]Tab[/cyan]            → Cycle to next tab (in tabbed views)
  [cyan]Shift+Tab[/cyan]      → Cycle to previous tab

[bold cyan]List Navigation (within screens):[/bold cyan]
  [cyan]j[/cyan] or [cyan]↓[/cyan]         → Move down in list
  [cyan]k[/cyan] or [cyan]↑[/cyan]         → Move up in list
  [cyan]Enter[/cyan]          → Select / Activate item
  [cyan]Home[/cyan] / [cyan]End[/cyan]    → Jump to start / end

[bold cyan]Modal Dialogs:[/bold cyan]
  [cyan]Enter[/cyan]          → Confirm action (Save, OK, Yes)
  [cyan]Esc[/cyan]            → Cancel / Close modal
  [cyan]Tab[/cyan]            → Move to next input/button

[bold cyan]Sidebar Navigation (if visible):[/bold cyan]
  Click or use [cyan]j/k[/cyan] to navigate sidebar items
  Press [cyan]Enter[/cyan] to select highlighted option

[dim]Tip: Each screen shows its specific keybindings in the footer bar![/dim]
"""

    def _get_omnibox_content(self) -> str:
        """Get omnibox tab content."""
        # fmt: off
        return """
[bold]Omnibox Commands ⚡[/bold]

[dim]The omnibox is the input bar at TOP of the screen.[/dim]
[dim]Press [cyan]/[/cyan] to focus it.[/dim]

[bold cyan]Log Entry (default on Dashboard/Logs screens):[/bold cyan]
  Format: [green]#tag[/green] [magenta]&project[/magenta] Your entry text
  Example: [green]#bug[/green] [magenta]&backend[/magenta] Fixed race condition

[bold cyan]Add Todo (on Todo screen - multi-step workflow):[/bold cyan]
  Step 1: Enter task with optional tags/project
    [green]#tag[/green] [magenta]&project[/magenta] Task description
  Step 2: Add more tags/project (or press Enter to skip)
  Step 3: Set priority: [cyan]L[/cyan]=Low, [cyan]N[/cyan]=Normal
    [cyan]H[/cyan]=High, [cyan]U[/cyan]=Urgent
  Step 4: Set due date: [cyan]tomorrow[/cyan], [cyan]+5d[/cyan], [cyan]2024-03-15[/cyan]

[bold cyan]Start Timer (works from ANY screen):[/bold cyan]
  Format: [green]#tag[/green] [magenta]&project[/magenta] [yellow]MINUTES[/yellow]
  Example: [green]#deepwork[/green] [magenta]&research[/magenta] [yellow]25[/yellow]
  Example: [green]#meeting[/green] [yellow]30[/yellow] (30-minute meeting)

[bold cyan]Special Syntax:[/bold cyan]
  [green]#tag[/green] → Add tags (multiple: [green]#bug #urgent[/green])
  [magenta]&project[/magenta] → Add project (use [magenta]&[/magenta] prefix)
  [cyan]YYYY-MM-DD[/cyan] → Log entry for specific date
  [yellow]NUMBER[/yellow] → Timer minutes (on Timer screen)

[bold cyan]Due Date Formats (for todos):[/bold cyan]
  [cyan]tomorrow[/cyan], [cyan]today[/cyan], [cyan]yesterday[/cyan]
  [cyan]+5d[/cyan] (5 days), [cyan]+1w[/cyan] (1 week), [cyan]+1m[/cyan] (1 month)
  [cyan]3 days[/cyan], [cyan]2 weeks[/cyan]
  [cyan]next Monday[/cyan], [cyan]last Friday[/cyan]
  [cyan]2024-03-15[/cyan], [cyan]03/15/2024[/cyan]

[bold cyan]Priority Shortcuts:[/bold cyan]
  [cyan]L[/cyan] → Low (dim display)
  [cyan]N[/cyan] → Normal (white display)
  [cyan]H[/cyan] → High (yellow display)
  [cyan]U[/cyan] → Urgent (red display)

[dim]Tip: Press 'q' in any multi-step workflow to cancel![/dim]
"""
        # fmt: on

    def _get_dashboard_content(self) -> str:
        """Get dashboard tab content."""
        # fmt: off
        return """
[bold]Dashboard & Analytics 📊[/bold]

[dim]Your activity overview with behavioral insights and visualizations.[/dim]

[bold cyan]Key Performance Indicators (KPIs):[/bold cyan]
  → [bold]Total Entries:[/bold] All-time count of journal entries.
  → [bold]Current Streak:[/bold] Consecutive days logged (up to today).
  → [bold]Longest Streak:[/bold] Your all-time record for consecutive logging.
  → [bold]Consistency:[/bold] % of active days over the last 30 days. [dim](Aim for >80%)[/dim]

[bold cyan]Behavioral Insights (Interpretation):[/bold cyan]

[bold]🔄 Context Switches (Cognitive Load):[/bold]
  [dim]Measures the average number of unique projects you touch per day.[/dim]
  → [green]Low (0-2):[/green] Deep focus. You are staying in the zone on few topics.
  → [yellow]Med (3-4):[/yellow] Moderate load. Typical for multi-tasking days.
  → [red]High (5+):[/red] Fragmentation. Frequent switching kills productivity.

[bold]⚙️ Friction Ratio (Project ROI):[/bold]
  [dim]Calculated as: (Journal Entries) / (Completed Tasks) per project.[/dim]
  → [green]Avg Activity (<= 2.0):[/green] Lean execution. Logs align with results.
  → [yellow]Prioritized (2.1 - 3.5):[/yellow] High documentation or complex tasks.
  → [red]Time Hog (> 3.5):[/red] High friction. You are logging a lot but not finishing tasks. 
    [dim]Tip: Break these tasks down into smaller, manageable pieces.[/dim]

[bold]📋 To-do Health (Staleness):[/bold]
  → [green]Fresh:[/green] Tasks added within the last 3 days.
  → [yellow]Stale:[/yellow] Tasks sitting for 4-14 days.
  → [red]Stuck:[/red] Tasks older than 2 weeks. [dim](Review or delete these!)[/dim]

[bold]⚡ Workload & Throughput:[/bold]
  → [bold]Backlog:[/bold] The difference between tasks added vs. done this week.
  → [bold]Completion:[/bold] Your "Say-Do" ratio percentage.
  → [bold]Throughput:[/bold] Average tasks completed per day.

[bold cyan]Visualizations:[/bold cyan]
  → [bold]📅 History:[/bold] 365-day activity heatmap. Darker colors = more logs.
  → [bold]📈 Trends:[/bold] 30-day sparkline showing daily activity volume.
  → [bold]🏷️ Top Tags:[/bold] Your most active topics over the last 30 days.

[bold cyan]Navigation:[/bold cyan]
  [cyan]r[/cyan]              → Refresh all analytics
  [cyan]1 / 2[/cyan]          → Switch between [Overview] and [Activity Trends]
  [cyan]Tab[/cyan]            → Cycle focus between charts
"""
        # fmt: on

    def _get_todo_content(self) -> str:
        """Get todo tab content."""
        # fmt: off
        return """
[bold]Todo Board 📋[/bold]

[dim]Task management with priorities, due dates, and auto-logging.[/dim]

[bold cyan]Adding Todos:[/bold cyan]
  Via omnibox (on Todo screen):
    Press [cyan]/[/cyan] → Type task → Enter multi-step workflow
  Via CLI:
    [cyan]dwriter todo "task" --priority high --due tomorrow[/cyan]

[bold cyan]Key Bindings:[/bold cyan]
  [cyan]j/k[/cyan]            → Navigate up/down
  [cyan]Space[/cyan] / [cyan]Enter[/cyan]   → Mark complete (auto-logs to journal!)
  [cyan]e[/cyan]              → Edit task (content, due, tags, project)
  [cyan]d[/cyan]              → Delete task (with confirmation)
  [cyan]+/-[/cyan]            → Change priority
  [cyan]a[/cyan]              → Add new task (modal dialog)
  [cyan]1/2/3[/cyan]          → Switch tabs

[bold cyan]Tabs:[/bold cyan]
  [cyan]⏳ Pending (X)[/cyan]    → All pending tasks (shows count)
  [cyan]📅 Upcoming (Y)[/cyan]   → Due today, tomorrow, next 2 days
  [cyan]✓ Completed (Z)[/cyan]   → Completed tasks with completion date

[bold cyan]Display Format:[/bold cyan]
  [cyan]\\[5d\\][/cyan] [yellow]\\[H\\][/yellow] Task description [yellow]#tag1 #tag2[/yellow] [magenta]: Project[/magenta]
  ↑      ↑            ↑                    ↑
  Due    Priority   Content            Tags & Project

[bold cyan]Priority Colors:[/bold cyan]
  [red]\\[U\\][/red] Urgent    → Critical tasks
  [yellow]\\[H\\][/yellow] High      → Important tasks
  [white]\\[N\\][/white] Normal    → Regular tasks
  [dim]\\[L\\][/dim] Low       → When time permits

[bold cyan]Due Date Display:[/bold cyan]
  [red]\\[OVD\\][/red]       → Overdue (past due, appears FIRST!)
  [bold yellow]\\[TDY\\][/bold yellow]     → Due today
  [yellow]\\[TMR\\][/yellow]       → Due tomorrow
  [cyan]\\[5d\\][/cyan] / [cyan]\\[2m\\][/cyan]   → Days/months until due
  [dim]\\[---\\][/dim]       → No due date set

[bold cyan]Edit Dialog (press e):[/bold cyan]
  → Content: Task description
  → Due Date: YYYY-MM-DD, tomorrow, +5d, +1w, etc.
  → Tags: Comma-separated (e.g., work, urgent)
  → Project: Single project name

[dim]Tip: Completing a task auto-logs to your journal![/dim]
[dim]Format: "✓ Task content #tag : project"[/dim]
"""
        # fmt: on

    def _get_timer_content(self) -> str:
        """Get timer tab content."""
        # fmt: off
        return """
[bold]Timer Screen ⏱️[/bold]

[dim]Pomodoro-style focused work sessions with automatic logging.[/dim]

[bold cyan]Starting a Timer:[/bold cyan]
  Via omnibox (any screen): [green]#tag[/green] [magenta]&project[/magenta] [yellow]25[/yellow]
  Via CLI: [cyan]dwriter timer 25 -t tag -p project[/cyan]
  Via TUI: Navigate → Adjust time → Start

[bold cyan]Controls:[/bold cyan]
  [cyan]Space[/cyan]          → Start / Pause timer
  [cyan]+/-[/cyan]            → Add / Subtract 5 minutes
  [cyan]Enter[/cyan]          → Finish session early
  [cyan]q/Esc[/cyan]          → Quit (prompts to log)

[bold cyan]When Timer Completes:[/bold cyan]
  → Modal prompts for session log entry
  → Tags & project auto-inherited
  → Entry logged with timestamp

[bold cyan]Display Format:[/bold cyan]
  [cyan]mm:ss[/cyan]  [ ▮▮▮🥭▯▯▯ ]  [cyan]40%[/cyan]
  ↑ Time    ↑ Progress bar  ↑ Percentage

  Session: [green]#tag1[/green] [green]#tag2[/green] | [magenta]project[/magenta]
  ↑ Shows below pause button

[bold cyan]Progress Bar Colors:[/bold cyan]
  [green]▮[/green] Green (0-25%)    → Fresh start
  [lime]▮[/lime] Lime (25-50%)    → Getting going
  [yellow]▮[/yellow] Yellow (50-75%)  → Halfway there
  [orange]▮[/orange] Orange (75-85%) → Almost done
  [red]▮[/red] Red (85-100%)     → Final stretch
  [magenta]🥭[/magenta] Mango = Current position

[dim]Tip: Timer commands work from ANY screen via omnibox![/dim]
"""
        # fmt: on

    def _get_search_content(self) -> str:
        """Get search tab content."""
        return """
[bold]Search & Logs 🔍📓[/bold]

[dim]Fuzzy search across entries and todos, plus logs view.[/dim]

[bold cyan]Search Screen:[/bold cyan]

[bold]Starting Search:[/bold]
  Via CLI: [cyan]dwriter search "query"[/cyan]
  Via TUI: [cyan]dwriter search[/cyan] (interactive)

[bold]Key Bindings:[/bold]
  [cyan]j/k[/cyan]            → Navigate results
  [cyan]Enter[/cyan]          → Select (copy content to clipboard)
  [cyan]/[/cyan]              → Focus search input
  [cyan]Ctrl+N[/cyan]         → Toggle search type (All/Entry/Todo)
  [cyan]q/Esc[/cyan]          → Quit

[bold]Search Syntax:[/bold]
  Type naturally - fuzzy matching handles typos!
  
  Examples:
  [cyan]auth bug[/cyan]      → Matches "authentication bug fix"
  [cyan]refactor[/cyan]      → Matches "refactored database"
  [cyan]meeting[/cyan]       → Matches "team meeting notes"

[bold]Match Scores:[/bold]
  [green]90%+[/green]   → Excellent match (green)
  [yellow]75%+[/yellow]   → Good match (yellow)
  [dim]60%+[/dim]   → Partial match (dim)

[bold cyan]Logs Screen:[/bold cyan]

[bold]View Entries:[/bold]
  → Chronological list of all journal entries
  → Shows date, time, content, tags, project
  → Completed todos appear as "✓ Task" entries

[bold]Key Bindings:[/bold]
  [cyan]j/k[/cyan]            → Navigate up/down
  [cyan]e/Enter[/cyan]        → Edit selected entry
  [cyan]t[/cyan]              → Edit tags
  [cyan]p[/cyan]              → Edit project
  [cyan]d[/cyan]              → Delete entry (confirmation)
  [cyan]r[/cyan]              → Refresh list
  [cyan]/[/cyan]              → Focus search/filter
  [cyan]q/Esc[/cyan]          → Quit

[bold]Edit Entry Modal:[/bold]
  → Content: Entry text
  → Date: YYYY-MM-DD, yesterday, 2 days ago, last Friday
  → Time: HH:MM AM/PM or 24-hour format (or leave blank)
  → Tags: Comma-separated
  → Project: Single project name

[dim]Tip: Search is typo-tolerant! "fucntion" finds "function"
    Press Enter on a search result to copy its content to clipboard.[/dim]
"""

    def _get_shortcuts_content(self) -> str:
        """Get shortcuts reference tab content."""
        return """
[bold]Keyboard Shortcuts Reference ⌨️[/bold]

[bold cyan]Global (All Screens):[/bold cyan]
  [cyan]/[/cyan]              → Focus omnibox
  [cyan]Ctrl+P[/cyan]         → Command palette
  [cyan]q[/cyan] / [cyan]Esc[/cyan]       → Quit / Close
  [cyan]?[/cyan]              → Open help
  [cyan]1[/cyan]              → Dashboard
  [cyan]2[/cyan]              → Logs
  [cyan]3[/cyan]              → Todo Board
  [cyan]4[/cyan]              → Timer

[bold cyan]Dashboard:[/bold cyan]
  [cyan]r[/cyan]              → Refresh data
  [cyan]1/2[/cyan]            → Switch tabs (Overview/Activity)
  [cyan]Tab[/cyan]            → Navigate sections
  [cyan]d[/cyan]              → Drill down (tag/project)

[bold cyan]Logs:[/bold cyan]
  [cyan]j/k[/cyan]            → Navigate entries
  [cyan]e/Enter[/cyan]        → Edit entry
  [cyan]t[/cyan]              → Edit tags
  [cyan]p[/cyan]              → Edit project
  [cyan]d[/cyan]              → Delete entry
  [cyan]r[/cyan]              → Refresh
  [cyan]/[/cyan]              → Focus search

[bold cyan]Todo Board:[/bold cyan]
  [cyan]a[/cyan]              → Add task
  [cyan]j/k[/cyan]            → Navigate tasks
  [cyan]Space/Enter[/cyan]    → Complete task (auto-logs!)
  [cyan]e[/cyan]              → Edit task
  [cyan]d[/cyan]              → Delete task
  [cyan]+/-[/cyan]            → Change priority
  [cyan]1/2/3[/cyan]          → Switch tabs

[bold cyan]Timer:[/bold cyan]
  [cyan]Space[/cyan]          → Start/Pause
  [cyan]+/-[/cyan]            → Adjust time (±5 min)
  [cyan]Enter[/cyan]          → Finish early
  [cyan]q/Esc[/cyan]          → Quit (with prompt)

[bold cyan]Search:[/bold cyan]
  [cyan]j/k[/cyan]            → Navigate results
  [cyan]Enter[/cyan]          → Select (copy)
  [cyan]/[/cyan]              → Focus search
  [cyan]Ctrl+N[/cyan]         → Toggle type

[bold cyan]Omnibox:[/bold cyan]
  [cyan]Enter[/cyan]          → Submit command
  [cyan]Esc[/cyan]            → Unfocus / Cancel
  [cyan]q[/cyan] (in workflow) → Cancel multi-step

[bold cyan]Modal Dialogs:[/bold cyan]
  [cyan]Enter[/cyan]          → Confirm (Save/OK/Yes)
  [cyan]Esc[/cyan]            → Cancel / Close
  [cyan]Tab[/cyan]            → Next field/button

[dim]Pro tip: Live in the omnibox! Most actions start there.
    Press / to focus, type your command, hit Enter.[/dim]
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
