"""Internal tools for the AI Agentic 2nd-Brain.

This module provides read-only tools that the AI can call to search
the local journal, todos, and git context.
"""

import json
import subprocess
from typing import Any

from ..database import Database, Entry, Todo
from ..search_utils import search_items


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
    """Fetches recent git commit messages from the current working directory.

    Use this to see the actual code changes the user has made recently.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h - %s (%cr)"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout if result.stdout else "No commits found."
    except subprocess.CalledProcessError:
        return (
            "Error: Current directory is not a valid git repository "
            "or git is not installed."
        )
    except Exception as e:
        return f"Error fetching commits: {str(e)}"
