from decimal import Decimal
from datetime import date, timedelta

from app.services.achievements_service import (
    check_first_saver, check_money_saver, check_no_spend_day, check_goal_crusher,
    calculate_budget_safe_streak, check_seven_day_streak, evaluate_achievements,
    ACHIEVEMENT_CATALOG,
)


def test_catalog_has_five_badges_with_required_fields():
    assert len(ACHIEVEMENT_CATALOG) == 5
    for badge in ACHIEVEMENT_CATALOG:
        assert set(badge.keys()) == {"code", "name", "icon", "description"}


def test_first_saver_threshold():
    assert check_first_saver(Decimal("500")) is True
    assert check_first_saver(Decimal("499")) is False


def test_money_saver_threshold():
    assert check_money_saver(20.0) is True
    assert check_money_saver(19.9) is False


def test_no_spend_day_threshold():
    assert check_no_spend_day(1) is True
    assert check_no_spend_day(0) is False


def test_goal_crusher_any_completed():
    assert check_goal_crusher([False, False, True]) is True
    assert check_goal_crusher([False, False]) is False
    assert check_goal_crusher([]) is False


def test_budget_safe_streak_no_budgets_all_days_safe():
    days = [date(2026, 8, 1) + timedelta(days=i) for i in range(10)]
    assert calculate_budget_safe_streak([], {}, days) == 10


def test_budget_safe_streak_all_days_within_limit():
    days = [date(2026, 8, 1) + timedelta(days=i) for i in range(7)]
    budgets = [{"category": "food", "amount": Decimal("2000")}]
    daily_spend = {d: {"food": Decimal("100")} for d in days}  # 700 total, well under 2000
    assert calculate_budget_safe_streak(budgets, daily_spend, days) == 7


def test_budget_safe_streak_breaks_on_overspend():
    days = [date(2026, 8, 1) + timedelta(days=i) for i in range(10)]
    budgets = [{"category": "food", "amount": Decimal("500")}]
    # Days 0-3: 100/day (safe, cumulative up to 400). Day 4: +200 -> cumulative 600, breaks streak.
    # Days 5-9: 50/day, cumulative climbs slowly from 600 but they're already over forever
    # since it's cumulative -- so streak should be exactly 4 (days 0-3).
    daily_spend = {days[i]: {"food": Decimal("100")} for i in range(4)}
    daily_spend[days[4]] = {"food": Decimal("200")}
    for i in range(5, 10):
        daily_spend[days[i]] = {"food": Decimal("10")}
    assert calculate_budget_safe_streak(budgets, daily_spend, days) == 4


def test_seven_day_streak_threshold():
    assert check_seven_day_streak(7) is True
    assert check_seven_day_streak(6) is False


def test_evaluate_achievements_combines_all_checks():
    context = {
        "total_savings": Decimal("600"),
        "savings_rate_pct": 25.0,
        "no_spend_count": 2,
        "goal_completion_flags": [True],
        "budget_safe_streak": 8,
    }
    result = evaluate_achievements(context)
    assert all(result.values())


def test_evaluate_achievements_none_qualify():
    context = {
        "total_savings": Decimal("100"),
        "savings_rate_pct": 5.0,
        "no_spend_count": 0,
        "goal_completion_flags": [False],
        "budget_safe_streak": 2,
    }
    result = evaluate_achievements(context)
    assert not any(result.values())
