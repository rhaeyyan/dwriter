"""Entry repository mixin for the dwriter Database class."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import delete, func, select

from .database_models import Entry, Tag, Todo


class EntryRepository:
    """Mixin providing entry CRUD and query methods for Database."""

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
        return self._queued_write(  # type: ignore[attr-defined, no-any-return]
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
        next_clock = self._get_next_lamport()  # type: ignore[attr-defined]
        with self.Session() as session:  # type: ignore[attr-defined]
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

            entry._tag_names_cache = list(tags) if tags else []  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
            entry = session.get(Entry, entry_id)
            if not entry:
                raise ValueError(f"Entry with id {entry_id} not found")
            return entry  # type: ignore[no-any-return]

    def get_entries_by_date(self, date: datetime) -> list[Entry]:
        """Retrieves all entries recorded on a specific calendar date.

        Args:
            date (datetime): The target date.

        Returns:
            list[Entry]: A list of entries matching the date.
        """
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
        exclude_projects: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> list[Entry]:
        """Retrieves entries within a specified date range with exclusion filters.

        Args:
            start_date (datetime): The beginning of the range (inclusive).
            end_date (datetime): The end of the range (inclusive).
            exclude_projects (list[str] | None): Projects to exclude.
            exclude_tags (list[str] | None): Tags to exclude.

        Returns:
            list[Entry]: A list of entries within the period.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Entry).where(Entry.created_at.between(start_date, end_date))

            if exclude_projects:
                from sqlalchemy import not_, or_

                prefix_excludes = [p.lower() for p in exclude_projects if p.endswith(":")]  # noqa: E501
                exact_excludes = [p.lower() for p in exclude_projects if not p.endswith(":")]  # noqa: E501

                conditions = []
                if exact_excludes:
                    conditions.append(func.lower(Entry.project).in_(exact_excludes))
                for prefix in prefix_excludes:
                    conditions.append(func.lower(Entry.project).like(f"{prefix}%"))

                if conditions:
                    stmt = stmt.where(or_(Entry.project.is_(None), not_(or_(*conditions))))  # noqa: E501

            if exclude_tags:
                from sqlalchemy import not_

                exclude_tags_lower = [t.lower() for t in exclude_tags]
                stmt = stmt.where(
                    not_(Entry.tags.any(func.lower(Tag.name).in_(exclude_tags_lower)))
                )

            stmt = stmt.order_by(Entry.created_at)
            return list(session.scalars(stmt).all())

    def get_unique_projects(self) -> list[str]:
        """Retrieves a list of all unique project names.

        Returns:
            list[str]: A list of unique project names, sorted alphabetically.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(func.distinct(Tag.name)).order_by(Tag.name)
            return list(session.scalars(stmt).all())

    def get_stale_todos(self, limit: int = 5) -> list[Todo]:
        """Retrieves the oldest pending todo tasks.

        Args:
            limit (int): Maximum number of tasks to return.

        Returns:
            list[Todo]: The oldest pending tasks ordered by creation date ascending.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(Todo)
                .where(Todo.status == "pending")
                .order_by(Todo.created_at.asc())
                .limit(limit)
            )
            return list(session.scalars(stmt).all())

    def get_latest_entry(self) -> Entry | None:
        """Retrieves the single most recently created journal entry.

        Returns:
            Entry | None: The newest Entry object, or None if the database is empty.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            return session.scalars(  # type: ignore[no-any-return]
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
        return self._queued_write(  # type: ignore[attr-defined, no-any-return]
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
            if embedding is not None:
                entry.embedding = json.dumps(embedding).encode("utf-8")

            session.commit()
            session.refresh(entry)
            return entry  # type: ignore[no-any-return]

    def delete_entry(self, entry_id: int) -> bool:
        """Removes an entry from the database."""
        return self._queued_write(self._delete_entry_sync, entry_id)  # type: ignore[attr-defined, no-any-return]

    def _delete_entry_sync(self, entry_id: int) -> bool:
        """Synchronous implementation of delete_entry."""
        with self.Session() as session:  # type: ignore[attr-defined]
            entry = session.get(Entry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_entry_by_todo_id(self, todo_id: int) -> None:
        """Deletes any journal entries linked to a specific todo task ID."""
        self._queued_write(self._delete_entry_by_todo_id_sync, todo_id)  # type: ignore[attr-defined]

    def _delete_entry_by_todo_id_sync(self, todo_id: int) -> None:
        """Synchronous implementation of delete_entry_by_todo_id."""
        with self.Session() as session:  # type: ignore[attr-defined]
            session.query(Entry).filter(Entry.todo_id == todo_id).delete(
                synchronize_session=False
            )
            session.commit()

    def delete_entries_before(self, before_date: datetime) -> int:
        """Deletes all journal entries recorded before a given date."""
        return self._queued_write(self._delete_entries_before_sync, before_date)  # type: ignore[attr-defined, no-any-return]

    def _delete_entries_before_sync(self, before_date: datetime) -> int:
        """Synchronous implementation of delete_entries_before."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = delete(Entry).where(Entry.created_at < before_date)
            result = session.execute(stmt)
            session.commit()
            return (
                int(result.rowcount) if result.rowcount is not None else 0
            )

    def get_all_entries_count(self) -> int:
        """Calculates the total number of journal entries in the database.

        Returns:
            int: The total entry count.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        """Counts journal entries per day within a specific time range.

        Args:
            start_date (datetime): Start of the aggregation period.
            end_date (datetime): End of the aggregation period.

        Returns:
            dict[str, int]: A mapping of date strings (YYYY-MM-DD) to entry counts.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(func.date(Entry.created_at), func.count(Entry.id))
                .where(Entry.created_at.between(start_date, end_date))
                .group_by(func.date(Entry.created_at))
                .order_by(func.date(Entry.created_at).desc())
            )
            results = session.execute(stmt).all()
            return {str(date): count for date, count in results if date}

    def get_activity_report_data(
        self,
        start_date: datetime,
        end_date: datetime,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieves both entries and todos for a specific activity report.

        Used by the 'Catch Up' feature to fetch context for AI synthesis.

        Args:
            start_date (datetime): Start of the period.
            end_date (datetime): End of the period.
            project (str | None): Optional project filter.
            tags (list[str] | None): Optional tag filter.

        Returns:
            dict[str, Any]: A dictionary containing 'entries' and 'todos'.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            # 1. Fetch Entries
            entry_stmt = select(Entry).where(Entry.created_at.between(start_date, end_date))  # noqa: E501
            if project:
                entry_stmt = entry_stmt.where(Entry.project == project)
            if tags:
                entry_stmt = entry_stmt.join(Entry.tags).where(Tag.name.in_(tags))
            entry_stmt = entry_stmt.order_by(Entry.created_at.asc())
            entries = list(session.scalars(entry_stmt).unique().all())

            # 2. Fetch Todos (either created or completed in range)
            from sqlalchemy import or_

            todo_stmt = select(Todo).where(
                or_(
                    Todo.created_at.between(start_date, end_date),
                    Todo.completed_at.between(start_date, end_date),
                )
            )
            if project:
                todo_stmt = todo_stmt.where(Todo.project == project)
            if tags:
                todo_stmt = todo_stmt.join(Todo.tags).where(Tag.name.in_(tags))
            todo_stmt = todo_stmt.order_by(Todo.created_at.asc())
            todos = list(session.scalars(todo_stmt).unique().all())

            return {"entries": entries, "todos": todos}

    def get_date_range(self) -> tuple[datetime | None, datetime | None]:
        """Determines the earliest and latest entry timestamps in the database.

        Returns:
            tuple[datetime | None, datetime | None]: A tuple containing the
                (min_date, max_date), or (None, None) if empty.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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

        with self.Session() as session:  # type: ignore[attr-defined]
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

    def get_entries_with_tags_count(self) -> dict[str, int]:
        """Aggregates usage counts for each tag across all entries.

        Returns:
            dict[str, int]: A mapping of tag names to their total usage count.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(Tag.name, func.count(Tag.id))
                .group_by(Tag.name)
                .order_by(func.count(Tag.id).desc())
            )
            results = session.execute(stmt).all()
            return {row[0]: row[1] for row in results}
