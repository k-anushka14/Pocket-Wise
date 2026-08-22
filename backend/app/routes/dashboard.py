from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta
from decimal import Decimal

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.transaction import Transaction
from app.models.savings_goal import SavingsGoal
from app.models.income import Income
from app.schemas.dashboard import (
    DashboardSummary, CategoryAmount, PeriodAmount, DailySpendingLimit,
    NeedsWantsSummary, InsightItem, FinancialHealthOut, NoSpendDaysOut,
)
from app.schemas.transaction import TransactionOut
from app.services.budget_queries import normalize_to_month_start, get_budgets_with_status, month_end
from app.services.dashboard_service import calculate_daily_spending_limit
from app.services.insights_service import generate_all_insights
from app.services.health_score_service import calculate_financial_health_score, generate_health_explanations
from app.services.no_spend_service import calculate_no_spend_days
from app.services.goal_service import calculate_goal_progress
from app.services.period_queries import (
    get_monthly_income, get_monthly_expenses, get_spending_by_category_dicts,
    get_needs_wants, get_transaction_dates,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    today = date.today()
    month_start = normalize_to_month_start(today)

    # --- All-time totals: your available balance is everything you've
    # ever received minus everything you've ever spent, not just this month.
    total_income = db.execute(
        select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user_id)
    ).scalar_one()
    total_expenses = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id)
    ).scalar_one()
    remaining_balance = total_income - total_expenses
    total_savings = remaining_balance

    # --- Spending by category, current month
    category_dicts = get_spending_by_category_dicts(db, user_id, month_start)
    spending_by_category = [CategoryAmount(**c) for c in category_dicts]

    # --- Monthly spending, last 6 months (including current)
    monthly_spending = []
    for i in range(5, -1, -1):
        m = month_start
        for _ in range(i):
            m = (m.replace(day=1) - timedelta(days=1)).replace(day=1)
        total = db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.date >= m,
                Transaction.date <= month_end(m),
            )
        ).scalar_one()
        monthly_spending.append(PeriodAmount(label=m.strftime("%b %Y"), amount=total))

    # --- Weekly spending, last 4 weeks (Mon-Sun buckets, most recent last)
    weekly_spending = []
    week_start = today - timedelta(days=today.weekday())
    for i in range(3, -1, -1):
        w_start = week_start - timedelta(weeks=i)
        w_end = w_start + timedelta(days=6)
        total = db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.date >= w_start,
                Transaction.date <= w_end,
            )
        ).scalar_one()
        weekly_spending.append(PeriodAmount(label=f"Week of {w_start.strftime('%b %d')}", amount=total))

    # --- Recent transactions
    recent_rows = db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(5)
    ).scalars().all()
    recent_transactions = [TransactionOut.model_validate(t) for t in recent_rows]

    # --- Budgets for the current month, with spent/remaining/status attached
    budgets = get_budgets_with_status(db, user_id, month_start)

    # --- Daily spending limit
    limit = calculate_daily_spending_limit(remaining_balance, today)

    # --- Needs vs Wants, current month
    needs_total, wants_total = get_needs_wants(db, user_id, month_start)
    nw_total = needs_total + wants_total
    wants_pct = float(wants_total / nw_total * 100) if nw_total > 0 else 0.0
    needs_vs_wants = NeedsWantsSummary(needs=needs_total, wants=wants_total, wants_percentage=round(wants_pct, 1))

    # --- Smart insights
    budget_dicts = [
        {"category": b.category, "percentage_used": b.percentage_used, "status": b.status,
         "spent": b.spent, "amount": b.amount}
        for b in budgets
    ]
    weekly_dicts = [{"label": w.label, "amount": w.amount} for w in weekly_spending]
    insights = generate_all_insights(
        budgets=budget_dicts, weekly_spending=weekly_dicts,
        needs=needs_total, wants=wants_total, spending_by_category=category_dicts,
    )

    # --- Financial Health Score
    monthly_income = get_monthly_income(db, user_id, month_start)
    monthly_expenses = get_monthly_expenses(db, user_id, month_start)
    weekly_amounts = [w.amount for w in weekly_spending]

    goal_rows = db.execute(select(SavingsGoal).where(SavingsGoal.user_id == user_id)).scalars().all()
    goal_progress_list = [calculate_goal_progress(g.target_amount, g.current_amount) for g in goal_rows]

    health_result = calculate_financial_health_score(
        income=monthly_income, expenses=monthly_expenses, budgets=budget_dicts,
        wants_pct=wants_pct, weekly_amounts=weekly_amounts, goal_progress_list=goal_progress_list,
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

    # --- No-spend days, month-to-date
    spend_dates = get_transaction_dates(db, user_id, month_start, today)
    no_spend_result = calculate_no_spend_days(spend_dates, month_start, today)
    no_spend_days = NoSpendDaysOut(**no_spend_result)

    return DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        remaining_balance=remaining_balance,
        total_savings=total_savings,
        spending_by_category=spending_by_category,
        monthly_spending=monthly_spending,
        weekly_spending=weekly_spending,
        recent_transactions=recent_transactions,
        budgets=budgets,
        daily_spending_limit=DailySpendingLimit(**limit),
        needs_vs_wants=needs_vs_wants,
        insights=[InsightItem(**i) for i in insights],
        financial_health=financial_health,
        no_spend_days=no_spend_days,
    )

