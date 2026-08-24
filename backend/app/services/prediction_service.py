"""
Pure spending-prediction math. Explainable statistical projection --
"if you keep spending at this rate" -- not a black-box ML model, per spec.
"""
from decimal import Decimal
from typing import Optional, List, Dict


def project_monthly_total(current_spent: Decimal, days_elapsed: int, days_in_month: int) -> Decimal:
    """Straight-line projection: (spent so far / days so far) * days in month."""
    if days_elapsed <= 0:
        return Decimal("0")
    daily_rate = current_spent / days_elapsed
    return round(daily_rate * days_in_month, 2)


def project_category_spending(
    category_spent: Dict[str, Decimal], days_elapsed: int, days_in_month: int
) -> List[dict]:
    results = []
    for category, spent in category_spent.items():
        projected = project_monthly_total(spent, days_elapsed, days_in_month)
        results.append({"category": category, "current_spent": spent, "projected_spent": projected})
    return sorted(results, key=lambda r: r["projected_spent"], reverse=True)


def calculate_budget_overrun(projected_total: Decimal, total_budgeted: Optional[Decimal]) -> Optional[Decimal]:
    """None if no budgets are set (nothing to compare against)."""
    if total_budgeted is None or total_budgeted <= 0:
        return None
    overrun = projected_total - total_budgeted
    return overrun if overrun > 0 else Decimal("0")
