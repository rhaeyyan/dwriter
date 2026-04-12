"""SQLAlchemy ORM models for dwriter."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the application.

    Inherits from DeclarativeBase to provide a foundation for model definitions.
    """

    pass


class Tag(Base):
    """Represents a tag associated with a journal entry or todo task.

    Attributes:
        id (int): Unique identifier for the tag.
        entry_id (int | None): Foreign key referencing the associated journal entry.
        todo_id (int | None): Foreign key referencing the associated todo task.
        name (str): The string name of the tag, indexed for faster retrieval.
        entry (Entry | None): Relationship mapping back to the associated Entry object.
        todo (Todo | None): Relationship mapping back to the associated Todo object.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int | None] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"))
    todo_id: Mapped[int | None] = mapped_column(ForeignKey("todos.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped["Entry | None"] = relationship(back_populates="tags", foreign_keys="[Tag.entry_id]")
    todo: Mapped["Todo | None"] = relationship(back_populates="tags", foreign_keys="[Tag.todo_id]")


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
        foreign_keys="[Tag.entry_id]",
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
        tags (list[Tag]): Collection of tags for this task.
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

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="todo",
        lazy="selectin",
        cascade="all, delete-orphan",
        foreign_keys="[Tag.todo_id]",
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
