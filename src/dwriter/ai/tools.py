"""Internal tools for the AI Agentic 2nd-Brain.

This module provides read-only tools that the AI can call to search
the local journal, todos, and git context.
"""

import json
import subprocess
from datetime import datetime, time, timedelta
from typing import Any

from ..database import Database, Entry, Todo
from ..search_utils import search_items


def get_daily_standup(date_str: str | None = None, project: str | None = None) -> str:
    """Generates a formatted Daily Standup report for a specific date.

    Args:
        date_str (str | None): The date in YYYY-MM-DD format. Defaults to yesterday.
        project (str | None): Optional project filter (&name).

    Returns:
        str: A formatted Markdown report.
    """
    try:
        db = Database()
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            target_date = datetime.now() - timedelta(days=1)

        start_date = datetime.combine(target_date.date(), time.min)
        end_date = datetime.combine(target_date.date(), time.max)

        # We use a simple version of report generation here for the AI to consume
        entries = db.get_entries_in_range(start_date, end_date, exclude_projects=[project] if project else None)

        # Filter for the specific project if provided
        if project:
            entries = [e for e in entries if e.project == project.lstrip("&")]

        lines = [f"### Standup: {target_date.strftime('%Y-%m-%d')}"]

        lines.append("\n**What was done:**")
        if not entries:
            lines.append("- No entries logged.")
        else:
            for e in entries:
                p_str = f" &{e.project}" if e.project else ""
                t_str = f" {' '.join(f'#{t}' for t in e.tag_names)}" if e.tag_names else ""
                clean_content = e.content.lstrip("✅⏱️ ")
                lines.append(f"- {clean_content}{p_str}{t_str}")

        # Add plan (pending todos due today/tomorrow)
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        pending_todos = [
            t for t in db.get_all_todos()
            if t.status == "pending" and t.due_date and (t.due_date.date() == today or t.due_date.date() == tomorrow)
        ]

        if project:
            pending_todos = [t for t in pending_todos if t.project == project.lstrip("&")]

        lines.append("\n**Plan for today:**")
        if not pending_todos:
            lines.append("- Clear schedule.")
        else:
            for t in pending_todos:
                clean_content = t.content.lstrip("✅⏱️ ")
                lines.append(f"- [ ] {clean_content}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error generating standup: {str(e)}"


def entry_to_dict(entry: Entry) -> dict[str, Any]:
    """Converts an Entry model to a serializable dictionary."""
    return {
        "id": entry.id,
        "uuid": entry.uuid,
        "content": entry.content,
        "project": entry.project,
        "tags": entry.tag_names,
        "created_at": entry.created_at.isoformat(),
        "implicit_mood": entry.implicit_mood,
        "life_domain": entry.life_domain,
        "energy_level": entry.energy_level,
    }


def todo_to_dict(todo: Todo) -> dict[str, Any]:
    """Converts a Todo model to a serializable dictionary."""
    return {
        "id": todo.id,
        "uuid": todo.uuid,
        "content": todo.content,
        "project": todo.project,
        "priority": todo.priority,
        "status": todo.status,
        "tags": todo.tag_names,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "created_at": todo.created_at.isoformat(),
        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
    }


def search_journal(query: str, project: str | None = None) -> str:
    """Searches the user's journal entries and time logs.

    Use this to find what the user has worked on, their thoughts, or past notes.
    """
    try:
        db = Database()
        entries = db.get_all_entries(project=project)

        # Use fuzzy search from search_utils
        matches = search_items(query, entries, limit=10)

        if not matches:
            return "No matching journal entries found."

        results = [entry_to_dict(m[0]) for m in matches]
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching journal: {str(e)}"


def search_todos(query: str, project: str | None = None) -> str:
    """Searches the user's tasks and todo items.

    Use this to find specific tasks, their status, or deadlines.
    """
    try:
        db = Database()
        todos = db.get_all_todos(project=project)

        # Use fuzzy search from search_utils
        matches = search_items(query, todos, limit=10)

        if not matches:
            return "No matching todos found."

        results = [todo_to_dict(m[0]) for m in matches]
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching todos: {str(e)}"


def fetch_recent_commits(limit: int = 10) -> str:
    """Fetches recent git commit messages from the current git repository.

    Use this to see the actual code changes the user has made recently.
    """
    try:
        from ..git_utils import get_git_info

        git_info = get_git_info()
        if not git_info:
            return (
                "Error: Current directory is not a valid git repository "
                "or git is not installed."
            )

        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h - %s (%cr)"],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_info["toplevel"],
        )
        return result.stdout if result.stdout else "No commits found."
    except subprocess.CalledProcessError:
        return (
            "Error: Current directory is not a valid git repository "
            "or git is not installed."
        )
    except Exception as e:
        return f"Error fetching commits: {str(e)}"
