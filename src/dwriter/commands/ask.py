"""AI Natural Language Command for dwriter.

This module implements the 'ask' command, which utilizes a routing architecture
to interpret natural language requests and execute corresponding database operations.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Union

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
from ..ai.schemas.tasks import AddTodoIntent, ProjectBreakdownIntent
from ..ai.schemas.triage import BulkSnoozeIntent, TriageReview
from ..tui.colors import PROJECT, TAG


@click.command("ask")
@click.argument("content", nargs=-1)
@click.pass_obj
def ask(ctx: AppContext, content: tuple[str, ...]) -> None:
    """Interprets and executes natural language commands using AI.

    The command employs a multi-stage routing architecture to categorize user
    intent and extract relevant parameters for task management, triage,
    reflection, and analytics.

    Args:
        ctx: The application context containing configuration and database access.
        content: The raw natural language input from the user.

    Examples:
        dwriter ask "Remind me to call John tomorrow at 2pm"
        dwriter ask "Break down the 'Website Redesign' project into tasks"
        dwriter ask "I'm overwhelmed, help me triage my tasks"
        dwriter ask "Snooze all overdue tasks until Monday"
        dwriter ask "I'm back from vacation, what did I miss?"
        dwriter ask "Give me a reflection prompt for my journal"
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

            # Task management execution
            if route.category == "task_management":
                status.update("Extracting task details...")
                intent = client.chat.completions.create(
                    model=ctx.config.ai.model,
                    response_model=Union[AddTodoIntent, ProjectBreakdownIntent],
                    max_retries=2,
                    messages=[
                        {
                            "role": "system",
                            "content": get_system_prompt(
                                "Extract structured task management intent. "
                                "For single tasks, use AddTodoIntent. "
                                "For multiple tasks or project breakdowns, use ProjectBreakdownIntent. "
                                f"Current time: {datetime.now().isoformat()}"
                            ),
                        },
                        {"role": "user", "content": query_text},
                    ],
                )
                status.stop()
                _handle_task_management(ctx, intent)
                return

            # Triage and intervention execution
            if route.category == "triage":
                status.update("Analyzing tasks for triage...")
                intent = client.chat.completions.create(
                    model=ctx.config.ai.model,
                    response_model=Union[BulkSnoozeIntent, TriageReview],
                    max_retries=2,
                    messages=[
                        {
                            "role": "system",
                            "content": get_system_prompt(
                                "Identify if the user wants a bulk snooze or a triage review (intervention). "
                                "BulkSnoozeIntent is for snoozing overdue or low priority tasks. "
                                "TriageReview is for when the user is overwhelmed or asks for help/review of stale tasks. "
                                f"Current time: {datetime.now().isoformat()}"
                            ),
                        },
                        {"role": "user", "content": query_text},
                    ],
                )
                status.stop()
                _handle_triage(ctx, client, intent)
                return

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

    # Fallback for unhandled categories
    ctx.console.print(f"[bold yellow]Detected Category:[/bold yellow] {route.category.replace('_', ' ').title()}")


def _handle_task_management(
    ctx: AppContext, intent: AddTodoIntent | ProjectBreakdownIntent
) -> None:
    """Dispatches task management intents to specific execution handlers.

    Args:
        ctx: The application context.
        intent: The extracted task management intent.
    """
    if isinstance(intent, AddTodoIntent):
        _execute_add_todo(ctx, intent)
    elif isinstance(intent, ProjectBreakdownIntent):
        _execute_project_breakdown(ctx, intent)


def _execute_add_todo(ctx: AppContext, intent: AddTodoIntent) -> None:
    """Persists a single todo item to the database.

    Args:
        ctx: The application context.
        intent: The structured data for the new todo.
    """
    due_date = intent.due_date
    if due_date and due_date.tzinfo:
        due_date = due_date.replace(tzinfo=None)

    todo = ctx.db.add_todo(
        content=intent.content,
        priority=intent.priority,
        project=intent.project,
        tags=intent.tags,
        due_date=due_date,
    )

    priority_colors = {
        "urgent": "bold red",
        "high": "yellow",
        "normal": "white",
        "low": "dim",
    }
    color = priority_colors.get(intent.priority, "white")

    due_str = ""
    if due_date:
        due_str = f" [dim](due: {due_date.strftime('%Y-%m-%d %H:%M')})[/dim]"

    tags_str = f" [{TAG}]#{' #'.join(intent.tags)}[/{TAG}]" if intent.tags else ""
    proj_str = f" [{PROJECT}]&{intent.project}[/{PROJECT}]" if intent.project else ""

    ctx.console.print(
        f"[green]Added Task [{todo.id}]:[/green] "
        f"[{color}]{intent.priority.upper()}[/{color}] | "
        f"[{color}]{intent.content}[/{color}]{tags_str}{proj_str}{due_str}"
    )


