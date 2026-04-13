"""Database migration runner for dwriter."""

from __future__ import annotations

import os
import shutil
import sys
import uuid
from datetime import datetime

from rich.console import Console


def run_migrations(engine: object, db_path: str) -> None:
    """Executes manual schema migrations to maintain database compatibility.

    Checks for missing columns and applies ALTER TABLE statements as needed.
    Also performs maintenance tasks like cleaning up orphaned tags.

    Includes automated backup and rollback safeguards to prevent journal
    corruption during failed migrations.

    Args:
        engine: The SQLAlchemy engine instance.
        db_path: Path to the SQLite database file.
    """
    if not os.path.exists(db_path):
        return

    # Create a timestamped backup before migration
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{db_path}.{timestamp}.bak"
    shutil.copy2(db_path, backup_path)

    try:
        with engine.connect():  # type: ignore[attr-defined]
            import sqlite3

            with sqlite3.connect(db_path) as sqlite_conn:
                # SyncMetadata table
                sqlite_conn.execute(
                    "CREATE TABLE IF NOT EXISTS sync_metadata "
                    "(key TEXT PRIMARY KEY, value TEXT)"
                )

                cursor = sqlite_conn.execute("PRAGMA table_info(todos)")
                columns = [row[1] for row in cursor.fetchall()]

                if "uuid" not in columns:
                    sqlite_conn.execute("ALTER TABLE todos ADD COLUMN uuid TEXT")
                    # Initialize existing records with UUIDs
                    cursor = sqlite_conn.execute(
                        "SELECT id FROM todos WHERE uuid IS NULL"
                    )
                    for row in cursor.fetchall():
                        sqlite_conn.execute(
                            "UPDATE todos SET uuid = ? WHERE id = ?",
                            (str(uuid.uuid4()), row[0]),
                        )

                if "lamport_clock" not in columns:
                    sqlite_conn.execute(
                        "ALTER TABLE todos ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                    )

                if "due_date" not in columns:
                    sqlite_conn.execute(
                        "ALTER TABLE todos ADD COLUMN due_date DATETIME"
                    )

                if "reminder_last_sent" not in columns:
                    sqlite_conn.execute(
                        "ALTER TABLE todos ADD COLUMN reminder_last_sent DATETIME"
                    )

                cursor = sqlite_conn.execute("PRAGMA table_info(entries)")
                entry_columns = [row[1] for row in cursor.fetchall()]

                if "uuid" not in entry_columns:
                    sqlite_conn.execute("ALTER TABLE entries ADD COLUMN uuid TEXT")
                    # Initialize existing records with UUIDs
                    cursor = sqlite_conn.execute(
                        "SELECT id FROM entries WHERE uuid IS NULL"
                    )
                    for row in cursor.fetchall():
                        sqlite_conn.execute(
                            "UPDATE entries SET uuid = ? WHERE id = ?",
                            (str(uuid.uuid4()), row[0]),
                        )

                if "lamport_clock" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                    )

                if "todo_id" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN todo_id "
                        "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                    )

                if "implicit_mood" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN implicit_mood STRING"
                    )

                if "life_domain" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN life_domain STRING"
                    )

                if "energy_level" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN energy_level INTEGER"
                    )

                if "embedding" not in entry_columns:
                    sqlite_conn.execute(
                        "ALTER TABLE entries ADD COLUMN embedding LARGEBINARY"
                    )

                # Tag unification: merge todo_tags into tags (one-time migration)
                cursor = sqlite_conn.execute("PRAGMA table_info(tags)")
                tag_columns = [row[1] for row in cursor.fetchall()]

                if "todo_id" not in tag_columns:
                    # Recreate tags with nullable entry_id and new todo_id column
                    sqlite_conn.execute(
                        "CREATE TABLE tags_new ("
                        "id INTEGER PRIMARY KEY, "
                        "entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE, "
                        "todo_id INTEGER REFERENCES todos(id) ON DELETE CASCADE, "
                        "name VARCHAR NOT NULL"
                        ")"
                    )
                    sqlite_conn.execute(
                        "INSERT INTO tags_new (id, entry_id, name) "
                        "SELECT id, entry_id, name FROM tags"
                    )
                    # Migrate existing todo_tags rows if that table still exists
                    cursor = sqlite_conn.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='table' AND name='todo_tags'"
                    )
                    if cursor.fetchone():
                        sqlite_conn.execute(
                            "INSERT INTO tags_new (entry_id, todo_id, name) "
                            "SELECT NULL, todo_id, name FROM todo_tags"
                        )
                    sqlite_conn.execute("DROP TABLE tags")
                    sqlite_conn.execute("DROP TABLE IF EXISTS todo_tags")
                    sqlite_conn.execute(
                        "ALTER TABLE tags_new RENAME TO tags"
                    )
                    sqlite_conn.execute(
                        "CREATE INDEX IF NOT EXISTS ix_tags_name ON tags (name)"
                    )
                    sqlite_conn.execute(
                        "CREATE INDEX IF NOT EXISTS ix_tags_todo_id ON tags (todo_id)"
                    )

                # Clean up orphaned tags
                sqlite_conn.execute(
                    "DELETE FROM tags WHERE entry_id IS NOT NULL "
                    "AND entry_id NOT IN (SELECT id FROM entries)"
                )
                sqlite_conn.execute(
                    "DELETE FROM tags WHERE todo_id IS NOT NULL "
                    "AND todo_id NOT IN (SELECT id FROM todos)"
                )

                sqlite_conn.commit()

        # If successful, we could remove the backup, but keeping it for a short time is safer.  # noqa: E501
    except Exception as e:
        # Restore the backup on failure
        shutil.copy2(backup_path, db_path)
        console = Console()
        console.print(
            f"[bold red]FATAL DATABASE ERROR:[/bold red] Migration failed. {e}"
        )
        console.print("[yellow]Database has been rolled back from backup.[/yellow]")
        sys.exit(1)
