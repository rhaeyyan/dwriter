"""Model Context Protocol (MCP) server for dwriter.

Exposes dwriter's core database functions as MCP tools for AI assistants,
preserving all business logic and sorting rules natively.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

from .database import Database
from .search_utils import search_items
from .stats_utils import calculate_streak

# ──────────────────────────────────────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────────────────────────────────────

# Suppress FastMCP's default logging to avoid polluting stderr with ANSI/RPC logs
# which causes strictly-parsed MCP clients (like LM Studio) to disconnect.
logging.getLogger("mcp").setLevel(logging.CRITICAL)

mcp = FastMCP("dwriter")
db = Database()


# ──────────────────────────────────────────────────────────────────────────────
# Journal Entry Tools
# ──────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def add_journal_entry(
    content: str,
    project: str = "",
    tags: str = "",
) -> str:
    """Log a new journal entry.

    Use this to record accomplishments, notes, meetings, or daily activities.

    Args:
        content: The text content of the entry.
        project: Optional project name for categorization.
        tags: Optional list of tags for labeling.
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    proj_val = project if project else None

    entry = await asyncio.to_thread(
        db.add_entry,
        content=content,
        project=proj_val,
        tags=tag_list,
        created_at=datetime.now()
    )
    return f"Successfully logged entry #{entry.id}: {entry.content}"


