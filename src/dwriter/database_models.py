"""SQLAlchemy ORM models for dwriter."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
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
    """Base class for SQLAlchemy models."""

    pass


class Tag(Base):
    """Tag associated with a journal entry or a todo task."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("entries.id", ondelete="CASCADE"), nullable=True
    )
    todo_id: Mapped[int | None] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, index=True)

    entry: Mapped[Entry | None] = relationship(
        back_populates="tags", foreign_keys="[Tag.entry_id]"
    )
    todo: Mapped[Todo | None] = relationship(
        back_populates="tags", foreign_keys="[Tag.todo_id]"
    )


class Entry(Base):
    """Journal entry model."""

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
    life_domain: Mapped[str | None] = mapped_column(String)
    energy_level: Mapped[int | None] = mapped_column(Integer)

    tags: Mapped[list[Tag]] = relationship(
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
    project: Mapped[str | None] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="normal")
    status: Mapped[str] = mapped_column(String, default="pending")
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    reminder_last_sent: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    tags: Mapped[list[Tag]] = relationship(
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
