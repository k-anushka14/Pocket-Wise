from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from datetime import date

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.savings_goal import SavingsGoal
from app.schemas.report import MonthlyReport
from app.schemas.dashboard import FinancialHealthOut, InsightItem
from app.schemas.transaction import TransactionOut
from app.services.budget_queries import normalize_to_month_start, get_budgets_with_status
from app.services.period_queries import (
    get_monthly_income, get_monthly_expenses, get_spending_by_category_dicts,
    get_needs_wants, get_largest_expense,
)
from app.services.insights_service import generate_all_insights
from app.services.health_score_service import calculate_financial_health_score, generate_health_explanations
from app.services.goal_service import calculate_goal_progress

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(
    month: Optional[date] = Query(default=None, description="Any date within the target month; defaults to the current month"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    month_start = normalize_to_month_start(month or date.today())

    income = get_monthly_income(db, user_id, month_start)
    expenses = get_monthly_expenses(db, user_id, month_start)
    savings = income - expenses
    savings_rate_pct = float(savings / income * 100) if income > 0 else 0.0

    category_dicts = get_spending_by_category_dicts(db, user_id, month_start)
    top_category = category_dicts[0]["category"] if category_dicts else None

    largest_expense_row = get_largest_expense(db, user_id, month_start)
    largest_expense = TransactionOut.model_validate(largest_expense_row) if largest_expense_row else None

    needs, wants = get_needs_wants(db, user_id, month_start)
    nw_total = needs + wants
    wants_pct = float(wants / nw_total * 100) if nw_total > 0 else 0.0

    budgets = get_budgets_with_status(db, user_id, month_start)
    budget_dicts = [
        {"category": b.category, "percentage_used": b.percentage_used, "status": b.status,
         "spent": b.spent, "amount": b.amount}
        for b in budgets
    ]

    # The health score's "spending consistency" component compares week-to-
    # week variability, which is meaningful for a live, in-progress dashboard
    # but not for a single already-closed month being reported on -- so the
    # report passes an empty list here, and that component simply awards
    # full credit (see health_score_service.spending_consistency_score).
    goal_rows = db.execute(select(SavingsGoal).where(SavingsGoal.user_id == user_id)).scalars().all()
    goal_progress_list = [calculate_goal_progress(g.target_amount, g.current_amount) for g in goal_rows]

    health_result = calculate_financial_health_score(
        income=income, expenses=expenses, budgets=budget_dicts,
        wants_pct=wants_pct, weekly_amounts=[], goal_progress_list=goal_progress_list,
    )
    overspent_categories = [b.category for b in budgets if b.status == "overspent"]
    explanations = generate_health_explanations(health_result, wants_pct, overspent_categories)
    financial_health = FinancialHealthOut(
        score=health_result["score"],
        components=health_result["components"],
        savings_rate_pct=health_result["savings_rate_pct"],
        strengths=explanations["strengths"],
        weaknesses=explanations["weaknesses"],
    )

    insights = generate_all_insights(
        budgets=budget_dicts, weekly_spending=[], needs=needs, wants=wants,
        spending_by_category=category_dicts,
    )

    return MonthlyReport(
        month_label=month_start.strftime("%B %Y"),
        income=income,
        expenses=expenses,
        savings=savings,
        savings_rate_pct=round(savings_rate_pct, 1),
        top_category=top_category,
        largest_expense=largest_expense,
        needs=needs,
        wants=wants,
        financial_health=financial_health,
        insights=[InsightItem(**i) for i in insights],
    )
