"""Schema migrations for dwriter database."""

from __future__ import annotations

import os
import shutil
import sys
import uuid
from datetime import datetime

from rich.console import Console
from sqlalchemy.engine import Engine


def run_migrations(engine: Engine, db_path: str) -> None:
    """Run schema migrations with backup/rollback safeguards."""
    if not os.path.exists(db_path):
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{db_path}.{timestamp}.bak"
    shutil.copy2(db_path, backup_path)

    try:
        with engine.connect():
            import sqlite3

            with sqlite3.connect(db_path) as conn:
                # Ensure sync_metadata table exists
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS sync_metadata "
                    "(key TEXT PRIMARY KEY, value TEXT)"
                )

                # --- todos ---
                cursor = conn.execute("PRAGMA table_info(todos)")
                todo_cols = [row[1] for row in cursor.fetchall()]

                if "uuid" not in todo_cols:
                    conn.execute("ALTER TABLE todos ADD COLUMN uuid TEXT")
                    cursor = conn.execute("SELECT id FROM todos WHERE uuid IS NULL")
                    for row in cursor.fetchall():
                        conn.execute(
                            "UPDATE todos SET uuid = ? WHERE id = ?",
                            (str(uuid.uuid4()), row[0]),
                        )

                if "lamport_clock" not in todo_cols:
                    conn.execute(
                        "ALTER TABLE todos ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                    )

                if "due_date" not in todo_cols:
                    conn.execute("ALTER TABLE todos ADD COLUMN due_date DATETIME")

                if "reminder_last_sent" not in todo_cols:
                    conn.execute(
                        "ALTER TABLE todos ADD COLUMN reminder_last_sent DATETIME"
                    )

                # --- entries ---
                cursor = conn.execute("PRAGMA table_info(entries)")
                entry_cols = [row[1] for row in cursor.fetchall()]

                if "uuid" not in entry_cols:
                    conn.execute("ALTER TABLE entries ADD COLUMN uuid TEXT")
                    cursor = conn.execute(
                        "SELECT id FROM entries WHERE uuid IS NULL"
                    )
                    for row in cursor.fetchall():
                        conn.execute(
                            "UPDATE entries SET uuid = ? WHERE id = ?",
                            (str(uuid.uuid4()), row[0]),
                        )

                if "lamport_clock" not in entry_cols:
                    conn.execute(
                        "ALTER TABLE entries ADD COLUMN lamport_clock INTEGER DEFAULT 0"
                    )

                if "todo_id" not in entry_cols:
                    conn.execute(
                        "ALTER TABLE entries ADD COLUMN todo_id "
                        "INTEGER REFERENCES todos(id) ON DELETE CASCADE"
                    )

                if "life_domain" not in entry_cols:
                    conn.execute(
                        "ALTER TABLE entries ADD COLUMN life_domain STRING"
                    )

                if "energy_level" not in entry_cols:
                    conn.execute(
                        "ALTER TABLE entries ADD COLUMN energy_level INTEGER"
                    )

                # Tag Unification migration: merge todo_tags into tags
                tag_cols = {
                    row[1]
                    for row in conn.execute("PRAGMA table_info(tags)").fetchall()
                }
                if "todo_id" not in tag_cols:
                    conn.execute(
                        "CREATE TABLE tags_new ("
                        "id INTEGER PRIMARY KEY, "
                        "entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE, "
                        "todo_id INTEGER REFERENCES todos(id) ON DELETE CASCADE, "
                        "name TEXT NOT NULL"
                        ")"
                    )
                    conn.execute(
                        "INSERT INTO tags_new (entry_id, name) "
                        "SELECT entry_id, name FROM tags"
                    )
                    if "todo_tags" in {
                        row[0]
                        for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        ).fetchall()
                    }:
                        conn.execute(
                            "INSERT INTO tags_new (todo_id, name) "
                            "SELECT todo_id, name FROM todo_tags"
                        )
                        conn.execute("DROP TABLE todo_tags")
                    conn.execute("DROP TABLE tags")
                    conn.execute("ALTER TABLE tags_new RENAME TO tags")
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS ix_tags_name ON tags (name)"
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS ix_tags_todo_id ON tags (todo_id)"
                    )

                # Orphan cleanup
                conn.execute(
                    "DELETE FROM tags "
                    "WHERE entry_id IS NOT NULL "
                    "AND entry_id NOT IN (SELECT id FROM entries)"
                )
                conn.execute(
                    "DELETE FROM tags "
                    "WHERE todo_id IS NOT NULL "
                    "AND todo_id NOT IN (SELECT id FROM todos)"
                )

                conn.commit()

    except Exception as e:
        shutil.copy2(backup_path, db_path)
        console = Console()
        console.print(f"[bold red]FATAL DATABASE ERROR:[/bold red] Migration failed. {e}")
        console.print("[yellow]Database has been rolled back from backup.[/yellow]")
        sys.exit(1)
