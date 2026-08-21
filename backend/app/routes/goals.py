import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.savings_goal import SavingsGoal
from app.schemas.savings_goal import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalOut, ContributionCreate
)
from app.services.goal_service import calculate_goal_progress, calculate_savings_pace

router = APIRouter(prefix="/goals", tags=["goals"])


def _to_out(goal: SavingsGoal) -> SavingsGoalOut:
    pace = calculate_savings_pace(goal.target_amount, goal.current_amount, goal.deadline, date.today())
    return SavingsGoalOut(
        id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        deadline=goal.deadline,
        priority=goal.priority,
        progress_percentage=calculate_goal_progress(goal.target_amount, goal.current_amount),
        amount_per_week=pace["amount_per_week"],
        amount_per_month=pace["amount_per_month"],
        is_completed=pace["is_completed"],
        is_overdue=pace["is_overdue"],
        days_remaining=pace["days_remaining"],
    )


def _get_owned_goal(db: Session, goal_id: uuid.UUID, user_id: str) -> SavingsGoal:
    goal = db.get(SavingsGoal, goal_id)
    if not goal or str(goal.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings goal not found")
    return goal


@router.get("", response_model=List[SavingsGoalOut])
def list_goals(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(SavingsGoal).where(SavingsGoal.user_id == current_user.id).order_by(SavingsGoal.deadline.asc().nulls_last())
    goals = db.execute(stmt).scalars().all()
    return [_to_out(g) for g in goals]


@router.post("", response_model=SavingsGoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: SavingsGoalCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = SavingsGoal(id=uuid.uuid4(), user_id=current_user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _to_out(goal)


@router.put("/{goal_id}", response_model=SavingsGoalOut)
def update_goal(
    goal_id: uuid.UUID,
    payload: SavingsGoalUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, goal_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return _to_out(goal)


@router.post("/{goal_id}/contribute", response_model=SavingsGoalOut)
def contribute_to_goal(
    goal_id: uuid.UUID,
    payload: ContributionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, goal_id, current_user.id)
    goal.current_amount = goal.current_amount + payload.amount
    db.commit()
    db.refresh(goal)
    return _to_out(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, goal_id, current_user.id)
    db.delete(goal)
    db.commit()