@mcp.tool()
async def get_journal_entries(
    days_back: int = 7,
    project: str = "",
    tags: str = "",
) -> str:
    """Retrieve journal entries, optionally filtered by project, tags, or time.

    Use this to review past work, generate standup summaries, or write PR descriptions.

    Args:
        days_back: Number of days to look back (default: 7. Use 0 for "today only").
        project: Filter by project name (e.g., "backend", "client-x").
        tags: Filter by tag names.
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    proj_val = project if project else None
    entries = await asyncio.to_thread(db.get_all_entries, project=proj_val, tags=tag_list)

    start_date = datetime.now() - timedelta(days=days_back)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    filtered_entries = [e for e in entries if e.created_at >= start_date]

    if not filtered_entries:
        return f"No entries found for the past {days_back} days matching the criteria."

    lines = [f"--- Journal Entries (Past {days_back} Days) ---"]
    for e in filtered_entries:
        time_str = e.created_at.strftime("%Y-%m-%d %H:%M")
        tag_str = f" [{', '.join(t.name for t in e.tags)}]" if e.tags else ""
        proj_str = f" &{e.project}" if e.project else ""
        lines.append(f"[{time_str}] #{e.id}: {e.content}{proj_str}{tag_str}")

    return "\n".join(lines)


@mcp.tool()
async def get_standup_report(with_todos: bool = True) -> str:
    """Generate a standup report based on yesterday's work and today's plan.

    Args:
        with_todos: Whether to include pending tasks for "Plan for Today".
    """
    yesterday = datetime.now() - timedelta(days=1)
    entries = await asyncio.to_thread(db.get_entries_by_date, date=yesterday)

    lines = [f"--- Standup Report ({yesterday.strftime('%Y-%m-%d')}) ---"]

    if not entries:
        lines.append("No entries logged for yesterday.")
    else:
        lines.append("Yesterday's Accomplishments:")
        for e in entries:
            time_str = e.created_at.strftime("%I:%M %p")
            proj_str = f" &{e.project}" if e.project else ""
            lines.append(f"- {time_str}: {e.content}{proj_str}")

    if with_todos:
        todos = await asyncio.to_thread(db.get_todos, status="pending")
        if todos:
            lines.append("\nPlan for Today:")
            for t in todos:
                proj_str = f" &{t.project}" if t.project else ""
                lines.append(f"- [ ] {t.content}{proj_str}")
        else:
            lines.append("\nPlan for Today:\n(No pending tasks)")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Todo Tools
# ──────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_todos(
    status: str = "pending",
    project: str = "",
    tags: str = "",
) -> str:
    """Retrieve tasks from the to-do list.

    Tasks are automatically sorted by priority (urgent > high > normal > low),
    then by due date urgency, then by creation date.

    Args:
        status: Filter by status ("pending" or "completed").
        project: Optional project name filter.
        tags: Optional tag name filter.
    """
    tasks = await asyncio.to_thread(db.get_todos, status=status)

    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    proj_val = project if project else None

    if proj_val:
        tasks = [t for t in tasks if t.project == proj_val]
    if tag_list:
        tasks = [t for t in tasks if any(tag in t.tag_names for tag in tag_list)]

    if not tasks:
        return f"No {status} tasks found matching the criteria."

    lines = [f"--- {status.capitalize()} Tasks ---"]
    for t in tasks:
        tag_str = f" [{', '.join(t.tag_names)}]" if t.tag_names else ""
        proj_str = f" &{t.project}" if t.project else ""
        due_str = f" Due: {t.due_date.strftime('%Y-%m-%d')}" if t.due_date else ""
        lines.append(
            f"ID: {t.id} | Priority: {t.priority} | "
            f"{t.content}{proj_str}{tag_str}{due_str}"
        )

    return "\n".join(lines)


@mcp.tool()
async def add_todo(
    content: str,
    priority: str = "normal",
    project: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
) -> str:
    """Add a new task to the to-do list.

    Args:
        content: The task description.
        priority: Priority level (low, normal, high, urgent).
        project: Optional project name.
        tags: Optional list of tags.
        due_date: Optional due date in YYYY-MM-DD format.
    """
    parsed_date = None
    if due_date:
        try:
            parsed_date = datetime.fromisoformat(due_date)
        except ValueError:
            return (
                f"Error: Invalid due_date format '{due_date}'. "
                "Please use YYYY-MM-DD."
            )

    task = await asyncio.to_thread(
        db.add_todo,
        content=content,
        priority=priority,
        project=project,
        tags=tags,
        due_date=parsed_date
    )
    return f"Added task #{task.id} to your to-do list with priority '{task.priority}'."


@mcp.tool()
async def update_todo(
    task_id: int,
    content: str = "",
    priority: str = "",
    project: str = "",
    tags: str = "",
    due_date: str = "",
) -> str:
    """Update an existing task's properties.

    Only provide the fields you want to change. Unspecified fields remain unchanged.

    Args:
        task_id: The ID of the task to update.
        content: New task description (optional).
        priority: New priority level (optional).
        project: New project name (optional).
        tags: New comma-separated list of tags (optional, replaces existing).
        due_date: New due date in YYYY-MM-DD format (optional).
    """
    try:
        await asyncio.to_thread(db.get_todo, todo_id=task_id)
    except ValueError as e:
        return f"Error: {e}"

    parsed_date = None
    if due_date:
        try:
            parsed_date = datetime.fromisoformat(due_date)
        except ValueError:
            return (
                f"Error: Invalid due_date format '{due_date}'. "
                "Please use YYYY-MM-DD."
            )

    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    content_val = content if content else None
    priority_val = priority if priority else None
    proj_val = project if project else None

    task = await asyncio.to_thread(
        db.update_todo,
        todo_id=task_id,
        content=content_val,
        priority=priority_val,
        project=proj_val,
        tags=tag_list,
        due_date=parsed_date
    )
    return f"Successfully updated task #{task.id}."


@mcp.tool()
async def complete_todo(task_id: int) -> str:
    """Mark a task as complete AND log it as a journal entry.

    This is a dual-action tool: it updates the task status to "completed"
    and automatically creates a journal entry to maintain accurate standup logs.

    Args:
        task_id: The ID of the task to complete.
    """
    try:
        task = await asyncio.to_thread(db.get_todo, todo_id=task_id)
    except ValueError as e:
        return f"Error: {e}"

    if task.status == "completed":
        return f"Task {task_id} is already completed."

    await asyncio.to_thread(
        db.update_todo,
        todo_id=task_id,
        status="completed",
        completed_at=datetime.now()
    )

    entry_content = f"Completed: {task.content}"
    entry = await asyncio.to_thread(
        db.add_entry,
        content=entry_content,
        tags=task.tag_names,
        project=task.project,
        created_at=datetime.now()
    )

    return (
        f"Successfully completed task #{task_id} and "
        f"logged it as journal entry #{entry.id}."
    )


@mcp.tool()
async def delete_todo(task_id: int) -> str:
    """Permanently delete a task from the to-do list.

    Use this when a task is no longer relevant or was added by mistake.

    Args:
        task_id: The ID of the task to delete.
    """
    try:
        await asyncio.to_thread(db.get_todo, todo_id=task_id)
    except ValueError as e:
        return f"Error: {e}"

    await asyncio.to_thread(db.delete_todo, todo_id=task_id)
    return f"Successfully deleted task #{task_id}."


# ──────────────────────────────────────────────────────────────────────────────
# Search and Analytics Tools
# ──────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_dwriter(
    query: str,
    search_type: str = "all",
    limit: int = 10,
) -> str:
    """Fuzzy search across journal entries and tasks.

    Args:
        query: The search term (typo-tolerant).
        search_type: Type of items to search ("all", "entry", "todo").
        limit: Maximum number of results.
    """
    results = []

    if search_type in ["all", "entry"]:
        entries = await asyncio.to_thread(db.get_all_entries)
        matched_entries = await asyncio.to_thread(
            search_items, query, entries, limit=limit
        )
        for e, score in matched_entries:
            results.append(f"[Entry #{e.id}] (Score: {int(score)}%) {e.content}")

    if search_type in ["all", "todo"]:
        todos = await asyncio.to_thread(db.get_all_todos)
        matched_todos = await asyncio.to_thread(
            search_items, query, todos, limit=limit
        )
        for t, score in matched_todos:
            results.append(f"[Todo #{t.id}] (Score: {int(score)}%) {t.content}")

    if not results:
        return f"No results found for '{query}'."

    return "\n".join(results)


@mcp.tool()
async def get_user_stats() -> str:
    """Get overall statistics about your dwriter activity.

    Includes total entries, streaks, project distribution, and tag usage.
    """
    total_entries = await asyncio.to_thread(db.get_all_entries_count)
    project_stats = await asyncio.to_thread(db.get_project_stats)
    tag_stats = await asyncio.to_thread(db.get_entries_with_tags_count)

    streak_dates = await asyncio.to_thread(db.get_entries_with_streaks)
    current_streak, longest_streak = calculate_streak(streak_dates)

    lines = ["--- dwriter Analytics ---"]
    lines.append(f"Total Entries: {total_entries}")
    lines.append(f"Current Streak: {current_streak} days")
    lines.append(f"Longest Streak: {longest_streak} days")

    if project_stats:
        lines.append("\nProject Activity:")
        for proj, count in project_stats.items():
            lines.append(f"- {proj}: {count} entries")

    if tag_stats:
        lines.append("\nTop Tags:")
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for tag, count in sorted_tags:
            lines.append(f"- {tag}: {count} uses")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
