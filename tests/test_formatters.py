"""Tests for standup formatting functions."""

from datetime import datetime

from dwriter.database import Entry, Tag


def create_test_entry(content, tags=None, project=None):
    """Helper to create test entries."""
    entry = Entry(
        id=1,
        content=content,
        created_at=datetime.now(),
        project=project,
    )
    if tags:
        entry.tags = [Tag(name=t) for t in tags]
    return entry


def test_format_bullets_basic():
    """Test basic bullet formatting."""
    from dwriter.commands.standup import format_standup_bullets

    entries = [create_test_entry("Fixed bug")]
    result = format_standup_bullets(entries)

    assert "- Fixed bug" in result


def test_format_bullets_with_tags():
    """Test bullet formatting with tags."""
    from dwriter.commands.standup import format_standup_bullets

    entries = [create_test_entry("Fixed bug", tags=["bug", "backend"])]
    result = format_standup_bullets(entries)

    assert "bug" in result
    assert "backend" in result


def test_format_bullets_with_project():
    """Test bullet formatting with project."""
    from dwriter.commands.standup import format_standup_bullets

    entries = [create_test_entry("Fixed bug", project="myapp")]
    result = format_standup_bullets(entries)

    assert "myapp" in result
    assert "[magenta]" in result


def test_format_slack():
    """Test Slack formatting."""
    from dwriter.commands.standup import format_standup_slack

    entries = [create_test_entry("Fixed bug")]
    result = format_standup_slack(entries)

    assert "• Fixed bug" in result


def test_format_jira():
    """Test Jira formatting."""
    from dwriter.commands.standup import format_standup_jira

    entries = [create_test_entry("Fixed bug")]
    result = format_standup_jira(entries)

    assert "* Fixed bug" in result


def test_format_markdown():
    """Test Markdown formatting."""
    from dwriter.commands.standup import format_standup_markdown

    entries = [create_test_entry("Fixed bug")]
    result = format_standup_markdown(entries)

    assert "- Fixed bug" in result


def test_format_multiple_entries():
    """Test formatting with multiple entries."""
    from dwriter.commands.standup import format_standup_bullets

    entries = [
        create_test_entry("Task 1"),
        create_test_entry("Task 2"),
        create_test_entry("Task 3"),
    ]
    result = format_standup_bullets(entries)

    assert "- Task 1" in result
    assert "- Task 2" in result
    assert "- Task 3" in result
