"""Add command for logging new entries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext

import click

from ..date_utils import parse_date_or_default
from ..git_utils import get_git_info
from ..ui_utils import display_entry


@click.command(context_settings={"help_option_names": ["-h", "--help"], "allow_interspersed_args": True})
@click.argument("content", nargs=-1, required=True)
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Add a tag (can be used multiple times)",
)
@click.option(
    "-p",
    "--project",
    "project",
    default=None,
    help="Set project name",
)
@click.option(
    "-d",
    "--date",
    "date_str",
    default=None,
    help="Set entry date using natural language (e.g., 'yesterday', "
    "'last Friday', '3 days ago') or standard date format (YYYY-MM-DD)",
)
@click.pass_obj
def add(
    ctx: AppContext,
    content: tuple[str, ...],
    tags: tuple[Any, ...],
    project: str | None,
    date_str: str | None,
) -> None:
    """Add a new log entry.

    Quickly capture tasks, notes, or accomplishments. You can use
    shorthand like #tag and &project directly in the content.

    [{TAG}]Note:[/{TAG}] When using &project or #tag in your shell, wrap the
    content in quotes to avoid shell interpretation:
      dwriter add "Implemented feature X #backend &core"

    Supported Date Formats:
      - Relative: today, yesterday, tomorrow
      - Days ago: 3 days ago, 2 weeks ago
      - Last weekday: last Monday, last Friday
      - Standard: 2024-01-15, 01/15/2024

    Examples:
      dwriter add "Fixed the race condition in auth"
      dwriter add "Fixed login bug" -t bug -t backend
      dwriter add "Refactored database layer" -p myapp
      dwriter add "Implementation complete #backend &core"
      dwriter add "Finished report" --date yesterday
      dwriter add "Meeting notes" --date "last Friday"
    """
    # Join multiple content arguments into a single string
    content_str = " ".join(content)

    # Extract tags/project from content if present
    from ..tui.parsers import parse_quick_add
    date_format = ctx.config.display.date_format
    parsed = parse_quick_add(content_str, date_format=date_format)

    # Merge default tags, content-extracted tags, and explicitly provided tags
    all_tags = list(ctx.config.defaults.tags) + list(parsed.tags) + list(tags)

    # Use explicitly provided project, then content-extracted project, then default
    if project is None:
        project = parsed.project or ctx.config.defaults.project

    # Git CWD auto-tagging
    if ctx.config.defaults.git_auto_tag:
        git_info = get_git_info()
        if git_info:
            if project is None:
                project = git_info["repo_name"]
            branch_tag = f"git-{git_info['branch']}"
            if branch_tag not in all_tags:
                all_tags.append(branch_tag)

    # Use the cleaned content (tags/project removed)
    final_content = parsed.content

    # Parse the date (or use current time if not provided)
    fmt_map = {
        "YYYY-MM-DD": "%Y-%m-%d",
        "MM/DD/YYYY": "%m/%d/%Y",
        "DD/MM/YYYY": "%d/%m/%Y",
    }
    hint = fmt_map.get(date_format)
    entry_date = parse_date_or_default(date_str, format_hint=hint)

    entry = ctx.db.add_entry(
        content=final_content, tags=all_tags, project=project, created_at=entry_date
    )

    if ctx.config.display.show_confirmation:
        display_entry(ctx.console, entry, ctx.config)
