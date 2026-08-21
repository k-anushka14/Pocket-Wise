from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.schemas.enums import ExpenseCategory
from app.services.budget_service import BudgetStatus


class BudgetCreate(BaseModel):
    category: ExpenseCategory
    amount: Decimal = Field(gt=0)
    month: date  # any date within the target month; normalized to the 1st server-side


class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)


class BudgetOut(BaseModel):
    id: UUID
    category: ExpenseCategory
    amount: Decimal
    month: date
    spent: Decimal
    remaining: Decimal
    percentage_used: float
    status: BudgetStatus

    class Config:
        from_attributes = True
