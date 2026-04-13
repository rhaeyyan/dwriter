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
    """Dumps the database to JSONL files for synchronization using atomic writes.

    Args:
        db: The database instance.
        sync_dir: Directory to store .jsonl files.
    """
    sync_dir.mkdir(parents=True, exist_ok=True)

    # 1. Serialize Entries
    entries_path = sync_dir / "entries.jsonl"
    entries_tmp_path = sync_dir / "entries.tmp.jsonl"
    with open(entries_tmp_path, "w") as f:
        entries = db.get_all_entries()
        for entry in entries:
            data = {
                "uuid": entry.uuid,
                "lamport_clock": entry.lamport_clock,
                "content": entry.content,
                "project": entry.project,
                "created_at": entry.created_at.isoformat(),
                "tags": entry.tag_names,
                "todo_id": entry.todo_id,
                "implicit_mood": entry.implicit_mood,
                "life_domain": entry.life_domain,
                "energy_level": entry.energy_level,
            }
            f.write(json.dumps(data) + "\n")
    os.replace(entries_tmp_path, entries_path)

    # 2. Serialize Todos
    todos_path = sync_dir / "todos.jsonl"
    todos_tmp_path = sync_dir / "todos.tmp.jsonl"
    with open(todos_tmp_path, "w") as f:
        todos = db.get_all_todos()
        for todo in todos:
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
                "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,  # noqa: E501
            }
            f.write(json.dumps(data) + "\n")
    os.replace(todos_tmp_path, todos_path)


def merge_jsonl_to_db(db: Database, sync_dir: Path) -> None:
    """Merges JSONL data back into SQLite using CRDT logic.

    Args:
        db: The database instance.
        sync_dir: Directory containing .jsonl files.
    """
    # 1. Merge Entries
    entries_path = sync_dir / "entries.jsonl"
    if entries_path.exists():
        with open(entries_path) as f:
            for line in f:
                data = json.loads(line)
                _merge_entry(db, data)

    # 2. Merge Todos
    todos_path = sync_dir / "todos.jsonl"
    if todos_path.exists():
        with open(todos_path) as f:
            for line in f:
                data = json.loads(line)
                _merge_todo(db, data)


def _merge_entry(db: Database, data: dict[str, Any]) -> None:
    """Merges a single entry based on Lamport clock."""
    from ..database import Entry, Tag

    with db.Session() as session:
        from sqlalchemy import select
        stmt = select(Entry).where(Entry.uuid == data["uuid"])
        existing = session.scalar(stmt)

        if not existing or data["lamport_clock"] > existing.lamport_clock:
            # Update or Create
            if not existing:
                existing = Entry(uuid=data["uuid"])
                session.add(existing)

            existing.lamport_clock = data["lamport_clock"]
            existing.content = data["content"]
            existing.project = data["project"]
            existing.created_at = datetime.fromisoformat(data["created_at"])
            existing.implicit_mood = data["implicit_mood"]
            existing.life_domain = data["life_domain"]
            existing.energy_level = data["energy_level"]
            existing.tags = [Tag(name=t) for t in data["tags"]]

            session.commit()


def _merge_todo(db: Database, data: dict[str, Any]) -> None:
    """Merges a single todo based on Lamport clock."""
    from ..database import Tag, Todo

    with db.Session() as session:
        from sqlalchemy import select
        stmt = select(Todo).where(Todo.uuid == data["uuid"])
        existing = session.scalar(stmt)

        if not existing or data["lamport_clock"] > existing.lamport_clock:
            # Update or Create
            if not existing:
                existing = Todo(uuid=data["uuid"])
                session.add(existing)

            existing.lamport_clock = data["lamport_clock"]
            existing.content = data["content"]
            existing.project = data["project"]
            existing.priority = data["priority"]
            existing.status = data["status"]
            existing.due_date = datetime.fromisoformat(data["due_date"]) if data["due_date"] else None  # noqa: E501
            existing.created_at = datetime.fromisoformat(data["created_at"])
            existing.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None  # noqa: E501
            existing.tags = [Tag(name=t) for t in data["tags"]]

            session.commit()
