"""Standup command for generating standup summaries."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click

from .standup_service import build_standup_text, fetch_standup_data


@click.command()
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["bullets", "slack", "jira", "markdown"]),
    default=None,
    help="Output format: bullets, slack, jira, markdown",
)
@click.option(
    "--no-copy",
    is_flag=True,
    default=None,
    help="Don't copy to clipboard",
)
@click.option(
    "--with-todos",
    is_flag=True,
    default=False,
    help="Append your pending tasks as a 'Plan for Today' section",
)
@click.option(
    "--weekly",
    is_flag=True,
    default=False,
    help="Include the 7-day Weekly Pulse wrap-up summary",
)
@click.option(
    "--obsidian",
    is_flag=True,
    default=False,
    help="Export standup to Obsidian vault",
)
@click.pass_obj
def standup(
    ctx: AppContext,
    output_format: str,
    no_copy: bool,
    with_todos: bool,
    weekly: bool,
    obsidian: bool,
) -> None:
    """Generate yesterday's standup.

    Queries all entries from yesterday and formats them for standup meetings.
    By default, copies the output to clipboard for easy pasting into Slack,
    Jira, or other tools.

    Output Formats:
      - bullets: Simple bullet points
      - slack: Slack-optimized formatting with bullets
      - jira: Jira-compatible formatting
      - markdown: Markdown with proper syntax

    Examples:
      dwriter standup                 # Default (copies to clipboard)
      dwriter standup --format slack
      dwriter standup --format jira
      dwriter standup --no-copy
      dwriter standup --with-todos    # Include pending tasks
      dwriter standup --weekly        # Include 7-day Pulse Wrap-up
      dwriter standup --obsidian      # Export to Obsidian vault
    """
    # Use config defaults if not specified
    if output_format is None:
        output_format = ctx.config.standup.format

    if no_copy is None:
        should_copy = ctx.config.standup.copy_to_clipboard
    else:
        should_copy = not no_copy

    # Fetch data via service
    yesterday = datetime.now() - timedelta(days=1)
    entries, pending_todos = fetch_standup_data(ctx.db, yesterday, with_todos=with_todos)

    # Handle empty state
    if not entries and not pending_todos and not weekly:
        ctx.console.print("No entries found for yesterday and no pending tasks.")
        return

    # Assemble output via service
    output = build_standup_text(
        entries=entries,
        pending_todos=pending_todos,
        output_format=output_format,
        date=yesterday,
        with_todos=with_todos,
        with_weekly=weekly,
        db=ctx.db if weekly else None,
    )

    # Export to Obsidian if requested
    if obsidian:
        from ..export.obsidian import (
            get_note_path,
            obsidian_is_configured,
            render_ai_report_note,
            strip_rich_markup,
            write_note,
        )

        obs_cfg = ctx.config.obsidian
        if not obsidian_is_configured(obs_cfg):
            ctx.console.print(
                "[yellow]![/yellow] Obsidian vault not configured. Set [bold]obsidian.vault_path[/bold] in config."
            )
        else:
            # Strip Rich markup before rendering the note
            clean_output = strip_rich_markup(output)
            note_content = render_ai_report_note(
                title=f"Standup · {yesterday.strftime('%B %d, %Y')}",
                report_kind="standup",
                content=clean_output,
                date=yesterday,
            )
            try:
                note_path = get_note_path(obs_cfg, "standup", yesterday, "Standup")
                write_note(note_path, note_content)
                ctx.console.print(
                    f"[green]✅[/green] Saved to Obsidian: [dim]{note_path}[/dim]"
                )
            except (OSError, ValueError) as e:
                ctx.console.print(f"[red]![/red] Failed to save to Obsidian: {e}")

    # Copy to clipboard if enabled
    if should_copy:
        try:
            import pyperclip

            pyperclip.copy(output)
            ctx.console.print("[green]✅[/green] Standup copied to clipboard!")
        except Exception:
            ctx.console.print(
                "[yellow]![/yellow] Could not copy to clipboard. Displaying instead:"
            )
            ctx.console.print()
            ctx.console.print(output)
    else:
        ctx.console.print()
        ctx.console.print(output)
