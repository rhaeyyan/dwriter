"""Todo repository mixin for dwriter Database."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import case, func, select

from .database_models import Tag, Todo


class TodoRepository:
    """Mixin providing todo CRUD operations for the Database class."""

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
    ) -> Todo:
        """Add a new task."""
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
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
    ) -> Todo:
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
        """Retrieve a single todo by ID."""
        with self.Session() as session:  # type: ignore[attr-defined]
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")
            return todo

    def get_todos(self, status: Optional[str] = "pending") -> list[Todo]:
        """Retrieve tasks, ordered by priority and urgency."""
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
        content: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[list[str]] = None,
        completed_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        reminder_last_sent: Optional[datetime] = None,
    ) -> Todo:
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
        """Query for urgent tasks that need a reminder alert."""
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
        """Delete a task by ID."""
        return self._queued_write(self._delete_todo_sync, todo_id)  # type: ignore[attr-defined]

    def _delete_todo_sync(self, todo_id: int) -> bool:
        with self.Session() as session:  # type: ignore[attr-defined]
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
    ) -> list[Todo]:
        """Retrieve all todos, optionally filtered."""
        with self.Session() as session:  # type: ignore[attr-defined]
            stmt = select(Todo).order_by(Todo.created_at.desc())
            if project:
                stmt = stmt.where(Todo.project == project)
            if tags:
                stmt = stmt.join(Tag, Tag.todo_id == Todo.id).where(Tag.name.in_(tags))
            return list(session.scalars(stmt).all())
