"""
Deterministic dashboard calculations. Every number here is computed from
the user's actual income/transaction/budget rows -- nothing here is
AI-generated or approximated, so it stays transparent and testable.
"""
from datetime import date, timedelta
from decimal import Decimal
from calendar import monthrange


def calculate_daily_spending_limit(remaining_balance: Decimal, today: date) -> dict:
    """
    Recommended daily spending = remaining balance / days left until the
    end of the current month.

    This is a simple proxy for "days until your next income" -- Phase 4
    (recurring expenses) will let us track actual next-income dates and
    make this smarter. For now, end-of-month is the most defensible
    assumption we can make without guessing.
    """
    last_day_of_month = monthrange(today.year, today.month)[1]
    days_remaining = (date(today.year, today.month, last_day_of_month) - today).days + 1
    days_remaining = max(days_remaining, 1)

    safe_balance = max(remaining_balance, Decimal("0"))
    recommended = safe_balance / days_remaining

    return {
        "days_remaining": days_remaining,
        "remaining_balance": safe_balance,
        "recommended_daily_spending": round(recommended, 2),
    }
