"""Entry repository mixin for dwriter Database."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import delete, func, select

from .database_models import Entry, Tag

if TYPE_CHECKING:
    pass


class EntryRepository:
    """Mixin providing entry CRUD operations for the Database class."""

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
    ) -> Entry:
        """Add a new journal entry."""
        return self._queued_write(  # type: ignore[attr-defined]
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
    ) -> Entry:
        next_clock = self._get_next_lamport()  # type: ignore[attr-defined]
        with self.Session() as session:  # type: ignore[attr-defined]
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

    def get_entry(self, entry_id: int) -> Entry:
        """Retrieve a single entry by ID."""
        with self.Session() as session:  # type: ignore[attr-defined]
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry

    def get_entries_by_date(self, date: datetime) -> list[Entry]:
        """Retrieve all entries for a specific date."""
        with self.Session() as session:  # type: ignore[attr-defined]
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
    ) -> list[Entry]:
        """Retrieve entries within a date range with optional exclusion filters."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Entry).where(Entry.created_at.between(start_date, end_date))

            if exclude_projects:
                from sqlalchemy import not_, or_

                prefix_excludes = [p.lower() for p in exclude_projects if p.endswith(":")]
                exact_excludes = [p.lower() for p in exclude_projects if not p.endswith(":")]
                conditions: list[Any] = []
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

    def get_latest_entry(self) -> Optional[Entry]:
        """Retrieve the most recent entry."""
        with self.Session() as session:  # type: ignore[attr-defined]
            return session.scalars(
                select(Entry).order_by(Entry.created_at.desc()).limit(1)
            ).first()

    def update_entry(
        self,
        entry_id: int,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> Entry:
        """Update an existing entry."""
        return self._queued_write(  # type: ignore[attr-defined]
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
    ) -> Entry:
        next_clock = self._get_next_lamport()  # type: ignore[attr-defined]
        with self.Session() as session:  # type: ignore[attr-defined]
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

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID."""
        return self._queued_write(self._delete_entry_sync, entry_id)  # type: ignore[attr-defined]

    def _delete_entry_sync(self, entry_id: int) -> bool:
        with self.Session() as session:  # type: ignore[attr-defined]
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Delete entry linked to a todo ID."""
        self._queued_write(self._delete_entry_by_todo_id_sync, todo_id)  # type: ignore[attr-defined]

    def _delete_entry_by_todo_id_sync(self, todo_id: int) -> None:
        with self.Session() as session:  # type: ignore[attr-defined]
            session.query(Entry).filter(Entry.todo_id == todo_id).delete(
                synchronize_session=False
            )
            session.commit()

    def delete_entries_before(self, before_date: datetime) -> int:
        """Delete all entries before a specific date."""
        return self._queued_write(self._delete_entries_before_sync, before_date)  # type: ignore[attr-defined]

    def _delete_entries_before_sync(self, before_date: datetime) -> int:
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = delete(Entry).where(Entry.created_at < before_date)
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount) if result.rowcount is not None else 0  # type: ignore[attr-defined]

    def get_all_entries_count(self) -> int:
        """Get the total count of all entries."""
        with self.Session() as session:  # type: ignore[attr-defined]
            return session.scalar(select(func.count(Entry.id))) or 0

    def get_entries_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Entry]:
        """Retrieve a page of entries, optionally filtered."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            stmt = stmt.limit(limit).offset(offset)
            return list(session.scalars(stmt).all())

    def get_entries_with_streaks(self) -> list[datetime]:
        """Get unique dates with entries."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(func.distinct(func.date(Entry.created_at)))
                .order_by(Entry.created_at.desc())
            )
            result = session.execute(stmt).all()
            return [datetime.strptime(row[0], "%Y-%m-%d") for row in result if row[0]]

    def get_project_stats(self) -> dict[str, int]:
        """Get entry counts grouped by project."""
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Entry).order_by(Entry.created_at.desc())
            if project:
                stmt = stmt.where(Entry.project == project)
            if tags:
                stmt = stmt.join(Tag).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def get_unique_projects(self) -> list[str]:
        """Retrieve a list of all unique project names."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(func.distinct(Entry.project))
                .where(Entry.project.isnot(None))
                .order_by(Entry.project)
            )
            return list(session.scalars(stmt).all())

    def get_unique_tags(self) -> list[str]:
        """Retrieve a list of all unique tag names."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(func.distinct(Tag.name)).order_by(Tag.name)
            return list(session.scalars(stmt).all())

    def get_entries_with_tags_count(self) -> dict[str, int]:
        """Get entry counts grouped by tag."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(Tag.name, func.count(Tag.id))
                .group_by(Tag.name)
                .order_by(func.count(Tag.id).desc())
            )
            results = session.execute(stmt).all()
            return {row[0]: row[1] for row in results}
