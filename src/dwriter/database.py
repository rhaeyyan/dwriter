"""Database layer for dwriter."""

import json
import os
import queue
import shutil
import sys
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
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
    """Base class for all SQLAlchemy models in the application.

    Inherits from DeclarativeBase to provide a foundation for model definitions.
    """

    pass


class Tag(Base):
    """Represents a tag associated with a journal entry.

    Attributes:
        id (int): Unique identifier for the tag.
        entry_id (int): Foreign key referencing the associated journal entry.
        name (str): The string name of the tag, indexed for faster retrieval.
        entry (Entry): Relationship mapping back to the associated Entry object.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped["Entry"] = relationship(back_populates="tags")


class Entry(Base):
    """Represents a discrete journal entry in the database.

    Attributes:
        id (int): Primary key for the entry.
        uuid (str): Unique identifier for synchronization.
        lamport_clock (int): Logical clock for conflict resolution.
        content (str): The textual content of the journal entry.
        project (str | None): Optional project name associated with the entry.
        created_at (datetime): Timestamp when the entry was created.
        updated_at (datetime): Timestamp when the entry was last modified.
        todo_id (int | None): Optional link to a related todo task.
        tags (list[Tag]): Collection of tags associated with this entry.
        implicit_mood (str | None): Inferred emotional tone of the entry.
        life_domain (str | None): Categorization of the entry (e.g., Health, Career).
        energy_level (int | None): Inferred energy level (1-10).
        embedding (bytes | None): Vector embedding of the entry content.
    """

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True)
    lamport_clock: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    todo_id: Mapped[int | None] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True
    )

    implicit_mood: Mapped[str | None] = mapped_column(String)
    life_domain: Mapped[str | None] = mapped_column(String)
    energy_level: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary)

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="entry",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Retrieves the list of tag names associated with this entry.

        Returns:
            list[str]: A list of tag names.
        """
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class TodoTag(Base):
    """Represents a tag specifically associated with a todo task.

    Attributes:
        id (int): Unique identifier for the todo tag.
        todo_id (int): Foreign key referencing the associated todo task.
        name (str): The name of the tag, indexed for searching.
        todo (Todo): Relationship mapping back to the associated Todo object.
    """

    __tablename__ = "todo_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    todo: Mapped["Todo"] = relationship(back_populates="tags")


