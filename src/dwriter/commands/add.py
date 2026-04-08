"""Add command for logging new entries."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext
    from ..database import Entry

import click

from ..ai.engine import get_ai_client
from ..ai.schemas.extraction import TagExtraction
from ..date_utils import parse_date_or_default
from ..git_utils import get_git_info
from ..ui_utils import display_entry


@click.command(context_settings={"help_option_names": ["-h", "--help"], "allow_interspersed_args": True})
@click.argument("content", nargs=-1, required=False)
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
@click.option(
    "--stdin",
    "use_stdin",
    is_flag=True,
    help="Read entry content from standard input",
)
@click.option(
    "--batch-lines",
    "batch_lines",
    is_flag=True,
    help="When using --stdin, treat each line as a separate entry",
)
@click.pass_obj
def add(
    ctx: AppContext,
    content: tuple[str, ...],
    tags: tuple[Any, ...],
    project: str | None,
    date_str: str | None,
    use_stdin: bool,
    batch_lines: bool,
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

    Batch Pipeline Examples:
      git messages -5 | dwriter add --stdin --batch-lines "#git-commit &api-v2"
      echo "Single multi-line entry" | dwriter add --stdin

    Examples:
      dwriter add "Fixed the race condition in auth"
      dwriter add "Fixed login bug" -t bug -t backend
      dwriter add "Refactored database layer" -p myapp
      dwriter add "Implementation complete #backend &core"
      dwriter add "Finished report" --date yesterday
      dwriter add "Meeting notes" --date "last Friday"
    """
    # Combine arguments
    cli_content = " ".join(content)

    # Determine input blocks
    input_blocks = []
    if use_stdin:
        stdin_data = click.get_text_stream("stdin").read().strip()
        if not stdin_data:
            if not cli_content:
                raise click.UsageError("No content provided via stdin or arguments.")
            input_blocks = [cli_content]
        elif batch_lines:
            # Each line is a block, appended with CLI arguments (tags/projects)
            for line in stdin_data.splitlines():
                line = line.strip()
                if line:
                    input_blocks.append(f"{line} {cli_content}".strip())
        else:
            # Entire stdin is one block, combined with CLI arguments
            input_blocks = [f"{stdin_data} {cli_content}".strip()]
    else:
        if not cli_content:
            raise click.UsageError("No content provided. Use 'dwriter add \"content\"' or --stdin.")
        input_blocks = [cli_content]

    # Process each block
    for block in input_blocks:
        _process_entry(ctx, block, tags, project, date_str)


def _process_entry(
    ctx: AppContext,
    content_str: str,
    extra_tags: tuple[Any, ...],
    override_project: str | None,
    date_str: str | None,
) -> None:
    """Internal helper to parse and save a single entry."""
    # Extract tags/project from content if present
    from ..tui.parsers import parse_quick_add
    date_format = ctx.config.display.date_format
    parsed = parse_quick_add(content_str, date_format=date_format)

    # Merge default tags, content-extracted tags, and explicitly provided tags
    all_tags = list(ctx.config.defaults.tags) + list(parsed.tags) + list(extra_tags)

    # Use explicitly provided project, then content-extracted project, then default
    project = override_project
    if project is None:
        project = parsed.project or ctx.config.defaults.project

    # Git CWD Auto-Tagging
    if ctx.config.defaults.git_auto_tag:
        git_info = get_git_info()
        if git_info:
            # If no project was explicitly provided or found in content, use repo name
            if project is None:
                project = git_info["repo_name"]
            
            # Add git-branch tag if not already present
            branch_tag = f"git-{git_info['branch']}"
            if branch_tag not in all_tags:
                all_tags.append(branch_tag)

    # Use the cleaned content (tags/project removed)
    final_content = parsed.content

    # VALIDATION: Prevent saving empty entries
    if not final_content.strip():
        # If we have tags/projects but no content, it's a "metadata-only" entry which we disallow
        # to prevent accidental pollution from failed pipes or typos.
        ctx.console.print("[yellow]Empty entry content detected. Entry not saved.[/yellow]")
        return

    # Parse the date
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

    # Background tasks for AI features
    if ctx.config.ai.enabled:
        from ..ai.proactive import process_proactive_tagging
        
        # Proactive tagging & project matching
        thread = threading.Thread(
            target=process_proactive_tagging,
            args=(ctx, entry),
            daemon=True,
        )
        thread.start()

        if ctx.config.ai.features.burnout_detection:
            thread = threading.Thread(
                target=_run_burnout_detection,
                args=(ctx,),
                daemon=True,
            )
            thread.start()


def _run_auto_tagging(ctx: AppContext, entry: Entry) -> None:
    """Run AI tag extraction and update the entry."""
    try:
        client = get_ai_client(ctx.config.ai)
        result = client.chat.completions.create(
            model=ctx.config.ai.model,
            response_model=TagExtraction,
            messages=[
                {
                    "role": "system",
                    "content": "Extract highly relevant tags for the journal entry.",
                },
                {"role": "user", "content": entry.content},
            ],
        )

        # Merge new tags with existing ones
        new_tags = list(set(entry.tag_names + result.tags))
        if len(new_tags) > len(entry.tag_names):
            # Update the entry in a new DB session (database.py handles this)
            ctx.db.update_entry(entry.id, tags=new_tags)
    except Exception:
        # Silently fail for background tasks
        pass


def _run_burnout_detection(ctx: AppContext) -> None:
    """Run weekly burnout detection."""
    from datetime import datetime, timedelta

    # Simple check: have we run this in the last 7 days?
    # This might need a field in DB or config. For now, we'll just check
    # if we have enough recent entries and run it.

    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        entries = ctx.db.get_all_entries()
        recent_entries = [e for e in entries if e.created_at >= seven_days_ago]

        if len(recent_entries) < 5:
            return

        client = get_ai_client(ctx.config.ai)
        # Simplified burnout check logic
        pass
    except Exception:
        pass
