"""Database layer for dwriter."""

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
    """Tag associated with a journal entry."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped["Entry"] = relationship(back_populates="tags")


class Entry(Base):
    """Journal entry model."""

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
        """Return tag names, using cache if available."""
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class TodoTag(Base):
    """Tag associated with a todo task."""

    __tablename__ = "todo_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    todo: Mapped["Todo"] = relationship(back_populates="tags")


class Todo(Base):
    """Task model."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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

    tags: Mapped[list["TodoTag"]] = relationship(
        back_populates="todo",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def tag_names(self) -> list[str]:
        """Return tag names, using cache if available."""
        if hasattr(self, "_tag_names_cache"):
            return self._tag_names_cache
        return [tag.name for tag in self.tags]


class Database:
    """Manager for SQLite database operations."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection and schema."""
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

    def _migrate(self) -> None:
        """Run schema migrations."""
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

                if "reminder_last_sent" not in columns:
                    sqlite_conn.execute(
                        "ALTER TABLE todos ADD COLUMN reminder_last_sent DATETIME"
                    )

                cursor = sqlite_conn.execute("PRAGMA table_info(entries)")
                entry_columns = [row[1] for row in cursor.fetchall()]
                if "todo_id" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN todo_id "
                        "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                    )

                # Clean up orphaned tags
                sqlite_conn.execute(
                    "DELETE FROM tags WHERE entry_id NOT IN (SELECT id FROM entries)"
                )
                sqlite_conn.execute(
                    "DELETE FROM todo_tags WHERE todo_id NOT IN (SELECT id FROM todos)"
                )

                sqlite_conn.commit()

    def connection(self) -> Any:
        """Return a raw SQLite connection."""
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
        """Add a new journal entry."""
        with self.Session() as session:
            entry = Entry(content=content, project=project, todo_id=todo_id)

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
        """Retrieve a single entry by ID."""
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry

    def get_entries_by_date(self, date: datetime) -> list[Entry]:
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
        self, start_date: datetime, end_date: datetime
    ) -> list[Entry]:
        """Retrieve entries within a date range."""
        with self.Session() as session:
            stmt = (
                select(Entry)
                .where(Entry.created_at.between(start_date, end_date))
                .order_by(Entry.created_at)
            )
            return list(session.scalars(stmt).all())

    def get_latest_entry(self) -> Optional[Entry]:
        """Retrieve the most recent entry."""
        with self.Session() as session:
            return session.scalars(
                select(Entry).order_by(Entry.created_at.desc()).limit(1)
            ).first()

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID."""
        with self.Session() as session:
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Delete entry linked to a todo ID."""
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
        """Update an existing entry."""
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
        """Delete all entries before a specific date."""
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
    ) -> list[Entry]:
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
    ) -> list[Entry]:
        """Retrieve all entries, optionally filtered."""
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
        """Retrieve all todos, optionally filtered."""
        with self.Session() as session:
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(TodoTag).where(TodoTag.name.in_(tags))
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

    def add_todo(
        self,
        content: str,
        priority: str = "normal",
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
    ) -> Todo:
        """Add a new task."""
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
            session.refresh(todo)

            todo._tag_names_cache = list(tags) if tags else []
            return todo

    def get_todo(self, todo_id: int) -> Todo:
        """Retrieve a single todo by ID."""
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: Optional[str] = "pending") -> list[Todo]:
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
    ) -> Todo:
        """Update an existing task."""
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
        with self.Session() as session:
            todo = session.get(Todo, todo_id)
            if todo:
                session.delete(todo)
                session.commit()
                return True
            return False
