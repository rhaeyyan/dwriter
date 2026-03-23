"""Standup command for generating standup summaries."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..cli import AppContext

import click

from ..tui.colors import PROJECT, TAG


def format_standup_bullets(entries: Any) -> str:
    """Format entries as bullet points."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] - {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'[{TAG}]#[/]{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_slack(entries: Any) -> str:
    """Format entries for Slack."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] • {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_jira(entries: Any) -> str:
    """Format entries for Jira."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] * {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_markdown(entries: Any) -> str:
    """Format entries as Markdown."""
    lines = []
    for entry in entries:
        time_str = entry.created_at.strftime("%I:%M %p")
        line = f"[#23c76b]{time_str}[/#23c76b] - {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{PROJECT}]&{entry.project}[/{PROJECT}]"
        lines.append(line)
    return "\n".join(lines)


def format_todos(todos: Any, output_format: str) -> str:
    """Format pending todos based on the selected output format."""
    lines = []
    for todo in todos:
        if output_format == "slack":
            bullet = "•"
        elif output_format == "jira":
            bullet = "*"
        elif output_format == "markdown":
            bullet = "- [ ]"
        else:
            bullet = "-"

        line = f"{bullet} {todo.content}"

        if todo.tag_names:
            if output_format == "bullets":
                tags_list = ", ".join(f"[{TAG}]#{tag}[/{TAG}]" for tag in todo.tag_names)
            else:
                tags_list = ", ".join(f"#{tag}" for tag in todo.tag_names)
            line += f" ({tags_list})"

        if todo.project:
            if output_format in ["bullets", "markdown"]:
                line += f" [{PROJECT}]&{todo.project}[/{PROJECT}]"
            else:
                line += f" &{todo.project}"

        lines.append(line)
    return "\n".join(lines)


FORMATTERS = {
    "bullets": format_standup_bullets,
    "slack": format_standup_slack,
    "jira": format_standup_jira,
    "markdown": format_standup_markdown,
}


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
@click.pass_obj
def standup(
    ctx: AppContext,
    output_format: str,
    no_copy: bool,
    with_todos: bool,
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
    """
    # Use config defaults if not specified
    if output_format is None:
        output_format = ctx.config.standup.format

    if no_copy is None:
        should_copy = ctx.config.standup.copy_to_clipboard
    else:
        should_copy = not no_copy

    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    entries = ctx.db.get_entries_by_date(yesterday)

    # Get pending todos if requested
    pending_todos = []
    if with_todos:
        pending_todos = ctx.db.get_todos(status="pending")

    # Handle empty state
    if not entries and not pending_todos:
        ctx.console.print("No entries found for yesterday and no pending tasks.")
        return

    # Format the standup
    formatter = FORMATTERS.get(output_format, format_standup_bullets)
    standup_text = formatter(entries) if entries else ""

    # Add header
    header = f"Yesterday's Standup ({yesterday.strftime('%Y-%m-%d')})"
    output = f"{header}\n{standup_text}" if standup_text else header

    # Append pending todos if requested
    if with_todos:
        if pending_todos:
            todo_header = "\n\nPlan for Today:"
            if output_format in ["slack", "jira"]:
                todo_header = f"\n\n*{todo_header.strip()}*"
            elif output_format == "markdown":
                todo_header = f"\n\n### {todo_header.strip()}"

            todo_text = format_todos(pending_todos, output_format)
            output += f"{todo_header}\n{todo_text}"
        else:
            output += "\n\nPlan for Today:\n(No pending tasks)"

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
