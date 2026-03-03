"""Database layer for Day Writer.

This module handles all SQLite database operations for storing and retrieving
journal entries.
"""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional


@dataclass
class Entry:
    """Represents a journal entry.

    Attributes:
        id: Unique identifier for the entry.
        content: The text content of the entry.
        created_at: Timestamp when the entry was created.
        tags: List of tags associated with the entry.
        project: Optional project name.
    """

    id: int
    content: str
    created_at: datetime
    tags: List[str]
    project: Optional[str] = None


class Database:
    """SQLite database manager for Day Writer entries.

    This class handles database connections, schema management, and CRUD
    operations for journal entries.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database connection.

        Args:
            db_path: Optional path to the database file. If not provided,
                uses the default location at ~/.day-writer/entries.db.
        """
        if db_path is None:
            data_dir = Path.home() / ".day-writer"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "entries.db"

        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections.

        Yields:
            A sqlite3.Connection object.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initialize the database schema."""
        with self.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    project TEXT,
                    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_created_at
                ON entries(created_at)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags_entry_id
                ON tags(entry_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags_name
                ON tags(name)
            """)

            conn.commit()

    def add_entry(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
    ) -> Entry:
        """Add a new journal entry.

        Args:
            content: The text content of the entry.
            tags: Optional list of tags to associate with the entry.
            project: Optional project name.

        Returns:
            The created Entry object.
        """
        with self.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO entries (content, project) VALUES (?, ?)",
                (content, project),
            )
            entry_id = cursor.lastrowid

            if tags:
                for tag in tags:
                    conn.execute(
                        "INSERT INTO tags (entry_id, name) VALUES (?, ?)",
                        (entry_id, tag),
                    )

            conn.commit()

            return self.get_entry(entry_id)

    def get_entry(self, entry_id: int) -> Entry:
        """Retrieve a single entry by ID.

        Args:
            entry_id: The ID of the entry to retrieve.

        Returns:
            The Entry object.

        Raises:
            ValueError: If no entry exists with the given ID.
        """
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM entries WHERE id = ?", (entry_id,)
            ).fetchone()

            if row is None:
                msg = f"Entry with id {entry_id} not found"
                raise ValueError(msg)

            tags = self._get_tags_for_entry(conn, entry_id)

            return Entry(
                id=row["id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
                tags=tags,
                project=row["project"],
            )

    def get_entries_by_date(
        self,
        date: datetime,
    ) -> List[Entry]:
        """Retrieve all entries for a specific date.

        Args:
            date: The date to filter entries by.

        Returns:
            A list of Entry objects for the specified date.
        """
        with self.connection() as conn:
            # Use SQLite's DATE function for reliable date comparison
            date_str = date.strftime("%Y-%m-%d")

            rows = conn.execute(
                """
                SELECT * FROM entries
                WHERE DATE(created_at) = ?
                ORDER BY created_at ASC
                """,
                (date_str,),
            ).fetchall()

            entries = []
            for row in rows:
                tags = self._get_tags_for_entry(conn, row["id"])
                entries.append(
                    Entry(
                        id=row["id"],
                        content=row["content"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        tags=tags,
                        project=row["project"],
                    )
                )

            return entries

    def get_entries_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Entry]:
        """Retrieve entries within a date range.

        Args:
            start_date: The start date (inclusive).
            end_date: The end date (inclusive).

        Returns:
            A list of Entry objects within the specified range.
        """
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM entries
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at ASC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            ).fetchall()

            entries = []
            for row in rows:
                tags = self._get_tags_for_entry(conn, row["id"])
                entries.append(
                    Entry(
                        id=row["id"],
                        content=row["content"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        tags=tags,
                        project=row["project"],
                    )
                )

            return entries

    def get_latest_entry(self) -> Optional[Entry]:
        """Retrieve the most recent entry.

        Returns:
            The most recent Entry, or None if no entries exist.
        """
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM entries ORDER BY created_at DESC LIMIT 1"
            ).fetchone()

            if row is None:
                return None

            tags = self._get_tags_for_entry(conn, row["id"])

            return Entry(
                id=row["id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
                tags=tags,
                project=row["project"],
            )

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID.

        Args:
            entry_id: The ID of the entry to delete.

        Returns:
            True if the entry was deleted, False if it didn't exist.
        """
        with self.connection() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_entry(
        self,
        entry_id: int,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
    ) -> Entry:
        """Update an existing entry.

        Args:
            entry_id: The ID of the entry to update.
            content: New content for the entry (optional).
            tags: New list of tags (optional, replaces existing).
            project: New project name (optional).

        Returns:
            The updated Entry object.

        Raises:
            ValueError: If no entry exists with the given ID.
        """
        with self.connection() as conn:
            if content is not None or project is not None:
                current = self.get_entry(entry_id)
                new_content = content if content is not None else current.content
                new_project = project if project is not None else current.project

                conn.execute(
                    """
                    UPDATE entries
                    SET content = ?, project = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (new_content, new_project, entry_id),
                )

            if tags is not None:
                conn.execute("DELETE FROM tags WHERE entry_id = ?", (entry_id,))
                for tag in tags:
                    conn.execute(
                        "INSERT INTO tags (entry_id, name) VALUES (?, ?)",
                        (entry_id, tag),
                    )

            conn.commit()
            return self.get_entry(entry_id)

    def delete_entries_before(self, before_date: datetime) -> int:
        """Delete all entries before a specific date.

        Args:
            before_date: Delete entries created before this date.

        Returns:
            The number of entries deleted.
        """
        with self.connection() as conn:
            cursor = conn.execute(
                "DELETE FROM entries WHERE created_at < ?",
                (before_date.isoformat(),),
            )
            conn.commit()
            return cursor.rowcount

    def get_all_entries_count(self) -> int:
        """Get the total count of all entries.

        Returns:
            The total number of entries in the database.
        """
        with self.connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM entries").fetchone()
            return row["count"]

    def get_entries_with_streaks(self) -> List[datetime]:
        """Get dates with entries for streak calculation.

        Returns:
            A list of unique dates (datetime objects) that have entries.
        """
        with self.connection() as conn:
            rows = conn.execute("""
                SELECT DISTINCT DATE(created_at) as entry_date
                FROM entries
                ORDER BY entry_date DESC
                """).fetchall()

            return [datetime.strptime(row["entry_date"], "%Y-%m-%d") for row in rows]

    def _get_tags_for_entry(
        self,
        conn: sqlite3.Connection,
        entry_id: int,
    ) -> List[str]:
        """Retrieve tags for a specific entry.

        Args:
            conn: Database connection.
            entry_id: The entry ID to get tags for.

        Returns:
            A list of tag names.
        """
        rows = conn.execute(
            "SELECT name FROM tags WHERE entry_id = ?", (entry_id,)
        ).fetchall()
        return [row["name"] for row in rows]
