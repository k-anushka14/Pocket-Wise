from decimal import Decimal
from datetime import date

from app.services.goal_service import calculate_goal_progress, calculate_savings_pace
from app.services.recurring_service import add_months, advance_due_date, days_until_due, is_due_soon


def test_goal_progress_basic():
    assert calculate_goal_progress(Decimal("8000"), Decimal("2000")) == 25.0


def test_goal_progress_caps_at_100():
    assert calculate_goal_progress(Decimal("1000"), Decimal("1500")) == 100.0


def test_goal_progress_avoids_division_by_zero():
    assert calculate_goal_progress(Decimal("0"), Decimal("500")) == 0.0


def test_savings_pace_weekly_amount():
    # Need 700/week, 8 weeks (56 days) out, remaining 5600
    result = calculate_savings_pace(
        target_amount=Decimal("8000"),
        current_amount=Decimal("2400"),
        deadline=date(2026, 10, 15),
        today=date(2026, 8, 20),
    )
    assert result["is_completed"] is False
    assert result["is_overdue"] is False
    assert result["amount_per_week"] > 0


def test_savings_pace_already_completed():
    result = calculate_savings_pace(Decimal("1000"), Decimal("1000"), date(2026, 12, 1), date(2026, 8, 20))
    assert result["is_completed"] is True
    assert result["amount_per_week"] is None


def test_savings_pace_overdue():
    result = calculate_savings_pace(Decimal("1000"), Decimal("200"), date(2026, 1, 1), date(2026, 8, 20))
    assert result["is_overdue"] is True
    assert result["amount_per_week"] is None


def test_savings_pace_no_deadline():
    result = calculate_savings_pace(Decimal("1000"), Decimal("200"), None, date(2026, 8, 20))
    assert result["amount_per_week"] is None
    assert result["is_completed"] is False
    assert result["is_overdue"] is False


def test_add_months_handles_month_end_clamping():
    # Jan 31 + 1 month -> Feb has no 31st, should clamp to Feb 28 (2026 not a leap year)
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_add_months_rolls_over_year():
    assert add_months(date(2026, 12, 15), 1) == date(2027, 1, 15)


def test_advance_due_date_weekly():
    assert advance_due_date(date(2026, 8, 20), "weekly") == date(2026, 8, 27)


def test_advance_due_date_monthly():
    assert advance_due_date(date(2026, 8, 20), "monthly") == date(2026, 9, 20)


def test_advance_due_date_yearly():
    assert advance_due_date(date(2026, 8, 20), "yearly") == date(2027, 8, 20)


def test_days_until_due():
    assert days_until_due(date(2026, 8, 25), date(2026, 8, 20)) == 5


def test_is_due_soon_within_threshold():
    assert is_due_soon(2, threshold=3) is True
    assert is_due_soon(3, threshold=3) is True


def test_is_due_soon_outside_threshold():
    assert is_due_soon(4, threshold=3) is False


def test_is_due_soon_false_when_overdue():
    assert is_due_soon(-1, threshold=3) is False
