from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from app.schemas.enums import IncomeSource, RecurrenceFrequency


class IncomeBase(BaseModel):
    amount: Decimal = Field(gt=0)
    source: IncomeSource
    date: date
    is_recurring: bool = False
    frequency: Optional[RecurrenceFrequency] = None
    notes: Optional[str] = None

    @field_validator("frequency")
    @classmethod
    def frequency_requires_recurring(cls, v, info):
        # If a frequency is given, is_recurring must be true -- validated
        # against info.data since is_recurring is parsed first.
        if v is not None and not info.data.get("is_recurring", False):
            raise ValueError("frequency can only be set when is_recurring is true")
        return v


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    source: Optional[IncomeSource] = None
    date: Optional[date] = None
    is_recurring: Optional[bool] = None
    frequency: Optional[RecurrenceFrequency] = None
    notes: Optional[str] = None


class IncomeOut(IncomeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
