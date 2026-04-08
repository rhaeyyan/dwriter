"""2nd-Brain screen for dwriter TUI.

This module provides an interactive AI chat interface that is context-aware
of the user's current tasks and journal entries, featuring long-term memory
via weekly summaries and targeted historical retrieval.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import AppContext

from rich.markup import escape
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, Static

from ...ai.engine import get_ai_client, get_raw_ai_client, get_system_prompt
from ...ai.schemas.router import ActionRouter


class ChatMessage(Container):
    """Base class for chat messages acting as a full-width container."""
    def __init__(self, content: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.content = content

class UserChatMessage(ChatMessage):
    """Widget for user chat messages aligned to the right."""
    DEFAULT_CSS = """
    UserChatMessage {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    .user-bubble {
        width: auto;
        max-width: 94%;
        margin: 1 2;
        padding: 0 1;
        background: $surface;
        color: white;
        border: solid cyan;
    }
    """
    def compose(self) -> ComposeResult:
        # Wrap self.content in escape() so users can't inject Rich markup
        yield Static(f"[bold cyan]You:[/bold cyan]\n{escape(self.content)}", classes="user-bubble")

class AIChatMessage(ChatMessage):
    """Widget for AI chat messages aligned to the left."""
    DEFAULT_CSS = """
    AIChatMessage {
        width: 100%;
        height: auto;
        align-horizontal: left;
    }
    .ai-bubble {
        width: auto;
        max-width: 98%;
        margin: 1 2;
        padding: 0 1;
        background: $panel;
        color: white;
        border: round #cba6f7;
    }
    """
    def compose(self) -> ComposeResult:
        yield Static(f"[bold #cba6f7]2nd-Brain:[/bold #cba6f7]\n{self.content}", classes="ai-bubble")

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
        overflow-y: scroll;
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
        self._welcome_shown: bool = False

    def compose(self) -> ComposeResult:
        """Composes the 2nd-Brain layout components."""
        with Vertical():
            with Vertical(id="second-brain-log"):
                yield Static("[bold black on yellow] SYSTEM [/bold black on yellow]\n[dim]2nd-Brain initialized with recent task and log context.[/dim]")
            yield Static("", id="second-brain-status")
            yield Input(placeholder="Ask your 2nd-Brain anything...", id="second-brain-input")

    def on_mount(self) -> None:
        """Initializes chat history and refreshes the primary context."""
        self._refresh_context()

    def on_show(self) -> None:
        """Triggers welcome message with 7-day wrap info when screen is shown."""
        if not self._welcome_shown:
            self._display_welcome_message()
            self._welcome_shown = True

    @work(thread=True)
    def _display_welcome_message(self) -> None:
        """Fetches 7-day wrap info and displays it as a welcome message.

        Throttles the heavy 7-Day Pulse wrap-up to once per day. If already
        shown today, returns a fast, minimalist greeting.
        """
        from ...analytics import AnalyticsEngine, InsightGenerator
        
        try:
            today = datetime.now().date().isoformat()
            last_pulse = self.ctx.config.ai.last_pulse_greeting
            
            # Check if we should show the full pulse or a minimalist greeting
            if last_pulse == today:
                welcome_content = (
                    "Welcome back. [bold #cba6f7]Ready to log or retrieve?[/bold #cba6f7]\n\n"
                    "How can I help you optimize your focus today?"
                )
            else:
                engine = AnalyticsEngine(self.ctx.db)
                insight_gen = InsightGenerator(engine)
                nudges = insight_gen.generate_weekly_wrapup()
                
                if nudges:
                    # Add extra newline between nudge items for better "Dashboard" separation
                    wrap_text = "\n\n".join(nudges)
                    welcome_content = (
                        "Welcome back! Here's your [bold #cba6f7]7-Day Pulse[/bold #cba6f7] wrap-up:\n\n"
                        f"{wrap_text}\n\n"
                        "How can I help you optimize your focus today?"
                    )
                    
                    # Update the last_pulse_greeting timestamp
                    self.ctx.config.ai.last_pulse_greeting = today
                    self.ctx.save_config()
                else:
                    welcome_content = (
                        "Welcome back. [bold #cba6f7]Ready to log or retrieve?[/bold #cba6f7]\n\n"
                        "How can I help you optimize your focus today?"
                    )
            
            # We want this to look like an AI message
            # Skip _format_ai_response because welcome_content is already Rich-formatted
            ai_msg = AIChatMessage(welcome_content)
            log = self.query_one("#second-brain-log", Vertical)
            
            self.app.call_from_thread(log.mount, ai_msg)
            self.app.call_from_thread(ai_msg.scroll_visible)
        except Exception:
            pass

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
                    except Exception:
                        continue
        except Exception:
            pass

        # Activity Layer: Short-Term Memory (Past 72 hours)
        three_days_ago = datetime.now() - timedelta(days=3)
        entries = self.ctx.db.get_all_entries()
        recent = [e for e in entries if e.created_at >= three_days_ago]
        todos = self.ctx.db.get_todos(status="pending")

        short_term = "[SHORT-TERM ACTIVITY (PAST 72H)]\n"
        if recent:
            for e in recent[:20]:
                short_term += f"- [{e.created_at.strftime('%Y-%m-%d %H:%M')}] {e.content}\n"
        else:
            short_term += "- No recent logs.\n"

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

        log = self.query_one("#second-brain-log", Vertical)
        status = self.query_one("#second-brain-status", Static)
        
        # User message
        user_msg = UserChatMessage(user_input)
        log.mount(user_msg)
        user_msg.scroll_visible()
        
        status.update("[bold #cba6f7]Thinking...[/bold #cba6f7]")
        event.input.value = ""

        if not self.ctx.config.ai.enabled:
            log.mount(Static("[yellow]AI features are disabled in configuration.[/yellow]"))
            status.update("")
            return

        self._run_ai_chat(user_input)

    @work(thread=True)
    def _run_ai_chat(self, user_input: str) -> None:
        """Executes the AI chat workflow focusing on historical retrieval and analysis.

        Args:
            user_input (str): The raw text query from the user.
        """
        log = self.query_one("#second-brain-log", Vertical)
        status = self.query_one("#second-brain-status", Static)
        
        try:
            # Intent classification phase
            client_structured = get_ai_client(self.ctx.config.ai)
            
            self.app.call_from_thread(status.update, "[bold #cba6f7]Categorizing intent...[/bold #cba6f7]")
            client_structured.chat.completions.create(
                model=self.ctx.config.ai.model,
                response_model=ActionRouter,
                messages=[
                    {
                        "role": "system",
                        "content": get_system_prompt(
                            "Categorize the user's request into a functional domain. "
                            "Functional areas: reflection, analytics, context_restore, unknown."
                        ),
                    },
                    {"role": "user", "content": user_input},
                ],
            )

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
                        "IMPORTANT: You are an analytical assistant. You CANNOT perform actions "
                        "like adding tasks, logging entries, or changing due dates. If asked "
                        "to do so, explain that you are designed for reflection and analysis only."
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
            
            # Mount AI message widget
            ai_msg = AIChatMessage(formatted_answer)
            self.app.call_from_thread(log.mount, ai_msg)
            self.app.call_from_thread(ai_msg.scroll_visible)
            
            self.app.call_from_thread(status.update, "")
            
        except Exception as e:
            error_msg = Static(f"[red]AI Error: {e}[/red]")
            self.app.call_from_thread(log.mount, error_msg)
            self.app.call_from_thread(status.update, "[bold red]AI Error[/bold red]")

    def _format_ai_response(self, text: str) -> str:
        """Transforms AI-generated Markdown into Rich-compatible markup for UI rendering.

        Args:
            text (str): Raw Markdown text from the AI.

        Returns:
            str: Formatted Rich markup string.
        """
        # 1. Escape the raw AI text first to make brackets literal
        text = escape(text)
        
        # 2. Colorize Tags and Projects
        # Use identical colors to InsightGenerator
        text = re.sub(r'(?<!\w)#([\w:-]+)', r'[bold #66D0BC]#\1[/bold #66D0BC]', text)
        text = re.sub(r'(?<!\w)&([\w:-]+)', r'[bold #F77F00]&\1[/bold #F77F00]', text)
        
        # 3. Colorize Dates (e.g., 2026-04-07)
        text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'[cyan]\1[/cyan]', text)
        
        # 4. Colorize Times (e.g., 14:00, 2:30pm)
        text = re.sub(r'(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)', r'[$success]\1[/$success]', text)

        # 5. Colorize Urgency/Priority levels
        text = re.sub(r'(?i)\b(urgent)\b', r'[bold #D53E0F]\1[/bold #D53E0F]', text)
        text = re.sub(r'(?i)\b(high)\b', r'[#D53E0F]\1[/#D53E0F]', text)
        text = re.sub(r'(?i)\b(normal)\b', r'[white]\1[/white]', text)
        text = re.sub(r'(?i)\b(low)\b', r'[dim]\1[/dim]', text)
        
        # 6. Convert Markdown bold and headers to Rich tags
        # Note: These regexes work on escaped text because escape() only touches [ and ]
        text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/bold #cba6f7]', text)
        text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/bold #cba6f7]', text, flags=re.MULTILINE)
        
        # 7. Code blocks and inline code
        text = re.sub(r'```[\w]*\n?(.*?)\n?```', lambda m: f"[dim]{m.group(1)}[/dim]", text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'[reverse]\1[/reverse]', text)
        
        # 8. Neat Emoji Lists (ensure space after emoji bullet)
        # Matches emoji at start of line followed by optional space, ensures 2 spaces for "neat" alignment
        text = re.sub(r'^([^\w\s\d\[\(])\s*', r'\1  ', text, flags=re.MULTILINE)

        return text
