"""Standup command for generating standup summaries."""

from datetime import datetime, timedelta

import click

from ..cli import AppContext


def format_standup_bullets(entries):
    """Format entries as bullet points."""
    lines = []
    for entry in entries:
        line = f"- {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{entry.project}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_slack(entries):
    """Format entries for Slack."""
    lines = []
    for entry in entries:
        line = f"• {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{entry.project}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_jira(entries):
    """Format entries for Jira."""
    lines = []
    for entry in entries:
        line = f"* {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{entry.project}]"
        lines.append(line)
    return "\n".join(lines)


def format_standup_markdown(entries):
    """Format entries as Markdown."""
    lines = []
    for entry in entries:
        line = f"- {entry.content}"
        if entry.tags:
            line += f" ({', '.join(f'#{tag.name}' for tag in entry.tags)})"
        if entry.project:
            line += f" [{entry.project}]"
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
@click.pass_obj
def standup(ctx: AppContext, output_format: str, no_copy: bool):
    """Generate yesterday's standup.

    Queries all entries from yesterday and formats them for standup meetings.
    By default, copies the output to clipboard.

    Examples:
        dwriter standup

        dwriter standup --format slack

        dwriter standup --format jira

        dwriter standup --no-copy
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

    if not entries:
        ctx.console.print("No entries found for yesterday.")
        return

    # Format the standup
    formatter = FORMATTERS.get(output_format, format_standup_bullets)
    standup_text = formatter(entries)

    # Add header
    header = f"Yesterday's Standup ({yesterday.strftime('%Y-%m-%d')})"
    output = f"{header}\n{standup_text}"

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
