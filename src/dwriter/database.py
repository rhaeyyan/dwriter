"""Database layer for dwriter."""

import json
import os
import queue
import shutil
import sys
import threading
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    case,
    create_engine,
    delete,
    event,
    func,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class Tag(Base):
    """Tag associated with a journal entry or a todo task."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("entries.id", ondelete="CASCADE"), nullable=True
    )
    todo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped["Entry | None"] = relationship(
        back_populates="tags", foreign_keys="[Tag.entry_id]"
    )
    todo: Mapped["Todo | None"] = relationship(
        back_populates="tags", foreign_keys="[Tag.todo_id]"
    )


class Entry(Base):
    """Journal entry model."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True)
    lamport_clock: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    todo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True
    )
    life_domain: Mapped[Optional[str]] = mapped_column(String)
    energy_level: Mapped[Optional[int]] = mapped_column(Integer)

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="entry",
        foreign_keys="[Tag.entry_id]",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Return tag names, using cache if available."""
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class Todo(Base):
    """Task model."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True)
    lamport_clock: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[Optional[str]] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="normal")
    status: Mapped[str] = mapped_column(String, default="pending")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    reminder_last_sent: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="todo",
        foreign_keys="[Tag.todo_id]",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Return tag names, using cache if available."""
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class SyncMetadata(Base):
    """Metadata for distributed synchronization."""

    __tablename__ = "sync_metadata"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)


class Database:
    """Manager for SQLite database operations.

    All write operations are funnelled through a single background worker
    thread to prevent SQLite locking under concurrent TUI + CLI access.
    """

    def __init__(self, db_path: Optional[Path] = None):
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
        self._migrate()

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
    # Migration
    # ------------------------------------------------------------------

    def _migrate(self) -> None:
        """Run schema migrations with backup/rollback safeguards."""
        db_path = str(self.engine.url.database)
        if not os.path.exists(db_path):
            return

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{db_path}.{timestamp}.bak"
        shutil.copy2(db_path, backup_path)

        try:
            with self.engine.connect():
                import sqlite3

                with sqlite3.connect(db_path) as conn:
                    # Ensure sync_metadata table exists
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS sync_metadata "
                        "(key TEXT PRIMARY KEY, value TEXT)"
                    )

                    # --- todos ---
                    cursor = conn.execute("PRAGMA table_info(todos)")
                    todo_cols = [row[1] for row in cursor.fetchall()]

                    if "uuid" not in todo_cols:
                        conn.execute("ALTER TABLE todos ADD COLUMN uuid TEXT")
                        cursor = conn.execute("SELECT id FROM todos WHERE uuid IS NULL")
                        for row in cursor.fetchall():
                            conn.execute(
                                "UPDATE todos SET uuid = ? WHERE id = ?",
                                (str(uuid.uuid4()), row[0]),
                            )

                    if "lamport_clock" not in todo_cols:
                        conn.execute(
                            "ALTER TABLE todos ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                        )

                    if "due_date" not in todo_cols:
                        conn.execute("ALTER TABLE todos ADD COLUMN due_date DATETIME")

                    if "reminder_last_sent" not in todo_cols:
                        conn.execute(
                            "ALTER TABLE todos ADD COLUMN reminder_last_sent DATETIME"
                        )

                    # --- entries ---
                    cursor = conn.execute("PRAGMA table_info(entries)")
                    entry_cols = [row[1] for row in cursor.fetchall()]

                    if "uuid" not in entry_cols:
                        conn.execute("ALTER TABLE entries ADD COLUMN uuid TEXT")
                        cursor = conn.execute(
                            "SELECT id FROM entries WHERE uuid IS NULL"
                        )
                        for row in cursor.fetchall():
                            conn.execute(
                                "UPDATE entries SET uuid = ? WHERE id = ?",
                                (str(uuid.uuid4()), row[0]),
                            )

                    if "lamport_clock" not in entry_cols:
                        conn.execute(
                            "ALTER TABLE entries ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                        )

                    if "todo_id" not in entry_cols:
                        conn.execute(
                            "ALTER TABLE entries ADD COLUMN todo_id "
                            "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                        )

                    if "life_domain" not in entry_cols:
                        conn.execute(
                            "ALTER TABLE entries ADD COLUMN life_domain STRING"
                        )

                    if "energy_level" not in entry_cols:
                        conn.execute(
                            "ALTER TABLE entries ADD COLUMN energy_level INTEGER"
                        )

                    # Tag Unification migration: merge todo_tags into tags
                    tag_cols = {
                        row[1]
                        for row in conn.execute("PRAGMA table_info(tags)").fetchall()
                    }
                    if "todo_id" not in tag_cols:
                        conn.execute(
                            "CREATE TABLE tags_new ("
                            "id INTEGER PRIMARY KEY, "
                            "entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE, "
                            "todo_id INTEGER REFERENCES todos(id) ON DELETE CASCADE, "
                            "name TEXT NOT NULL"
                            ")"
                        )
                        conn.execute(
                            "INSERT INTO tags_new (entry_id, name) "
                            "SELECT entry_id, name FROM tags"
                        )
                        if "todo_tags" in {
                            row[0]
                            for row in conn.execute(
                                "SELECT name FROM sqlite_master WHERE type='table'"
                            ).fetchall()
                        }:
                            conn.execute(
                                "INSERT INTO tags_new (todo_id, name) "
                                "SELECT todo_id, name FROM todo_tags"
                            )
                            conn.execute("DROP TABLE todo_tags")
                        conn.execute("DROP TABLE tags")
                        conn.execute("ALTER TABLE tags_new RENAME TO tags")
                        conn.execute(
                            "CREATE INDEX IF NOT EXISTS ix_tags_name ON tags (name)"
                        )
                        conn.execute(
                            "CREATE INDEX IF NOT EXISTS ix_tags_todo_id ON tags (todo_id)"
                        )

                    # Orphan cleanup
                    conn.execute(
                        "DELETE FROM tags "
                        "WHERE entry_id IS NOT NULL "
                        "AND entry_id NOT IN (SELECT id FROM entries)"
                    )
                    conn.execute(
                        "DELETE FROM tags "
                        "WHERE todo_id IS NOT NULL "
                        "AND todo_id NOT IN (SELECT id FROM todos)"
                    )

                    conn.commit()

        except Exception as e:
            shutil.copy2(backup_path, db_path)
            console = Console()
            console.print(f"[bold red]FATAL DATABASE ERROR:[/bold red] Migration failed. {e}")
            console.print("[yellow]Database has been rolled back from backup.[/yellow]")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def connection(self) -> Any:
        """Return a raw SQLite connection."""
        import sqlite3
        conn = sqlite3.connect(str(self.engine.url.database))
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Entry CRUD
    # ------------------------------------------------------------------

    def add_entry(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
        todo_id: Optional[int] = None,
        life_domain: Optional[str] = None,
        energy_level: Optional[int] = None,
    ) -> "Entry":
        """Add a new journal entry."""
        return self._queued_write(
            self._add_entry_sync,
            content,
            tags=tags,
            project=project,
            created_at=created_at,
            todo_id=todo_id,
            life_domain=life_domain,
            energy_level=energy_level,
        )

    def _add_entry_sync(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
        todo_id: Optional[int] = None,
        life_domain: Optional[str] = None,
        energy_level: Optional[int] = None,
    ) -> "Entry":
        next_clock = self._get_next_lamport()
        with self.Session() as session:
            entry = Entry(
                uuid=str(uuid.uuid4()),
                lamport_clock=next_clock,
                content=content,
                project=project,
                todo_id=todo_id,
                life_domain=life_domain,
                energy_level=energy_level,
            )
            if tags:
                for tag_name in tags:
                    entry.tags.append(Tag(name=tag_name))
            entry.created_at = created_at or datetime.now()
            session.add(entry)
            session.commit()
            session.refresh(entry)
            entry._tag_names_cache = list(tags) if tags else []
            return entry

    def get_entry(self, entry_id: int) -> "Entry":
        """Retrieve a single entry by ID."""
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry

    def get_entries_by_date(self, date: datetime) -> list["Entry"]:
        """Retrieve all entries for a specific date."""
        with self.Session() as session:
            date_str = date.strftime("%Y-%m-%d")
            stmt = (
                select(Entry)
                .where(func.date(Entry.created_at) == date_str)
                .order_by(Entry.created_at)
            )
            return list(session.scalars(stmt).all())

    def get_entries_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        exclude_projects: Optional[list[str]] = None,
        exclude_tags: Optional[list[str]] = None,
    ) -> list["Entry"]:
        """Retrieve entries within a date range with optional exclusion filters."""
        with self.Session() as session:
            stmt = select(Entry).where(Entry.created_at.between(start_date, end_date))

            if exclude_projects:
                from sqlalchemy import not_, or_

                prefix_excludes = [p.lower() for p in exclude_projects if p.endswith(":")]
                exact_excludes = [p.lower() for p in exclude_projects if not p.endswith(":")]
                conditions = []
                if exact_excludes:
                    conditions.append(func.lower(Entry.project).in_(exact_excludes))
                for prefix in prefix_excludes:
                    conditions.append(func.lower(Entry.project).like(f"{prefix}%"))
                if conditions:
                    stmt = stmt.where(
                        or_(Entry.project.is_(None), not_(or_(*conditions)))
                    )

            if exclude_tags:
                from sqlalchemy import not_

                exclude_tags_lower = [t.lower() for t in exclude_tags]
                stmt = stmt.where(
                    not_(Entry.tags.any(func.lower(Tag.name).in_(exclude_tags_lower)))
                )

            stmt = stmt.order_by(Entry.created_at)
            return list(session.scalars(stmt).all())

    def get_latest_entry(self) -> Optional["Entry"]:
        """Retrieve the most recent entry."""
        with self.Session() as session:
            return session.scalars(
                select(Entry).order_by(Entry.created_at.desc()).limit(1)
            ).first()

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID."""
        return self._queued_write(self._delete_entry_sync, entry_id)

    def _delete_entry_sync(self, entry_id: int) -> bool:
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Delete entry linked to a todo ID."""
        self._queued_write(self._delete_entry_by_todo_id_sync, todo_id)

    def _delete_entry_by_todo_id_sync(self, todo_id: int) -> None:
        with self.Session() as session:
            session.query(Entry).filter(Entry.todo_id == todo_id).delete(
                synchronize_session=False
            )
            session.commit()

    def update_entry(
        self,
        entry_id: int,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> "Entry":
        """Update an existing entry."""
        return self._queued_write(
            self._update_entry_sync,
            entry_id,
            content=content,
            tags=tags,
            project=project,
            created_at=created_at,
        )

    def _update_entry_sync(
        self,
        entry_id: int,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> "Entry":
        next_clock = self._get_next_lamport()
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry {entry_id} not found")
            entry.lamport_clock = next_clock
            if content is not None:
                entry.content = content
            if project is not None:
                entry.project = project
            if tags is not None:
                entry.tags = [Tag(name=t) for t in tags]
            if created_at is not None:
                entry.created_at = created_at
            session.commit()
            session.refresh(entry)
            return entry

    def delete_entries_before(self, before_date: datetime) -> int:
        """Delete all entries before a specific date."""
        return self._queued_write(self._delete_entries_before_sync, before_date)

    def _delete_entries_before_sync(self, before_date: datetime) -> int:
        with self.Session() as session:
            stmt = delete(Entry).where(Entry.created_at < before_date)
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount) if result.rowcount is not None else 0  # type: ignore[attr-defined]

    def get_all_entries_count(self) -> int:
        """Get the total count of all entries."""
        with self.Session() as session:
            return session.scalar(select(func.count(Entry.id))) or 0

    def get_entries_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list["Entry"]:
        """Retrieve a page of entries, optionally filtered."""
        with self.Session() as session:
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            stmt = stmt.limit(limit).offset(offset)
            return list(session.scalars(stmt).all())

    def get_entries_with_streaks(self) -> list[datetime]:
        """Get unique dates with entries."""
        with self.Session() as session:
            stmt = (
                select(func.distinct(func.date(Entry.created_at)))
                .order_by(Entry.created_at.desc())
            )
            result = session.execute(stmt).all()
            return [datetime.strptime(row[0], "%Y-%m-%d") for row in result if row[0]]

    def get_project_stats(self) -> dict[str, int]:
        """Get entry counts grouped by project."""
        with self.Session() as session:
            stmt = (
                select(Entry.project, func.count(Entry.id))
                .group_by(Entry.project)
                .order_by(func.count(Entry.id).desc())
            )
            results = session.execute(stmt).all()
            return {project: count for project, count in results if project}

    def get_entries_count_by_date(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, int]:
        """Get entry counts grouped by date."""
        with self.Session() as session:
            stmt = (
                select(func.date(Entry.created_at), func.count(Entry.id))
                .where(Entry.created_at.between(start_date, end_date))
                .group_by(func.date(Entry.created_at))
                .order_by(func.date(Entry.created_at).desc())
            )
            results = session.execute(stmt).all()
            return {str(date): count for date, count in results if date}

    def get_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get the date range of all entries."""
        with self.Session() as session:
            stmt = select(func.min(Entry.created_at), func.max(Entry.created_at))
            result = session.execute(stmt).first()
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None, None

    def get_all_entries(
        self,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list["Entry"]:
        """Retrieve all entries, optionally filtered."""
        with self.Session() as session:
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def get_unique_projects(self) -> list[str]:
        """Retrieve a list of all unique project names."""
        with self.Session() as session:
            stmt = (
                select(func.distinct(Entry.project))
                .where(Entry.project.isnot(None))
                .order_by(Entry.project)
            )
            return list(session.scalars(stmt).all())

    def get_unique_tags(self) -> list[str]:
        """Retrieve a list of all unique tag names."""
        with self.Session() as session:
            stmt = select(func.distinct(Tag.name)).order_by(Tag.name)
            return list(session.scalars(stmt).all())

    def get_entries_with_tags_count(self) -> dict[str, int]:
        """Get entry counts grouped by tag."""
        with self.Session() as session:
            stmt = (
                select(Tag.name, func.count(Tag.id))
                .group_by(Tag.name)
                .order_by(func.count(Tag.id).desc())
            )
            results = session.execute(stmt).all()
            return {row[0]: row[1] for row in results}

    # ------------------------------------------------------------------
    # Todo CRUD
    # ------------------------------------------------------------------

    def add_todo(
        self,
        content: str,
        priority: str = "normal",
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
    ) -> "Todo":
        """Add a new task."""
        return self._queued_write(
            self._add_todo_sync,
            content,
            priority=priority,
            project=project,
            tags=tags,
            due_date=due_date,
        )

    def _add_todo_sync(
        self,
        content: str,
        priority: str = "normal",
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
    ) -> "Todo":
        next_clock = self._get_next_lamport()
        with self.Session() as session:
            todo = Todo(
                uuid=str(uuid.uuid4()),
                lamport_clock=next_clock,
                content=content,
                priority=priority,
                project=project,
                due_date=due_date,
            )
            if tags:
                for tag_name in tags:
                    todo.tags.append(Tag(name=tag_name))
            session.add(todo)
            session.commit()
            session.refresh(todo)
            todo._tag_names_cache = list(tags) if tags else []
            return todo

    def get_todo(self, todo_id: int) -> "Todo":
        """Retrieve a single todo by ID."""
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: Optional[str] = "pending") -> list["Todo"]:
        """Retrieve tasks, ordered by priority and urgency."""
        with self.Session() as session:
            stmt = select(Todo)
            if status:
                stmt = stmt.where(Todo.status == status)

            priority_order = case(
                (Todo.priority == "urgent", 1),
                (Todo.priority == "high", 2),
                (Todo.priority == "normal", 3),
                (Todo.priority == "low", 4),
                else_=5,
            )

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            due_date_order = case(
                (Todo.due_date < today, 0),
                (Todo.due_date == today, 1),
                (Todo.due_date == tomorrow, 2),
                else_=3,
            )

            stmt = stmt.order_by(priority_order, due_date_order, Todo.created_at.desc())
            return list(session.scalars(stmt).all())

    def update_todo(
        self,
        todo_id: int,
        content: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        completed_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        reminder_last_sent: Optional[datetime] = None,
    ) -> "Todo":
        """Update an existing task."""
        return self._queued_write(
            self._update_todo_sync,
            todo_id,
            content=content,
            status=status,
            priority=priority,
            project=project,
            tags=tags,
            completed_at=completed_at,
            due_date=due_date,
            reminder_last_sent=reminder_last_sent,
        )

    def _update_todo_sync(
        self,
        todo_id: int,
        content: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        completed_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        reminder_last_sent: Optional[datetime] = None,
    ) -> "Todo":
        next_clock = self._get_next_lamport()
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo {todo_id} not found")
            todo.lamport_clock = next_clock
            if content is not None:
                todo.content = content
            if status is not None:
                todo.status = status
            if priority is not None:
                todo.priority = priority
            if project is not None:
                todo.project = project
            if completed_at is not None:
                todo.completed_at = completed_at
            if due_date is not None:
                todo.due_date = due_date
            if reminder_last_sent is not None:
                todo.reminder_last_sent = reminder_last_sent
            if tags is not None:
                todo.tags = [Tag(name=t) for t in tags]
            session.commit()
            session.refresh(todo)
            return todo

    def get_reminders(
        self, due_before: datetime, reminded_since: datetime
    ) -> list["Todo"]:
        """Query for urgent tasks that need a reminder alert."""
        with self.Session() as session:
            stmt = (
                select(Todo)
                .where(Todo.status == "pending")
                .where(Todo.priority == "urgent")
                .where(Todo.due_date <= due_before)
                .where(
                    (Todo.reminder_last_sent == None)  # noqa: E711
                    | (Todo.reminder_last_sent < reminded_since)
                )
            )
            return list(session.scalars(stmt).all())

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a task by ID."""
        return self._queued_write(self._delete_todo_sync, todo_id)

    def _delete_todo_sync(self, todo_id: int) -> bool:
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if todo:
                session.delete(todo)
                session.commit()
                return True
            return False

    def get_all_todos(
        self,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list["Todo"]:
        """Retrieve all todos, optionally filtered."""
        with self.Session() as session:
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(Tag, Tag.todo_id == Todo.id).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())
