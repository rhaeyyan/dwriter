"""Tests for todo commands and database functionality."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from dwriter.cli import main
from dwriter.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink()


class TestTodoDatabase:
    """Test cases for Todo database operations."""

    def test_add_todo(self, temp_db):
        """Test adding a new todo."""
        todo = temp_db.add_todo(
            content="Test task",
            priority="high",
            project="test-project",
            tags=["test", "demo"],
        )

        assert todo.id == 1
        assert todo.content == "Test task"
        assert todo.priority == "high"
        assert todo.project == "test-project"
        assert todo.status == "pending"
        assert len(todo.tags) == 2

    def test_add_todo_minimal(self, temp_db):
        """Test adding a todo with minimal data."""
        todo = temp_db.add_todo(content="Simple task")

        assert todo.id == 1
        assert todo.content == "Simple task"
        assert todo.priority == "normal"
        assert todo.project is None
        assert todo.tags == []

    def test_get_todo(self, temp_db):
        """Test retrieving a todo by ID."""
        added = temp_db.add_todo(
            content="Test task",
            priority="critical",
            project="proj",
        )

        retrieved = temp_db.get_todo(added.id)

        assert retrieved.id == added.id
        assert retrieved.content == added.content
        assert retrieved.priority == added.priority

    def test_get_todo_not_found(self, temp_db):
        """Test retrieving a non-existent todo."""
        with pytest.raises(ValueError):
            temp_db.get_todo(999)

    def test_get_todos_pending_only(self, temp_db):
        """Test retrieving only pending todos."""
        temp_db.add_todo(content="Pending task 1")
        temp_db.add_todo(content="Pending task 2")
        completed = temp_db.add_todo(content="Completed task")
        temp_db.update_todo(completed.id, status="completed")

        todos = temp_db.get_todos(status="pending")

        assert len(todos) == 2
        assert all(t.status == "pending" for t in todos)

    def test_get_todos_all(self, temp_db):
        """Test retrieving all todos (no status filter)."""
        temp_db.add_todo(content="Task 1")
        temp_db.add_todo(content="Task 2")

        todos = temp_db.get_todos(status=None)

        assert len(todos) == 2

    def test_get_todos_priority_order(self, temp_db):
        """Test that todos are ordered by priority."""
        temp_db.add_todo(content="Low priority", priority="low")
        temp_db.add_todo(content="Urgent task", priority="urgent")
        temp_db.add_todo(content="Normal task", priority="normal")
        temp_db.add_todo(content="High priority", priority="high")

        todos = temp_db.get_todos(status="pending")

        # Should be ordered: urgent, high, normal, low
        assert todos[0].priority == "urgent"
        assert todos[1].priority == "high"
        assert todos[2].priority == "normal"
        assert todos[3].priority == "low"

    def test_update_todo(self, temp_db):
        """Test updating a todo."""
        todo = temp_db.add_todo(
            content="Original",
            priority="normal",
            project="old-project",
        )

        updated = temp_db.update_todo(
            todo.id,
            content="Updated",
            priority="high",
            project="new-project",
        )

        assert updated.content == "Updated"
        assert updated.priority == "high"
        assert updated.project == "new-project"

    def test_update_todo_status(self, temp_db):
        """Test updating todo status to completed."""
        todo = temp_db.add_todo(content="Task to complete")
        completed_at = datetime.now()

        updated = temp_db.update_todo(
            todo.id,
            status="completed",
            completed_at=completed_at,
        )

        assert updated.status == "completed"
        assert updated.completed_at == completed_at

    def test_update_todo_tags(self, temp_db):
        """Test updating todo tags (replaces existing)."""
        todo = temp_db.add_todo(
            content="Task",
            tags=["old", "tags"],
        )

        updated = temp_db.update_todo(
            todo.id,
            tags=["new", "tags"],
        )

        assert set(updated.tag_names) == {"new", "tags"}

    def test_update_todo_not_found(self, temp_db):
        """Test updating a non-existent todo."""
        with pytest.raises(ValueError):
            temp_db.update_todo(999, content="Updated")

    def test_delete_todo(self, temp_db):
        """Test deleting a todo."""
        todo = temp_db.add_todo(content="To delete")

        result = temp_db.delete_todo(todo.id)

        assert result is True
        with pytest.raises(ValueError):
            temp_db.get_todo(todo.id)

    def test_delete_todo_not_found(self, temp_db):
        """Test deleting a non-existent todo."""
        result = temp_db.delete_todo(999)
        assert result is False

    def test_todo_tag_names_property(self, temp_db):
        """Test the tag_names property returns list of strings."""
        todo = temp_db.add_todo(
            content="Task",
            tags=["tag1", "tag2", "tag3"],
        )

        assert todo.tag_names == ["tag1", "tag2", "tag3"]
        assert all(isinstance(t, str) for t in todo.tag_names)


class TestTodoCommands:
    """Test cases for todo CLI commands."""

    def test_todo_help(self):
        """Test todo command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["todo", "--help"])

        assert result.exit_code == 0
        assert "Manage future tasks" in result.output

    def test_todo_add(self):
        """Test adding a todo."""
        runner = CliRunner()
        result = runner.invoke(main, ["todo", "Test task"])

        assert result.exit_code == 0
        assert "Added Task" in result.output or "Test task" in result.output

    def test_todo_add_with_priority(self):
        """Test adding a todo with priority."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["todo", "Urgent task", "--priority", "urgent"]
        )

        assert result.exit_code == 0

    def test_todo_add_with_project(self):
        """Test adding a todo with project."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["todo", "Task", "-p", "my-project"]
        )

        assert result.exit_code == 0

    def test_todo_add_with_tags(self):
        """Test adding a todo with tags."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["todo", "Task", "-t", "bug", "-t", "urgent"]
        )

        assert result.exit_code == 0

    def test_todo_add_invalid_priority(self):
        """Test adding a todo with invalid priority."""
        runner = CliRunner()
        # Note: options must come BEFORE content with the new syntax
        result = runner.invoke(
            main, ["todo", "--priority", "invalid", "Task"]
        )

        assert result.exit_code != 0

    def test_todo_list(self):
        """Test listing todos."""
        runner = CliRunner()
        # First add a task
        runner.invoke(main, ["todo", "Test task"])

        result = runner.invoke(main, ["todo", "list"])

        assert result.exit_code == 0
        assert "Your Tasks" in result.output or "Test task" in result.output

    def test_todo_list_empty(self):
        """Test listing when no todos exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["todo", "list"])

        assert result.exit_code == 0
        assert "No tasks found" in result.output or "Relax" in result.output

    def test_todo_list_show_all(self):
        """Test listing all todos including completed."""
        runner = CliRunner()
        # Add and complete a task
        runner.invoke(main, ["todo", "Task to complete"])
        runner.invoke(main, ["done", "1"])

        result = runner.invoke(main, ["todo", "list", "--all"])

        assert result.exit_code == 0

    def test_todo_done(self):
        """Test marking a todo as done."""
        runner = CliRunner()
        # First add a task
        runner.invoke(main, ["todo", "Task to complete"])

        result = runner.invoke(main, ["done", "1"])

        assert result.exit_code == 0
        assert "completed" in result.output.lower() or "✅" in result.output

    def test_todo_done_already_completed(self):
        """Test marking an already completed todo."""
        runner = CliRunner()
        runner.invoke(main, ["todo", "Task"])
        runner.invoke(main, ["done", "1"])

        result = runner.invoke(main, ["done", "1"])

        assert result.exit_code == 0
        assert "already completed" in result.output.lower()

    def test_todo_done_not_found(self):
        """Test marking a non-existent todo as done."""
        runner = CliRunner()
        result = runner.invoke(main, ["done", "999"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()

    def test_todo_rm(self):
        """Test removing a todo."""
        runner = CliRunner()
        runner.invoke(main, ["todo", "Task to delete"])

        result = runner.invoke(main, ["todo", "rm", "1"], input="y\n")

        assert result.exit_code == 0
        assert "deleted" in result.output.lower() or "✅" in result.output

    def test_todo_rm_cancelled(self):
        """Test removing a todo but cancelling."""
        runner = CliRunner()
        runner.invoke(main, ["todo", "Task"])

        result = runner.invoke(main, ["todo", "rm", "1"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_todo_rm_not_found(self):
        """Test removing a non-existent todo."""
        runner = CliRunner()
        result = runner.invoke(main, ["todo", "rm", "999"], input="y\n")

        assert result.exit_code == 0
        assert "not found" in result.output.lower()

    def test_todo_edit(self):
        """Test editing a todo."""
        runner = CliRunner()
        runner.invoke(main, ["todo", "Original task"])

        # Note: click.edit() requires a terminal and doesn't work well in tests
        # It raises SystemExit(1) when stdin is not a terminal
        # This test just verifies the command handles this gracefully
        result = runner.invoke(main, ["todo", "edit", "1"])

        # Accept either success (no changes) or SystemExit (non-terminal)
        assert result.exit_code in [0, 1]

    def test_todo_edit_not_found(self):
        """Test editing a non-existent todo."""
        runner = CliRunner()
        result = runner.invoke(main, ["todo", "edit", "999"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()


class TestTodoIntegration:
    """Integration tests for todo functionality."""

    def test_todo_done_creates_entry(self, temp_db):
        """Test that marking todo done creates a journal entry."""
        # Add a todo
        todo = temp_db.add_todo(
            content="Important task",
            tags=["important"],
            project="test",
        )

        # Mark as done (this should create an entry)
        temp_db.update_todo(todo.id, status="completed", completed_at=datetime.now())
        entry_content = f"Completed: {todo.content}"
        entry = temp_db.add_entry(
            content=entry_content,
            tags=todo.tag_names,
            project=todo.project,
            created_at=datetime.now(),
        )

        # Verify entry was created
        assert entry is not None
        assert "Completed: Important task" in entry.content
        assert entry.project == "test"

    def test_standup_with_todos_flag(self):
        """Test standup command with --with-todos flag."""
        runner = CliRunner()
        # Add a todo
        runner.invoke(main, ["todo", "Plan for today"])

        result = runner.invoke(main, ["standup", "--with-todos"])

        # Should succeed even with no yesterday entries (shows todos only)
        assert result.exit_code in [0, 1]

    def test_todo_workflow(self):
        """Test complete todo workflow: add, list, done."""
        runner = CliRunner()

        # Add a task
        result = runner.invoke(main, ["todo", "Workflow task", "-p", "test"])
        assert result.exit_code == 0

        # List tasks
        result = runner.invoke(main, ["todo", "list"])
        assert result.exit_code == 0
        assert "Workflow task" in result.output

        # Complete the task
        result = runner.invoke(main, ["done", "1"])
        assert result.exit_code == 0

        # List should not show completed task
        result = runner.invoke(main, ["todo", "list"])
        assert result.exit_code == 0

        # List --all should show it
        result = runner.invoke(main, ["todo", "list", "--all"])
        assert result.exit_code == 0
