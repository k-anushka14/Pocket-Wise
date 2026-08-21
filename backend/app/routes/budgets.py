import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from app.services.budget_queries import (
    normalize_to_month_start,
    get_budgets_with_status,
    budget_to_out,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _get_owned_budget(db: Session, budget_id: uuid.UUID, user_id: str) -> Budget:
    budget = db.get(Budget, budget_id)
    if not budget or str(budget.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.get("", response_model=List[BudgetOut])
def list_budgets(
    month: Optional[date] = Query(default=None, description="Any date within the target month; defaults to the current month"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = normalize_to_month_start(month or date.today())
    return get_budgets_with_status(db, current_user.id, target_month)


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    month_start = normalize_to_month_start(payload.month)
    budget = Budget(
        id=uuid.uuid4(),
        user_id=current_user.id,
        category=payload.category,
        amount=payload.amount,
        month=month_start,
    )
    db.add(budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A budget for this category already exists this month -- edit it instead.",
        )
    db.refresh(budget)
    return budget_to_out(db, budget)


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: uuid.UUID,
    payload: BudgetUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = _get_owned_budget(db, budget_id, current_user.id)
    if payload.amount is not None:
        budget.amount = payload.amount
    db.commit()
    db.refresh(budget)
    return budget_to_out(db, budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = _get_owned_budget(db, budget_id, current_user.id)
    db.delete(budget)
    db.commit()
