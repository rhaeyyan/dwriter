"""2nd-Brain screen for dwriter TUI.

This module provides an interactive AI chat interface that is context-aware
of the user's current tasks and journal entries, featuring long-term memory
via weekly summaries and targeted historical retrieval.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from ...cli import AppContext

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, RichLog, Static

from ...ai.engine import get_ai_client, get_raw_ai_client, get_system_prompt
from ...ai.schemas.router import ActionRouter
from ...ai.schemas.tasks import AddTodoIntent, LogEntryIntent, ProjectBreakdownIntent
from ...ai.schemas.triage import BulkSnoozeIntent, TriageReview
from ..messages import EntryAdded, TodoUpdated


class SecondBrainScreen(Container):
    """Interactive AI 2nd-Brain Screen.

    Provides a chat interface for querying productivity data and receiving
    strategic advice. Context is constructed using a three-tier hierarchy:
    1. Long-Term Memory (AI-generated weekly retrospectives).
    2. Short-Term Memory (Activity logs from the preceding 72 hours).
    3. Targeted History (Contextual retrieval based on detected project or tag keywords).

    Attributes:
        ctx (AppContext): The application context for database and config access.
    """

    DEFAULT_CSS = """
    SecondBrainScreen {
        height: 1fr;
        width: 1fr;
        background: $background;
        padding: 0;
    }

    #second-brain-log {
        height: 1fr;
        border: none;
        padding: 0;
        margin: 0;
        background: transparent;
        scrollbar-size-vertical: 1;
        scrollbar-gutter: stable;
    }
    
    #second-brain-status {
        height: 1;
        margin: 0 1;
        padding: 0;
        color: $text-muted;
    }
    
    #second-brain-input {
        margin: 0;
        border: solid #cba6f7;
        background: $surface;
    }
    """

    def __init__(self, ctx: AppContext, **kwargs: Any) -> None:
        """Initializes the 2nd-Brain screen.

        Args:
            ctx (AppContext): Application context.
            **kwargs (Any): Additional widget arguments.
        """
        super().__init__(**kwargs)
        self.ctx = ctx
        self._chat_history: list[dict[str, str]] = []
        self._context_data: str = ""

    def compose(self) -> ComposeResult:
        """Composes the 2nd-Brain layout components."""
        with Vertical():
            yield RichLog(id="second-brain-log", highlight=True, markup=True, wrap=True)
            yield Static("", id="second-brain-status")
            yield Input(placeholder="Ask your 2nd-Brain anything...", id="second-brain-input")

    def on_mount(self) -> None:
        """Initializes chat history and refreshes the primary context."""
        log = self.query_one("#second-brain-log", RichLog)
        log.write("[bold black on yellow] SYSTEM [/bold black on yellow]")
        log.write("[dim]2nd-Brain initialized with recent task and log context.\n[/dim]")
        self._refresh_context()

    def _refresh_context(self) -> None:
        """Assembles the primary context from long-term and short-term memory.

        Long-term summaries are prepended to ensure the model maintains global
        awareness, while short-term data is appended to leverage recency bias
        for immediate tasks and logs.
        """
        # Historical Layer: Weekly Summaries
        long_term = ""
        try:
            summaries = self.ctx.db.get_summaries(summary_type="weekly", limit=4)
            if summaries:
                long_term = "[LONG-TERM MEMORY (WEEKLY SUMMARIES)]\n"
                for s in summaries:
                    try:
                        data = json.loads(s.content)
                        week_label = s.period_start.strftime("%b %d")
                        wins = ", ".join(data.get("biggest_wins", [])[:2])
                        mood = data.get("dominant_mood", "N/A")
                        velocity = data.get("velocity", "N/A")
                        projects = ", ".join(
                            f"&{p}" for p in data.get("key_projects", [])
                        )
                        long_term += (
                            f"- Week of {week_label}: {mood}. {velocity}. "
                            f"Focus: {projects}. Wins: {wins}\n"
                        )
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception:
            pass

        # Immediate Layer: Activity from the last 72 hours
        three_days_ago = datetime.now() - timedelta(days=3)
        entries = self.ctx.db.get_all_entries()
        recent_entries = [e for e in entries if e.created_at >= three_days_ago]
        todos = self.ctx.db.get_todos(status="pending")

        short_term = "[SHORT-TERM MEMORY (LAST 3 DAYS)]\n"
        short_term += "Recent Entries:\n"
        short_term += "\n".join(
            [
                f"- [{e.created_at.strftime('%Y-%m-%d')}] {e.content}"
                for e in recent_entries[:15]
            ]
        )
        short_term += "\n\nPending Tasks:\n"
        short_term += "\n".join(
            [f"- [{t.priority.upper()}] {t.content}" for t in todos[:10]]
        )

        self._context_data = f"{long_term}\n{short_term}"

    def _get_targeted_context(self, user_input: str) -> str:
        """Retrieves historical data based on keywords detected in the user input.

        Identifies project names (&project) and tags (#tag) to fetch related
        historical entries, providing more granular context for the AI.

        Args:
            user_input (str): The raw text from the user.

        Returns:
            str: Formatted historical context string.
        """
        three_days_ago = datetime.now() - timedelta(days=3)
        context_parts: list[str] = []

        # Keyword matching for project history
        try:
            all_projects = list(self.ctx.db.get_project_stats().keys())
            mentioned_projects = [
                p
                for p in all_projects
                if re.search(
                    r"&" + re.escape(p) + r"\b", user_input, re.IGNORECASE
                )
            ]

            for project in mentioned_projects[:2]:
                history = self.ctx.db.get_all_entries(project=project)
                past = [e for e in history if e.created_at < three_days_ago][:15]
                if past:
                    lines = [
                        f"- [{e.created_at.strftime('%Y-%m-%d')}] {e.content}"
                        for e in past
                    ]
                    context_parts.append(
                        f"\n[TARGETED HISTORY: &{project}]\n" + "\n".join(lines)
                    )
        except Exception:
            pass

        # Keyword matching for tag history
        try:
            all_tags = list(self.ctx.db.get_entries_with_tags_count().keys())
            mentioned_tags = [
                t
                for t in all_tags
                if re.search(
                    r"#" + re.escape(t) + r"\b", user_input, re.IGNORECASE
                )
            ]

            for tag in mentioned_tags[:2]:
                history = self.ctx.db.get_all_entries(tags=[tag])
                past = [e for e in history if e.created_at < three_days_ago][:15]
                if past:
                    lines = [
                        f"- [{e.created_at.strftime('%Y-%m-%d')}] {e.content}"
                        for e in past
                    ]
                    context_parts.append(
                        f"\n[TARGETED HISTORY: #{tag}]\n" + "\n".join(lines)
                    )
        except Exception:
            pass

        return "\n".join(context_parts)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handles the submission of a user query.

        Args:
            event (Input.Submitted): The input submission event.
        """
        user_input = event.value.strip()
        if not user_input:
            return

        log = self.query_one("#second-brain-log", RichLog)
        status = self.query_one("#second-brain-status", Static)
        
        log.write("\n[bold black on cyan] YOU [/bold black on cyan]")
        log.write(f"[cyan]{user_input}[/cyan]\n")
        status.update("[bold #cba6f7]Thinking...[/bold #cba6f7]")
        event.input.value = ""

        if not self.ctx.config.ai.enabled:
            log.write("[yellow]AI features are disabled in configuration.[/yellow]")
            status.update("")
            return

        self._run_ai_chat(user_input)

    @work(thread=True)
    def _run_ai_chat(self, user_input: str) -> None:
        """Executes the AI chat workflow including intent routing and action dispatch.

        Args:
            user_input (str): The raw text query from the user.
        """
        log = self.query_one("#second-brain-log", RichLog)
        status = self.query_one("#second-brain-status", Static)
        
        try:
            # Intent classification phase
            client_structured = get_ai_client(self.ctx.config.ai)
            
            self.app.call_from_thread(status.update, "[bold #cba6f7]Categorizing intent...[/bold #cba6f7]")
            route = client_structured.chat.completions.create(
                model=self.ctx.config.ai.model,
                response_model=ActionRouter,
                messages=[
                    {
                        "role": "system",
                        "content": get_system_prompt(
                            "Categorize the user's request into a functional domain. "
                            "Functional areas: task_management, log_entry, triage, reflection, analytics, context_restore."
                        ),
                    },
                    {"role": "user", "content": user_input},
                ],
            )

            # Automated action dispatch phase
            if route.category == "log_entry":
                self.app.call_from_thread(status.update, "[bold #cba6f7]Logging entry...[/bold #cba6f7]")
                intent = client_structured.chat.completions.create(
                    model=self.ctx.config.ai.model,
                    response_model=LogEntryIntent,
                    messages=[
                        {
                            "role": "system",
                            "content": get_system_prompt(f"Extract log entry metadata. Current time: {datetime.now().isoformat()}"),
                        },
                        {"role": "user", "content": user_input},
                    ],
                )
                
                entry = self.ctx.db.add_entry(
                    content=intent.content,
                    project=intent.project,
                    tags=intent.tags,
                    created_at=intent.created_at.replace(tzinfo=None) if intent.created_at else None
                )
                
                self.app.call_from_thread(log.write, "[bold black on yellow] SYSTEM [/bold black on yellow]")
                self.app.call_from_thread(log.write, f"[dim]Logged new entry #{entry.id}.[/dim]\n")
                self.app.post_message(EntryAdded(entry.id, entry.content, entry.created_at))
                self.app.call_from_thread(status.update, "")
                return

            elif route.category == "task_management":
                self.app.call_from_thread(status.update, "[bold #cba6f7]Creating task...[/bold #cba6f7]")
                intent = client_structured.chat.completions.create(
                    model=self.ctx.config.ai.model,
                    response_model=Union[AddTodoIntent, ProjectBreakdownIntent],
                    messages=[
                        {
                            "role": "system",
                            "content": get_system_prompt(
                                "Extract task management metadata. "
                                "Use AddTodoIntent for single tasks and ProjectBreakdownIntent for project-level requests. "
                                f"Current time: {datetime.now().isoformat()}"
                            ),
                        },
                        {"role": "user", "content": user_input},
                    ],
                )
                
                if hasattr(intent, "tasks"): # ProjectBreakdown
                    for task in intent.tasks:
                        due = datetime.now() + timedelta(days=task.estimated_days_out)
                        t = self.ctx.db.add_todo(
                            content=task.content,
                            priority=task.priority,
                            project=intent.project_name,
                            due_date=due
                        )
                        self.app.post_message(TodoUpdated(t.id, "added"))
                    self.app.call_from_thread(log.write, "[bold black on yellow] SYSTEM [/bold black on yellow]")
                    self.app.call_from_thread(log.write, f"[dim]Added {len(intent.tasks)} tasks to &{intent.project_name}.[/dim]\n")
                else: # AddTodo
                    t = self.ctx.db.add_todo(
                        content=intent.content,
                        priority=intent.priority,
                        project=intent.project,
                        tags=intent.tags,
                        due_date=intent.due_date.replace(tzinfo=None) if intent.due_date else None
                    )
                    self.app.call_from_thread(log.write, "[bold black on yellow] SYSTEM [/bold black on yellow]")
                    self.app.call_from_thread(log.write, f"[dim]Added task #{t.id} to board.[/dim]\n")
                    self.app.post_message(TodoUpdated(t.id, "added"))
                self.app.call_from_thread(status.update, "")
                return

            # Conversational refinement phase
            self.app.call_from_thread(status.update, "[bold #cba6f7]Thinking...[/bold #cba6f7]")
            client = get_raw_ai_client(self.ctx.config.ai)
            targeted_context = self._get_targeted_context(user_input)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are dwriter 2nd-Brain, a productivity assistant. "
                        "You have access to historical summaries and recent activity logs. "
                        "Instructions: You provide conversational assistance and analysis. "
                        "You do not have direct write access to the database in this mode."
                        f"\n\n{self._context_data}"
                        f"{targeted_context}"
                    ),
                }
            ]
            messages.extend(self._chat_history[-10:])
            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=self.ctx.config.ai.model,
                messages=messages,  # type: ignore
            )
            
            answer = response.choices[0].message.content or ""
            self._chat_history.append({"role": "user", "content": user_input})
            self._chat_history.append({"role": "assistant", "content": answer})
            
            formatted_answer = self._format_ai_response(answer)
            self.app.call_from_thread(log.write, "[bold black on #cba6f7] 2ND-BRAIN [/bold black on #cba6f7]")
            self.app.call_from_thread(log.write, formatted_answer)
            self.app.call_from_thread(status.update, "")
            
        except Exception as e:
            self.app.call_from_thread(log.write, f"\n[red]AI Error: {e}[/red]")
            self.app.call_from_thread(status.update, "[bold red]AI Error[/bold red]")

    def _format_ai_response(self, text: str) -> str:
        """Transforms AI-generated Markdown into Rich-compatible markup for UI rendering.

        Args:
            text (str): Raw Markdown text from the AI.

        Returns:
            str: Formatted Rich markup string.
        """
        text = text.replace("[", "\\[")
        text = re.sub(r'(?<!\w)#([\w:-]+)', r'[bold #66D0BC]#\1[/bold #66D0BC]', text)
        text = re.sub(r'(?<!\w)&([\w:-]+)', r'[bold #F77F00]&\1[/bold #F77F00]', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/bold #cba6f7]', text)
        text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/bold #cba6f7]', text, flags=re.MULTILINE)
        text = re.sub(r'```[\w]*\n?(.*?)\n?```', lambda m: f"[dim]{m.group(1)}[/dim]", text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'[reverse]\1[/reverse]', text)
        
        return text
