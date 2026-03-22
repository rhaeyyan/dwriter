"""Help screen for dwriter TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
from ..colors import get_icon


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
[bold]Welcome to dwriter! {get_icon('note', use_emojis)}[/bold]

[dim]A low-friction terminal journaling tool for developers.[/dim]

[bold #cba6f7]Quick Start:[/bold #cba6f7]
  [cyan]dwriter[/cyan]                    → Launch TUI
  [cyan]dwriter add "message"[/cyan]       → Quick log entry
  [cyan]dwriter todo "task"[/cyan]         → Add a todo
  [cyan]dwriter search "query"[/cyan]      → Fuzzy search
  [cyan]dwriter standup[/cyan]             → Yesterday's summary
  [cyan]dwriter timer [#89dceb]25[/#89dceb][/cyan]            → Start [#89dceb]25[/#89dceb]min timer
  [cyan]dwriter stats[/cyan]               → View dashboard
  [cyan]dwriter edit[/cyan]                → Edit entries
  [cyan]dwriter help[/cyan]                → This help screen

[bold #cba6f7]Omnibox Syntax (press / to focus):[/bold #cba6f7]
  [bold yellow]#tag[/bold yellow]               → Add tags (e.g., [bold yellow]#bug[/bold yellow], [bold yellow]#feature[/bold yellow])
  [magenta]&project[/magenta]           → Add project (e.g., [magenta]&backend[/magenta])
  [#89dceb]15[/#89dceb]                → Timer minutes (e.g., [#89dceb]25[/#89dceb])

[bold #cba6f7]Examples:[/bold #cba6f7]
  [bold yellow]#bug[/bold yellow] [magenta]&backend[/magenta] Fixed login issue
  [bold yellow]#work[/bold yellow] [magenta]&frontend[/magenta] Implement new feature
  [bold yellow]#deepwork[/bold yellow] [magenta]&research[/magenta] [#89dceb]25[/#89dceb] (25min timer)
  [bold yellow]#meeting[/bold yellow] [magenta]&team[/magenta] Weekly standup notes

[bold #cba6f7]TUI Screens:[/bold #cba6f7]
  [#89dceb]1[/#89dceb] → {get_icon('dashboard', use_emojis)} Dashboard (stats, calendar, activity)
  [#89dceb]2[/#89dceb] → {get_icon('logs', use_emojis)} Logs (journal entries)
  [#89dceb]3[/#89dceb] → {get_icon('todo', use_emojis)} Todo Board (task management)
  [#89dceb]4[/#89dceb] → {get_icon('timer', use_emojis)} Timer (timer sessions)

[dim]Press Tab to navigate between help topics[/dim]
[dim]Press q or Esc to close[/dim]
"""

    def _get_navigation_content(self) -> str:
        """Get navigation tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]TUI Navigation {get_icon('navigation', use_emojis)}[/bold]

[bold #cba6f7]Global Keys (work everywhere):[/bold #cba6f7]
  [cyan]/[/cyan]              → Focus omnibox (quick-add bar at top)
  [cyan]Ctrl+P[/cyan]         → Open command palette
  [cyan]q[/cyan] or [cyan]Esc[/cyan]     → Quit current screen / Close modal
  [cyan]?[/cyan]              → Open this help screen
  [#89dceb]1-4[/#89dceb]            → Switch between main screens

[bold #cba6f7]Screen Navigation:[/bold #cba6f7]
  [#89dceb]1[/#89dceb]              → {get_icon('dashboard', use_emojis)} Dashboard (statistics & calendar)
  [#89dceb]2[/#89dceb]              → {get_icon('logs', use_emojis)} Logs (journal entries view)
  [#89dceb]3[/#89dceb]              → {get_icon('todo', use_emojis)} Todo Board (task management)
  [#89dceb]4[/#89dceb]              → {get_icon('timer', use_emojis)} Timer (timer sessions)

  [cyan]Tab[/cyan]            → Cycle to next tab (in tabbed views)
  [cyan]Shift+Tab[/cyan]      → Cycle to previous tab

[bold #cba6f7]List Navigation (within screens):[/bold #cba6f7]
  [cyan]j[/cyan] or [cyan]↓[/cyan]         → Move down in list
  [cyan]k[/cyan] or [cyan]↑[/cyan]         → Move up in list
  [cyan]Enter[/cyan]          → Select / Activate item
  [cyan]Home[/cyan] / [cyan]End[/cyan]    → Jump to start / end

[bold #cba6f7]Modal Dialogs:[/bold #cba6f7]
  [cyan]Enter[/cyan]          → Confirm action (Save, OK, Yes)
  [cyan]Esc[/cyan]            → Cancel / Close modal
  [cyan]Tab[/cyan]            → Move to next input/button

[bold #cba6f7]Sidebar Navigation (if visible):[/bold #cba6f7]
  Click or use [cyan]j/k[/cyan] to navigate sidebar items
  Press [cyan]Enter[/cyan] to select highlighted option

[dim]Tip: Each screen shows its specific keybindings in the footer bar![/dim]
"""

    def _get_omnibox_content(self) -> str:
        """Get omnibox tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Omnibox Commands {get_icon('context', use_emojis)}[/bold]

[dim]The omnibox is the input bar at TOP of the screen.[/dim]
[dim]Press [cyan]/[/cyan] to focus it.[/dim]

[bold #cba6f7]Log Entry (default on Dashboard/Logs screens):[/bold #cba6f7]
  Format: [bold yellow]#tag[/bold yellow] [magenta]&project[/magenta] Your entry text
  Example: [bold yellow]#bug[/bold yellow] [magenta]&backend[/magenta] Fixed race condition

[bold #cba6f7]Add Todo (on Todo screen - multi-step workflow):[/bold #cba6f7]
  Step 1: Enter task with optional tags/project
    [bold yellow]#tag[/bold yellow] [magenta]&project[/magenta] Task description
  Step 2: Add more tags/project (or press Enter to skip)
  Step 3: Set priority: [cyan]L[/cyan]=Low, [cyan]N[/cyan]=Normal
    [cyan]H[/cyan]=High, [cyan]U[/cyan]=Urgent
  Step 4: Set due date: [cyan]tomorrow[/cyan], [#89dceb]+5d[/#89dceb], [#89dceb]2024-03-15[/#89dceb]

[bold #cba6f7]Start Timer (works from ANY screen):[/bold #cba6f7]
  Format: [bold yellow]#tag[/bold yellow] [magenta]&project[/magenta] [#89dceb]MINUTES[/#89dceb]
  Example: [bold yellow]#deepwork[/bold yellow] [magenta]&research[/magenta] [#89dceb]25[/#89dceb]
  Example: [bold yellow]#meeting[/bold yellow] [#89dceb]30[/#89dceb] (30-minute meeting)

[bold #cba6f7]Special Syntax:[/bold #cba6f7]
  [bold yellow]#tag[/bold yellow] → Add tags (multiple: [bold yellow]#bug #urgent[/bold yellow])
  [magenta]&project[/magenta] → Add project (use [magenta]&[/magenta] prefix)
  [cyan]YYYY-MM-DD[/cyan] → Log entry for specific date
  [#89dceb]NUMBER[/#89dceb] → Timer minutes (on Timer screen)

[bold #cba6f7]Due Date Formats (for todos):[/bold #cba6f7]
  [cyan]tomorrow[/cyan], [cyan]today[/cyan], [cyan]yesterday[/cyan]
  [#89dceb]+5d[/#89dceb] (5 days), [#89dceb]+1w[/#89dceb] (1 week), [#89dceb]+1m[/#89dceb] (1 month)
  [#89dceb]3 days[/#89dceb], [#89dceb]2 weeks[/#89dceb]
  [cyan]next Monday[/cyan], [cyan]last Friday[/cyan]
  [#89dceb]2024-03-15[/#89dceb], [#89dceb]03/15/2024[/#89dceb]

[bold #cba6f7]Priority Shortcuts:[/bold #cba6f7]
  [cyan]L[/cyan] → Low (dim display)
  [cyan]N[/cyan] → Normal (white display)
  [cyan]H[/cyan] → High (yellow display)
  [cyan]U[/cyan] → Urgent (red display)

[dim]Tip: Press 'q' in any multi-step workflow to cancel![/dim]
"""
        # fmt: on

    def _get_dashboard_content(self) -> str:
        """Get dashboard tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Dashboard & Analytics {get_icon('csv', use_emojis)}[/bold]

[dim]Your activity overview with behavioral insights and visualizations.[/dim]

[bold #cba6f7]Key Performance Indicators (KPIs):[/bold #cba6f7]
  → [bold]Total Entries:[/bold] All-time count of journal entries.
  → [bold]Current Streak:[/bold] Consecutive days logged (up to today).
  → [bold]Longest Streak:[/bold] Your all-time record for consecutive logging.
  → [bold]Consistency:[/bold] % of active days over the last [#89dceb]30[/#89dceb] days. [dim](Aim for >[#89dceb]80%[/#89dceb])[/dim]

[bold #cba6f7]Behavioral Insights (Interpretation):[/bold #cba6f7]

[bold]{get_icon('context', use_emojis)} Context Switches (Cognitive Load):[/bold]
  [dim]Measures the average number of unique projects you touch per day.[/dim]
  → [#a6e3a1]Low[/#a6e3a1] [#89dceb](0-2)[/#89dceb]: Deep focus. You are staying in the zone on few topics.
  → [yellow]Med[/yellow] [#89dceb](3-4)[/#89dceb]: Moderate load. Typical for multi-tasking days.
  → [red]High[/red] [#89dceb](5+)[/#89dceb]: Fragmentation. Frequent switching kills productivity.

[bold]{get_icon('friction', use_emojis)} Friction Ratio (Project ROI):[/bold]
  [dim]Calculated as: (Journal Entries) / (Completed Tasks) per project.[/dim]
  → [#a6e3a1]Avg Activity[/#a6e3a1] [#89dceb](<= 2.0)[/#89dceb]: Lean execution. Logs align with results.
  → [yellow]Prioritized[/yellow] [#89dceb](2.1 - 3.5)[/#89dceb]: High documentation or complex tasks.
  → [red]Time Hog[/red] [#89dceb](> 3.5)[/#89dceb]: High friction. You are logging a lot but not finishing tasks. 
    [dim]Tip: Break these tasks down into smaller, manageable pieces.[/dim]

[bold]{get_icon('todo', use_emojis)} To-do Health (Staleness):[/bold]
  → [#a6e3a1]Fresh[/#a6e3a1]: Tasks added within the last [#89dceb]3[/#89dceb] days.
  → [yellow]Stale[/yellow]: Tasks sitting for [#89dceb]4-14[/#89dceb] days.
  → [red]Stuck[/red]: Tasks older than [#89dceb]2[/#89dceb] weeks. [dim](Review or delete these!)[/dim]

[bold]{get_icon('workload', use_emojis)} Workload & Throughput:[/bold]
  → [bold]Backlog:[/bold] The difference between tasks added vs. done this week.
  → [bold]Completion:[/bold] Your "Say-Do" ratio percentage.
  → [bold]Throughput:[/bold] Average tasks completed per day.

[bold #cba6f7]Visualizations:[/bold #cba6f7]
  → [bold]{get_icon('history', use_emojis)} History:[/bold] [#89dceb]365[/#89dceb]-day activity heatmap. Darker colors = more logs.
  → [bold]{get_icon('search', use_emojis)} Trends:[/bold] [#89dceb]30[/#89dceb]-day sparkline showing daily activity volume.
  → [bold]{get_icon('tag', use_emojis)} Top Tags:[/bold] Your most active topics over the last [#89dceb]30[/#89dceb] days.

[bold #cba6f7]Navigation:[/bold #cba6f7]
  [cyan]r[/cyan]              → Refresh all analytics
  [#89dceb]1 / 2[/#89dceb]          → Switch between [Overview] and [Activity Trends]
  [cyan]Tab[/cyan]            → Cycle focus between charts
"""
        # fmt: on

    def _get_todo_content(self) -> str:
        """Get todo tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Todo Board {get_icon('todo', use_emojis)}[/bold]

[dim]Task management with priorities, due dates, and auto-logging.[/dim]

[bold #cba6f7]Adding Todos:[/bold #cba6f7]
  Via omnibox (on Todo screen):
    Press [cyan]/[/cyan] → Type task → Enter multi-step workflow
  Via CLI:
    [cyan]dwriter todo "task" --priority high --due tomorrow[/cyan]

[bold #cba6f7]Key Bindings:[/bold #cba6f7]
  [cyan]j/k[/cyan]            → Navigate up/down
  [cyan]Space[/cyan] / [cyan]Enter[/cyan]   → Mark complete (auto-logs to journal!)
  [cyan]e[/cyan]              → Edit task (content, due, tags, project)
  [cyan]d[/cyan]              → Delete task (with confirmation)
  [cyan]+/-[/cyan]            → Change priority
  [cyan]a[/cyan]              → Add new task (modal dialog)
  [cyan]1/2/3[/cyan]          → Switch tabs

[bold #cba6f7]Tabs:[/bold #cba6f7]
  [cyan]{get_icon('timer', use_emojis)} Pending (X)[/cyan]    → All pending tasks (shows count)
  [cyan]{get_icon('history', use_emojis)} Upcoming (Y)[/cyan]   → Due today, tomorrow, next [#89dceb]2[/#89dceb] days
  [cyan]{get_icon('check', use_emojis)} Completed (Z)[/cyan]   → Completed tasks with completion date

[bold #cba6f7]Display Format:[/bold #cba6f7]
  [#89dceb]\\[5d][/#89dceb] [yellow]\\[H][/yellow] Task description [bold yellow]#tag1 #tag2[/bold yellow] [magenta]&Project[/magenta]
  ↑      ↑            ↑                    ↑
  Due    Priority   Content            Tags & Project

[bold #cba6f7]Priority Colors:[/bold #cba6f7]
  [red]\\[U][/red] Urgent    → Critical tasks
  [yellow]\\[H][/yellow] High      → Important tasks
  [white]\\[N][/white] Normal    → Regular tasks
  [dim]\\[L][/dim] Low       → When time permits

[bold #cba6f7]Due Date Display:[/bold #cba6f7]
  [red]\\[OVD][/red]       → Overdue (past due, appears FIRST!)
  [bold #fab387]\\[TDY][/bold #fab387]     → Due today
  [#fab387]\\[TMR][/#fab387]     → Due tomorrow
  [#89dceb]\\[5d][/#89dceb] / [#89dceb]\\[2m][/#89dceb]   → Days/months until due
  [dim]\\[---][/dim]       → No due date set

[bold #cba6f7]Edit Dialog (press e):[/bold #cba6f7]
  → Content: Task description
  → Due Date: YYYY-MM-DD, tomorrow, [#89dceb]+5d[/#89dceb], [#89dceb]+1w[/#89dceb], etc.
  → Tags: Comma-separated (e.g., work, urgent)
  → Project: Single project name

[dim]Tip: Completing a task auto-logs to your journal![/dim]
[dim]Format: "{get_icon('check', use_emojis)} Task content [bold yellow]#tag[/bold yellow] &project"[/dim]
"""
        # fmt: on

    def _get_timer_content(self) -> str:
        """Get timer tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        # fmt: off
        return f"""
