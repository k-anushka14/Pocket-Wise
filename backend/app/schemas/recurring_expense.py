from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.schemas.enums import ExpenseCategory, RecurrenceFrequency, PaymentMethod


class RecurringExpenseCreate(BaseModel):
    name: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    category: ExpenseCategory
    frequency: RecurrenceFrequency
    next_due_date: date


class RecurringExpenseUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category: Optional[ExpenseCategory] = None
    frequency: Optional[RecurrenceFrequency] = None
    next_due_date: Optional[date] = None


class MarkPaidRequest(BaseModel):
    payment_method: PaymentMethod = PaymentMethod.other


class RecurringExpenseOut(BaseModel):
    id: UUID
    name: str
    amount: Decimal
    category: ExpenseCategory
    frequency: RecurrenceFrequency
    next_due_date: date
    days_until_due: int
    is_due_soon: bool
    is_overdue: bool

    class Config:
        from_attributes = True
