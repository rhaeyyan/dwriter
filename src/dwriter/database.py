"""Database layer for Day Writer.

This module handles all SQLite database operations for storing and retrieving
journal entries using SQLAlchemy 2.0.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    case,
    create_engine,
    delete,
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


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class Tag(Base):
    """Represents a tag associated with a journal entry."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(
        ForeignKey("entries.id", ondelete="CASCADE")
    )
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

    tags: Mapped[List["Tag"]] = relationship(
        back_populates="entry",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> List[str]:
        """Return tag names as a list of strings."""
        return [tag.name for tag in self.tags]


class TodoTag(Base):
    """Represents a tag associated with a todo task."""

    __tablename__ = "todo_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_id: Mapped[int] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE")
    )
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    tags: Mapped[List["TodoTag"]] = relationship(
        back_populates="todo",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> List[str]:
        """Return tag names as a list of strings."""
        return [tag.name for tag in self.tags]


class Database:
    """SQLite database manager for Day Writer entries.

    This class handles database connections, schema management, and CRUD
    operations for journal entries using SQLAlchemy.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database connection.

        Args:
            db_path: Optional path to the database file. If not provided,
                uses the default location at ~/.day-writer/entries.db.
        """
        if db_path is None:
            data_dir = Path.home() / ".day-writer"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "entries.db"

        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def connection(self):
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
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> Entry:
        """Add a new journal entry.

        Args:
            content: The text content of the entry.
            tags: Optional list of tags to associate with the entry.
            project: Optional project name.
            created_at: Optional datetime for the entry. If not provided,
                uses the current time.

        Returns:
            The created Entry object.
        """
        with self.Session() as session:
            entry = Entry(content=content, project=project)
            if tags:
                entry.tags = [Tag(name=t) for t in tags]
            if created_at is not None:
                entry.created_at = created_at
            session.add(entry)
            session.commit()
            session.refresh(entry)
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

    def get_entries_by_date(self, date: datetime) -> List[Entry]:
        """Retrieve all entries for a specific date.

        Args:
            date: The date to filter entries by.

        Returns:
            A list of Entry objects for the specified date.
        """
        with self.Session() as session:
            # Convert UTC to local time before comparing dates
            # SQLite stores datetimes in UTC, so we use 'localtime' modifier
            date_str = date.strftime("%Y-%m-%d")
            stmt = (
                select(Entry)
                .where(func.date(Entry.created_at, "localtime") == date_str)
                .order_by(Entry.created_at)
            )
            return list(session.scalars(stmt).all())

    def get_entries_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Entry]:
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

    def update_entry(
        self,
        entry_id: int,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
    ) -> Entry:
        """Update an existing entry.

        Args:
            entry_id: The ID of the entry to update.
            content: New content for the entry (optional).
            tags: New list of tags (optional, replaces existing).
            project: New project name (optional).

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
            return result.rowcount or 0

    def get_all_entries_count(self) -> int:
        """Get the total count of all entries.

        Returns:
            The total number of entries in the database.
        """
        with self.Session() as session:
            return session.scalar(select(func.count(Entry.id)))

    def get_entries_with_streaks(self) -> List[datetime]:
        """Get dates with entries for streak calculation.

        Returns:
            A list of unique dates (datetime objects) that have entries.
        """
        with self.Session() as session:
            # Returns distinct dates with entries
            stmt = (
                select(func.date(Entry.created_at))
                .distinct()
                .order_by(Entry.created_at.desc())
            )
            date_strings = session.scalars(stmt).all()
            return [
                datetime.strptime(d, "%Y-%m-%d")
                for d in date_strings
                if d
            ]

    def get_project_stats(self) -> Dict[str, int]:
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
    ) -> Dict[str, int]:
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
            stmt = select(
                func.min(Entry.created_at),
                func.max(Entry.created_at)
            )
            result = session.execute(stmt).first()
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None, None

    def get_total_entries_count(self) -> int:
        """Get the total count of all entries.

        Returns:
            The total number of entries in the database.
        """
        with self.Session() as session:
            return session.scalar(select(func.count(Entry.id)))

    def get_all_entries(
        self,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Entry]:
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
        tags: Optional[List[str]] = None,
    ) -> List[Todo]:
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

    def get_entries_with_tags_count(self) -> Dict[str, int]:
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
            return {name: count for name, count in results}

    def add_todo(
        self,
        content: str,
        priority: str = "normal",
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Todo:
        """Add a new prospective task."""
        with self.Session() as session:
            todo = Todo(content=content, priority=priority, project=project)
            if tags:
                todo.tags = [TodoTag(name=t) for t in tags]

            session.add(todo)
            session.commit()
            session.refresh(todo)
            return todo

    def get_todo(self, todo_id: int) -> Todo:
        """Retrieve a single todo by ID.

        Raises:
            ValueError: If no todo exists with the given ID.
        """
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: Optional[str] = "pending") -> List[Todo]:
        """Retrieve tasks, optionally filtered by status.

        Results are ordered by priority (urgent > high > normal > low)
        and then by creation date (newest first).
        """
        with self.Session() as session:
            stmt = select(Todo)

            if status:
                stmt = stmt.where(Todo.status == status)

            # Order by priority (urgent=1, high=2, normal=3, low=4) then by date
            priority_order = case(
                (Todo.priority == "urgent", 1),
                (Todo.priority == "high", 2),
                (Todo.priority == "normal", 3),
                (Todo.priority == "low", 4),
                else_=5,
            )
            stmt = stmt.order_by(priority_order, Todo.created_at.desc())

            return list(session.scalars(stmt).all())

    def update_todo(
        self,
        todo_id: int,
        content: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        completed_at: Optional[datetime] = None,
    ) -> Todo:
        """Update an existing task.

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
            if tags is not None:
                # Replace existing tags
                todo.tags = [TodoTag(name=t) for t in tags]

            session.commit()
            session.refresh(todo)
            return todo

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a task by ID.

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
