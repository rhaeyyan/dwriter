"""Tests for the database module."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from dwriter.database import Database, Entry


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink()


class TestDatabase:
    """Test cases for the Database class."""

    def test_add_entry(self, temp_db):
        """Test adding a new entry."""
        entry = temp_db.add_entry(
            content="Test entry",
            tags=["test", "demo"],
            project="test-project",
        )

        assert entry.id == 1
        assert entry.content == "Test entry"
        assert entry.tag_names == ["test", "demo"]
        assert entry.project == "test-project"
        assert isinstance(entry.created_at, datetime)

    def test_add_entry_minimal(self, temp_db):
        """Test adding an entry with minimal data."""
        entry = temp_db.add_entry(content="Simple entry")

        assert entry.id == 1
        assert entry.content == "Simple entry"
        assert entry.tags == []
        assert entry.project is None

    def test_get_entry(self, temp_db):
        """Test retrieving an entry by ID."""
        added = temp_db.add_entry(
            content="Test entry",
            tags=["test"],
            project="proj",
        )

        retrieved = temp_db.get_entry(added.id)

        assert retrieved.id == added.id
        assert retrieved.content == added.content
        assert retrieved.tag_names == added.tag_names
        assert retrieved.project == added.project

    def test_get_entry_not_found(self, temp_db):
        """Test retrieving a non-existent entry."""
        with pytest.raises(ValueError):
            temp_db.get_entry(999)

    def test_get_entries_by_date(self, temp_db):
        """Test retrieving entries for a specific date."""
        today = datetime.now()
        temp_db.add_entry(content="Entry 1")
        temp_db.add_entry(content="Entry 2")

        entries = temp_db.get_entries_by_date(today)

        assert len(entries) == 2
        assert entries[0].content == "Entry 1"
        assert entries[1].content == "Entry 2"

    def test_delete_entry(self, temp_db):
        """Test deleting an entry."""
        entry = temp_db.add_entry(content="To delete")

        result = temp_db.delete_entry(entry.id)

        assert result is True
        with pytest.raises(ValueError):
            temp_db.get_entry(entry.id)

    def test_delete_entry_not_found(self, temp_db):
        """Test deleting a non-existent entry."""
        result = temp_db.delete_entry(999)
        assert result is False

    def test_update_entry(self, temp_db):
        """Test updating an entry."""
        entry = temp_db.add_entry(
            content="Original",
            tags=["old"],
            project="old-project",
        )

        updated = temp_db.update_entry(
            entry.id,
            content="Updated",
            tags=["new"],
            project="new-project",
        )

        assert updated.content == "Updated"
        assert updated.tag_names == ["new"]
        assert updated.project == "new-project"

    def test_update_entry_partial(self, temp_db):
        """Test updating only some fields of an entry."""
        entry = temp_db.add_entry(
            content="Original",
            tags=["tag1"],
            project="proj",
        )

        updated = temp_db.update_entry(entry.id, content="New content only")

        assert updated.content == "New content only"
        assert updated.tag_names == ["tag1"]  # Unchanged
        assert updated.project == "proj"  # Unchanged

    def test_get_latest_entry(self, temp_db):
        """Test retrieving the most recent entry."""
        temp_db.add_entry(content="First")
        temp_db.add_entry(content="Second")
        temp_db.add_entry(content="Third")

        latest = temp_db.get_latest_entry()

        assert latest.content == "Third"

    def test_get_latest_entry_empty(self, temp_db):
        """Test retrieving latest entry from empty database."""
        latest = temp_db.get_latest_entry()
        assert latest is None

    def test_get_all_entries_count(self, temp_db):
        """Test counting all entries."""
        temp_db.add_entry(content="Entry 1")
        temp_db.add_entry(content="Entry 2")
        temp_db.add_entry(content="Entry 3")

        count = temp_db.get_all_entries_count()

        assert count == 3

    def test_delete_entries_before(self, temp_db):
        """Test bulk deleting entries before a date."""
        temp_db.add_entry(content="Old entry")

        # Manually update the created_at to be in the past
        with temp_db.connection() as conn:
            conn.execute(
                "UPDATE entries SET created_at = ? WHERE id = 1",
                ("2020-01-01 00:00:00",),
            )
            conn.commit()

        temp_db.add_entry(content="New entry")

        cutoff = datetime(2021, 1, 1)
        deleted = temp_db.delete_entries_before(cutoff)

        assert deleted == 1
        assert temp_db.get_all_entries_count() == 1

    def test_get_entries_with_streaks(self, temp_db):
        """Test getting dates with entries for streak calculation."""
        temp_db.add_entry(content="Entry 1")
        temp_db.add_entry(content="Entry 2")

        dates = temp_db.get_entries_with_streaks()

        assert len(dates) >= 1
        assert all(isinstance(d, datetime) for d in dates)

    def test_entry_dataclass(self):
        """Test the Entry model tag_names property."""
        entry = Entry(
            id=1,
            content="Test",
            created_at=datetime.now(),
            project="test",
        )
        # Entry is now a SQLAlchemy model - tags are Tag objects
        # The tag_names property provides string access
        assert entry.id == 1
        assert entry.content == "Test"
        assert entry.project == "test"
        assert entry.tags == []
        assert entry.tag_names == []
