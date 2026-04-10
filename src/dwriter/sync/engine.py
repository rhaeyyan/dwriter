"""Serialization engine for database synchronization."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..database import Database


def serialize_db(db: Database, sync_dir: Path) -> None:
    """Dump the database to JSONL files using atomic writes.

    Args:
        db: The database instance.
        sync_dir: Directory to store .jsonl files.
    """
    sync_dir.mkdir(parents=True, exist_ok=True)

    # Entries
    entries_path = sync_dir / "entries.jsonl"
    entries_tmp = sync_dir / "entries.tmp.jsonl"
    with open(entries_tmp, "w") as f:
        for entry in db.get_all_entries():
            data = {
                "uuid": entry.uuid,
                "lamport_clock": entry.lamport_clock,
                "content": entry.content,
                "project": entry.project,
                "created_at": entry.created_at.isoformat(),
                "tags": entry.tag_names,
                "todo_id": entry.todo_id,
                "life_domain": entry.life_domain,
                "energy_level": entry.energy_level,
            }
            f.write(json.dumps(data) + "\n")
    os.replace(entries_tmp, entries_path)

    # Todos
    todos_path = sync_dir / "todos.jsonl"
    todos_tmp = sync_dir / "todos.tmp.jsonl"
    with open(todos_tmp, "w") as f:
        for todo in db.get_all_todos():
            data = {
                "uuid": todo.uuid,
                "lamport_clock": todo.lamport_clock,
                "content": todo.content,
                "project": todo.project,
                "priority": todo.priority,
                "status": todo.status,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "tags": todo.tag_names,
                "created_at": todo.created_at.isoformat(),
                "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
            }
            f.write(json.dumps(data) + "\n")
    os.replace(todos_tmp, todos_path)


def merge_jsonl_to_db(db: Database, sync_dir: Path) -> None:
    """Merge JSONL data back into SQLite using CRDT (Lamport clock) logic.

    Args:
        db: The database instance.
        sync_dir: Directory containing .jsonl files.
    """
    entries_path = sync_dir / "entries.jsonl"
    if entries_path.exists():
        with open(entries_path) as f:
            for line in f:
                _merge_entry(db, json.loads(line))

    todos_path = sync_dir / "todos.jsonl"
    if todos_path.exists():
        with open(todos_path) as f:
            for line in f:
                _merge_todo(db, json.loads(line))


def _merge_entry(db: Database, data: dict[str, Any]) -> None:
    """Merge a single entry record using Lamport clock ordering."""
    from ..database import Entry, Tag

    with db.Session() as session:
        from sqlalchemy import select
        existing = session.scalar(select(Entry).where(Entry.uuid == data["uuid"]))

        if not existing or data["lamport_clock"] > existing.lamport_clock:
            if not existing:
                existing = Entry(uuid=data["uuid"])
                session.add(existing)

            existing.lamport_clock = data["lamport_clock"]
            existing.content = data["content"]
            existing.project = data["project"]
            existing.created_at = datetime.fromisoformat(data["created_at"])
            existing.life_domain = data.get("life_domain")
            existing.energy_level = data.get("energy_level")
            existing.tags = [Tag(name=t) for t in data["tags"]]
            session.commit()


def _merge_todo(db: Database, data: dict[str, Any]) -> None:
    """Merge a single todo record using Lamport clock ordering."""
    from ..database import Todo, TodoTag

    with db.Session() as session:
        from sqlalchemy import select
        existing = session.scalar(select(Todo).where(Todo.uuid == data["uuid"]))

        if not existing or data["lamport_clock"] > existing.lamport_clock:
            if not existing:
                existing = Todo(uuid=data["uuid"])
                session.add(existing)

            existing.lamport_clock = data["lamport_clock"]
            existing.content = data["content"]
            existing.project = data["project"]
            existing.priority = data["priority"]
            existing.status = data["status"]
            existing.due_date = (
                datetime.fromisoformat(data["due_date"]) if data["due_date"] else None
            )
            existing.created_at = datetime.fromisoformat(data["created_at"])
            existing.completed_at = (
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"]
                else None
            )
            existing.tags = [TodoTag(name=t) for t in data["tags"]]
            session.commit()
