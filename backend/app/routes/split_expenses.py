import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import List

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.split_expense import SplitExpense, SplitParticipant
from app.schemas.split_expense import SplitExpenseCreate, SplitExpenseOut
from app.schemas.enums import SplitStatus

router = APIRouter(prefix="/split-expenses", tags=["split-expenses"])


def _get_owned_split(db: Session, split_id: uuid.UUID, user_id: str) -> SplitExpense:
    split = db.get(SplitExpense, split_id)
    if not split or str(split.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Split expense not found")
    return split


def _get_owned_participant(db: Session, split_id: uuid.UUID, participant_id: uuid.UUID, user_id: str) -> SplitParticipant:
    split = _get_owned_split(db, split_id, user_id)
    for p in split.participants:
        if p.id == participant_id:
            return p
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")


@router.get("", response_model=List[SplitExpenseOut])
def list_split_expenses(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(SplitExpense)
        .where(SplitExpense.user_id == current_user.id)
        .options(selectinload(SplitExpense.participants))
        .order_by(SplitExpense.date.desc())
    )
    return db.execute(stmt).scalars().all()


@router.post("", response_model=SplitExpenseOut, status_code=status.HTTP_201_CREATED)
def create_split_expense(
    payload: SplitExpenseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    split = SplitExpense(
        id=uuid.uuid4(),
        user_id=current_user.id,
        description=payload.description,
        total_amount=payload.total_amount,
        date=payload.date,
    )
    for p in payload.participants:
        split.participants.append(
            SplitParticipant(
                id=uuid.uuid4(),
                person_name=p.person_name,
                amount_owed=p.amount_owed,
                direction=p.direction,
                status="pending",
            )
        )
    db.add(split)
    db.commit()
    db.refresh(split)
    return split


@router.put("/{split_id}/participants/{participant_id}/mark-paid", response_model=SplitExpenseOut)
def mark_participant_paid(
    split_id: uuid.UUID,
    participant_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = _get_owned_participant(db, split_id, participant_id, current_user.id)
    participant.status = SplitStatus.paid
    db.commit()
    split = _get_owned_split(db, split_id, current_user.id)
    db.refresh(split)
    return split


@router.delete("/{split_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_split_expense(
    split_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    split = _get_owned_split(db, split_id, current_user.id)
    db.delete(split)
    db.commit()
