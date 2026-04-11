"""Background reminder coordinator for due urgent tasks."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import DWriterApp


class ReminderCoordinator:
    """Manages the recurring background reminder-check lifecycle.

    Runs a daemon threading.Timer that polls for urgent overdue tasks and
    surfaces them via OS desktop notification and Textual toast. All UI
    updates are dispatched through ``call_from_thread`` — safe to call from
    the background timer thread.

    Uses only thread-safe repository methods (``db.get_todos``,
    ``db.update_todo``) and never opens a raw SQLAlchemy session directly.
    """

    def __init__(self, app: DWriterApp) -> None:
        """Initialize the coordinator with a reference to the parent app."""
        self._app = app
        self._timer: threading.Timer | None = None

    def start(self, interval_seconds: int = 300) -> None:
        """Schedule a recurring background reminder check.

        Fires an immediate check, then re-arms itself every
        ``interval_seconds`` (default 5 min) using a daemon timer.

        Args:
            interval_seconds: How often to poll in seconds.
        """
        self._check()
        self._timer = threading.Timer(
            interval_seconds,
            self.start,
            kwargs={"interval_seconds": interval_seconds},
        )
        self._timer.daemon = True
        self._timer.start()

    def stop(self) -> None:
        """Cancel the background timer. Called on app unmount."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _check(self) -> None:
        """Check for due urgent tasks and surface them in-app and via OS.

        Safe to call from a background thread — all UI updates are dispatched
        through ``call_from_thread``.
        """
        from datetime import datetime, timedelta

        from ..ui_utils import send_system_notification

        try:
            now = datetime.now()
            todos = self._app.ctx.db.get_todos(status="pending")
            due_soon = [
                t
                for t in todos
                if t.priority == "urgent"
                and t.due_date is not None
                and t.due_date <= now + timedelta(minutes=30)
                and (
                    t.reminder_last_sent is None
                    or t.reminder_last_sent < now - timedelta(hours=1)
                )
            ]

            for task in due_soon:
                self._app.ctx.db.update_todo(task.id, reminder_last_sent=now)
                send_system_notification("dwriter Reminder", task.content)

                if task.due_date is not None:
                    if task.due_date.hour == 0 and task.due_date.minute == 0:
                        due_label = task.due_date.strftime("%Y-%m-%d")
                    else:
                        due_label = task.due_date.strftime("%H:%M")
                    msg = f"🔔 [{task.id}] {task.content} (Due: {due_label})"
                else:
                    msg = f"🔔 [{task.id}] {task.content}"

                self._app.call_from_thread(
                    self._app.notify, msg, severity="warning", timeout=8
                )
        except Exception:
            pass  # Never crash the TUI for a reminder failure
