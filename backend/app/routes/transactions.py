import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.schemas.enums import ExpenseCategory, PaymentMethod, ExpenseType, SortField, SortDirection

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _get_owned_transaction(db: Session, transaction_id: uuid.UUID, user_id: str) -> Transaction:
    txn = db.get(Transaction, transaction_id)
    if not txn or str(txn.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    search: Optional[str] = Query(default=None, description="Matches against description/notes"),
    category: Optional[ExpenseCategory] = None,
    payment_method: Optional[PaymentMethod] = None,
    type: Optional[ExpenseType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: SortField = SortField.date,
    sort_dir: SortDirection = SortDirection.desc,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conditions = [Transaction.user_id == current_user.id]

    if category:
        conditions.append(Transaction.category == category.value)
    if payment_method:
        conditions.append(Transaction.payment_method == payment_method.value)
    if type:
        conditions.append(Transaction.type == type.value)
    if date_from:
        conditions.append(Transaction.date >= date_from)
    if date_to:
        conditions.append(Transaction.date <= date_to)
    if search:
        like = f"%{search}%"
        conditions.append(
            Transaction.description.ilike(like) | Transaction.notes.ilike(like)
        )

    stmt = select(Transaction).where(and_(*conditions))

    sort_column = Transaction.date if sort_by == SortField.date else Transaction.amount
    stmt = stmt.order_by(sort_column.desc() if sort_dir == SortDirection.desc else sort_column.asc())

    return db.execute(stmt).scalars().all()


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txn = Transaction(id=uuid.uuid4(), user_id=current_user.id, **payload.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_transaction(db, transaction_id, current_user.id)


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txn = _get_owned_transaction(db, transaction_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txn = _get_owned_transaction(db, transaction_id, current_user.id)
    db.delete(txn)
    db.commit()
