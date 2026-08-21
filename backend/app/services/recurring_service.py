"""
Pure date math for recurring expenses -- advancing due dates and figuring
out whether a reminder should fire. No DB access, unit testable directly.
"""
from datetime import date
from calendar import monthrange


def add_months(d: date, months: int) -> date:
    total_month_index = d.month - 1 + months
    year = d.year + total_month_index // 12
    month = total_month_index % 12 + 1
    last_day_of_target_month = monthrange(year, month)[1]
    day = min(d.day, last_day_of_target_month)
    return date(year, month, day)


def advance_due_date(current_due: date, frequency: str) -> date:
    if frequency == "weekly":
        from datetime import timedelta
        return current_due + timedelta(days=7)
    if frequency == "monthly":
        return add_months(current_due, 1)
    if frequency == "yearly":
        return add_months(current_due, 12)
    raise ValueError(f"Unknown frequency: {frequency}")


def days_until_due(due_date: date, today: date) -> int:
    return (due_date - today).days


def is_due_soon(days_until: int, threshold: int = 3) -> bool:
    """True if due within `threshold` days (including today) but not yet overdue."""
    return 0 <= days_until <= threshold
