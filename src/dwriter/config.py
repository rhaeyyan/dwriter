"""Configuration management for Day Writer.

This module handles loading, saving, and managing user configuration
stored in TOML format.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import tomlkit
import tomllib


@dataclass
class StandupConfig:
    """Standup output configuration.

    Attributes:
        format: Output format (bullets, slack, jira, markdown).
        copy_to_clipboard: Whether to copy output to clipboard.
    """

    format: str = "bullets"
    copy_to_clipboard: bool = True


@dataclass
class ReviewConfig:
    """Review output configuration.

    Attributes:
        default_days: Default number of days to review.
        format: Output format (markdown, plain, slack).
    """

    default_days: int = 5
    format: str = "markdown"


@dataclass
class DisplayConfig:
    """Display configuration.

    Attributes:
        show_confirmation: Whether to show confirmation after adding entries.
        show_id: Whether to show entry IDs in output.
        colors: Whether to use colors in output.
    """

    show_confirmation: bool = True
    show_id: bool = True
    colors: bool = True


@dataclass
class DefaultsConfig:
    """Default values for new entries.

    Attributes:
        tags: Default tags to apply to all entries.
        project: Default project name.
    """

    tags: List[str] = field(default_factory=list)
    project: Optional[str] = None


@dataclass
class Config:
    """Main configuration container.

    Attributes:
        standup: Standup-related settings.
        review: Review-related settings.
        display: Display-related settings.
        defaults: Default values for entries.
    """

    standup: StandupConfig = field(default_factory=StandupConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)


class ConfigManager:
    """Manages Day Writer configuration.

    This class handles loading, saving, and accessing user configuration
    from the TOML config file.

    Attributes:
        config_path: Path to the configuration file.
    """

    DEFAULT_CONFIG = Config()

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Optional path to the config file. If not provided,
                uses the default location at ~/.day-writer/config.toml.
        """
        if config_path is None:
            data_dir = Path.home() / ".day-writer"
            data_dir.mkdir(parents=True, exist_ok=True)
            config_path = data_dir / "config.toml"

        self.config_path = config_path
        self._config: Optional[Config] = None

    def load(self) -> Config:
        """Load configuration from file.

        Returns:
            The loaded Config object. Uses defaults if file doesn't exist.
        """
        if self._config is not None:
            return self._config

        if not self.config_path.exists():
            self._config = Config()
            self.save()
            return self._config

        try:
            with open(self.config_path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            self._config = Config()
            self.save()
            return self._config

        self._config = Config(
            standup=StandupConfig(
                format=data.get("standup", {}).get("format", "bullets"),
                copy_to_clipboard=data.get("standup", {}).get(
                    "copy_to_clipboard", True
                ),
            ),
            review=ReviewConfig(
                default_days=data.get("review", {}).get("default_days", 5),
                format=data.get("review", {}).get("format", "markdown"),
            ),
            display=DisplayConfig(
                show_confirmation=data.get("display", {}).get(
                    "show_confirmation", True
                ),
                show_id=data.get("display", {}).get("show_id", True),
                colors=data.get("display", {}).get("colors", True),
            ),
            defaults=DefaultsConfig(
                tags=data.get("defaults", {}).get("tags", []),
                project=data.get("defaults", {}).get("project"),
            ),
        )

        return self._config

    def save(self, config: Optional[Config] = None) -> None:
        """Save configuration to file.

        Args:
            config: Optional Config object to save. If not provided,
                saves the currently loaded config.
        """
        if config is not None:
            self._config = config

        if self._config is None:
            self._config = Config()

        doc = tomlkit.document()

        doc.add("standup", tomlkit.table())
        doc["standup"]["format"] = self._config.standup.format
        doc["standup"]["copy_to_clipboard"] = self._config.standup.copy_to_clipboard

        doc.add("review", tomlkit.table())
        doc["review"]["default_days"] = self._config.review.default_days
        doc["review"]["format"] = self._config.review.format

        doc.add("display", tomlkit.table())
        doc["display"]["show_confirmation"] = self._config.display.show_confirmation
        doc["display"]["show_id"] = self._config.display.show_id
        doc["display"]["colors"] = self._config.display.colors

        doc.add("defaults", tomlkit.table())
        if self._config.defaults.tags:
            doc["defaults"]["tags"] = self._config.defaults.tags
        if self._config.defaults.project:
            doc["defaults"]["project"] = self._config.defaults.project

        with open(self.config_path, "w") as f:
            f.write(tomlkit.dumps(doc))

    def reset(self) -> Config:
        """Reset configuration to defaults.

        Returns:
            The default Config object.
        """
        self._config = Config()
        self.save()
        return self._config

    def get_config_path(self) -> Path:
        """Get the path to the configuration file.

        Returns:
            The path to the config file.
        """
        return self.config_path

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary.

        Returns:
            A dictionary representation of the configuration.
        """
        config = self.load()
        return {
            "standup": {
                "format": config.standup.format,
                "copy_to_clipboard": config.standup.copy_to_clipboard,
            },
            "review": {
                "default_days": config.review.default_days,
                "format": config.review.format,
            },
            "display": {
                "show_confirmation": config.display.show_confirmation,
                "show_id": config.display.show_id,
                "colors": config.display.colors,
            },
            "defaults": {
                "tags": config.defaults.tags,
                "project": config.defaults.project,
            },
        }
