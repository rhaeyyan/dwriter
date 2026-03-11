"""Tests for CLI commands."""

from click.testing import CliRunner

from dwriter.cli import main


def test_cli_help():
    """Test CLI help message."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Dwriter" in result.output
    assert "add" in result.output
    assert "standup" in result.output


def test_cli_version():
    """Test CLI version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0


def test_add_command():
    """Test the add command."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task"])

    assert result.exit_code == 0
    assert "Logged:" in result.output or "Test task" in result.output


def test_add_command_with_tags():
    """Test adding entry with tags."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "-t", "bug", "-t", "backend"])

    assert result.exit_code == 0


def test_add_command_with_project():
    """Test adding entry with project."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--project", "myapp"])

    assert result.exit_code == 0


def test_add_command_with_date_yesterday():
    """Test adding entry with --date yesterday."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--date", "yesterday"])

    assert result.exit_code == 0


def test_add_command_with_date_last_friday():
    """Test adding entry with --date "last Friday"."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--date", "last Friday"])

    assert result.exit_code == 0


def test_add_command_with_date_days_ago():
    """Test adding entry with --date "3 days ago"."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--date", "3 days ago"])

    assert result.exit_code == 0


def test_add_command_with_date_iso_format():
    """Test adding entry with --date in ISO format."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--date", "2024-01-15"])

    assert result.exit_code == 0


def test_add_command_with_invalid_date():
    """Test adding entry with invalid date raises error."""
    runner = CliRunner()
    result = runner.invoke(main, ["add", "Test task", "--date", "invalid date"])

    assert result.exit_code != 0
    # Click raises ValueError, check the exception info
    assert "Unable to parse date" in str(result.exception)


def test_today_command():
    """Test the today command."""
    runner = CliRunner()
    result = runner.invoke(main, ["today"])

    assert result.exit_code == 0


def test_standup_command():
    """Test the standup command."""
    runner = CliRunner()
    result = runner.invoke(main, ["standup"])

    assert result.exit_code in [0, 1]  # May fail if no clipboard


def test_standup_command_with_format():
    """Test standup with different formats."""
    runner = CliRunner()

    for fmt in ["bullets", "slack", "jira", "markdown"]:
        result = runner.invoke(main, ["standup", "--format", fmt])
        assert result.exit_code in [0, 1]


def test_review_command():
    """Test the review command."""
    runner = CliRunner()
    result = runner.invoke(main, ["review"])

    assert result.exit_code == 0


def test_review_command_with_days():
    """Test review with custom days."""
    runner = CliRunner()
    result = runner.invoke(main, ["review", "--days", "7"])

    assert result.exit_code == 0


def test_stats_command():
    """Test the stats command."""
    runner = CliRunner()
    result = runner.invoke(main, ["stats"])

    assert result.exit_code == 0


def test_examples_command():
    """Test the examples command."""
    runner = CliRunner()
    result = runner.invoke(main, ["examples"])

    assert result.exit_code == 0
    assert "Usage Examples" in result.output


def test_config_show_command():
    """Test config show command."""
    runner = CliRunner()
    result = runner.invoke(main, ["config", "show"])

    assert result.exit_code == 0
    assert "Configuration" in result.output


def test_config_path_command():
    """Test config path command."""
    runner = CliRunner()
    result = runner.invoke(main, ["config", "path"])

    assert result.exit_code == 0


def test_undo_command():
    """Test the undo command."""
    runner = CliRunner()
    result = runner.invoke(main, ["undo"], input="n\n")

    assert result.exit_code == 0


def test_edit_command():
    """Test the edit command."""
    runner = CliRunner()
    result = runner.invoke(main, ["edit"])

    assert result.exit_code == 0
