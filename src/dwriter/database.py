"""Database layer for dwriter.

This module handles all SQLite database operations for storing and retrieving
journal entries using SQLAlchemy 2.0.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
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
    """Represents a tag associated with a journal entry."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped["Entry"] = relationship(back_populates="tags")


class Entry(Base):
    """Represents a journal entry."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Link the entry to a specific Todo (for synced state)
    todo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True
    )

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="entry",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Return tag names as a list of strings."""
        # Use cached tag names if available (to avoid SQLAlchemy lazy loading issues)
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class TodoTag(Base):
    """Represents a tag associated with a todo task."""

    __tablename__ = "todo_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    todo: Mapped["Todo"] = relationship(back_populates="tags")


class Todo(Base):
    """Represents a prospective task."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    project: Mapped[Optional[str]] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="normal")
    status: Mapped[str] = mapped_column(String, default="pending")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    tags: Mapped[list["TodoTag"]] = relationship(
        back_populates="todo",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Return tag names as a list of strings."""
        # Use cached tag names if available (to avoid SQLAlchemy lazy loading issues)
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class Database:
    """SQLite database manager for dwriter entries.

    This class handles database connections, schema management, and CRUD
    operations for journal entries using SQLAlchemy.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database connection.

        Args:
            db_path: Optional path to the database file. If not provided,
                uses the default location at ~/.dwriter/entries.db.
        """
        if db_path is None:
            data_dir = Path.home() / ".dwriter"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "entries.db"

        # NullPool is appropriate for CLI/TUI tools where connection overhead
        # is negligible compared to the risk of session corruption across
        # Textual's @work threads.
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Base.metadata.create_all(self.engine)

        # Configure SQLite pragmas for foreign keys and WAL mode
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        # Disable object expiration on commit to avoid lazy loading issues
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Run migrations to add new columns if needed
        self._migrate()

    def _migrate(self) -> None:
        """Run database migrations and cleanups."""
        with self.engine.connect():
            import sqlite3

            db_path = str(self.engine.url.database)
            with sqlite3.connect(db_path) as sqlite_conn:
                cursor = sqlite_conn.execute("PRAGMA table_info(todos)")
                columns = [row[1] for row in cursor.fetchall()]

                if "due_date" not in columns:
                    sqlite_conn.execute(
                        "ALTER TABLE todos ADD COLUMN due_date DATETIME"
                    )

                # Migration: Add todo_id to entries for synced state
                cursor = sqlite_conn.execute("PRAGMA table_info(entries)")
                entry_columns = [row[1] for row in cursor.fetchall()]
                if "todo_id" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN todo_id "
                        "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                    )

                # Clean up orphaned tags and todo_tags referencing deleted entries/todos
                sqlite_conn.execute(
                    "DELETE FROM tags WHERE entry_id NOT IN (SELECT id FROM entries)"
                )
                sqlite_conn.execute(
                    "DELETE FROM todo_tags WHERE todo_id NOT IN (SELECT id FROM todos)"
                )

                sqlite_conn.commit()

    def connection(self) -> Any:
        """Return a raw SQLite connection for low-level operations.

        Returns:
            A sqlite3.Connection object.

        Note:
            This is provided for backward compatibility and advanced use cases.
            Prefer using the high-level methods when possible.
        """
        import sqlite3

        conn = sqlite3.connect(str(self.engine.url.database))
        conn.row_factory = sqlite3.Row
        return conn

    def add_entry(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
        todo_id: Optional[int] = None,
    ) -> Entry:
        """Add a new journal entry.

        Args:
            content: The text content of the entry.
            tags: Optional list of tags to associate with the entry.
            project: Optional project name.
            created_at: Optional datetime for the entry. If not provided,
                uses the current time. If provided, the exact datetime is preserved.
            todo_id: Optional ID of a todo task this entry is linked to.

        Returns:
            The created Entry object.
        """
        with self.Session() as session:
            entry = Entry(content=content, project=project, todo_id=todo_id)

            if tags:
                # Use standard SQLAlchemy relationship pattern to avoid orphaned
                # tags or identity map cross-contamination
                for tag_name in tags:
                    entry.tags.append(Tag(name=tag_name))

            if created_at is not None:
                entry.created_at = created_at
            else:
                entry.created_at = datetime.now()

            session.add(entry)
            session.commit()

            # Refresh to populate DB-generated fields before session closes
            session.refresh(entry)

            # Cache tag names to avoid lazy loading
            entry._tag_names_cache = list(tags) if tags else []

            return entry

    def get_entry(self, entry_id: int) -> Entry:
        """Retrieve a single entry by ID.

        Args:
            entry_id: The ID of the entry to retrieve.

        Returns:
            The Entry object.

        Raises:
            ValueError: If no entry exists with the given ID.
        """
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry

    def get_entries_by_date(self, date: datetime) -> list[Entry]:
        """Retrieve all entries for a specific date.

        Args:
            date: The date to filter entries by.

        Returns:
            A list of Entry objects for the specified date.
        """
        with self.Session() as session:
            # Entries are stored in local time, so we compare dates directly
            date_str = date.strftime("%Y-%m-%d")
            stmt = (
                select(Entry)
                .where(func.date(Entry.created_at) == date_str)
                .order_by(Entry.created_at)
            )
            return list(session.scalars(stmt).all())

    def get_entries_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Entry]:
        """Retrieve entries within a date range.

        Args:
            start_date: The start date (inclusive).
            end_date: The end date (inclusive).

        Returns:
            A list of Entry objects within the specified range.
        """
        with self.Session() as session:
            stmt = (
                select(Entry)
                .where(Entry.created_at.between(start_date, end_date))
                .order_by(Entry.created_at)
            )
            return list(session.scalars(stmt).all())

    def get_latest_entry(self) -> Optional[Entry]:
        """Retrieve the most recent entry.

        Returns:
            The most recent Entry, or None if no entries exist.
        """
        with self.Session() as session:
            return session.scalars(
                select(Entry).order_by(Entry.created_at.desc()).limit(1)
            ).first()

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID.

        Args:
            entry_id: The ID of the entry to delete.

        Returns:
            True if the entry was deleted, False if it didn't exist.
        """
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Silently delete a journal entry if its linked Todo is un-completed.

        Args:
            todo_id: The ID of the linked todo task.
        """
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
    ) -> Entry:
        """Update an existing entry.

        Args:
            entry_id: The ID of the entry to update.
            content: New content for the entry (optional).
            tags: New list of tags (optional, replaces existing).
            project: New project name (optional).
            created_at: New creation datetime (optional).

        Returns:
            The updated Entry object.

        Raises:
            ValueError: If no entry exists with the given ID.
        """
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry {entry_id} not found")

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
        """Delete all entries before a specific date.

        Args:
            before_date: Delete entries created before this date.

        Returns:
            The number of entries deleted.
        """
        with self.Session() as session:
            stmt = delete(Entry).where(Entry.created_at < before_date)
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount) if result.rowcount is not None else 0  # type: ignore[attr-defined]

    def get_all_entries_count(self) -> int:
        """Get the total count of all entries.

        Returns:
            The total number of entries in the database.
        """
        with self.Session() as session:
            return session.scalar(select(func.count(Entry.id))) or 0

    def get_entries_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Entry]:
        """Retrieve a page of entries, optionally filtered.

        Args:
            limit: Maximum number of entries to return.
            offset: Number of entries to skip.
            project: Optional project name to filter by.
            tags: Optional list of tag names to filter by.

        Returns:
            A list of Entry objects, ordered by creation date (newest first).
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
        """Get unique dates with entries for streak calculation.
        
        Uses optimized SQL to only fetch unique date strings.
        """
        with self.Session() as session:
            stmt = (
                select(func.distinct(func.date(Entry.created_at)))
                .order_by(Entry.created_at.desc())
            )
            result = session.execute(stmt).all()
            return [datetime.strptime(row[0], "%Y-%m-%d") for row in result if row[0]]

    def get_project_stats(self) -> dict[str, int]:
        """Get entry counts grouped by project.

        Returns:
            A dictionary mapping project names to entry counts.
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
        """Get entry counts grouped by date.

        Args:
            start_date: Start of date range.
            end_date: End of date range.

        Returns:
            A dictionary mapping date strings (YYYY-MM-DD) to entry counts.
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

    def get_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get the date range of all entries.

        Returns:
            A tuple of (first_entry_date, last_entry_date) or (None, None) if empty.
        """
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
    ) -> list[Entry]:
        """Retrieve all entries, optionally filtered by project and/or tags.

        Args:
            project: Optional project name to filter by.
            tags: Optional list of tag names to filter by.

        Returns:
            A list of Entry objects, ordered by creation date (newest first).
        """
        with self.Session() as session:
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def get_all_todos(
        self,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Todo]:
        """Retrieve all todos, optionally filtered by project and/or tags.

        Args:
            project: Optional project name to filter by.
            tags: Optional list of tag names to filter by.

        Returns:
            A list of Todo objects, ordered by priority and creation date.
        """
        with self.Session() as session:
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(TodoTag).where(TodoTag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def get_entries_with_tags_count(self) -> dict[str, int]:
        """Get entry counts grouped by tag.

        Returns:
            A dictionary mapping tag names to entry counts.
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
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
    ) -> Todo:
        """Add a new prospective task.

        Args:
            content: The text content of the task.
            priority: Task priority (low, normal, high, urgent).
            project: Optional project name.
            tags: Optional list of tags.
            due_date: Optional due date.

        Returns:
            The created Todo object.
        """
        with self.Session() as session:
            todo = Todo(
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

            # Refresh to populate DB-generated fields before detaching
            session.refresh(todo)

            todo._tag_names_cache = list(tags) if tags else []

            return todo

    def get_todo(self, todo_id: int) -> Todo:
        """Retrieve a single todo by ID.

        Args:
            todo_id: The ID of the todo to retrieve.

        Returns:
            The Todo object.

        Raises:
            ValueError: If no todo exists with the given ID.
        """
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: Optional[str] = "pending") -> list[Todo]:
        """Retrieve tasks, optionally filtered by status.

        Args:
            status: Optional status to filter by (e.g., "pending", "completed").

        Returns:
            A list of Todo objects.

        Results are ordered by:
        1. Priority (urgent > high > normal > low)
        2. Due date urgency (overdue < today < tomorrow < other days)
        3. Creation date (newest first)
        """
        with self.Session() as session:
            stmt = select(Todo)

            if status:
                stmt = stmt.where(Todo.status == status)

            # Order by priority (urgent=1, high=2, normal=3, low=4)
            priority_order = case(
                (Todo.priority == "urgent", 1),
                (Todo.priority == "high", 2),
                (Todo.priority == "normal", 3),
                (Todo.priority == "low", 4),
                else_=5,
            )

            # Order by due date urgency
            # Overdue tasks first, then today, then tomorrow, then others
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            due_date_order = case(
                # Overdue tasks (due_date < today)
                (Todo.due_date < today, 0),
                # Due today
                (Todo.due_date == today, 1),
                # Due tomorrow
                (Todo.due_date == tomorrow, 2),
                # All other due dates (including no due date)
                else_=3,
            )

            # Sort by priority first, then due date urgency, then creation date
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
    ) -> Todo:
        """Update an existing task.

        Args:
            todo_id: The ID of the todo to update.
            content: New content (optional).
            status: New status (optional).
            priority: New priority (optional).
            project: New project (optional).
            tags: New tags (optional).
            completed_at: New completion date (optional).
            due_date: New due date (optional).

        Returns:
            The updated Todo object.

        Raises:
            ValueError: If no todo exists with the given ID.
        """
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo {todo_id} not found")

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
            if tags is not None:
                # Replace existing tags
                todo.tags = [TodoTag(name=t) for t in tags]

            session.commit()
            session.refresh(todo)
            return todo

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a task by ID.

        Args:
            todo_id: The ID of the todo to delete.

        Returns:
            True if the task was deleted, False if it didn't exist.
        """
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if todo:
                session.delete(todo)
                session.commit()
                return True
            return False
