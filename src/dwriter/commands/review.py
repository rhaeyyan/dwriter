"""Review command for generating periodic summaries."""

from datetime import datetime, timedelta

import click

from ..cli import AppContext


def format_review_markdown(entries_by_date):
    """Format entries as Markdown grouped by date."""
    lines = []
    for date, entries in entries_by_date.items():
        date_str = date.strftime("%A, %Y-%m-%d")
        lines.append(f"## {date_str}")
        lines.append("")
        for entry in entries:
            line = f"- {entry.content}"
            if entry.tag_names:
                line += f" ({', '.join(f'#{t}' for t in entry.tag_names)})"
            if entry.project:
                line += f" [{entry.project}]"
            lines.append(line)
        lines.append("")
    return "\n".join(lines)


def format_review_plain(entries_by_date):
    """Format entries as plain text grouped by date."""
    lines = []
    for date, entries in entries_by_date.items():
        date_str = date.strftime("%A, %Y-%m-%d")
        lines.append(f"{date_str}")
        lines.append("-" * 40)
        for entry in entries:
            line = f"  • {entry.content}"
            if entry.tag_names:
                line += f" ({', '.join(f'#{t}' for t in entry.tag_names)})"
            if entry.project:
                line += f" [{entry.project}]"
            lines.append(line)
        lines.append("")
    return "\n".join(lines)


def format_review_slack(entries_by_date):
    """Format entries for Slack grouped by date."""
    lines = []
    for date, entries in entries_by_date.items():
        date_str = date.strftime("*%A, %Y-%m-%d*")
        lines.append(date_str)
        for entry in entries:
            line = f"  • {entry.content}"
            if entry.tag_names:
                line += f" ({', '.join(f'#{t}' for t in entry.tag_names)})"
            if entry.project:
                line += f" [{entry.project}]"
            lines.append(line)
        lines.append("")
    return "\n".join(lines)


FORMATTERS = {
    "markdown": format_review_markdown,
    "plain": format_review_plain,
    "slack": format_review_slack,
}


@click.command()
@click.option(
    "-d",
    "--days",
    "num_days",
    type=int,
    default=None,
    help="Number of days to review (default: 5)",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["markdown", "plain", "slack"]),
    default=None,
    help="Output format: markdown, plain, slack",
)
@click.pass_obj
def review(ctx: AppContext, num_days: int, output_format: str):
    """Review last N days.

    Generates a summary of all entries from the past N days,
    grouped by date. Useful for sprint retrospectives or timesheets.

    Examples:
        dwriter review

        dwriter review --days 7

        dwriter review --format markdown
    """
    # Use config defaults if not specified
    if num_days is None:
        num_days = ctx.config.review.default_days

    if output_format is None:
        output_format = ctx.config.review.format

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)

    entries = ctx.db.get_entries_in_range(start_date, end_date)

    if not entries:
        ctx.console.print(f"No entries found in the last {num_days} days.")
        return

    # Group entries by date
    entries_by_date = {}
    for entry in entries:
        date_key = entry.created_at.date()
        if date_key not in entries_by_date:
            entries_by_date[date_key] = []
        entries_by_date[date_key].append(entry)

    # Sort dates in descending order
    sorted_dates = sorted(entries_by_date.keys(), reverse=True)
    sorted_entries_by_date = {date: entries_by_date[date] for date in sorted_dates}

    # Format the review
    formatter = FORMATTERS.get(output_format, format_review_markdown)
    review_text = formatter(sorted_entries_by_date)

    # Add header
    header = f"Review: Last {num_days} Days"
    output = f"{header}\n{review_text}"

    ctx.console.print()
    ctx.console.print(output)
