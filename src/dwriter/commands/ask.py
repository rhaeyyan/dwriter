"""AI Natural Language Command for dwriter.

This module implements the 'ask' command, which utilizes a routing architecture
to interpret natural language queries for historical analysis and reflection.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext

import click
import openai
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from ..ai.engine import get_ai_client, get_system_prompt
from ..ai.schemas.reflection import ContextRestore, ReflectionPrompt
from ..ai.schemas.router import ActionRouter
from ..tui.colors import PROJECT, TAG


@click.command("ask")
@click.argument("content", nargs=-1)
@click.pass_obj
def ask(ctx: AppContext, content: tuple[str, ...]) -> None:
    """Queries the AI 2nd-Brain for insights and retrospective data.

    Utilizes a routing architecture to interpret user queries and extract
    parameters for historical retrieval, task summarization, and reflection.

    Args:
        ctx: Application context.
        content: Natural language query string.

    Examples:
        dwriter ask "What were my biggest wins this week?"
        dwriter ask "How much time did I spend on &project-x?"
        dwriter ask "I'm overwhelmed, help me summarize my pending tasks"
        dwriter ask "Analyze my productivity patterns for the last month"
    """
    if not ctx.config.ai.enabled:
        ctx.console.print(
            "[yellow]AI features are currently disabled in config.[/yellow]"
        )
        return

    query_text = " ".join(content)
    if not query_text:
        ctx.console.print("[red]Please provide a question or command.[/red]")
        return

    try:
        client = get_ai_client(ctx.config.ai)
    except Exception as e:
        ctx.console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        return

    with Status("Thinking...", console=ctx.console, spinner="dots") as status:
        # Configure Instructor hooks for dynamic status updates
        client.on("completion:kwargs", lambda *args, **kwargs: status.update("Analyzing request context..."))
        client.on("completion:response", lambda *args, **kwargs: status.update("Categorizing intent..."))
        client.on("completion:error", lambda *args, **kwargs: status.stop())

        try:
            # Intent classification
            route = client.chat.completions.create(
                model=ctx.config.ai.model,
                response_model=ActionRouter,
                max_retries=2,
                messages=[
                    {
                        "role": "system",
                        "content": get_system_prompt("Categorize the user's request into one of the main functional areas."),
                    },
                    {"role": "user", "content": query_text},
                ],
            )

            # Reflection and context restoration
            if route.category == "reflection":
                status.update("Generating reflection prompt...")
                _execute_reflection(ctx, client)
                return

            if route.category == "context_restore":
                status.update("Restoring context...")
                _execute_context_restore(ctx, client)
                return

            # Productivity analytics
            if route.category == "analytics":
                status.update("Analyzing productivity patterns...")
                _execute_analytics(ctx, client)
                return

            # If category is unknown, fallback to a conversational analysis
            status.update("Generating response...")
            _execute_general_query(ctx, client, query_text)

        except (ConnectionError, openai.APIConnectionError):
            status.stop()
            ctx.console.print(
                "\n[bold red]Connection Error:[/bold red] Unable to connect to AI provider. "
                "If using Ollama, ensure it is running with `ollama serve`."
            )
            return
        except Exception as e:
            status.stop()
            ctx.console.print(f"\n[bold red]AI Error:[/bold red] {e}")
            return


def _execute_general_query(ctx: AppContext, client: Any, query: str) -> None:
    """Handles general conversational queries about history or productivity.

    Uses a local RAG pipeline to retrieve semantically similar historical entries.

    Args:
        ctx: Application context.
        client: AI client.
        query: User's natural language question.
    """
    from ..ai.engine import get_embedding

    try:
        # Generate query embedding and retrieve similar entries
        query_embedding = get_embedding(query, ctx.config.ai)
        similar_entries = ctx.db.search_similar_entries(query_embedding, limit=5)
        todos = ctx.db.get_todos(status="pending")

        historical_context = "HISTORICAL CONTEXT (Relevant Past Entries):\n"
        if similar_entries:
            historical_context += "\n".join(
                [
                    f"- [{e.created_at.strftime('%Y-%m-%d')}] {e.content}"
                    for e in similar_entries
                ]
            )
        else:
            historical_context += "- No semantically similar entries found."

        current_tasks = "\n\nPENDING TASKS:\n"
        current_tasks += "\n".join([f"- {t.content}" for t in todos[:10]])

        response = client.chat.completions.create(
            model=ctx.config.ai.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are dwriter 2nd-Brain. Use the provided historical context to answer "
                        "the user's questions about their past habits, trends, and accomplishments. "
                        "IMPORTANT: You are an analytical assistant. You CANNOT perform actions "
                        "like adding tasks or logging entries. If asked to do so, explain that "
                        "you are designed for reflection and analysis only."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{historical_context}\n{current_tasks}\n\nQuestion: {query}",
                },
            ],
        )
        ctx.console.print("\n[bold cyan]2nd-Brain Response:[/bold cyan]")
        ctx.console.print(
            Panel(response.choices[0].message.content, border_style="cyan")
        )
    except Exception as e:
        ctx.console.print(f"[red]Error generating response:[/red] {e}")


def _execute_reflection(ctx: AppContext, client: Any) -> None:
    """Generates a personalized journaling prompt based on recent user activity.

    Args:
        ctx: The application context.
        client: The AI client.
    """
    seven_days_ago = datetime.now() - timedelta(days=7)
    entries = ctx.db.get_all_entries()
    recent_entries = [e for e in entries if e.created_at >= seven_days_ago]

    entries_data = "\n".join([f"- {e.content}" for e in recent_entries[:20]])

    try:
        reflection = client.chat.completions.create(
            model=ctx.config.ai.model,
            response_model=ReflectionPrompt,
            max_retries=2,
            messages=[
                {
                    "role": "system",
                    "content": get_system_prompt(
                        "Generate a personalized journaling prompt based on recent activity. "
                        "Identify recurring themes and ask a targeted question."
                    ),
                },
                {"role": "user", "content": f"Recent activity:\n{entries_data}"},
            ],
        )
    except Exception as e:
        ctx.console.print(f"[red]Error generating reflection prompt:[/red] {e}")
        return

    ctx.console.print("\n[bold blue]Personalized Reflection:[/bold blue]")
    ctx.console.print(Panel(reflection.prompt_text, title="Reflection Prompt", border_style="blue"))
    if reflection.recurring_themes:
        themes_str = f"[{TAG}]#{' #'.join(reflection.recurring_themes)}[/{TAG}]"
        ctx.console.print(f"[dim]Detected Themes: {themes_str}[/dim]")


def _execute_context_restore(ctx: AppContext, client: Any) -> None:
    """Summarizes recent state and urgent tasks to restore user workflow context.

    Args:
        ctx: The application context.
        client: The AI client.
    """
    three_days_ago = datetime.now() - timedelta(days=3)
    entries = ctx.db.get_all_entries()
    recent_entries = [e for e in entries if e.created_at >= three_days_ago]
    todos = ctx.db.get_todos(status="pending")
    urgent_todos = [t for t in todos if t.priority == "urgent"]

    activity_summary = "RECENT JOURNAL ENTRIES:\n"
    activity_summary += "\n".join([f"- {e.content}" for e in recent_entries[:10]])
    activity_summary += "\n\nURGENT PENDING TASKS:\n"
    activity_summary += "\n".join([f"- {t.content}" for t in urgent_todos[:5]])

    try:
        restore = client.chat.completions.create(
            model=ctx.config.ai.model,
            response_model=ContextRestore,
            max_retries=2,
            messages=[
                {
                    "role": "system",
                    "content": get_system_prompt(
                        "Provide a 'Welcome Back' summary to restore the user's workflow context. "
                        "Summarize their last known state and highlight urgent items."
                    ),
                },
                {"role": "user", "content": f"Recent activity context:\n{activity_summary}"},
            ],
        )
    except Exception as e:
        ctx.console.print(f"[red]Error restoring context:[/red] {e}")
        return

    ctx.console.print("\n[bold green]Welcome Back! Here is where you left off:[/bold green]")
    ctx.console.print(Panel(restore.summary_of_last_known_state, title="Context Summary", border_style="green"))

    if restore.urgent_pending_items:
        ctx.console.print("\n[bold red]Immediate Priorities:[/bold red]")
        for item in restore.urgent_pending_items:
            ctx.console.print(f" [red]![/red] {item}")


def _execute_analytics(ctx: AppContext, client: Any) -> None:
    """Analyzes 30-day productivity patterns and returns AI-driven insights.

    Args:
        ctx: The application context.
        client: The AI client.
    """
    # Aggregate activity data from the preceding 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    entries = ctx.db.get_all_entries()
    recent_entries = [e for e in entries if e.created_at >= thirty_days_ago]
    todos = ctx.db.get_all_todos()
    recent_todos = [t for t in todos if t.created_at >= thirty_days_ago]

    stats_data = f"Total Entries: {len(recent_entries)}\n"
    stats_data += f"Total Tasks Added: {len(recent_todos)}\n"
    stats_data += f"Tasks Completed: {len([t for t in recent_todos if t.status == 'completed'])}\n"
    stats_data += "Sample Content:\n"
    stats_data += "\n".join([f"- {e.content}" for e in recent_entries[:20]])

    try:
        analysis = client.chat.completions.create(
            model=ctx.config.ai.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Identify hidden productivity patterns and correlations in the user's data. "
                        "Look for peak performance times, project intensity, and recurring bottlenecks. "
                        "Provide actionable insights in a concise, bulleted format."
                    ),
                },
                {"role": "user", "content": stats_data},
            ],
        )
        ctx.console.print("\n[bold magenta]Hidden Patterns Analyzer:[/bold magenta]")
        ctx.console.print(Panel(analysis.choices[0].message.content, title="Productivity Insights", border_style="magenta"))
    except Exception as e:
        ctx.console.print(f"[red]Error analyzing patterns:[/red] {e}")