class Todo(Base):
    """Represents a task or todo item.

    Attributes:
        id (int): Primary key for the todo task.
        uuid (str): Unique identifier for synchronization.
        lamport_clock (int): Logical clock for conflict resolution.
        content (str): Description of the task.
        project (str | None): Optional project identifier.
        priority (str): Urgency level (e.g., 'urgent', 'high', 'normal', 'low').
        status (str): Task completion status (e.g., 'pending', 'completed').
        due_date (datetime | None): Optional deadline for the task.
        reminder_last_sent (datetime | None): Timestamp of the last reminder notification.
        created_at (datetime): Creation timestamp.
        completed_at (datetime | None): Completion timestamp.
        tags (list[TodoTag]): Collection of tags for this task.
    """

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True)
    lamport_clock: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[str | None] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="normal")
    status: Mapped[str] = mapped_column(String, default="pending")
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    reminder_last_sent: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    tags: Mapped[list["TodoTag"]] = relationship(
        back_populates="todo",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Retrieves the list of tag names associated with this todo task.

        Returns:
            list[str]: A list of tag names.
        """
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class Summary(Base):
    """Represents an AI-generated activity summary for long-term memory.

    Attributes:
        id (int): Primary key for the summary.
        content (str): The summarized data, typically stored as JSON.
        period_start (datetime): The start date of the summarized period.
        period_end (datetime): The end date of the summarized period.
        summary_type (str): Category of summary (e.g., 'weekly').
        created_at (datetime): Timestamp when the summary was generated.
    """

    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    period_start: Mapped[datetime] = mapped_column(DateTime, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, index=True)
    summary_type: Mapped[str] = mapped_column(String, default="weekly")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class SyncMetadata(Base):
    """Metadata for distributed synchronization.

    Attributes:
        key (str): Configuration key (e.g., 'device_id', 'lamport_clock').
        value (str): Configuration value.
    """

    __tablename__ = "sync_metadata"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)


class Database:
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
        self._migrate()

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

    def _migrate(self) -> None:
        """Executes manual schema migrations to maintain database compatibility.

        Checks for missing columns and applies ALTER TABLE statements as needed.
        Also performs maintenance tasks like cleaning up orphaned tags.

        Includes automated backup and rollback safeguards to prevent journal
        corruption during failed migrations.
        """
        db_path = str(self.engine.url.database)
        if not os.path.exists(db_path):
            return

        # Create a timestamped backup before migration
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{db_path}.{timestamp}.bak"
        shutil.copy2(db_path, backup_path)

        try:
            with self.engine.connect():
                import sqlite3

                with sqlite3.connect(db_path) as sqlite_conn:
                    # SyncMetadata table
                    sqlite_conn.execute(
                        "CREATE TABLE IF NOT EXISTS sync_metadata "
                        "(key TEXT PRIMARY KEY, value TEXT)"
                    )

                    cursor = sqlite_conn.execute("PRAGMA table_info(todos)")
                    columns = [row[1] for row in cursor.fetchall()]

                    if "uuid" not in columns:
                        sqlite_conn.execute("ALTER TABLE todos ADD COLUMN uuid TEXT")
                        # Initialize existing records with UUIDs
                        cursor = sqlite_conn.execute(
                            "SELECT id FROM todos WHERE uuid IS NULL"
                        )
                        for row in cursor.fetchall():
                            sqlite_conn.execute(
                                "UPDATE todos SET uuid = ? WHERE id = ?",
                                (str(uuid.uuid4()), row[0]),
                            )

                    if "lamport_clock" not in columns:
                        sqlite_conn.execute(
                            "ALTER TABLE todos ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                        )

                    if "due_date" not in columns:
                        sqlite_conn.execute(
                            "ALTER TABLE todos ADD COLUMN due_date DATETIME"
                        )

                    if "reminder_last_sent" not in columns:
                        sqlite_conn.execute(
                            "ALTER TABLE todos ADD COLUMN reminder_last_sent DATETIME"
                        )

                    cursor = sqlite_conn.execute("PRAGMA table_info(entries)")
                    entry_columns = [row[1] for row in cursor.fetchall()]

                    if "uuid" not in entry_columns:
                        sqlite_conn.execute("ALTER TABLE entries ADD COLUMN uuid TEXT")
                        # Initialize existing records with UUIDs
                        cursor = sqlite_conn.execute(
                            "SELECT id FROM entries WHERE uuid IS NULL"
                        )
                        for row in cursor.fetchall():
                            sqlite_conn.execute(
                                "UPDATE entries SET uuid = ? WHERE id = ?",
                                (str(uuid.uuid4()), row[0]),
                            )

                    if "lamport_clock" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                        )

                    if "todo_id" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN todo_id "
                            "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                        )

                    if "implicit_mood" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN implicit_mood STRING"
                        )

                    if "life_domain" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN life_domain STRING"
                        )

                    if "energy_level" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN energy_level INTEGER"
                        )

                    if "embedding" not in entry_columns:
                        sqlite_conn.execute(
                            "ALTER TABLE entries ADD COLUMN embedding LARGEBINARY"
                        )

                    # Clean up orphaned tags
                    sqlite_conn.execute(
                        "DELETE FROM tags WHERE entry_id NOT IN (SELECT id FROM entries)"
                    )
                    sqlite_conn.execute(
                        "DELETE FROM todo_tags WHERE todo_id NOT IN (SELECT id FROM todos)"
                    )

                    sqlite_conn.commit()

            # If successful, we could remove the backup, but keeping it for a short time is safer.
        except Exception as e:
            # Restore the backup on failure
            shutil.copy2(backup_path, db_path)
            console = Console()
            console.print(
                f"[bold red]FATAL DATABASE ERROR:[/bold red] Migration failed. {e}"
            )
            console.print("[yellow]Database has been rolled back from backup.[/yellow]")
            sys.exit(1)

    def connection(self) -> Any:
        """Provides a raw SQLite connection for low-level operations.

        Returns:
            Any: A standard sqlite3.Connection object with Row factory enabled.
        """
        import sqlite3

        conn = sqlite3.connect(str(self.engine.url.database))
        conn.row_factory = sqlite3.Row
        return conn

    def add_entry(
        self,
        content: str,
        tags: list[str] | None = None,
        project: str | None = None,
        created_at: datetime | None = None,
        todo_id: int | None = None,
        implicit_mood: str | None = None,
        life_domain: str | None = None,
        energy_level: int | None = None,
        embedding: list[float] | None = None,
    ) -> Entry:
        """Persists a new journal entry to the database."""
        return self._queued_write(
            self._add_entry_sync,
            content,
            tags=tags,
            project=project,
            created_at=created_at,
            todo_id=todo_id,
            implicit_mood=implicit_mood,
            life_domain=life_domain,
            energy_level=energy_level,
            embedding=embedding,
        )

    def _add_entry_sync(
        self,
        content: str,
        tags: list[str] | None = None,
        project: str | None = None,
        created_at: datetime | None = None,
        todo_id: int | None = None,
        implicit_mood: str | None = None,
        life_domain: str | None = None,
        energy_level: int | None = None,
        embedding: list[float] | None = None,
    ) -> Entry:
        """Synchronous implementation of add_entry."""
        next_clock = self._get_next_lamport()
        with self.Session() as session:
            entry = Entry(
                uuid=str(uuid.uuid4()),
                lamport_clock=next_clock,
                content=content,
                project=project,
                todo_id=todo_id,
                implicit_mood=implicit_mood,
                life_domain=life_domain,
                energy_level=energy_level,
            )

            if embedding:
                entry.embedding = json.dumps(embedding).encode("utf-8")

            if tags:
                for tag_name in tags:
                    entry.tags.append(Tag(name=tag_name))

            entry.created_at = created_at or datetime.now()

            session.add(entry)
            session.commit()
            session.refresh(entry)

            entry._tag_names_cache = list(tags) if tags else []
            return entry

    def get_entry(self, entry_id: int) -> Entry:
        """Fetches a specific entry by its unique ID.

        Args:
            entry_id (int): The ID of the entry to retrieve.

        Returns:
            Entry: The retrieved Entry object.

        Raises:
            ValueError: If no entry is found with the given ID.
        """
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry

    def get_entries_by_date(self, date: datetime) -> list[Entry]:
        """Retrieves all entries recorded on a specific calendar date.

        Args:
            date (datetime): The target date.

        Returns:
            list[Entry]: A list of entries matching the date.
        """
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
        exclude_projects: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> list[Entry]:
        """Retrieves entries that fall within a specified date range with exclusion filters.

        Args:
            start_date (datetime): The beginning of the range (inclusive).
            end_date (datetime): The end of the range (inclusive).
            exclude_projects (list[str] | None): Projects to exclude.
            exclude_tags (list[str] | None): Tags to exclude.

        Returns:
            list[Entry]: A list of entries within the period.
        """
        with self.Session() as session:
            stmt = select(Entry).where(Entry.created_at.between(start_date, end_date))

            if exclude_projects:
                stmt = stmt.where(Entry.project.not_in(exclude_projects))

            if exclude_tags:
                # To exclude entries with specific tags, we check that none of the entry's tags are in the excluded list
                from sqlalchemy import not_

                stmt = stmt.where(not_(Entry.tags.any(Tag.name.in_(exclude_tags))))

            stmt = stmt.order_by(Entry.created_at)
            return list(session.scalars(stmt).all())

    def get_unique_projects(self) -> list[str]:
        """Retrieves a list of all unique project names.

        Returns:
            list[str]: A list of unique project names, sorted alphabetically.
        """
        with self.Session() as session:
            stmt = (
                select(func.distinct(Entry.project))
                .where(Entry.project.isnot(None))
                .order_by(Entry.project)
            )
            return list(session.scalars(stmt).all())

    def get_unique_tags(self) -> list[str]:
        """Retrieves a list of all unique tag names.

        Returns:
            list[str]: A list of unique tag names, sorted alphabetically.
        """
        with self.Session() as session:
            stmt = select(func.distinct(Tag.name)).order_by(Tag.name)
            return list(session.scalars(stmt).all())

    def get_latest_entry(self) -> Entry | None:
        """Retrieves the single most recently created journal entry.

        Returns:
            Entry | None: The newest Entry object, or None if the database is empty.
        """
        with self.Session() as session:
            return session.scalars(
                select(Entry).order_by(Entry.created_at.desc()).limit(1)
            ).first()

    def update_entry(
        self,
        entry_id: int,
        content: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
        created_at: datetime | None = None,
        embedding: list[float] | None = None,
    ) -> Entry:
        """Modifies attributes of an existing journal entry."""
        return self._queued_write(
            self._update_entry_sync,
            entry_id,
            content=content,
            tags=tags,
            project=project,
            created_at=created_at,
            embedding=embedding,
        )

    def _update_entry_sync(
        self,
        entry_id: int,
        content: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
        created_at: datetime | None = None,
        embedding: list[float] | None = None,
    ) -> Entry:
        """Synchronous implementation of update_entry."""
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
            if embedding is not None:
                entry.embedding = json.dumps(embedding).encode("utf-8")

            session.commit()
            session.refresh(entry)
            return entry

    def delete_entry(self, entry_id: int) -> bool:
        """Removes an entry from the database."""
        return self._queued_write(self._delete_entry_sync, entry_id)

    def _delete_entry_sync(self, entry_id: int) -> bool:
        """Synchronous implementation of delete_entry."""
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Deletes any journal entries linked to a specific todo task ID."""
        self._queued_write(self._delete_entry_by_todo_id_sync, todo_id)

    def _delete_entry_by_todo_id_sync(self, todo_id: int) -> None:
        """Synchronous implementation of delete_entry_by_todo_id."""
        with self.Session() as session:
            session.query(Entry).filter(Entry.todo_id == todo_id).delete(
                synchronize_session=False
            )
            session.commit()

    def delete_entries_before(self, before_date: datetime) -> int:
        """Deletes all journal entries recorded before a given date."""
        return self._queued_write(self._delete_entries_before_sync, before_date)

    def _delete_entries_before_sync(self, before_date: datetime) -> int:
        """Synchronous implementation of delete_entries_before."""
        with self.Session() as session:
            stmt = delete(Entry).where(Entry.created_at < before_date)
            result = session.execute(stmt)
            session.commit()
            return (
                int(result.rowcount) if result.rowcount is not None else 0
            )  # type: ignore[attr-defined]

    def get_all_entries_count(self) -> int:
        """Calculates the total number of journal entries in the database.

        Returns:
            int: The total entry count.
        """
        with self.Session() as session:
            return session.scalar(select(func.count(Entry.id))) or 0

    def get_entries_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Entry]:
        """Retrieves a subset of entries with optional filtering and pagination.

        Args:
            limit (int): Maximum number of entries to return. Defaults to 50.
            offset (int): Number of entries to skip. Defaults to 0.
            project (str | None): Filter by project name.
            tags (list[str] | None): Filter by associated tag names.

        Returns:
            list[Entry]: A list of matching Entry objects.
        """
        with self.Session() as session:
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))

            stmt = stmt.limit(limit).offset(offset)
            return list(session.scalars(stmt).all())

    def get_entries_with_streaks(self) -> list[datetime]:
        """Retrieves a unique list of dates on which entries were recorded.

        Used for calculating productivity streaks.

        Returns:
            list[datetime]: A list of distinct dates, ordered descending.
        """
        with self.Session() as session:
            stmt = (
                select(func.distinct(func.date(Entry.created_at)))
                .order_by(Entry.created_at.desc())
            )
            result = session.execute(stmt).all()
            return [datetime.strptime(row[0], "%Y-%m-%d") for row in result if row[0]]

    def get_project_stats(self) -> dict[str, int]:
        """Aggregates entry counts for each project.

        Returns:
            dict[str, int]: A mapping of project names to their entry counts.
        """
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
        """Counts journal entries per day within a specific time range.

        Args:
            start_date (datetime): Start of the aggregation period.
            end_date (datetime): End of the aggregation period.

        Returns:
            dict[str, int]: A mapping of date strings (YYYY-MM-DD) to entry counts.
        """
        with self.Session() as session:
            stmt = (
                select(func.date(Entry.created_at), func.count(Entry.id))
                .where(Entry.created_at.between(start_date, end_date))
                .group_by(func.date(Entry.created_at))
                .order_by(func.date(Entry.created_at).desc())
            )
            results = session.execute(stmt).all()
            return {str(date): count for date, count in results if date}

    def get_date_range(self) -> tuple[datetime | None, datetime | None]:
        """Determines the earliest and latest entry timestamps in the database.

        Returns:
            tuple[datetime | None, datetime | None]: A tuple containing the
                (min_date, max_date), or (None, None) if empty.
        """
        with self.Session() as session:
            stmt = select(func.min(Entry.created_at), func.max(Entry.created_at))
            result = session.execute(stmt).first()
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None, None

    def get_all_entries(
        self,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Entry]:
        """Fetches all journal entries with optional filtering.

        Args:
            project (str | None): Optional project filter.
            tags (list[str] | None): Optional tag filter.

        Returns:
            list[Entry]: A list of all matching entries, ordered by creation date.
        """
        with self.Session() as session:
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def search_similar_entries(
        self, query_embedding: list[float], limit: int = 5
    ) -> list[Entry]:
        """Retrieves entries that are semantically similar to the query embedding.

        Args:
            query_embedding (list[float]): The embedding vector of the search query.
            limit (int): Maximum number of results to return.

        Returns:
            list[Entry]: A list of semantically similar entries.
        """
        from .search_utils import cosine_similarity

        with self.Session() as session:
            # Fetch all entries with embeddings
            stmt = select(Entry).where(Entry.embedding.isnot(None))
            entries = list(session.scalars(stmt).all())

            if not entries:
                return []

            # Calculate similarity scores
            scored_entries = []
            for entry in entries:
                if entry.embedding:
                    vec = json.loads(entry.embedding.decode("utf-8"))
                    score = cosine_similarity(query_embedding, vec)
                    scored_entries.append((entry, score))

            # Sort by score descending and take top limit
            scored_entries.sort(key=lambda x: x[1], reverse=True)
            return [entry for entry, score in scored_entries[:limit]]

    def get_all_todos(
        self,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Todo]:
        """Fetches all todo tasks with optional filtering.

        Args:
            project (str | None): Optional project filter.
            tags (list[str] | None): Optional tag filter.

        Returns:
            list[Todo]: A list of all matching todos.
        """
        with self.Session() as session:
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(TodoTag).where(TodoTag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def get_entries_with_tags_count(self) -> dict[str, int]:
        """Aggregates usage counts for each tag across all entries.

        Returns:
            dict[str, int]: A mapping of tag names to their total usage count.
        """
        with self.Session() as session:
            stmt = (
                select(Tag.name, func.count(Tag.id))
                .group_by(Tag.name)
                .order_by(func.count(Tag.id).desc())
            )
            results = session.execute(stmt).all()
            return {row[0]: row[1] for row in results}

    def add_todo(
        self,
        content: str,
        priority: str = "normal",
        project: str | None = None,
        tags: list[str] | None = None,
        due_date: datetime | None = None,
    ) -> Todo:
        """Creates and persists a new todo task."""
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
        project: str | None = None,
        tags: list[str] | None = None,
        due_date: datetime | None = None,
    ) -> Todo:
        """Synchronous implementation of add_todo."""
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
                    todo.tags.append(TodoTag(name=tag_name))

            session.add(todo)
            session.commit()
            session.refresh(todo)

            todo._tag_names_cache = list(tags) if tags else []
            return todo

    def get_todo(self, todo_id: int) -> Todo:
        """Fetches a specific todo task by its unique ID.

        Args:
            todo_id (int): The ID of the task to retrieve.

        Returns:
            Todo: The retrieved Todo object.

        Raises:
            ValueError: If no task is found with the given ID.
        """
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: str | None = "pending") -> list[Todo]:
        """Retrieves tasks sorted by priority, urgency (due date), and creation time.

        Args:
            status (str | None): Filter by task status. Defaults to 'pending'.

        Returns:
            list[Todo]: A sorted list of Todo tasks.
        """
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
        content: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
        completed_at: datetime | None = None,
        due_date: datetime | None = None,
        reminder_last_sent: datetime | None = None,
    ) -> Todo:
        """Modifies attributes of an existing todo task."""
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
        content: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
        completed_at: datetime | None = None,
        due_date: datetime | None = None,
        reminder_last_sent: datetime | None = None,
    ) -> Todo:
        """Synchronous implementation of update_todo."""
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
                todo.tags = [TodoTag(name=t) for t in tags]

            session.commit()
            session.refresh(todo)
            return todo

    def get_reminders(
        self, due_before: datetime, reminded_since: datetime
    ) -> list[Todo]:
        """Identifies urgent tasks that require notification alerts.

        Args:
            due_before (datetime): Deadline threshold for reminders.
            reminded_since (datetime): Cooldown threshold to avoid spamming.

        Returns:
            list[Todo]: A list of tasks meeting reminder criteria.
        """
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
        """Permanently removes a todo task from the database."""
        return self._queued_write(self._delete_todo_sync, todo_id)

    def _delete_todo_sync(self, todo_id: int) -> bool:
        """Synchronous implementation of delete_todo."""
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if todo:
                session.delete(todo)
                session.commit()
                return True
            return False

    # --- Summary (Long-Term Memory) Methods ---

    def add_summary(
        self,
        content: str,
        period_start: datetime,
        period_end: datetime,
        summary_type: str = "weekly",
    ) -> Summary:
        """Stores a new AI-generated period summary."""
        return self._queued_write(
            self._add_summary_sync,
            content,
            period_start,
            period_end,
            summary_type=summary_type,
        )

    def _add_summary_sync(
        self,
        content: str,
        period_start: datetime,
        period_end: datetime,
        summary_type: str = "weekly",
    ) -> Summary:
        """Synchronous implementation of add_summary."""
        with self.Session() as session:
            summary = Summary(
                content=content,
                period_start=period_start,
                period_end=period_end,
                summary_type=summary_type,
            )
            session.add(summary)
            session.commit()
            session.refresh(summary)
            return summary

    def get_summaries(
        self, summary_type: str = "weekly", limit: int = 4
    ) -> list[Summary]:
        """Retrieves recent summaries for historical context.

        Args:
            summary_type (str): Type of summaries to fetch.
            limit (int): Maximum number of summaries. Defaults to 4.

        Returns:
            list[Summary]: A list of recent Summary objects.
        """
        with self.Session() as session:
            stmt = (
                select(Summary)
                .where(Summary.summary_type == summary_type)
                .order_by(Summary.period_end.desc())
                .limit(limit)
            )
            return list(session.scalars(stmt).all())

    def get_latest_summary(self, summary_type: str = "weekly") -> Summary | None:
        """Fetches the single most recent summary of a given type.

        Args:
            summary_type (str): The summary category.

        Returns:
            Summary | None: The newest summary or None.
        """
        with self.Session() as session:
            stmt = (
                select(Summary)
                .where(Summary.summary_type == summary_type)
                .order_by(Summary.period_end.desc())
                .limit(1)
            )
            return session.scalars(stmt).first()