def _execute_project_breakdown(ctx: AppContext, intent: ProjectBreakdownIntent) -> None:
    """Decomposes a project into multiple tasks and persists them.

    Args:
        ctx: The application context.
        intent: The structured breakdown of the project.
    """
    ctx.console.print(
        f"[bold green]Breaking down project:[/bold green] [{PROJECT}]&{intent.project_name}[/{PROJECT}]"
    )

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right", style=PROJECT)
    table.add_column("Priority", justify="center")
    table.add_column("Task")
    table.add_column("Due (est)", style="cyan")

    now = datetime.now()
    for task in intent.tasks:
        due_date = now + timedelta(days=task.estimated_days_out)

        todo = ctx.db.add_todo(
            content=task.content,
            priority=task.priority,
            project=intent.project_name,
            due_date=due_date,
        )

        priority_colors = {
            "urgent": "bold red",
            "high": "yellow",
            "normal": "white",
            "low": "dim",
        }
        p_label = task.priority.upper()
        p_style = priority_colors.get(task.priority, "white")

        due_str = due_date.strftime("%Y-%m-%d") if task.estimated_days_out > 0 else "Today"
        table.add_row(str(todo.id), f"[{p_style}]{p_label}[/{p_style}]", task.content, due_str)

    ctx.console.print(table)
    ctx.console.print(f"[green]Successfully added {len(intent.tasks)} tasks to &{intent.project_name}[/green]")


def _handle_triage(
    ctx: AppContext, client: Any, intent: BulkSnoozeIntent | TriageReview
) -> None:
    """Dispatches triage intents to specific execution handlers.

    Args:
        ctx: The application context.
        client: The AI client for further interactions.
        intent: The extracted triage intent.
    """
    if isinstance(intent, BulkSnoozeIntent):
        _execute_bulk_snooze(ctx, intent)
    elif isinstance(intent, TriageReview):
        _execute_anti_procrastination(ctx, client)


def _execute_bulk_snooze(ctx: AppContext, intent: BulkSnoozeIntent) -> None:
    """Updates due dates for a batch of tasks based on criteria.

    Args:
        ctx: The application context.
        intent: The structured snooze criteria and target date.
    """
    todos = ctx.db.get_todos(status="pending")
    now = datetime.now()

    to_snooze = []
    if intent.target_tasks == "all_overdue":
        to_snooze = [t for t in todos if t.due_date and t.due_date < now]
    elif intent.target_tasks == "low_priority":
        to_snooze = [t for t in todos if t.priority == "low"]

    if not to_snooze:
        ctx.console.print("[yellow]No tasks matching the criteria to snooze.[/yellow]")
        return

    snooze_date = intent.snooze_until
    if snooze_date.tzinfo:
        snooze_date = snooze_date.replace(tzinfo=None)

    for t in to_snooze:
        ctx.db.update_todo(t.id, due_date=snooze_date)

    ctx.console.print(
        f"[green]Successfully snoozed {len(to_snooze)} tasks until {snooze_date.strftime('%Y-%m-%d')}.[/green]"
    )
    ctx.console.print(f"[dim]Reasoning: {intent.reasoning}[/dim]")


def _execute_anti_procrastination(ctx: AppContext, client: Any) -> None:
    """Identifies stale tasks and generates AI-driven micro-interventions.

    Args:
        ctx: The application context.
        client: The AI client.
    """
    todos = ctx.db.get_todos(status="pending")
    now = datetime.now()
    stale_limit = now - timedelta(days=14)

    stale_tasks = [t for t in todos if t.created_at < stale_limit]

    if not stale_tasks:
        ctx.console.print("[green]No stale tasks found! Your list is looking fresh.[/green]")
        return

    tasks_data = "\n".join([f"ID: {t.id} | Task: {t.content} | Created: {t.created_at.strftime('%Y-%m-%d')}" for t in stale_tasks])

    with Status("Generating interventions for stale tasks...", console=ctx.console) as status:
        try:
            review = client.chat.completions.create(
                model=ctx.config.ai.model,
                response_model=TriageReview,
                max_retries=2,
                messages=[
                    {
                        "role": "system",
                        "content": get_system_prompt(
                            "Provide gentle interventions for these stale tasks. "
                            "Create micro-tasks that take < 2 minutes. "
                            "Recommend deletion if the task seems no longer relevant."
                        ),
                    },
                    {"role": "user", "content": tasks_data},
                ],
            )
        except Exception as e:
            status.stop()
            ctx.console.print(f"[red]Error generating triage review:[/red] {e}")
            return

    table = Table(title="Anti-Procrastination Triage", show_header=True, header_style="bold red")
    table.add_column("ID", justify="right", style=PROJECT)
    table.add_column("Observation")
    table.add_column("Micro-Task (2 min)")
    table.add_column("Action", justify="center")

    for intervention in review.interventions:
        action_str = "[bold red]DELETE?[/bold red]" if intervention.recommend_delete else "[cyan]KEEP[/cyan]"
        table.add_row(
            str(intervention.task_id),
            intervention.user_friendly_callout,
            f"[italic]{intervention.suggested_micro_task}[/italic]",
            action_str
        )

    ctx.console.print(table)
    ctx.console.print("\n[dim]Use 'dwriter edit <id>' to update or 'dwriter delete <id>' to remove tasks.[/dim]")


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
