"""Database layer for dwriter."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .database_entry_repo import EntryRepository
from .database_migrations import run_migrations
from .database_models import Base, Entry, SyncMetadata, Tag, Todo
from .database_todo_repo import TodoRepository

__all__ = [
    "Database",
    "Base",
    "Entry",
    "Tag",
    "Todo",
    "SyncMetadata",
]


class Database(EntryRepository, TodoRepository):
    """Manager for SQLite database operations.

    All write operations are funnelled through a single background worker
    thread to prevent SQLite locking under concurrent TUI + CLI access.
    """

    def __init__(self, db_path: Path | None = None):
        """Initialize database connection and schema."""
        if db_path is None:
            data_dir = Path.home() / ".dwriter"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "entries.db"

        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Base.metadata.create_all(self.engine)

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        run_migrations(self.engine, str(db_path))

        # Background write queue — prevents SQLite locking under Textual workers
        self._write_queue: queue.Queue[
            tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any], queue.Queue[Any]]
        ] = queue.Queue()
        self._worker_thread = threading.Thread(target=self._db_worker, daemon=True)
        self._worker_thread.start()

    # ------------------------------------------------------------------
    # Background writer
    # ------------------------------------------------------------------

    def _db_worker(self) -> None:
        """Background thread that serialises all DB write operations."""
        while True:
            item = self._write_queue.get()
            if item is None:
                break
            fn, args, kwargs, resp_queue = item
            try:
                result = fn(*args, **kwargs)
                resp_queue.put((result, None))
            except Exception as e:
                resp_queue.put((None, e))
            finally:
                self._write_queue.task_done()

    def _queued_write(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Enqueue a write and block until the background worker completes it."""
        resp_queue: queue.Queue[tuple[Any, Exception | None]] = queue.Queue()
        self._write_queue.put((fn, args, kwargs, resp_queue))
        result, error = resp_queue.get()
        if error:
            raise error
        return result

    def _get_next_lamport(self) -> int:
        """Increment and return the global Lamport clock stored in sync_metadata."""
        with self.Session() as session:
            stmt = select(SyncMetadata).where(SyncMetadata.key == "lamport_clock")
            meta = session.scalar(stmt)
            if not meta:
                meta = SyncMetadata(key="lamport_clock", value="0")
                session.add(meta)
            current = int(meta.value)
            next_val = current + 1
            meta.value = str(next_val)
            session.commit()
            return next_val

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def connection(self) -> Any:
        """Return a raw SQLite connection."""
        import sqlite3
        conn = sqlite3.connect(str(self.engine.url.database))
        conn.row_factory = sqlite3.Row
        return conn
