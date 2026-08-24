from decimal import Decimal

from app.services.prediction_service import (
    project_monthly_total, project_category_spending, calculate_budget_overrun,
)


def test_project_monthly_total_basic():
    # spent 2000 in 10 days -> 200/day -> 30 days = 6000
    assert project_monthly_total(Decimal("2000"), 10, 30) == Decimal("6000.00")


def test_project_monthly_total_zero_days_elapsed():
    assert project_monthly_total(Decimal("0"), 0, 30) == Decimal("0")


def test_project_category_spending_sorted_descending():
    category_spent = {"food": Decimal("1000"), "shopping": Decimal("3000"), "transport": Decimal("200")}
    result = project_category_spending(category_spent, days_elapsed=10, days_in_month=30)
    assert result[0]["category"] == "shopping"
    assert result[-1]["category"] == "transport"


def test_calculate_budget_overrun_none_without_budgets():
    assert calculate_budget_overrun(Decimal("8000"), None) is None
    assert calculate_budget_overrun(Decimal("8000"), Decimal("0")) is None


def test_calculate_budget_overrun_positive():
    assert calculate_budget_overrun(Decimal("8500"), Decimal("8000")) == Decimal("500")


def test_calculate_budget_overrun_zero_when_under():
    assert calculate_budget_overrun(Decimal("7000"), Decimal("8000")) == Decimal("0")
