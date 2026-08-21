"""
Pure, deterministic budget math -- no DB access here on purpose, so these
functions can be unit tested directly (see tests/test_budget_calculations.py)
without needing a database connection.
"""
from decimal import Decimal
from typing import Literal

BudgetStatus = Literal["normal", "warning", "critical", "overspent"]


def calculate_budget_percentage(amount: Decimal, spent: Decimal) -> float:
    """Percentage of a budget used. 0 if the budget amount is 0 (avoid div/0)."""
    if amount <= 0:
        return 0.0
    return float((spent / amount) * 100)


def calculate_budget_status(percentage: float) -> BudgetStatus:
    """
    Warning levels, per spec:
    < 70%      -> normal
    70-90%     -> warning
    90-100%    -> critical
    > 100%     -> overspent
    """
    if percentage > 100:
        return "overspent"
    if percentage >= 90:
        return "critical"
    if percentage >= 70:
        return "warning"
    return "normal"
