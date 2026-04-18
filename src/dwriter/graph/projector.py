"""Projects SQLite records into the LadybugDB graph index (CQRS read side)."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ladybug as lb

from .schema import FTS_INDICES, NODE_TABLES, REL_TABLES

if TYPE_CHECKING:
    from ..database import Database, Entry, Todo


def get_graph_path() -> Path:
    """Returns the default path for the LadybugDB graph index directory."""
    return Path.home() / ".dwriter" / "graph.lbug"


class GraphProjector:
    """Projects dwriter SQLite records into a LadybugDB graph index.

    SQLite is the write-of-record. This index is derived and regenerable.
    All methods are thread-safe via an internal lock.
    """

    def __init__(self, graph_path: Path | None = None) -> None:
        """Opens (or creates) the graph database and ensures the schema exists."""
        self._path = str(graph_path or get_graph_path())
        self._db = lb.Database(self._path)
        self._conn = lb.Connection(self._db)
        self._lock = threading.Lock()
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _existing_tables(self) -> set[str]:
        try:
            result = self._conn.execute("CALL SHOW_TABLES() RETURN name")
            return {row[0] for row in result}  # type: ignore[index]
        except Exception:
            return set()

    def _load_extensions(self) -> None:
        for ext in ("fts", "vector"):
            try:
                self._conn.execute(f"INSTALL {ext.upper()}")
                self._conn.execute(f"LOAD EXTENSION {ext.upper()}")
            except Exception:
                pass

    def _ensure_schema(self) -> None:
        self._load_extensions()
        existing = self._existing_tables()
        for ddl in NODE_TABLES + REL_TABLES:
            table_name = ddl.split("TABLE")[1].split("(")[0].strip()
            if table_name not in existing:
                try:
                    self._conn.execute(ddl)
                except Exception:
                    pass
        for node_table, index_name, props in FTS_INDICES:
            props_str = str(props).replace("'", '"')
            try:
                self._conn.execute(
                    f"CALL CREATE_FTS_INDEX('{node_table}', "  # noqa: E501
                    f"'{index_name}', {props_str})"
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Projection helpers
    # ------------------------------------------------------------------

    def _upsert_tag(self, name: str) -> None:
        try:
            self._conn.execute("CREATE (:Tag {name: $name})", {"name": name})
        except Exception:
            pass

    def _upsert_project(self, name: str) -> None:
        try:
            self._conn.execute("CREATE (:Project {name: $name})", {"name": name})
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Public projection API
    # ------------------------------------------------------------------

    def project_entry(self, entry: Entry) -> None:
        """Upserts one Entry node and its tag/project edges."""
        created = entry.created_at.isoformat() if entry.created_at else ""
        with self._lock:
            self._conn.execute(
                "MATCH (e:Entry {uuid: $uuid}) DETACH DELETE e",
                {"uuid": entry.uuid},
            )
            self._conn.execute(
                """CREATE (:Entry {
                    uuid: $uuid, content: $content, project: $project,
                    created_at: $created_at, implicit_mood: $implicit_mood,
                    life_domain: $life_domain, energy_level: $energy_level
                })""",
                {
                    "uuid": entry.uuid,
                    "content": entry.content or "",
                    "project": entry.project or "",
                    "created_at": created,
                    "implicit_mood": entry.implicit_mood or "",
                    "life_domain": entry.life_domain or "",
                    "energy_level": float(entry.energy_level or 0.0),
                },
            )
            for tag in entry.tag_names:
                self._upsert_tag(tag)
                self._conn.execute(
                    "MATCH (e:Entry {uuid: $u}), (t:Tag {name: $t})"
                    " CREATE (e)-[:ENTRY_HAS_TAG]->(t)",
                    {"u": entry.uuid, "t": tag},
                )
            if entry.project:
                self._upsert_project(entry.project)
                self._conn.execute(
                    "MATCH (e:Entry {uuid: $u}), (p:Project {name: $p})"
                    " CREATE (e)-[:ENTRY_IN_PROJECT]->(p)",
                    {"u": entry.uuid, "p": entry.project},
                )

    def project_todo(self, todo: Todo) -> None:
        """Upserts one Todo node and its tag/project edges."""
        created = todo.created_at.isoformat() if todo.created_at else ""
        completed = todo.completed_at.isoformat() if todo.completed_at else ""
        due = todo.due_date.isoformat() if todo.due_date else ""
        with self._lock:
            self._conn.execute(
                "MATCH (t:Todo {uuid: $uuid}) DETACH DELETE t",
                {"uuid": todo.uuid},
            )
            self._conn.execute(
                """CREATE (:Todo {
                    uuid: $uuid, content: $content, project: $project,
                    priority: $priority, status: $status,
                    due_date: $due, created_at: $created, completed_at: $completed
                })""",
                {
                    "uuid": todo.uuid,
                    "content": todo.content or "",
                    "project": todo.project or "",
                    "priority": todo.priority or "normal",
                    "status": todo.status or "pending",
                    "due": due,
                    "created": created,
                    "completed": completed,
                },
            )
            for tag in todo.tag_names:
                self._upsert_tag(tag)
                self._conn.execute(
                    "MATCH (t:Todo {uuid: $u}), (tag:Tag {name: $t})"
                    " CREATE (t)-[:TODO_HAS_TAG]->(tag)",
                    {"u": todo.uuid, "t": tag},
                )
            if todo.project:
                self._upsert_project(todo.project)
                self._conn.execute(
                    "MATCH (t:Todo {uuid: $u}), (p:Project {name: $p})"
                    " CREATE (t)-[:TODO_IN_PROJECT]->(p)",
                    {"u": todo.uuid, "p": todo.project},
                )

    def build_index(self, db: Database) -> None:
        """Clears and fully rebuilds the graph index from SQLite."""
        with self._lock:
            for node_type in ("Entry", "Todo", "Tag", "Project"):
                try:
                    self._conn.execute(f"MATCH (n:{node_type}) DETACH DELETE n")
                except Exception:
                    pass

        for entry in db.get_all_entries():
            self.project_entry(entry)
        for todo in db.get_all_todos():
            self.project_todo(todo)

    # ------------------------------------------------------------------
    # Query API (used by ai/tools.py)
    # ------------------------------------------------------------------

    def run_cypher(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Executes a read-only Cypher query and returns rows as dicts."""
        with self._lock:
            result = self._conn.execute(query, params or {})
            return list(result.rows_as_dict())  # type: ignore[union-attr, arg-type]

    def search_fts(
        self,
        query: str,
        node_table: str,
        index_name: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Runs a full-text search and returns matching nodes with scores."""
        cypher = (
            f"CALL QUERY_FTS_INDEX('{node_table}', '{index_name}', $q, top := {limit})"
            " RETURN node.uuid AS uuid, node.content AS content,"
            " node.project AS project, score ORDER BY score DESC"
        )
        with self._lock:
            result = self._conn.execute(cypher, {"q": query})
            return list(result.rows_as_dict())  # type: ignore[union-attr, arg-type]
