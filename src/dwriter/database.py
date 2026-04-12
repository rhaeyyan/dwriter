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
from .database_models import Base, Entry, Summary, SyncMetadata, Tag, Todo
from .database_todo_repo import TodoSummaryRepository

# Re-export models for backwards compatibility
__all__ = ["Base", "Tag", "Entry", "Todo", "Summary", "SyncMetadata", "Database"]


class Database(EntryRepository, TodoSummaryRepository):
    """Manager for SQLite database operations.

    Handles initialization, migrations, and CRUD operations for entries, todos,
    tags, and AI summaries.

    All write operations are funneled through a single background worker thread
    to prevent SQLite locking and ensure thread-safety for async consumers.
    """

    def __init__(self, db_path: Path | None = None):
        """Initializes the database connection and ensures schema creation.

        Sets up the SQLAlchemy engine with optimized SQLite settings (WAL mode,
        foreign keys enabled).

        Args:
            db_path (Path | None): Custom path to the SQLite database file.
                Defaults to ~/.dwriter/entries.db if None.
        """
        if db_path is None:
            data_dir = Path.home() / ".dwriter"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "entries.db"

        # Use NullPool for CLI/TUI to avoid session issues with Textual threads
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

        # Initialize background writer queue and thread
        self._write_queue: queue.Queue[
            tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any], queue.Queue[Any]]
        ] = queue.Queue()
        self._worker_thread = threading.Thread(target=self._db_worker, daemon=True)
        self._worker_thread.start()

    def _db_worker(self) -> None:
        """Background thread that executes all database write operations."""
        while True:
            item = self._write_queue.get()
            if item is None:
                break

            func, args, kwargs, resp_queue = item
            try:
                result = func(*args, **kwargs)
                resp_queue.put((result, None))
            except Exception as e:
                resp_queue.put((None, e))
            finally:
                self._write_queue.task_done()

    def _queued_write(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Enqueues a write operation and waits for the result.

        This maintains a synchronous interface for the caller while ensuring
        the actual write happens in the background thread.
        """
        resp_queue: queue.Queue[tuple[Any, Exception | None]] = queue.Queue()
        self._write_queue.put((func, args, kwargs, resp_queue))
        result, error = resp_queue.get()
        if error:
            raise error
        return result

    def _get_next_lamport(self) -> int:
        """Increments and returns the global Lamport clock."""
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

    def connection(self) -> Any:
        """Provides a raw SQLite connection for low-level operations.

        Returns:
            Any: A standard sqlite3.Connection object with Row factory enabled.
        """
        import sqlite3

        conn = sqlite3.connect(str(self.engine.url.database))
        conn.row_factory = sqlite3.Row
        return conn
