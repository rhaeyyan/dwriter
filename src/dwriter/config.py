"""Configuration management for dwriter.

This module handles loading, saving, and managing user configuration
stored in TOML format.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomlkit

try:
    import tomllib
except ImportError:
    import tomli as tomllib


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
        use_emojis: Whether to use emojis in the UI.
        clock_24hr: Whether to use 24-hour clock format (vs 12-hour).
        theme: Theme preset name (cyberpunk, light, dark, minimal).
        ergonomic_mode: Whether to use spacious ergonomic layout.
        date_format: Date display format string.
        lock_mode: Whether to disable editing of date and time fields.
        color_scheme: Color blindness color scheme (normal, deuteranopia,
            protanopia, tritanopia).
        notifications_enabled: Whether to enable system desktop notifications
            for reminders.
        due_date_format: Format for displaying due dates (relative, YYYY-MM-DD,
            MM/DD/YYYY, DD/MM/YYYY).
        todo_sorting_mode: Urgency hierarchy (priority_first, date_first).
        permanent_omnibox: Whether to keep the omnibox visible at all times.
    """

    show_confirmation: bool = True
    show_id: bool = True
    colors: bool = True
    use_emojis: bool = True
    clock_24hr: bool = True
    theme: str = "cyberpunk"
    ergonomic_mode: bool = False
    date_format: str = "YYYY-MM-DD"
    lock_mode: bool = False
    color_scheme: str = "normal"
    notifications_enabled: bool = False
    due_date_format: str = "relative"
    todo_sorting_mode: str = "priority_first"
    permanent_omnibox: bool = True


@dataclass
class DefaultsConfig:
    """Default values for new entries.

    Attributes:
        tags: Default tags to apply to all entries.
        project: Default project name.
        default_priority: Default priority for new todos (normal/high/urgent).
        default_due_days: Default days until due for new todos.
        git_auto_tag: Whether to automatically apply git branch/repo tags.
        auto_sync: Whether to automatically sync changes in the background.
    """

    tags: list[str] = field(default_factory=list)
    project: str | None = None
    default_priority: str = "normal"
    default_due_days: int = 1
    git_auto_tag: bool = True
    auto_sync: bool = True


@dataclass
class TimerConfig:
    """Timer (Timer) configuration.

    Attributes:
        work_duration: Work session duration in minutes.
        break_duration: Short break duration in minutes.
        long_break_duration: Long break duration in minutes.
        sessions_before_long_break: Number of sessions before a long break.
        auto_start_breaks: Whether to auto-start breaks.
        sound_enabled: Whether to play sound notifications.
    """

    work_duration: int = 25
    break_duration: int = 5
    long_break_duration: int = 15
    sessions_before_long_break: int = 4
    auto_start_breaks: bool = False
    sound_enabled: bool = True


@dataclass
class AIFeaturesConfig:
    """AI feature-specific configuration.

    Attributes:
        auto_tagging: Whether to enable background auto-tagging.
        reflection_prompts: Whether to enable AI reflection prompts.
        burnout_detection: Whether to enable weekly burnout detection checks.
        permission_mode: Security strictness (read-only, append-only,
            prompt, danger-full-access).
    """

    auto_tagging: bool = False
    reflection_prompts: bool = True
    burnout_detection: bool = True
    permission_mode: str = "append-only"


@dataclass
class ObsidianConfig:
    """Obsidian vault export configuration.

    Attributes:
        vault_path: Absolute path to the Obsidian vault root directory.
                    If None or empty, export is disabled.
        ai_reports_folder: Vault subfolder for AI briefings and standup notes.
        reviews_folder: Vault subfolder for period review notes.
        wikilinks: Whether to render project names as [[wikilinks]].
        include_todos: Whether to include todo sections in standup notes.
        enabled: Master switch. Set automatically when vault_path is non-empty.
    """

    vault_path: str | None = None
    ai_reports_folder: str = "AI Reports"
    reviews_folder: str = "Reviews"
    wikilinks: bool = True
    include_todos: bool = True
    enabled: bool = False


