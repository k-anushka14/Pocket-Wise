"""
Pure achievement-qualification logic. No DB access -- each check takes
numbers already computed elsewhere and returns True/False. The catalog
itself (code/name/description/icon) is the single source of truth for
what badges exist; the route layer seeds this into the DB on startup.
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict

ACHIEVEMENT_CATALOG = [
    {"code": "first_saver", "name": "First Saver", "icon": "🏆",
     "description": "Saved your first ₹500"},
    {"code": "seven_day_streak", "name": "7-Day Streak", "icon": "🔥",
     "description": "Stayed within budget for 7 consecutive days"},
    {"code": "money_saver", "name": "Money Saver", "icon": "💰",
     "description": "Saved 20% of your monthly income"},
    {"code": "no_spend_day", "name": "No-Spend Day", "icon": "🚫",
     "description": "Spent ₹0 in one day"},
    {"code": "goal_crusher", "name": "Goal Crusher", "icon": "🎯",
     "description": "Completed a savings goal"},
]


def check_first_saver(total_savings: Decimal) -> bool:
    return total_savings >= 500


def check_money_saver(savings_rate_pct: float) -> bool:
    return savings_rate_pct >= 20


def check_no_spend_day(no_spend_count_this_month: int) -> bool:
    return no_spend_count_this_month >= 1


def check_goal_crusher(goal_completion_flags: List[bool]) -> bool:
    return any(goal_completion_flags)


def calculate_budget_safe_streak(
    budgets: List[dict],  # [{"category": str, "amount": Decimal}]
    daily_category_spend: Dict[date, Dict[str, Decimal]],  # per-day, NOT cumulative
    day_range: List[date],  # every day from month start to today, in order
) -> int:
    """
    Longest run of consecutive days where cumulative spend in every
    budgeted category stayed within that category's monthly limit.
    A day with no budgets at all counts as safe (nothing to violate).
    """
    if not budgets:
        return len(day_range)

    budget_map = {b["category"]: b["amount"] for b in budgets}
    cumulative = {cat: Decimal("0") for cat in budget_map}

    longest = 0
    current = 0
    for day in day_range:
        day_spend = daily_category_spend.get(day, {})
        for cat, amt in day_spend.items():
            if cat in cumulative:
                cumulative[cat] += amt

        safe = all(cumulative[cat] <= limit for cat, limit in budget_map.items())
        if safe:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def check_seven_day_streak(streak: int) -> bool:
    return streak >= 7


def evaluate_achievements(context: dict) -> Dict[str, bool]:
    """
    context keys: total_savings, savings_rate_pct, no_spend_count,
    goal_completion_flags, budget_safe_streak
    """
    return {
        "first_saver": check_first_saver(context["total_savings"]),
        "seven_day_streak": check_seven_day_streak(context["budget_safe_streak"]),
        "money_saver": check_money_saver(context["savings_rate_pct"]),
        "no_spend_day": check_no_spend_day(context["no_spend_count"]),
        "goal_crusher": check_goal_crusher(context["goal_completion_flags"]),
    }
