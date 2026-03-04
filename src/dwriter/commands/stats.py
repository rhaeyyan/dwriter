"""Stats command for showing logging statistics and streaks."""

from datetime import datetime, timedelta

import click

from ..cli import AppContext


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
@click.pass_obj
def stats(ctx: AppContext):
    """Show logging stats and streak.

    Displays statistics about your logging activity including:
    - Total entries
    - Current streak
    - Longest streak
    - First and last entry dates
    - Top projects and tags
    """
    total_entries = ctx.db.get_total_entries_count()

    if total_entries == 0:
        ctx.console.print(
            "No entries yet. Start logging with:\n"
            '  [bold]dwriter add "your task"[/bold]'
        )
        return

    dates_with_entries = ctx.db.get_entries_with_streaks()
    current_streak, longest_streak = calculate_streak(dates_with_entries)

    # Get date range using optimized SQL query
    first_date, last_date = ctx.db.get_date_range()

    ctx.console.print("[bold blue]Day Writer Statistics[/bold blue]")
    ctx.console.print("=" * 40)
    ctx.console.print()

    # Total entries
    ctx.console.print(f"Total Entries:     [bold]{total_entries}[/bold]")
    ctx.console.print()

    # Streaks
    streak_display = f"{current_streak} days"
    if current_streak >= 7:
        streak_display += " 🔥"
    ctx.console.print(f"Current Streak:    {streak_display}")
    ctx.console.print(f"Longest Streak:    {longest_streak} days")
    ctx.console.print()

    # Date range
    if first_date and last_date:
        first_date_str = first_date.strftime("%Y-%m-%d")
        last_date_str = last_date.strftime("%Y-%m-%d")
        ctx.console.print(f"First Entry:       {first_date_str}")
        ctx.console.print(f"Last Entry:        {last_date_str}")

        days_active = (last_date - first_date).days + 1
        if days_active > 0:
            consistency = (len(dates_with_entries) / days_active) * 100
            ctx.console.print(
                f"Consistency:       {consistency:.1f}% "
                f"({len(dates_with_entries)}/{days_active} days)"
            )

    ctx.console.print()

    # Project stats
    project_stats = ctx.db.get_project_stats()
    if project_stats:
        ctx.console.print("[purple]Top Projects:[/purple]")
        for project, count in list(project_stats.items())[:5]:
            ctx.console.print(f"  {project}: {count} entries")
        ctx.console.print()

    # Tag stats
    tag_stats = ctx.db.get_entries_with_tags_count()
    if tag_stats:
        ctx.console.print("[#ffae00]Top Tags:[/#ffae00]")
        for tag, count in list(tag_stats.items())[:5]:
            ctx.console.print(f"  #{tag}: {count} entries")
        ctx.console.print()

    # Encouragement
    if current_streak >= 30:
        ctx.console.print(
            "[bold green]🏆 Amazing! A month-long streak![/bold green]"
        )
    elif current_streak >= 7:
        ctx.console.print(
            "[yellow]🔥 Great job! Keep the momentum going![/yellow]"
        )
    elif current_streak > 0:
        ctx.console.print("Keep logging! Every entry counts!")
    else:
        ctx.console.print("Start your streak by logging something today!")
