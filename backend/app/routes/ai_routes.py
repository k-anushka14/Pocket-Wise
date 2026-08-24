from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from decimal import Decimal
from datetime import date

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.transaction import Transaction
from app.models.savings_goal import SavingsGoal
from app.schemas.ai import CategorizeRequest, CategorizeResponse, AssistantRequest, AssistantResponse
from app.schemas.affordability import AffordabilityRequest, AffordabilityResponse
from app.services.ai.categorizer import categorize_expense
from app.services.ai.assistant import ask_assistant
from app.services.ai.gemini_client import client_available
from app.services.affordability_service import evaluate_affordability
from app.models.recurring_expense import RecurringExpense
from app.models.savings_goal import SavingsGoal as SavingsGoalModel
from app.services.budget_queries import normalize_to_month_start, get_budgets_with_status, month_end
from app.services.period_queries import get_monthly_income, get_monthly_expenses, get_spending_by_category_dicts, get_needs_wants
from app.services.dashboard_service import calculate_daily_spending_limit
from app.services.health_score_service import calculate_financial_health_score
from app.services.goal_service import calculate_goal_progress, calculate_savings_pace

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/categorize-expense", response_model=CategorizeResponse)
def categorize(
    payload: CategorizeRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Takes a natural-language description and suggests category, type, amount.
    Falls back gracefully if AI is unavailable.
    """
    available = client_available()
    result = categorize_expense(payload.description) if available else None

    if result:
        return CategorizeResponse(
            category=result["category"],
            type=result["type"],
            amount=result.get("amount"),
            confidence=result.get("confidence", "low"),
            ai_available=True,
        )

    # Graceful fallback -- "other / want, no amount, low confidence"
    return CategorizeResponse(
        category="other",
        type="want",
        amount=None,
        confidence="low",
        ai_available=False,
    )


@router.post("/assistant", response_model=AssistantResponse)
def assistant(
    payload: AssistantRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Answers a financial question using the user's real data as context.

    Only aggregated summary numbers are sent to Gemini -- never raw
    transaction lists, IDs, or any field not already visible to the user
    on their own dashboard.
    """
    user_id = current_user.id
    today = date.today()
    month_start = normalize_to_month_start(today)

    monthly_income = get_monthly_income(db, user_id, month_start)
    monthly_expenses = get_monthly_expenses(db, user_id, month_start)
    needs, wants = get_needs_wants(db, user_id, month_start)
    nw_total = needs + wants
    wants_pct = float(wants / nw_total * 100) if nw_total > 0 else 0.0

    # All-time balance
    from app.models.income import Income
    total_income = db.execute(
        select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user_id)
    ).scalar_one()
    total_expenses = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id)
    ).scalar_one()
    remaining_balance = total_income - total_expenses

    budgets = get_budgets_with_status(db, user_id, month_start)
    budget_dicts = [
        {"category": b.category, "percentage_used": b.percentage_used,
         "status": b.status, "spent": b.spent, "amount": b.amount}
        for b in budgets
    ]
    overspent = [b.category for b in budgets if b.status == "overspent"]

    goal_rows = db.execute(select(SavingsGoal).where(SavingsGoal.user_id == user_id)).scalars().all()
    goal_progress_list = [calculate_goal_progress(g.target_amount, g.current_amount) for g in goal_rows]

    health = calculate_financial_health_score(
        income=monthly_income, expenses=monthly_expenses, budgets=budget_dicts,
        wants_pct=wants_pct, weekly_amounts=[], goal_progress_list=goal_progress_list,
    )
    limit = calculate_daily_spending_limit(remaining_balance, today)

    category_dicts = get_spending_by_category_dicts(db, user_id, month_start)
    savings_rate = float((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0.0

    context = {
        "remaining_balance": remaining_balance,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "savings_rate_pct": savings_rate,
        "health_score": health["score"],
        "wants_pct": wants_pct,
        "days_remaining": limit["days_remaining"],
        "recommended_daily": limit["recommended_daily_spending"],
        "top_categories": category_dicts[:5],
        "overspent_budgets": overspent,
    }

    answer = ask_assistant(payload.question, context)
    return AssistantResponse(answer=answer, ai_available=client_available())


@router.post("/affordability-check", response_model=AffordabilityResponse)
def affordability_check(
    payload: AffordabilityRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    "Can I afford this?" -- fully deterministic (not AI-guessed), considers
    current balance, upcoming recurring expenses due this month, whether it
    would push a matching budget over, and whether it would delay your
    nearest-deadline savings goal.
    """
    user_id = current_user.id
    today = date.today()
    month_start = normalize_to_month_start(today)

    from app.models.income import Income
    total_income = db.execute(
        select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user_id)
    ).scalar_one()
    total_expenses = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id)
    ).scalar_one()
    current_balance = total_income - total_expenses

    # Upcoming recurring expenses due before the end of this month
    upcoming_recurring_total = db.execute(
        select(func.coalesce(func.sum(RecurringExpense.amount), 0)).where(
            RecurringExpense.user_id == user_id,
            RecurringExpense.next_due_date >= today,
            RecurringExpense.next_due_date <= month_end(month_start),
        )
    ).scalar_one()

    budget_context = None
    if payload.category:
        budgets = get_budgets_with_status(db, user_id, month_start)
        matching = next((b for b in budgets if b.category == payload.category), None)
        if matching:
            budget_context = {"category": matching.category, "spent": matching.spent, "amount": matching.amount}

    # Nearest-deadline goal with an active weekly pace, if any
    goal_context = None
    goal_rows = db.execute(
        select(SavingsGoalModel)
        .where(SavingsGoalModel.user_id == user_id, SavingsGoalModel.deadline.isnot(None))
        .order_by(SavingsGoalModel.deadline.asc())
    ).scalars().all()
    for g in goal_rows:
        pace = calculate_savings_pace(g.target_amount, g.current_amount, g.deadline, today)
        if pace["amount_per_week"]:
            goal_context = {"name": g.name, "amount_per_week": pace["amount_per_week"]}
            break

    result = evaluate_affordability(
        current_balance=current_balance,
        purchase_amount=payload.amount,
        upcoming_recurring_total=upcoming_recurring_total,
        budget_context=budget_context,
        goal_context=goal_context,
    )

    return AffordabilityResponse(
        verdict=result["verdict"],
        item_name=payload.item_name,
        amount=payload.amount,
        current_balance=current_balance,
        after_purchase_balance=result["after_purchase_balance"],
        upcoming_recurring_total=upcoming_recurring_total,
        explanation=result["explanation"],
    )
