from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date
from calendar import monthrange
from decimal import Decimal

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.budget import Budget
from app.schemas.prediction import SpendingPrediction, CategoryPrediction
from app.services.budget_queries import normalize_to_month_start
from app.services.period_queries import get_monthly_expenses, get_spending_by_category_dicts
from app.services.prediction_service import project_monthly_total, project_category_spending, calculate_budget_overrun

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=SpendingPrediction)
def get_predictions(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simple, explainable straight-line projection: if you keep spending at
    your current daily rate, here's where you'll likely land by month end.
    Deliberately NOT a black-box ML model, per spec.
    """
    user_id = current_user.id
    today = date.today()
    month_start = normalize_to_month_start(today)
    days_in_month = monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    days_remaining = days_in_month - days_elapsed

    current_month_spent = get_monthly_expenses(db, user_id, month_start)
    projected_total = project_monthly_total(current_month_spent, days_elapsed, days_in_month)

    total_budgeted = db.execute(
        select(func.coalesce(func.sum(Budget.amount), 0)).where(
            Budget.user_id == user_id, Budget.month == month_start
        )
    ).scalar_one()
    total_budgeted = total_budgeted if total_budgeted > 0 else None
    overrun = calculate_budget_overrun(projected_total, total_budgeted)

    category_dicts = get_spending_by_category_dicts(db, user_id, month_start)
    category_spent_map = {c["category"]: c["amount"] for c in category_dicts}
    category_predictions = project_category_spending(category_spent_map, days_elapsed, days_in_month)

    return SpendingPrediction(
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        current_month_spent=current_month_spent,
        projected_month_total=projected_total,
        total_budgeted=total_budgeted,
        projected_overrun=overrun,
        category_predictions=[CategoryPrediction(**c) for c in category_predictions],
    )
