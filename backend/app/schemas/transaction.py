from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from app.schemas.enums import ExpenseCategory, PaymentMethod, ExpenseType


class TransactionBase(BaseModel):
    amount: Decimal = Field(gt=0)
    category: ExpenseCategory
    description: Optional[str] = None
    date: date
    payment_method: PaymentMethod
    type: ExpenseType
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    type: Optional[ExpenseType] = None
    notes: Optional[str] = None


class TransactionOut(TransactionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
