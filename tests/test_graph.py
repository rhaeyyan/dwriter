"""Tests for the LadybugDB graph index module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dwriter.graph import GraphProjector, search_graph_journal, search_graph_todos


@pytest.fixture
def tmp_graph(tmp_path: Path) -> GraphProjector:
    """GraphProjector backed by a temporary LadybugDB directory."""
    return GraphProjector(graph_path=tmp_path / "test.lbug")


@pytest.fixture
def mock_entry() -> MagicMock:
    entry = MagicMock()
    entry.uuid = "entry-uuid-1"
    entry.content = "Implemented login flow for auth-service"
    entry.project = "auth-service"
    entry.created_at.isoformat.return_value = "2026-04-17T10:00:00"
    entry.implicit_mood = "focused"
    entry.life_domain = "work"
    entry.energy_level = 8.0
    entry.tag_names = ["backend", "security"]
    return entry


@pytest.fixture
def mock_todo() -> MagicMock:
    todo = MagicMock()
    todo.uuid = "todo-uuid-1"
    todo.content = "Write integration tests for auth-service"
    todo.project = "auth-service"
    todo.priority = "high"
    todo.status = "pending"
    todo.due_date = None
    todo.created_at.isoformat.return_value = "2026-04-17T09:00:00"
    todo.completed_at = None
    todo.tag_names = ["testing"]
    return todo


class TestGraphProjectorSchema:
    def test_projector_initializes(self, tmp_graph: GraphProjector) -> None:
        assert tmp_graph is not None

    def test_schema_tables_created(self, tmp_graph: GraphProjector) -> None:
        tables = tmp_graph._existing_tables()
        assert "Entry" in tables
        assert "Todo" in tables
        assert "Tag" in tables
        assert "Project" in tables

    def test_rel_tables_created(self, tmp_graph: GraphProjector) -> None:
        tables = tmp_graph._existing_tables()
        assert "ENTRY_HAS_TAG" in tables
        assert "TODO_HAS_TAG" in tables
        assert "ENTRY_IN_PROJECT" in tables
        assert "TODO_IN_PROJECT" in tables
        assert "REFERENCES_TODO" in tables


class TestEntryProjection:
    def test_project_entry_inserts_node(
        self, tmp_graph: GraphProjector, mock_entry: MagicMock
    ) -> None:
        tmp_graph.project_entry(mock_entry)
        rows = tmp_graph.run_cypher(
            "MATCH (e:Entry {uuid: $uuid}) RETURN e.content AS content",
            {"uuid": "entry-uuid-1"},
        )
        assert len(rows) == 1
        assert "login flow" in rows[0]["content"]

    def test_project_entry_creates_tag_edges(
        self, tmp_graph: GraphProjector, mock_entry: MagicMock
    ) -> None:
        tmp_graph.project_entry(mock_entry)
        rows = tmp_graph.run_cypher(
            "MATCH (e:Entry {uuid: $uuid})-[:ENTRY_HAS_TAG]->(t:Tag) RETURN t.name AS name",
            {"uuid": "entry-uuid-1"},
        )
        names = {r["name"] for r in rows}
        assert names == {"backend", "security"}

    def test_project_entry_creates_project_edge(
        self, tmp_graph: GraphProjector, mock_entry: MagicMock
    ) -> None:
        tmp_graph.project_entry(mock_entry)
        rows = tmp_graph.run_cypher(
            "MATCH (e:Entry {uuid: $uuid})-[:ENTRY_IN_PROJECT]->(p:Project)"
            " RETURN p.name AS name",
            {"uuid": "entry-uuid-1"},
        )
        assert rows[0]["name"] == "auth-service"

    def test_project_entry_is_idempotent(
        self, tmp_graph: GraphProjector, mock_entry: MagicMock
    ) -> None:
        tmp_graph.project_entry(mock_entry)
        tmp_graph.project_entry(mock_entry)
        rows = tmp_graph.run_cypher(
            "MATCH (e:Entry {uuid: $uuid}) RETURN e.uuid",
            {"uuid": "entry-uuid-1"},
        )
        assert len(rows) == 1


class TestTodoProjection:
    def test_project_todo_inserts_node(
        self, tmp_graph: GraphProjector, mock_todo: MagicMock
    ) -> None:
        tmp_graph.project_todo(mock_todo)
        rows = tmp_graph.run_cypher(
            "MATCH (t:Todo {uuid: $uuid}) RETURN t.priority AS priority",
            {"uuid": "todo-uuid-1"},
        )
        assert rows[0]["priority"] == "high"

    def test_project_todo_creates_tag_edges(
        self, tmp_graph: GraphProjector, mock_todo: MagicMock
    ) -> None:
        tmp_graph.project_todo(mock_todo)
        rows = tmp_graph.run_cypher(
            "MATCH (t:Todo {uuid: $uuid})-[:TODO_HAS_TAG]->(tag:Tag) RETURN tag.name AS name",
            {"uuid": "todo-uuid-1"},
        )
        assert rows[0]["name"] == "testing"


class TestBuildIndex:
    def test_build_index_clears_and_repopulates(
        self,
        tmp_graph: GraphProjector,
        mock_entry: MagicMock,
        mock_todo: MagicMock,
    ) -> None:
        mock_db = MagicMock()
        mock_db.get_all_entries.return_value = [mock_entry]
        mock_db.get_all_todos.return_value = [mock_todo]

        tmp_graph.build_index(mock_db)

        entries = tmp_graph.run_cypher("MATCH (e:Entry) RETURN e.uuid AS uuid")
        todos = tmp_graph.run_cypher("MATCH (t:Todo) RETURN t.uuid AS uuid")
        assert len(entries) == 1
        assert len(todos) == 1

    def test_build_index_replaces_stale_data(
        self,
        tmp_graph: GraphProjector,
        mock_entry: MagicMock,
        mock_todo: MagicMock,
    ) -> None:
        mock_db = MagicMock()
        mock_db.get_all_entries.return_value = [mock_entry]
        mock_db.get_all_todos.return_value = [mock_todo]
        tmp_graph.build_index(mock_db)

        mock_db.get_all_entries.return_value = []
        mock_db.get_all_todos.return_value = []
        tmp_graph.build_index(mock_db)

        entries = tmp_graph.run_cypher("MATCH (e:Entry) RETURN e.uuid")
        assert len(entries) == 0


class TestGraphSearch:
    def test_search_journal_returns_results(
        self, tmp_graph: GraphProjector, mock_entry: MagicMock
    ) -> None:
        tmp_graph.project_entry(mock_entry)
        results = search_graph_journal("login", tmp_graph)
        assert isinstance(results, list)

    def test_search_todos_returns_results(
        self, tmp_graph: GraphProjector, mock_todo: MagicMock
    ) -> None:
        tmp_graph.project_todo(mock_todo)
        results = search_graph_todos("integration tests", tmp_graph)
        assert isinstance(results, list)
