"""Utility functions for stats calculations."""

from datetime import datetime, timedelta


def calculate_streak(dates: list[datetime]) -> tuple[int, int]:
    """Calculate current and longest streaks from a list of dates.

    Args:
        dates: List of datetime objects representing entry dates.

    Returns:
        Tuple of (current_streak, longest_streak) in days.
    """
    if not dates:
        return 0, 0

    # Get unique dates (as date objects)
    unique_dates = {d.date() for d in dates}
    sorted_dates = sorted(unique_dates)

    today = datetime.now().date()

    # Calculate current streak (counting back from today)
    current = 0
    for i in range(365):  # Check up to a year back
        check_date = today - timedelta(days=i)
        if check_date in unique_dates:
            current += 1
        elif i == 0:
            # Today might not have entries yet, continue checking
            continue
        else:
            # Gap found, streak ends
            break

    # Calculate longest streak
    longest = 1
    streak = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1

    return current, longest
