"""Sync coordinator — debounced push and background pull scheduling.

Owned by the Infrastructure Engineer. Manages all traffic between the TUI
and the sync daemon, including debounce timing and background worker dispatch.
The TUI app holds an instance of this class and delegates sync calls to it.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tui.app import DWriterApp


class SyncCoordinator:
    """Manages background sync lifecycle: pull on startup, debounced push on writes.

    Debounce window: 10 seconds. Any write event within that window resets the
    timer, coalescing rapid successive writes into a single push.
    """

    def __init__(self, app: DWriterApp) -> None:
        """Initialize the coordinator with a reference to the parent app."""
        self._app = app
        self._debounce_timer: threading.Timer | None = None

    def trigger_pull(self) -> None:
        """Dispatch a non-blocking background pull sync."""
        from datetime import datetime

        from .daemon import pull_sync
        from ..tui.messages import EntryAdded, SyncStatus, TodoUpdated

        async def pull_sync_worker() -> None:
            self._app.post_message(SyncStatus(is_syncing=True, message="Syncing..."))
            merged = await self._app.run_worker(
                lambda: pull_sync(self._app.ctx.db), thread=True
            ).wait()
            if merged:
                self._app.post_message(
                    EntryAdded(entry_id=0, content="", created_at=datetime.now())
                )
                self._app.post_message(TodoUpdated(todo_id=0, action="updated"))
            self._app.post_message(SyncStatus(is_syncing=False, message="Synced"))

        self._app.run_worker(pull_sync_worker())

    def trigger_push_debounced(self) -> None:
        """Schedule a debounced background sync push.

        Resets the 10-second debounce window on every call, so rapid writes
        coalesce into a single push rather than flooding the remote.
        """
        if not self._app.ctx.config.defaults.auto_sync:
            return

        if self._debounce_timer is not None:
            self._debounce_timer.cancel()

        self._debounce_timer = threading.Timer(10.0, self._run_push)
        self._debounce_timer.daemon = True
        self._debounce_timer.start()

    def _run_push(self) -> None:
        """Execute the push sync worker through the Textual event loop.

        Called from the debounce timer thread; uses ``call_from_thread`` to
        safely schedule the coroutine on the Textual event loop.
        """
        from .daemon import push_sync
        from ..tui.messages import SyncStatus

        async def push_sync_worker() -> None:
            self._app.post_message(SyncStatus(is_syncing=True, message="Syncing..."))
            success = await self._app.run_worker(
                lambda: push_sync(self._app.ctx.db), thread=True
            ).wait()
            status = "Synced" if success else "Sync Failed"
            self._app.post_message(SyncStatus(is_syncing=False, message=status))

        self._app.call_from_thread(self._app.run_worker, push_sync_worker())
