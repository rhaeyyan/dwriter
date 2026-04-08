"""Message classes for TUI event bus.

This module defines custom Textual Message classes used for communication
between components in the unified TUI architecture.
"""

from __future__ import annotations

from datetime import datetime

from textual.message import Message


class EntryAdded(Message):
    """Dispatched when a new journal entry is created via the Omnibox.

    This message is posted by the master app when the omnibox input is
    submitted, allowing screens like Dashboard and Search to reactively
    update their displays.

    Attributes:
        entry_id: The database ID of the newly created entry.
        content: The content text of the entry.
        created_at: The datetime when the entry was created.
    """

    def __init__(self, entry_id: int, content: str, created_at: datetime) -> None:
        """Initialize the EntryAdded message.

        Args:
            entry_id: The database ID of the newly created entry.
            content: The content text of the entry.
            created_at: The datetime when the entry was created.
        """
        super().__init__()
        self.entry_id = entry_id
        self.content = content
        self.created_at = created_at


class TodoUpdated(Message):
    """Dispatched when a todo is modified, completed, or deleted.

    This message is posted when todo operations complete, allowing
    screens like TodoScreen and Dashboard to reactively update.

    Attributes:
        todo_id: The database ID of the affected todo.
        action: The action performed: "completed", "deleted", "updated", or "added".
    """

    def __init__(self, todo_id: int, action: str) -> None:
        """Initialize the TodoUpdated message.

        Args:
            todo_id: The database ID of the affected todo.
            action: The action performed: "completed", "deleted", "updated", or "added".
        """
        super().__init__()
        self.todo_id = todo_id
        self.action = action


class TimerStateChanged(Message):
    """Dispatched when the timer state changes (start/stop/complete).

    This message is posted when the timer state changes, allowing
    the app to update the timer tab styling.

    Attributes:
        is_running: Whether the timer is currently running.
        remaining_seconds: Remaining seconds on the timer.
    """

    def __init__(self, is_running: bool, remaining_seconds: int = 0) -> None:
        """Initialize the TimerStateChanged message.

        Args:
            is_running: Whether the timer is currently running.
            remaining_seconds: Remaining seconds on the timer.
        """
        super().__init__()
        self.is_running = is_running
        self.remaining_seconds = remaining_seconds


class SemanticRecommendationReady(Message):
    """Dispatched when proactive AI recommendations are available for an entry.

    Attributes:
        entry_id: The database ID of the entry.
        project: Recommended project name (starting with &).
        tags: Recommended hashtags (starting with #).
    """

    def __init__(self, entry_id: int, project: str | None, tags: list[str]) -> None:
        super().__init__()
        self.entry_id = entry_id
        self.project = project
        self.tags = tags


class SyncStatus(Message):
    """Dispatched when background sync status changes.

    Attributes:
        is_syncing: Whether a sync operation is currently in progress.
        message: A short status message (e.g., "Synced", "Syncing...", "Sync Failed").
    """

    def __init__(self, is_syncing: bool, message: str) -> None:
        super().__init__()
        self.is_syncing = is_syncing
        self.message = message
