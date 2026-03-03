"""Stats command for showing logging statistics and streaks."""

from datetime import datetime, timedelta

import click

from ..database import Database


def calculate_streak(dates_with_entries):
    """Calculate current logging streak.

    Args:
        dates_with_entries: List of datetime objects with entries.

    Returns:
        Tuple of (current_streak, longest_streak).
    """
    if not dates_with_entries:
        return 0, 0

    # Get unique dates sorted descending
    unique_dates = sorted(set(d.date() for d in dates_with_entries), reverse=True)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Calculate current streak
    current_streak = 0
    expected_date = today

    # Check if there's an entry today
    if unique_dates and unique_dates[0] == today:
        current_streak = 1
        expected_date = yesterday
    elif unique_dates and unique_dates[0] == yesterday:
        expected_date = yesterday - timedelta(days=1)
    else:
        current_streak = 0
        expected_date = yesterday

    # Count consecutive days
    for i, date in enumerate(unique_dates):
        if i == 0 and date == today:
            continue

        if date == expected_date:
            current_streak += 1
            expected_date = date - timedelta(days=1)
        else:
            break

    # Calculate longest streak
    if not unique_dates:
        return current_streak, 0

    longest_streak = 1
    current_count = 1

    sorted_dates = sorted(unique_dates)
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
            current_count += 1
            longest_streak = max(longest_streak, current_count)
        else:
            current_count = 1

    return current_streak, longest_streak


@click.command()
@click.pass_context
def stats(ctx):
    """Show logging stats and streak.

    Displays statistics about your logging activity including:
    - Total entries
    - Current streak
    - Longest streak
    - First and last entry dates
    """
    db = Database()

    total_entries = db.get_all_entries_count()

    if total_entries == 0:
        click.echo("No entries yet. Start logging with:")
        click.echo(click.style('  dwriter add "your task"', bold=True))
        return

    dates_with_entries = db.get_entries_with_streaks()
    current_streak, longest_streak = calculate_streak(dates_with_entries)

    # Get first and last entry
    all_entries = db.get_entries_in_range(datetime(2000, 1, 1), datetime(2100, 1, 1))

    first_entry = min(all_entries, key=lambda e: e.created_at) if all_entries else None
    last_entry = max(all_entries, key=lambda e: e.created_at) if all_entries else None

    click.echo(click.style("Day Writer Statistics", bold=True, fg="blue"))
    click.echo("=" * 40)
    click.echo()

    # Total entries
    click.echo(f"Total Entries:     {click.style(str(total_entries), bold=True)}")
    click.echo()

    # Streaks
    streak_display = f"{current_streak} days"
    if current_streak >= 7:
        streak_display += click.style(" 🔥", fg="yellow")
    click.echo(f"Current Streak:    {streak_display}")
    click.echo(f"Longest Streak:    {longest_streak} days")
    click.echo()

    # Date range
    if first_entry and last_entry:
        first_date = first_entry.created_at.strftime("%Y-%m-%d")
        last_date = last_entry.created_at.strftime("%Y-%m-%d")
        click.echo(f"First Entry:       {first_date}")
        click.echo(f"Last Entry:        {last_date}")

        days_active = (last_entry.created_at - first_entry.created_at).days + 1
        if days_active > 0:
            consistency = (len(dates_with_entries) / days_active) * 100
            click.echo(
                f"Consistency:       {consistency:.1f}% "
                f"({len(dates_with_entries)}/{days_active} days)"
            )

    click.echo()

    # Encouragement
    if current_streak >= 30:
        click.echo(
            click.style(
                "🏆 Amazing! A month-long streak!",
                fg="green",
                bold=True,
            )
        )
    elif current_streak >= 7:
        click.echo(
            click.style(
                "🔥 Great job! Keep the momentum going!",
                fg="yellow",
            )
        )
    elif current_streak > 0:
        click.echo("Keep logging! Every entry counts!")
    else:
        click.echo("Start your streak by logging something today!")
