"""Todo and Summary repository mixin for the dwriter Database class."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import case, select

from .database_models import Summary, Tag, Todo


class TodoSummaryRepository:
    """Mixin providing todo and summary CRUD methods for Database."""

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
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(Todo.tags).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())

    def add_todo(
        self,
        content: str,
        priority: str = "normal",
        project: str | None = None,
        tags: list[str] | None = None,
        due_date: datetime | None = None,
    ) -> Todo:
        """Creates and persists a new todo task."""
        return self._queued_write(  # type: ignore[attr-defined]
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
        next_clock = self._get_next_lamport()  # type: ignore[attr-defined]
        with self.Session() as session:  # type: ignore[attr-defined]
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

    def get_todo(self, todo_id: int) -> Todo:
        """Fetches a specific todo task by its unique ID.

        Args:
            todo_id (int): The ID of the task to retrieve.

        Returns:
            Todo: The retrieved Todo object.

        Raises:
            ValueError: If no task is found with the given ID.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        return self._queued_write(  # type: ignore[attr-defined]
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
        next_clock = self._get_next_lamport()  # type: ignore[attr-defined]
        with self.Session() as session:  # type: ignore[attr-defined]
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
    ) -> list[Todo]:
        """Identifies urgent tasks that require notification alerts.

        Args:
            due_before (datetime): Deadline threshold for reminders.
            reminded_since (datetime): Cooldown threshold to avoid spamming.

        Returns:
            list[Todo]: A list of tasks meeting reminder criteria.
        """
        with self.Session() as session:  # type: ignore[attr-defined]
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
        return self._queued_write(self._delete_todo_sync, todo_id)  # type: ignore[attr-defined]

    def _delete_todo_sync(self, todo_id: int) -> bool:
        """Synchronous implementation of delete_todo."""
        with self.Session() as session:  # type: ignore[attr-defined]
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
        return self._queued_write(  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
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
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = (
                select(Summary)
                .where(Summary.summary_type == summary_type)
                .order_by(Summary.period_end.desc())
                .limit(1)
            )
            return session.scalars(stmt).first()
