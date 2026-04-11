"""Tests for the configuration module."""

from dwriter.config import (
    Config,
    ConfigManager,
)


def test_default_config():
    """Test default configuration values."""
    config = Config()

    assert config.standup.format == "bullets"
    assert config.standup.copy_to_clipboard is True
    assert config.review.default_days == 5
    assert config.review.format == "markdown"
    assert config.display.show_confirmation is True
    assert config.display.show_id is True
    assert config.display.colors is True
    assert config.display.lock_mode is False
    assert config.display.color_scheme == "normal"
    assert config.defaults.tags == []
    assert config.defaults.project is None


def test_config_manager_load_default(temp_path):
    """Test loading config when file doesn't exist."""
    config_path = temp_path / "config.toml"
    manager = ConfigManager(config_path)

    config = manager.load()

    assert config.standup.format == "bullets"
    assert config.review.default_days == 5


def test_config_manager_save_and_load(temp_path):
    """Test saving and loading configuration."""
    config_path = temp_path / "config.toml"
    manager = ConfigManager(config_path)

    # Modify and save
    config = manager.load()
    config.standup.format = "slack"
    config.review.default_days = 7
    config.defaults.tags = ["work", "dev"]
    config.defaults.project = "myapp"
    config.display.lock_mode = True
    config.display.color_scheme = "deuteranopia"
    manager.save(config)

    # Load again
    manager._config = None
    loaded = manager.load()

    assert loaded.standup.format == "slack"
    assert loaded.review.default_days == 7
    assert loaded.defaults.tags == ["work", "dev"]
    assert loaded.defaults.project == "myapp"
    assert loaded.display.lock_mode is True
    assert loaded.display.color_scheme == "deuteranopia"


def test_config_manager_reset(temp_path):
    """Test resetting configuration to defaults."""
    config_path = temp_path / "config.toml"
    manager = ConfigManager(config_path)

    # Modify
    config = manager.load()
    config.standup.format = "jira"
    manager.save(config)

    # Reset
    manager.reset()

    # Verify defaults
    assert manager.load().standup.format == "bullets"


def test_config_manager_to_dict(temp_path):
    """Test converting config to dictionary."""
    config_path = temp_path / "config.toml"
    manager = ConfigManager(config_path)

    config_dict = manager.to_dict()

    assert "standup" in config_dict
    assert "review" in config_dict
    assert "display" in config_dict
    assert "defaults" in config_dict


def test_config_manager_get_path(temp_path):
    """Test getting config file path."""
    manager = ConfigManager(temp_path / "config.toml")
    assert manager.get_config_path() == temp_path / "config.toml"


def test_config_manager_obsidian_roundtrip(temp_path):
    """Test ObsidianConfig saving and loading."""
    config_path = temp_path / "config.toml"
    manager = ConfigManager(config_path)

    # Set non-default values
    config = manager.load()
    config.obsidian.vault_path = "/path/to/vault"
    config.obsidian.ai_reports_folder = "My Reports"
    config.obsidian.reviews_folder = "My Reviews"
    config.obsidian.wikilinks = False
    config.obsidian.include_todos = False
    manager.save(config)

    # Load in new manager
    new_manager = ConfigManager(config_path)
    loaded = new_manager.load()

    assert loaded.obsidian.vault_path == "/path/to/vault"
    assert loaded.obsidian.ai_reports_folder == "My Reports"
    assert loaded.obsidian.reviews_folder == "My Reviews"
    assert loaded.obsidian.wikilinks is False
    assert loaded.obsidian.include_todos is False
    assert loaded.obsidian.enabled is True
