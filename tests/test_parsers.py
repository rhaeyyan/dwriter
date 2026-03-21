"""Tests for omnibox quick-add parser."""

from dwriter.tui.parsers import ParsedEntry, parse_quick_add


def test_parse_basic_entry() -> None:
    """Test parsing a simple entry without tags or project."""
    result = parse_quick_add("Fixed the bug")
    assert result.content == "Fixed the bug"
    assert result.tags == []
    assert result.project is None


def test_parse_with_tags() -> None:
    """Test parsing entry with tags."""
    result = parse_quick_add("Fixed race condition #bug #critical")
    assert result.content == "Fixed race condition"
    assert result.tags == ["bug", "critical"]


def test_parse_with_project() -> None:
    """Test parsing entry with project."""
    result = parse_quick_add("Deployed to prod &backend-api")
    assert result.content == "Deployed to prod"
    assert result.project == "backend-api"


def test_parse_mixed() -> None:
    """Test parsing entry with mixed tags and project."""
    result = parse_quick_add("Fixed auth #security &core-engine #bug")
    assert result.content == "Fixed auth"
    assert set(result.tags) == {"security", "bug"}
    assert result.project == "core-engine"


def test_parse_empty() -> None:
    """Test parsing empty or whitespace-only input."""
    result = parse_quick_add("   ")
    assert result.content == ""
    assert result.tags == []
    assert result.project is None


def test_parse_multiple_projects() -> None:
    """Test that only first project is captured."""
    result = parse_quick_add("Task &project-a with &project-b")
    assert result.content == "Task with"
    assert result.project == "project-a"
    assert len(result.tags) == 0


def test_parse_tag_with_hyphen() -> None:
    """Test parsing tags containing hyphens."""
    result = parse_quick_add("Work on feature #feature-branch")
    assert result.content == "Work on feature"
    assert result.tags == ["feature-branch"]


def test_parse_project_with_hyphen() -> None:
    """Test parsing projects containing hyphens."""
    result = parse_quick_add("Update docs &my-project")
    assert result.content == "Update docs"
    assert result.project == "my-project"


def test_parse_preserves_content_order() -> None:
    """Test that content order is preserved when tags/projects are removed."""
    result = parse_quick_add("Started #work on &project the #feature")
    assert result.content == "Started on the"
    assert result.tags == ["work", "feature"]
    assert result.project == "project"


def test_parsed_entry_defaults() -> None:
    """Test ParsedEntry dataclass default values."""
    entry = ParsedEntry(content="test")
    assert entry.content == "test"
    assert entry.tags == []
    assert entry.project is None


def test_parsed_entry_with_values() -> None:
    """Test ParsedEntry with all values specified."""
    entry = ParsedEntry(
        content="test content",
        tags=["tag1", "tag2"],
        project="my-project",
    )
    assert entry.content == "test content"
    assert entry.tags == ["tag1", "tag2"]
    assert entry.project == "my-project"
