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

from ...ai.compression import compress_summary
from ...ai.engine import ask_second_brain_agentic


class ThinkingIndicator(Static):
    """Unified thinking indicator with Braille spinner, text, and elapsed timer."""
    DEFAULT_CSS = """
    ThinkingIndicator {
        display: none;
        height: 1;
        margin: 0 2;
    }
    """

    CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    COLORS = ["#D53E0F", "#66D0BC", "#00E5FF", "#FCBF49"]

    def on_mount(self) -> None:
        self._frame = 0
        self._start_time: float | None = None
        self.update(self._build_text())
        self.set_interval(0.1, self._update_spinner)

    def start(self) -> None:
        """Start the indicator and reset the timer."""
        import time
        self._start_time = time.monotonic()
        self._frame = 0
        self.update(self._build_text())
        self.display = True

    def stop(self) -> None:
        """Hide the indicator."""
        self.display = False
        self._start_time = None

    def _build_text(self) -> str:
        """Build the indicator text with spinner and elapsed time."""
        import time
        try:
            char = self.CHARS[self._frame]
            color = self.COLORS[self._frame % len(self.COLORS)]
            elapsed = 0.0
            if self._start_time is not None:
                elapsed = time.monotonic() - self._start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"  [{color}]{char}[/] [dim]thinking[/]  [dim]{mins:02d}:{secs:02d}[/]"
        except Exception:
            return "  [dim]thinking...[/]"

    def _update_spinner(self) -> None:
        if self.display:
            self._frame = (self._frame + 1) % len(self.CHARS)
            self.update(self._build_text())


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
        margin: 1 0 0 0;
    }
    .user-label {
        width: auto;
        height: 1;
        color: $primary;
        margin: 0 2 0 0;
    }
    .user-bubble {
        width: auto;
        max-width: 80%;
        height: auto;
        padding: 0 2;
        background: $surface;
        border: none;
        border-right: solid $primary;
        margin: 0 1 1 0;
    }
    """
    def compose(self) -> ComposeResult:
        # Escape user input to prevent Rich markup injection
        escaped = escape(self.content)
        yield Static("you", classes="user-label")
        yield Static(escaped, classes="user-bubble")

class AIChatMessage(ChatMessage):
    """Widget for AI chat messages aligned to the left.

    Renders the response in a clean unified block with a labelled header
    and a left-side accent border for modern, scannable output.
    """
    DEFAULT_CSS = """
    AIChatMessage {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    .ai-label {
        width: auto;
        height: 1;
        margin: 0 0 0 2;
    }
    .ai-bubble {
        width: auto;
        max-width: 96%;
        height: auto;
        padding: 0 2;
        background: $panel;
        border: none;
        border-left: solid #cba6f7;
        margin: 0 0 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        # Pre-indent all non-empty lines for consistent hanging alignment
        lines = self.content.split("\n")
        indented = "\n".join(f"  {line}" if line.strip() else "" for line in lines)
        yield Static("[bold #cba6f7]▸ 2nd-Brain[/]", classes="ai-label")
        yield Static(indented, markup=True, classes="ai-bubble")

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

    .system-message {
        height: auto;
        margin: 1 2 0 2;
        padding: 0;
        color: $text-muted;
        text-align: center;
    }

    #second-brain-status {
        height: 1;
        margin: 0 1;
        padding: 0;
        color: $text-muted;
        display: none;
    }

    #ai-status-indicator {
        height: 1;
        margin: 0 2;
        padding: 0;
        display: none;
    }

    #thinking-indicator {
        height: 1;
        margin: 0 0 0 1;
        padding: 0;
        display: none;
    }

    #second-brain-input {
        margin: 0;
        border: none;
        border-top: solid #cba6f7;
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
                yield Static("[dim]── 2nd-Brain ready · context loaded ──[/dim]", classes="system-message")
            yield ThinkingIndicator(id="thinking-indicator")
            yield Input(placeholder="Ask your 2nd-Brain anything...", id="second-brain-input")

    def on_mount(self) -> None:
        """Initializes chat history and refreshes the primary context."""
        self._refresh_context()

    def on_show(self) -> None:
        """Refreshes context and triggers welcome message when screen is shown."""
        self._refresh_context()
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
                    "Welcome back. [bold #cba6f7]Ready to log or retrieve?[/]\n\n"
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
                        "Welcome back! Here's your [bold #cba6f7]7-Day Pulse[/] wrap-up:\n\n"
                        f"{wrap_text}\n\n"
                        "How can I help you optimize your focus today?"
                    )
                    
                    # Update the last_pulse_greeting timestamp
                    self.ctx.config.ai.last_pulse_greeting = today
                    self.ctx.save_config()
                else:
                    welcome_content = (
                        "Welcome back. [bold #cba6f7]Ready to log or retrieve?[/]\n\n"
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

        raw_context = f"{long_term}\n{short_term}"
        self._context_data = compress_summary(raw_context)

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

        # Keyword matching for project history — matches &name and plain name as a word
        try:
            all_projects = list(self.ctx.db.get_project_stats().keys())
            mentioned_projects = [
                p
                for p in all_projects
                if re.search(
                    r"(?:&|\b)" + re.escape(p) + r"\b", user_input, re.IGNORECASE
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

        # Keyword matching for tag history — matches #name and plain name as a word
        try:
            all_tags = list(self.ctx.db.get_entries_with_tags_count().keys())
            mentioned_tags = [
                t
                for t in all_tags
                if re.search(
                    r"(?:#|\b)" + re.escape(t) + r"\b", user_input, re.IGNORECASE
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

        # User message
        user_msg = UserChatMessage(user_input)
        log.mount(user_msg)
        user_msg.scroll_visible()

        event.input.value = ""

        if not self.ctx.config.ai.enabled:
            log.mount(Static("[yellow]AI features are disabled in configuration.[/yellow]"))
            return

        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        thinking.start()
        self._run_ai_chat(user_input)

    @work(thread=True)
    def _run_ai_chat(self, user_input: str) -> None:
        """Executes the agentic AI chat workflow with tool calling.

        Args:
            user_input (str): The raw text query from the user.
        """
        log = self.query_one("#second-brain-log", Vertical)
        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)

        try:
            # 1. Targeted context retrieval (keywords)
            targeted_context = self._get_targeted_context(user_input)
            combined_context = compress_summary(f"{self._context_data}\n{targeted_context}")

            # 2. Run agentic loop (with tool-calling)
            answer = ask_second_brain_agentic(
                prompt=user_input,
                config=self.ctx.config.ai,
                context_data=combined_context,
                app_context=self,
            )

            # 3. Hide indicator
            self.app.call_from_thread(thinking.stop)

            # 4. Update chat history and display response
            self._chat_history.append({"role": "user", "content": user_input})
            self._chat_history.append({"role": "assistant", "content": answer})

            formatted_answer = self._format_ai_response(answer)
            ai_msg = AIChatMessage(formatted_answer)
            self.app.call_from_thread(log.mount, ai_msg)
            self.app.call_from_thread(ai_msg.scroll_visible)

        except Exception as e:
            # Ensure indicator is hidden on error
            self.app.call_from_thread(thinking.stop)

            error_msg = Static(f"[red]AI Error: {e}[/red]")
            self.app.call_from_thread(log.mount, error_msg)
            self.app.call_from_thread(error_msg.scroll_visible)

    def _format_ai_response(self, text: str) -> str:
        """Transforms AI-generated Markdown into Rich-compatible markup for UI rendering.

        Focuses on clean, scannable output: proper paragraph spacing,
        selective colorization of dates/tags/priorities, and minimal
        emoji amplification to avoid visual clutter.

        Args:
            text (str): Raw Markdown text from the AI.

        Returns:
            str: Formatted Rich markup string.
        """
        # 1. Escape the raw AI text first to make brackets literal
        text = escape(text)

        # 2. Reduce emoji density: remove redundant emoji bullets that local LLMs overuse
        # Strips lines that are *only* an emoji (common LLM habit: 📌, ✅, 🔥, etc.)
        # Replaces them with a clean dash marker for scanability.
        text = re.sub(
            r'^[\s]*[\U0001F300-\U0001FAD6\U00002700-\U000027BF\U00002600-\U000026FF]\s*',
            '  \u2013 ',  # en-dash bullet
            text,
            flags=re.MULTILINE,
        )

        # 3. Colorize Tags and Projects (selective — only when they're actual refs)
        text = re.sub(r'(?<!\w)#([\w:-]+)', r'[bold #66D0BC]#\1[/]', text)
        text = re.sub(r'(?<!\w)&([\w:-]+)', r'[bold #F77F00]&\1[/]', text)

        # 4. Colorize Dates (e.g., 2026-04-07)
        text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'[cyan]\1[/]', text)

        # 5. Colorize Times (e.g., 14:00, 2:30pm)
        text = re.sub(r'(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)', r'[$success]\1[/]', text)

        # 6. Colorize Urgency/Priority levels
        text = re.sub(r'(?i)\b(urgent)\b', r'[bold #D53E0F]\1[/]', text)
        text = re.sub(r'(?i)\b(high)\b', r'[#D53E0F]\1[/]', text)
        text = re.sub(r'(?i)\b(normal)\b', r'[white]\1[/]', text)
        text = re.sub(r'(?i)\b(low)\b', r'[dim]\1[/]', text)

        # 7. Convert Markdown bold and headers to Rich tags
        text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/]', text)
        text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/]', text, flags=re.MULTILINE)

        # 8. Code blocks and inline code
        text = re.sub(
            r'```[\w]*\n?(.*?)\n?```',
            lambda m: f"[dim]{m.group(1)}[/dim]",
            text,
            flags=re.DOTALL,
        )
        text = re.sub(r'`(.*?)`', r'[#89b4fa]\1[/]', text)

        # 9. Normalize paragraph spacing: collapse 3+ newlines into 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text
