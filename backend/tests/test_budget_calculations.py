from decimal import Decimal
from datetime import date

from app.services.budget_service import calculate_budget_percentage, calculate_budget_status
from app.services.dashboard_service import calculate_daily_spending_limit


def test_budget_percentage_basic():
    assert calculate_budget_percentage(Decimal("2000"), Decimal("1000")) == 50.0


def test_budget_percentage_avoids_division_by_zero():
    assert calculate_budget_percentage(Decimal("0"), Decimal("500")) == 0.0


def test_budget_status_normal():
    assert calculate_budget_status(50) == "normal"


def test_budget_status_warning_boundary():
    assert calculate_budget_status(70) == "warning"
    assert calculate_budget_status(89.9) == "warning"


def test_budget_status_critical_boundary():
    assert calculate_budget_status(90) == "critical"
    assert calculate_budget_status(100) == "critical"


def test_budget_status_overspent():
    assert calculate_budget_status(101) == "overspent"


def test_daily_spending_limit_never_negative():
    result = calculate_daily_spending_limit(Decimal("-500"), date(2026, 8, 20))
    assert result["remaining_balance"] == Decimal("0")
    assert result["recommended_daily_spending"] == Decimal("0.00")


def test_daily_spending_limit_end_of_month():
    # Aug 31 -> only today counts as remaining, 1 day
    result = calculate_daily_spending_limit(Decimal("200"), date(2026, 8, 31))
    assert result["days_remaining"] == 1
    assert result["recommended_daily_spending"] == Decimal("200.00")


def test_daily_spending_limit_mid_month():
    # Aug 20 -> 12 days remain (20 through 31 inclusive)
    result = calculate_daily_spending_limit(Decimal("3200"), date(2026, 8, 20))
    assert result["days_remaining"] == 12
