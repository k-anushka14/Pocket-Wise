"""
Pure no-spend-day calculation. No DB access -- takes a set of dates that
already had at least one transaction and does the counting/streak math.
"""
from datetime import date, timedelta
from typing import Set


def calculate_no_spend_days(spend_dates: Set[date], range_start: date, range_end: date) -> dict:
    """
    range_end should be "today" if the month is still in progress, or the
    actual month-end if it's a past month -- the caller decides that,
    this function just counts/walks whatever range it's given.
    """
    if range_end < range_start:
        return {"count": 0, "longest_streak": 0}

    total_days = (range_end - range_start).days + 1
    no_spend_count = 0
    longest_streak = 0
    current_streak = 0

    d = range_start
    for _ in range(total_days):
        if d not in spend_dates:
            no_spend_count += 1
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0
        d += timedelta(days=1)

    return {"count": no_spend_count, "longest_streak": longest_streak}
