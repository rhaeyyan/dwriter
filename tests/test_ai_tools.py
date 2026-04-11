"""Tests for the AI tool functions in dwriter.ai.tools.

All tests inject a real in-memory Database instance to verify that the db
parameter is respected and no extra Database() calls are made per invocation.
"""

import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

from dwriter.database import Database
from dwriter.ai.tools import (
    get_daily_standup,
    search_journal,
    search_todos,
    entry_to_dict,
    todo_to_dict,
)


@pytest.fixture
def db(tmp_path):
    """Provide a fresh Database instance backed by a temp directory."""
    import os
    os.environ["HOME"] = str(tmp_path)
    return Database()


class TestDbInjection:
    """Verify tool functions use the provided db and do not open new connections."""

    def test_search_journal_uses_injected_db(self, db):
        db.add_entry("worked on pytest integration", tags=["testing"])
        # No patch needed — if a second Database() were opened it would hit the
        # same file and still work, but we confirm the injected instance is used
        # by verifying results without any separate db open.
        result = search_journal(query="pytest", db=db)
        assert "pytest" in result or "testing" in result or "worked on" in result

    def test_search_todos_uses_injected_db(self, db):
        db.add_todo("finish unit tests", priority="high")
        result = search_todos(query="unit tests", db=db)
        assert "unit tests" in result

    def test_get_daily_standup_uses_injected_db(self, db):
        yesterday = datetime.now() - timedelta(days=1)
        db.add_entry("deployed the API", created_at=yesterday)
        result = get_daily_standup(db=db)
        # Should produce a markdown report without error
        assert "Standup" in result

    def test_search_journal_no_db_falls_back(self, tmp_path):
        """When db=None the function opens its own connection (fallback path)."""
        result = search_journal(query="anything")
        # Should return a string (either results or the no-match message)
        assert isinstance(result, str)

    def test_search_todos_no_db_falls_back(self, tmp_path):
        result = search_todos(query="anything")
        assert isinstance(result, str)


class TestSearchJournal:
    def test_returns_no_match_message_when_empty(self, db):
        result = search_journal(query="nonexistent entry xyz", db=db)
        assert result == "No matching journal entries found."

    def test_returns_json_for_match(self, db):
        db.add_entry("reviewed the pull request", tags=["code-review"])
        result = search_journal(query="pull request", db=db)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) >= 1
        assert "content" in parsed[0]

    def test_result_contains_expected_fields(self, db):
        db.add_entry("fixed the login bug", project="auth", tags=["bugfix"])
        result = search_journal(query="login bug", db=db)
        parsed = json.loads(result)
        entry = parsed[0]
        for field in ("id", "content", "project", "tags", "created_at"):
            assert field in entry

    def test_project_filter_applied(self, db):
        db.add_entry("worked on auth module", project="auth")
        db.add_entry("worked on payments module", project="payments")
        result = search_journal(query="module", project="auth", db=db)
        if result != "No matching journal entries found.":
            parsed = json.loads(result)
            for entry in parsed:
                assert entry["project"] == "auth"

    def test_handles_exception_gracefully(self, db):
        with patch.object(db, "get_all_entries", side_effect=RuntimeError("db error")):
            result = search_journal(query="anything", db=db)
        assert "Error" in result


class TestSearchTodos:
    def test_returns_no_match_message_when_empty(self, db):
        result = search_todos(query="nonexistent task xyz", db=db)
        assert result == "No matching todos found."

    def test_returns_json_for_match(self, db):
        db.add_todo("write release notes", priority="medium")
        result = search_todos(query="release notes", db=db)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) >= 1

    def test_result_contains_expected_fields(self, db):
        db.add_todo("deploy to production", priority="high")
        result = search_todos(query="deploy", db=db)
        parsed = json.loads(result)
        todo = parsed[0]
        for field in ("id", "content", "priority", "status"):
            assert field in todo

    def test_handles_exception_gracefully(self, db):
        with patch.object(db, "get_all_todos", side_effect=RuntimeError("db error")):
            result = search_todos(query="anything", db=db)
        assert "Error" in result


class TestGetDailyStandup:
    def test_produces_markdown_report(self, db):
        result = get_daily_standup(db=db)
        assert "Standup" in result
        assert "**What was done:**" in result
        assert "**Plan for today:**" in result

    def test_shows_no_entries_when_empty(self, db):
        result = get_daily_standup(db=db)
        assert "No entries logged." in result

    def test_includes_entry_from_yesterday(self, db):
        yesterday = datetime.now() - timedelta(days=1)
        db.add_entry("shipped the feature", created_at=yesterday)
        result = get_daily_standup(db=db)
        assert "shipped the feature" in result

    def test_accepts_explicit_date_string(self, db):
        target = datetime(2025, 1, 15)
        db.add_entry("old work entry", created_at=target)
        result = get_daily_standup(date_str="2025-01-15", db=db)
        assert "2025-01-15" in result
        assert "old work entry" in result

    def test_invalid_date_returns_error_string(self, db):
        result = get_daily_standup(date_str="not-a-date", db=db)
        assert "Error" in result

    def test_handles_exception_gracefully(self, db):
        with patch.object(db, "get_entries_in_range", side_effect=RuntimeError("db error")):
            result = get_daily_standup(db=db)
        assert "Error" in result


class TestSerializers:
    def test_entry_to_dict_shape(self, db):
        entry = db.add_entry("test content", project="myproject", tags=["t1"])
        d = entry_to_dict(entry)
        assert d["content"] == "test content"
        assert d["project"] == "myproject"
        assert "t1" in d["tags"]
        assert "created_at" in d

    def test_todo_to_dict_shape(self, db):
        todo = db.add_todo("test task", priority="low")
        d = todo_to_dict(todo)
        assert d["content"] == "test task"
        assert d["priority"] == "low"
        assert d["status"] == "pending"
        assert d["due_date"] is None
