import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.recurring_expense import RecurringExpense
from app.models.transaction import Transaction
from app.schemas.recurring_expense import (
    RecurringExpenseCreate, RecurringExpenseUpdate, RecurringExpenseOut, MarkPaidRequest
)
from app.services.recurring_service import advance_due_date, days_until_due, is_due_soon

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])


def _to_out(expense: RecurringExpense) -> RecurringExpenseOut:
    days = days_until_due(expense.next_due_date, date.today())
    return RecurringExpenseOut(
        id=expense.id,
        name=expense.name,
        amount=expense.amount,
        category=expense.category,
        frequency=expense.frequency,
        next_due_date=expense.next_due_date,
        days_until_due=days,
        is_due_soon=is_due_soon(days),
        is_overdue=days < 0,
    )


def _get_owned_expense(db: Session, expense_id: uuid.UUID, user_id: str) -> RecurringExpense:
    expense = db.get(RecurringExpense, expense_id)
    if not expense or str(expense.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring expense not found")
    return expense


@router.get("", response_model=List[RecurringExpenseOut])
def list_recurring_expenses(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(RecurringExpense).where(RecurringExpense.user_id == current_user.id).order_by(RecurringExpense.next_due_date.asc())
    expenses = db.execute(stmt).scalars().all()
    return [_to_out(e) for e in expenses]


@router.post("", response_model=RecurringExpenseOut, status_code=status.HTTP_201_CREATED)
def create_recurring_expense(
    payload: RecurringExpenseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = RecurringExpense(id=uuid.uuid4(), user_id=current_user.id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return _to_out(expense)


@router.put("/{expense_id}", response_model=RecurringExpenseOut)
def update_recurring_expense(
    expense_id: uuid.UUID,
    payload: RecurringExpenseUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = _get_owned_expense(db, expense_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return _to_out(expense)


@router.post("/{expense_id}/mark-paid", response_model=RecurringExpenseOut)
def mark_paid(
    expense_id: uuid.UUID,
    payload: MarkPaidRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logs this cycle's payment as a real transaction (so it shows up in your
    spending history and budgets like any other expense) and rolls
    next_due_date forward by one frequency period.
    """
    expense = _get_owned_expense(db, expense_id, current_user.id)

    transaction = Transaction(
        id=uuid.uuid4(),
        user_id=current_user.id,
        amount=expense.amount,
        category=expense.category,
        description=f"{expense.name} (recurring)",
        date=date.today(),
        payment_method=payload.payment_method,
        type="need",
    )
    db.add(transaction)

    expense.next_due_date = advance_due_date(expense.next_due_date, expense.frequency)
    db.commit()
    db.refresh(expense)
    return _to_out(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_expense(
    expense_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = _get_owned_expense(db, expense_id, current_user.id)
    db.delete(expense)
    db.commit()