@dataclass
class AIConfig:
    """AI configuration.

    Attributes:
        enabled: Whether AI features are enabled.
        provider: AI provider (ollama, openai).
        model: Legacy model name (deprecated).
        chat_model: Model name for the 2nd-Brain ReAct loop.
        daemon_model: Model name for background Auto-Semantic Tagging.
        base_url: Base URL for the AI provider.
        features: Feature-specific settings.
        last_pulse_greeting: ISO timestamp of the last 7-day pulse greeting.
    """

    enabled: bool = True
    provider: str = "ollama"
    model: str = "gemma4:e4b"
    chat_model: str = "gemma4:e4b"
    daemon_model: str = "gemma4:e2b"
    base_url: str = "http://localhost:11434/v1"
    features: AIFeaturesConfig = field(default_factory=AIFeaturesConfig)
    last_pulse_greeting: str | None = None


@dataclass
class Config:
    """Main configuration container.

    Attributes:
        standup: Standup-related settings.
        review: Review-related settings.
        display: Display-related settings.
        defaults: Default values for entries.
        timer: Timer (Timer) settings.
        ai: AI-related settings.
        obsidian: Obsidian-related settings.
    """

    standup: StandupConfig = field(default_factory=StandupConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    timer: TimerConfig = field(default_factory=TimerConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    obsidian: ObsidianConfig = field(default_factory=ObsidianConfig)


class ConfigManager:
    """Manages dwriter configuration.

    This class handles loading, saving, and accessing user configuration
    from the TOML config file.

    Attributes:
        config_path: Path to the configuration file.
    """

    DEFAULT_CONFIG = Config()

    def __init__(self, config_path: Path | None = None):
        """Initialize the configuration manager.

        Args:
            config_path: Optional path to the config file. If not provided,
                uses the default location at ~/.dwriter/config.toml.
        """
        if config_path is None:
            data_dir = Path.home() / ".dwriter"
            data_dir.mkdir(parents=True, exist_ok=True)
            config_path = data_dir / "config.toml"

        self.config_path = config_path
        self._config: Config | None = None

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
                data: dict[str, Any] = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            self._config = Config()
            self.save()
            return self._config

        # Safe access with defaults for backward compatibility
        display_data = data.get("display", {})
        defaults_data = data.get("defaults", {})
        timer_data = data.get("timer", {})  # May not exist in old configs
        ai_data = data.get("ai", {})
        ai_features_data = ai_data.get("features", {})
        obsidian_data = data.get("obsidian", {})

        vault_path = obsidian_data.get("vault_path")

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
                show_confirmation=display_data.get("show_confirmation", True),
                show_id=display_data.get("show_id", True),
                colors=display_data.get("colors", True),
                use_emojis=display_data.get("use_emojis", True),
                clock_24hr=display_data.get("clock_24hr", True),
                theme=display_data.get("theme", "cyberpunk"),
                ergonomic_mode=display_data.get("ergonomic_mode", False),
                date_format=display_data.get("date_format", "YYYY-MM-DD"),
                lock_mode=display_data.get("lock_mode", False),
                color_scheme=display_data.get("color_scheme", "normal"),
                notifications_enabled=display_data.get("notifications_enabled", False),
                due_date_format=display_data.get("due_date_format", "relative"),
                todo_sorting_mode=display_data.get(
                    "todo_sorting_mode", "priority_first"
                ),
                permanent_omnibox=display_data.get("permanent_omnibox", True),
            ),
            defaults=DefaultsConfig(
                tags=defaults_data.get("tags", []),
                project=defaults_data.get("project"),
                default_priority=defaults_data.get("default_priority", "normal"),
                default_due_days=defaults_data.get("default_due_days", 1),
                git_auto_tag=defaults_data.get("git_auto_tag", True),
                auto_sync=defaults_data.get("auto_sync", True),
            ),
            timer=TimerConfig(
                work_duration=timer_data.get("work_duration", 25),
                break_duration=timer_data.get("break_duration", 5),
                long_break_duration=timer_data.get("long_break_duration", 15),
                sessions_before_long_break=timer_data.get(
                    "sessions_before_long_break", 4
                ),
                auto_start_breaks=timer_data.get("auto_start_breaks", False),
                sound_enabled=timer_data.get("sound_enabled", True),
            ),
            ai=AIConfig(
                enabled=ai_data.get("enabled", True),
                provider=ai_data.get("provider", "ollama"),
                model=ai_data.get("model", "gemma4:e4b"),
                chat_model=ai_data.get("chat_model", "gemma4:e4b"),
                daemon_model=ai_data.get("daemon_model", "gemma4:e2b"),
                base_url=ai_data.get("base_url", "http://localhost:11434/v1"),
                features=AIFeaturesConfig(
                    auto_tagging=ai_features_data.get("auto_tagging", False),
                    reflection_prompts=ai_features_data.get("reflection_prompts", True),
                    burnout_detection=ai_features_data.get("burnout_detection", True),
                    permission_mode=ai_features_data.get(
                        "permission_mode", "append-only"
                    ),
                ),
                last_pulse_greeting=ai_data.get("last_pulse_greeting"),
            ),
            obsidian=ObsidianConfig(
                vault_path=vault_path,
                ai_reports_folder=obsidian_data.get(
                    "ai_reports_folder", "AI Reports"
                ),
                reviews_folder=obsidian_data.get("reviews_folder", "Reviews"),
                wikilinks=obsidian_data.get("wikilinks", True),
                include_todos=obsidian_data.get("include_todos", True),
                enabled=bool(vault_path),
            ),
        )

        return self._config

    def save(self, config: Config | None = None) -> None:
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

        standup_table = tomlkit.table()
        standup_table["format"] = self._config.standup.format
        standup_table["copy_to_clipboard"] = self._config.standup.copy_to_clipboard
        doc.add("standup", standup_table)

        review_table = tomlkit.table()
        review_table["default_days"] = self._config.review.default_days
        review_table["format"] = self._config.review.format
        doc.add("review", review_table)

        display_table = tomlkit.table()
        display_table["show_confirmation"] = self._config.display.show_confirmation
        display_table["show_id"] = self._config.display.show_id
        display_table["colors"] = self._config.display.colors
        display_table["use_emojis"] = self._config.display.use_emojis
        display_table["clock_24hr"] = self._config.display.clock_24hr
        display_table["theme"] = self._config.display.theme
        display_table["ergonomic_mode"] = self._config.display.ergonomic_mode
        display_table["date_format"] = self._config.display.date_format
        display_table["lock_mode"] = self._config.display.lock_mode
        display_table["color_scheme"] = self._config.display.color_scheme
        display_table["notifications_enabled"] = (
            self._config.display.notifications_enabled
        )
        display_table["due_date_format"] = self._config.display.due_date_format
        display_table["todo_sorting_mode"] = self._config.display.todo_sorting_mode
        display_table["permanent_omnibox"] = self._config.display.permanent_omnibox
        doc.add("display", display_table)

        defaults_table = tomlkit.table()
        if self._config.defaults.tags:
            defaults_table["tags"] = self._config.defaults.tags
        if self._config.defaults.project:
            defaults_table["project"] = self._config.defaults.project
        defaults_table["default_priority"] = self._config.defaults.default_priority
        defaults_table["default_due_days"] = self._config.defaults.default_due_days
        defaults_table["git_auto_tag"] = self._config.defaults.git_auto_tag
        defaults_table["auto_sync"] = self._config.defaults.auto_sync
        doc.add("defaults", defaults_table)

        timer_table = tomlkit.table()
        timer_table["work_duration"] = self._config.timer.work_duration
        timer_table["break_duration"] = self._config.timer.break_duration
        timer_table["long_break_duration"] = self._config.timer.long_break_duration
        timer_table["sessions_before_long_break"] = (
            self._config.timer.sessions_before_long_break
        )
        timer_table["auto_start_breaks"] = self._config.timer.auto_start_breaks
        timer_table["sound_enabled"] = self._config.timer.sound_enabled
        doc.add("timer", timer_table)

        ai_table = tomlkit.table()
        ai_table["enabled"] = self._config.ai.enabled
        ai_table["provider"] = self._config.ai.provider
        ai_table["model"] = self._config.ai.model
        ai_table["chat_model"] = self._config.ai.chat_model
        ai_table["daemon_model"] = self._config.ai.daemon_model
        ai_table["base_url"] = self._config.ai.base_url
        if self._config.ai.last_pulse_greeting:
            ai_table["last_pulse_greeting"] = self._config.ai.last_pulse_greeting

        ai_features = tomlkit.table()
        ai_features["auto_tagging"] = self._config.ai.features.auto_tagging
        ai_features["reflection_prompts"] = self._config.ai.features.reflection_prompts
        ai_features["burnout_detection"] = self._config.ai.features.burnout_detection
        ai_features["permission_mode"] = self._config.ai.features.permission_mode
        ai_table["features"] = ai_features
        doc.add("ai", ai_table)

        obsidian_table = tomlkit.table()
        if self._config.obsidian.vault_path:
            obsidian_table["vault_path"] = self._config.obsidian.vault_path
        obsidian_table["ai_reports_folder"] = self._config.obsidian.ai_reports_folder
        obsidian_table["reviews_folder"] = self._config.obsidian.reviews_folder
        obsidian_table["wikilinks"] = self._config.obsidian.wikilinks
        obsidian_table["include_todos"] = self._config.obsidian.include_todos
        obsidian_table["enabled"] = self._config.obsidian.enabled
        doc.add("obsidian", obsidian_table)

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

    def to_dict(self) -> dict[str, Any]:
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
                "use_emojis": config.display.use_emojis,
                "clock_24hr": config.display.clock_24hr,
                "theme": config.display.theme,
                "ergonomic_mode": config.display.ergonomic_mode,
                "date_format": config.display.date_format,
                "lock_mode": config.display.lock_mode,
                "color_scheme": config.display.color_scheme,
                "notifications_enabled": config.display.notifications_enabled,
                "due_date_format": config.display.due_date_format,
                "todo_sorting_mode": config.display.todo_sorting_mode,
                "permanent_omnibox": config.display.permanent_omnibox,
            },
            "defaults": {
                "tags": config.defaults.tags,
                "project": config.defaults.project,
                "default_priority": config.defaults.default_priority,
                "default_due_days": config.defaults.default_due_days,
                "git_auto_tag": config.defaults.git_auto_tag,
                "auto_sync": config.defaults.auto_sync,
            },
            "timer": {
                "work_duration": config.timer.work_duration,
                "break_duration": config.timer.break_duration,
                "long_break_duration": config.timer.long_break_duration,
                "sessions_before_long_break": config.timer.sessions_before_long_break,
                "auto_start_breaks": config.timer.auto_start_breaks,
                "sound_enabled": config.timer.sound_enabled,
            },
            "ai": {
                "enabled": config.ai.enabled,
                "provider": config.ai.provider,
                "model": config.ai.model,
                "chat_model": config.ai.chat_model,
                "daemon_model": config.ai.daemon_model,
                "base_url": config.ai.base_url,
                "features": {
                    "auto_tagging": config.ai.features.auto_tagging,
                    "reflection_prompts": config.ai.features.reflection_prompts,
                    "burnout_detection": config.ai.features.burnout_detection,
                    "permission_mode": config.ai.features.permission_mode,
                },
                "last_pulse_greeting": config.ai.last_pulse_greeting,
            },
            "obsidian": {
                "vault_path": config.obsidian.vault_path,
                "ai_reports_folder": config.obsidian.ai_reports_folder,
                "reviews_folder": config.obsidian.reviews_folder,
                "wikilinks": config.obsidian.wikilinks,
                "include_todos": config.obsidian.include_todos,
                "enabled": config.obsidian.enabled,
            },
        }

