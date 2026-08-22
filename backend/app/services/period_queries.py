"""
Shared DB queries for "give me numbers for this month" -- used by both
/dashboard and /reports/monthly so the two never drift out of sync with
slightly different SQL for the same underlying question.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.income import Income
from app.models.transaction import Transaction
from app.services.budget_queries import month_end


def get_monthly_income(db: Session, user_id, month_start: date) -> Decimal:
    return db.execute(
        select(func.coalesce(func.sum(Income.amount), 0)).where(
            Income.user_id == user_id,
            Income.date >= month_start,
            Income.date <= month_end(month_start),
        )
    ).scalar_one()


def get_monthly_expenses(db: Session, user_id, month_start: date) -> Decimal:
    return db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.date <= month_end(month_start),
        )
    ).scalar_one()


def get_spending_by_category_dicts(db: Session, user_id, month_start: date) -> List[dict]:
    rows = db.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.date <= month_end(month_start),
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    return [{"category": cat, "amount": amt} for cat, amt in rows]


def get_needs_wants(db: Session, user_id, month_start: date) -> tuple[Decimal, Decimal]:
    rows = db.execute(
        select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.date <= month_end(month_start),
        )
        .group_by(Transaction.type)
    ).all()
    m = {t: amt for t, amt in rows}
    return m.get("need", Decimal("0")), m.get("want", Decimal("0"))


def get_largest_expense(db: Session, user_id, month_start: date) -> Optional[Transaction]:
    return db.execute(
        select(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.date <= month_end(month_start),
        )
        .order_by(Transaction.amount.desc())
        .limit(1)
    ).scalar_one_or_none()


def get_transaction_dates(db: Session, user_id, range_start: date, range_end: date) -> set:
    rows = db.execute(
        select(Transaction.date).where(
            Transaction.user_id == user_id,
            Transaction.date >= range_start,
            Transaction.date <= range_end,
        ).distinct()
    ).all()
    return {r[0] for r in rows}
