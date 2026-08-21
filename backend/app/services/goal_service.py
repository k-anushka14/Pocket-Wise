"""
Pure savings-goal math -- no DB access, so it's unit testable directly.
"""
from decimal import Decimal
from datetime import date
from typing import Optional


def calculate_goal_progress(target_amount: Decimal, current_amount: Decimal) -> float:
    if target_amount <= 0:
        return 0.0
    pct = float((current_amount / target_amount) * 100)
    return min(round(pct, 1), 100.0)


def calculate_savings_pace(
    target_amount: Decimal,
    current_amount: Decimal,
    deadline: Optional[date],
    today: date,
) -> dict:
    """
    How much to save per week/month to hit the goal by its deadline.

    Returns amount_per_week / amount_per_month as None when there's no
    deadline (nothing to pace against) or the goal is already complete.
    is_overdue is true when there's a deadline in the past and the goal
    isn't finished yet.
    """
    remaining = max(target_amount - current_amount, Decimal("0"))
    is_completed = current_amount >= target_amount

    if is_completed or deadline is None:
        return {
            "amount_per_week": None,
            "amount_per_month": None,
            "is_completed": is_completed,
            "is_overdue": False,
            "days_remaining": None,
        }

    days_remaining = (deadline - today).days

    if days_remaining <= 0:
        return {
            "amount_per_week": None,
            "amount_per_month": None,
            "is_completed": False,
            "is_overdue": True,
            "days_remaining": days_remaining,
        }

    weeks_remaining = max(days_remaining / 7, 1 / 7)
    months_remaining = max(days_remaining / 30, 1 / 30)

    return {
        "amount_per_week": round(remaining / Decimal(str(weeks_remaining)), 2),
        "amount_per_month": round(remaining / Decimal(str(months_remaining)), 2),
        "is_completed": False,
        "is_overdue": False,
        "days_remaining": days_remaining,
    }
