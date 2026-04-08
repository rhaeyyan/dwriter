"""Tests for the synchronization engine and CRDT logic."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from dwriter.database import Database, Todo
from dwriter.sync.engine import merge_jsonl_to_db, serialize_db


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink()


@pytest.fixture
def sync_dir():
    """Create a temporary directory for sync files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_crdt_todo_merge_higher_clock_wins(temp_db, sync_dir):
    """Assert that the SQLite merge logic respects the higher lamport_clock."""
    # 1. Create an initial todo in the DB
    todo_uuid = "test-todo-uuid-123"
    with temp_db.Session() as session:
        todo = Todo(
            uuid=todo_uuid,
            lamport_clock=10,
            content="Original content",
            status="pending",
            created_at=datetime.now()
        )
        session.add(todo)
        session.commit()

    # 2. Prepare a JSONL file with a CONFLICTING todo (same UUID, higher clock)
    todos_path = sync_dir / "todos.jsonl"
    conflict_data = {
        "uuid": todo_uuid,
        "lamport_clock": 20, # HIGHER CLOCK
        "content": "Updated via sync",
        "project": "sync-proj",
        "priority": "high",
        "status": "pending",
        "due_date": None,
        "tags": ["sync-tag"],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    
    with open(todos_path, "w") as f:
        f.write(json.dumps(conflict_data) + "\n")

    # 3. Merge
    merge_jsonl_to_db(temp_db, sync_dir)

    # 4. Assert DB state - should have updated
    updated_todo = temp_db.get_all_todos()[0]
    assert updated_todo.uuid == todo_uuid
    assert updated_todo.lamport_clock == 20
    assert updated_todo.content == "Updated via sync"
    assert "sync-tag" in updated_todo.tag_names


def test_crdt_todo_merge_lower_clock_ignored(temp_db, sync_dir):
    """Assert that stale edits (lower lamport_clock) are discarded."""
    # 1. Create an initial todo in the DB
    todo_uuid = "test-todo-uuid-456"
    with temp_db.Session() as session:
        todo = Todo(
            uuid=todo_uuid,
            lamport_clock=100, # HIGHER CLOCK in DB
            content="Most recent content",
            status="pending",
            created_at=datetime.now()
        )
        session.add(todo)
        session.commit()

    # 2. Prepare a JSONL file with a STALE todo (same UUID, lower clock)
    todos_path = sync_dir / "todos.jsonl"
    stale_data = {
        "uuid": todo_uuid,
        "lamport_clock": 50, # LOWER CLOCK
        "content": "Stale content from other machine",
        "project": None,
        "priority": "normal",
        "status": "pending",
        "due_date": None,
        "tags": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    
    with open(todos_path, "w") as f:
        f.write(json.dumps(stale_data) + "\n")

    # 3. Merge
    merge_jsonl_to_db(temp_db, sync_dir)

    # 4. Assert DB state - should NOT have updated
    todo_in_db = temp_db.get_all_todos()[0]
    assert todo_in_db.uuid == todo_uuid
    assert todo_in_db.lamport_clock == 100
    assert todo_in_db.content == "Most recent content"


def test_atomic_serialization(temp_db, sync_dir):
    """Verify that serialize_db creates the expected JSONL files."""
    temp_db.add_entry(content="Sync entry 1")
    temp_db.add_todo(content="Sync todo 1")
    
    serialize_db(temp_db, sync_dir)
    
    assert (sync_dir / "entries.jsonl").exists()
    assert (sync_dir / "todos.jsonl").exists()
    assert not (sync_dir / "entries.tmp.jsonl").exists()
    assert not (sync_dir / "todos.tmp.jsonl").exists()
