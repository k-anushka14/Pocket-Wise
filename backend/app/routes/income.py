import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeOut

router = APIRouter(prefix="/income", tags=["income"])


def _get_owned_income(db: Session, income_id: uuid.UUID, user_id: str) -> Income:
    income = db.get(Income, income_id)
    if not income or str(income.user_id) != str(user_id):
        # Same 404 whether it doesn't exist or belongs to someone else --
        # never reveal that another user's record exists.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    return income


@router.get("", response_model=List[IncomeOut])
def list_income(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Income).where(Income.user_id == current_user.id).order_by(Income.date.desc())
    return db.execute(stmt).scalars().all()


@router.post("", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(
    payload: IncomeCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = Income(id=uuid.uuid4(), user_id=current_user.id, **payload.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.put("/{income_id}", response_model=IncomeOut)
def update_income(
    income_id: uuid.UUID,
    payload: IncomeUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = _get_owned_income(db, income_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(income, field, value)
    db.commit()
    db.refresh(income)
    return income


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = _get_owned_income(db, income_id, current_user.id)
    db.delete(income)
    db.commit()
