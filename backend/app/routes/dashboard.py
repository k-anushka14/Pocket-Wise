from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta
from decimal import Decimal

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.income import Income
from app.models.transaction import Transaction
from app.schemas.dashboard import DashboardSummary, CategoryAmount, PeriodAmount, DailySpendingLimit
from app.schemas.transaction import TransactionOut
from app.services.budget_queries import normalize_to_month_start, get_budgets_with_status, month_end
from app.services.dashboard_service import calculate_daily_spending_limit

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
    # Until Phase 4's Savings Goals / Emergency Fund exist, "savings" is
    # simply what's left unspent -- this will get more precise once money
    # can be explicitly earmarked.
    total_savings = remaining_balance

    # --- Spending by category, current month
    category_rows = db.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.date <= month_end(month_start),
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    spending_by_category = [CategoryAmount(category=cat, amount=amt) for cat, amt in category_rows]

    # --- Monthly spending, last 6 months (including current)
    monthly_spending = []
    for i in range(5, -1, -1):
        # Walk back month by month without relying on a DB-specific
        # date_trunc function, so this works the same in tests/sqlite too.
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
    )