[bold]Timer Screen {get_icon('timer', use_emojis)}[/bold]

[dim]Timer-style focused work sessions with automatic logging.[/dim]

[bold #cba6f7]Starting a Timer:[/bold #cba6f7]
  Via omnibox (any screen): [bold yellow]#tag[/bold yellow] [magenta]&project[/magenta] [#89dceb]25[/#89dceb]
  Via CLI: [cyan]dwriter timer [#89dceb]25[/#89dceb] -t tag -p project[/cyan]
  Via TUI: Navigate → Adjust time → Start

[bold #cba6f7]Controls:[/bold #cba6f7]
  [cyan]Space[/cyan]          → Start / Pause timer
  [cyan]+/-[/cyan]            → Add / Subtract [#89dceb]5[/#89dceb] minutes
  [cyan]Enter[/cyan]          → Finish session early
  [cyan]q/Esc[/cyan]          → Quit (prompts to log)

[bold #cba6f7]When Timer Completes:[/bold #cba6f7]
  → Modal prompts for session log entry
  → Tags & project auto-inherited
  → Entry logged with timestamp

[bold #cba6f7]Display Format:[/bold #cba6f7]
  [cyan]mm:ss[/cyan]  [ {'▮▮▮' if use_emojis else '###'}# {'▯▯▯' if use_emojis else '...'} ]  [#89dceb]40%[/#89dceb]
  ↑ Time    ↑ Progress bar  ↑ Percentage

  Session: [bold yellow]#tag1[/bold yellow] [bold yellow]#tag2[/bold yellow] | [magenta]&project[/magenta]
  ↑ Shows below pause button

[dim]Tip: Timer commands work from ANY screen via omnibox![/dim]
"""
        # fmt: on

    def _get_search_content(self) -> str:
        """Get search tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Search & Logs {get_icon('search', use_emojis)}{get_icon('logs', use_emojis)}[/bold]

[dim]Fuzzy search across entries and todos, plus logs view.[/dim]

[bold #cba6f7]Search Screen:[/bold #cba6f7]

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
  [#a6e3a1]90%+[/#a6e3a1]   → Excellent match (light green)
  [yellow]75%+[/yellow]   → Good match (yellow)
  [dim]60%+[/dim]   → Partial match (dim)

[bold #cba6f7]Logs Screen:[/bold #cba6f7]

[bold]View Entries:[/bold]
  → Chronological list of all journal entries
  → Shows date, time, content, tags, project
  → Completed todos appear as "{get_icon('check_small', use_emojis)} Task" entries

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
  → Date: YYYY-MM-DD, yesterday, [#89dceb]2[/#89dceb] days ago, last Friday
  → Time: HH:MM AM/PM or [#89dceb]24[/#89dceb]-hour format (or leave blank)
  → Tags: Comma-separated
  → Project: Single project name

[dim]Tip: Search is typo-tolerant! "fucntion" finds "function"
    Press Enter on a search result to copy its content to clipboard.[/dim]
"""

    def _get_shortcuts_content(self) -> str:
        """Get shortcuts reference tab content."""
        use_emojis = self.app.ctx.config.display.use_emojis
        return f"""
[bold]Keyboard Shortcuts Reference {get_icon('shortcuts', use_emojis)}[/bold]

[bold #cba6f7]Global (All Screens):[/bold #cba6f7]
  [cyan]/[/cyan]              → Focus omnibox
  [cyan]Ctrl+P[/cyan]         → Command palette
  [cyan]q[/cyan] / [cyan]Esc[/cyan]       → Quit / Close
  [cyan]?[/cyan]              → Open help
  [#89dceb]1[/#89dceb]              → {get_icon('dashboard', use_emojis)} Dashboard
  [#89dceb]2[/#89dceb]              → {get_icon('logs', use_emojis)} Logs
  [#89dceb]3[/#89dceb]              → {get_icon('todo', use_emojis)} Todo Board
  [#89dceb]4[/#89dceb]              → {get_icon('timer', use_emojis)} Timer

[bold #cba6f7]Dashboard:[/bold #cba6f7]
  [cyan]r[/cyan]              → Refresh data
  [#89dceb]1/2[/#89dceb]            → Switch tabs (Overview/Activity)
  [cyan]Tab[/cyan]            → Navigate sections
  [cyan]d[/cyan]              → Drill down (tag/project)

[bold #cba6f7]Logs:[/bold #cba6f7]
  [cyan]j/k[/cyan]            → Navigate entries
  [cyan]e/Enter[/cyan]        → Edit entry
  [cyan]t[/cyan]              → Edit tags
  [cyan]p[/cyan]              → Edit project
  [cyan]d[/cyan]              → Delete entry
  [cyan]r[/cyan]              → Refresh
  [cyan]/[/cyan]              → Focus search

[bold #cba6f7]Todo Board:[/bold #cba6f7]
  [cyan]a[/cyan]              → Add task
  [cyan]j/k[/cyan]            → Navigate tasks
  [cyan]Space/Enter[/cyan]    → Complete task (auto-logs!)
  [cyan]e[/cyan]              → Edit task
  [cyan]d[/cyan]              → Delete task
  [cyan]+/-[/cyan]            → Change priority
  [#89dceb]1/2/3[/#89dceb]          → Switch tabs

[bold #cba6f7]Timer:[/bold #cba6f7]
  [cyan]Space[/cyan]          → Start/Pause
  [cyan]+/-[/cyan]            → Adjust time (±[#89dceb]5[/#89dceb] min)
  [cyan]Enter[/cyan]          → Finish early
  [cyan]q/Esc[/cyan]          → Quit (with prompt)

[bold #cba6f7]Search:[/bold #cba6f7]
  [cyan]j/k[/cyan]            → Navigate results
  [cyan]Enter[/cyan]          → Select (copy)
  [cyan]/[/cyan]              → Focus search
  [cyan]Ctrl+N[/cyan]         → Toggle type

[bold #cba6f7]Omnibox:[/bold #cba6f7]
  [cyan]Enter[/cyan]          → Submit command
  [cyan]Esc[/cyan]            → Unfocus / Cancel
  [cyan]q[/cyan] (in workflow) → Cancel multi-step

[bold #cba6f7]Modal Dialogs:[/bold #cba6f7]
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
