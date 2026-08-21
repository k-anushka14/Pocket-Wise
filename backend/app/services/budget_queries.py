"""
DB-touching budget helpers. Kept separate from budget_service.py (which is
pure math) so the math stays unit-testable without a database, while this
module handles fetching the numbers that math needs.
"""
import uuid
from datetime import date
from decimal import Decimal
from calendar import monthrange
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetOut
from app.services.budget_service import calculate_budget_percentage, calculate_budget_status


def normalize_to_month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def month_end(d: date) -> date:
    last_day = monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last_day)


def _spent_for_category_month(db: Session, user_id, category: str, month_start: date) -> Decimal:
    end = month_end(month_start)
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.date >= month_start,
        Transaction.date <= end,
    )
    return db.execute(stmt).scalar_one()


def budget_to_out(db: Session, budget: Budget) -> BudgetOut:
    spent = _spent_for_category_month(db, budget.user_id, budget.category, budget.month)
    percentage = calculate_budget_percentage(budget.amount, spent)
    return BudgetOut(
        id=budget.id,
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        spent=spent,
        remaining=budget.amount - spent,
        percentage_used=round(percentage, 1),
        status=calculate_budget_status(percentage),
    )


def get_budgets_with_status(db: Session, user_id, month_start: date) -> list[BudgetOut]:
    stmt = select(Budget).where(Budget.user_id == user_id, Budget.month == month_start)
    budgets = db.execute(stmt).scalars().all()
    return [budget_to_out(db, b) for b in budgets]
