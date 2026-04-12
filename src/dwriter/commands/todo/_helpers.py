"""Shared internal implementations for the todo subcommands."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click
from rich.table import Table

from ...tui.colors import DUE_OVERDUE, DUE_SOON, DUE_TODAY, DUE_TOMORROW, PROJECT, TAG


def _execute_list(ctx: AppContext, show_all: bool, output_json: bool = False) -> None:
    """Internal implementation of todo list."""
    status_filter = None if show_all else "pending"
    tasks = ctx.db.get_todos(status=status_filter)

    if output_json:
        data = []
        for task in tasks:
            data.append({
                "id": task.id,
                "uuid": task.uuid,
                "content": task.content,
                "project": task.project,
                "priority": task.priority,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tag_names,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            })
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return

    if not tasks:
        ctx.console.print(
            "No tasks found. Relax or add one with [bold]dwriter todo[/bold]!"
        )
        return

    table = Table(title="Your Tasks", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right", style=PROJECT, no_wrap=True)
    table.add_column("Priority", justify="center")
    table.add_column("Task")
    table.add_column("Project", style=PROJECT)
    table.add_column("Tags", style=TAG)
    table.add_column("Due", style="cyan", justify="center")

    priority_styles = {
        "urgent": ("[bold red]URGENT[/bold red]", "bold red"),
        "high": ("[yellow]HIGH[/yellow]", "yellow"),
        "normal": ("NORMAL", "white"),
        "low": ("[dim]LOW[/dim]", "dim"),
    }

    for task in tasks:
        p_label, p_style = priority_styles.get(task.priority, ("NORMAL", "white"))

        content_str = (
            f"[strike]{task.content}[/strike]"
            if task.status == "completed"
            else f"[{p_style}]{task.content}[/{p_style}]"
        )

        tags_str = ", ".join(task.tag_names) if task.tag_names else ""
        project_str = f"&{task.project}" if task.project else ""

        # Format due date
        due_str = ""
        if task.due_date:
            due_date = task.due_date
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            due_date_only = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            days_until = (due_date_only - today).days

            if days_until < 0:
                due_str = f"[{DUE_OVERDUE}]{due_date.strftime('%Y-%m-%d')}[/{DUE_OVERDUE}]"
            elif days_until == 0:
                if due_date.hour == 0 and due_date.minute == 0:
                    due_str = f"[{DUE_TODAY}]TODAY[/{DUE_TODAY}]"
                else:
                    due_str = f"[{DUE_TODAY}]{due_date.strftime('%H:%M')}[/{DUE_TODAY}]"
            elif days_until == 1:
                due_str = f"[{DUE_TOMORROW}]Tomorrow[/{DUE_TOMORROW}]"
            elif days_until <= 7:
                due_str = f"[{DUE_SOON}]{days_until}d[/{DUE_SOON}]"
            else:
                due_str = due_date.strftime("%Y-%m-%d")

        table.add_row(
            str(task.id),
            p_label,
            content_str,
            project_str,
            tags_str,
            due_str,
        )

    ctx.console.print(table)


def _execute_rm(ctx: AppContext, task_id: int) -> None:
    """Internal implementation of todo rm."""
    try:
        ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    if click.confirm(f"Are you sure you want to delete task {task_id}?"):
        success = ctx.db.delete_todo(task_id)
        if success:
            ctx.console.print(f"[green]✅[/green] Task {task_id} deleted.")
        else:
            ctx.console.print(f"[red]![/red] Task {task_id} not found.")
    else:
        ctx.console.print("Cancelled.")


def _execute_edit(ctx: AppContext, task_id: int) -> None:
    """Internal implementation of todo edit."""
    try:
        task = ctx.db.get_todo(task_id)
    except ValueError:
        ctx.console.print(f"[red]![/red] Task {task_id} not found.")
        return

    edited_content = click.edit(task.content)

    if edited_content is None:
        ctx.console.print("No changes made.")
        return

    edited_content = edited_content.strip()

    if not edited_content:
        ctx.console.print("Task content cannot be empty. Use 'todo rm' to delete.")
        return

    if edited_content != task.content:
        ctx.db.update_todo(task_id, content=edited_content)
        ctx.console.print(f"[green]✅[/green] Task {task_id} updated.")
    else:
        ctx.console.print("No changes made.")
