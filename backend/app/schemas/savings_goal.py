from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.schemas.enums import GoalPriority


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1)
    target_amount: Decimal = Field(gt=0)
    current_amount: Decimal = Field(default=Decimal("0"), ge=0)
    deadline: Optional[date] = None
    priority: GoalPriority = GoalPriority.medium


class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[Decimal] = Field(default=None, gt=0)
    deadline: Optional[date] = None
    priority: Optional[GoalPriority] = None


class ContributionCreate(BaseModel):
    amount: Decimal = Field(gt=0)


class SavingsGoalOut(BaseModel):
    id: UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    deadline: Optional[date]
    priority: GoalPriority
    progress_percentage: float
    amount_per_week: Optional[Decimal]
    amount_per_month: Optional[Decimal]
    is_completed: bool
    is_overdue: bool
    days_remaining: Optional[int]

    class Config:
        from_attributes = True
