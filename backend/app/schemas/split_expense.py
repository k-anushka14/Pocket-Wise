from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from app.schemas.enums import SplitDirection, SplitStatus


class SplitParticipantCreate(BaseModel):
    person_name: str = Field(min_length=1)
    amount_owed: Decimal = Field(gt=0)
    direction: SplitDirection


class SplitExpenseCreate(BaseModel):
    description: str = Field(min_length=1)
    total_amount: Decimal = Field(gt=0)
    date: date
    participants: List[SplitParticipantCreate] = Field(min_length=1)


class SplitParticipantOut(BaseModel):
    id: UUID
    person_name: str
    amount_owed: Decimal
    direction: SplitDirection
    status: SplitStatus

    class Config:
        from_attributes = True


class SplitExpenseOut(BaseModel):
    id: UUID
    description: str
    total_amount: Decimal
    date: date
    created_at: datetime
    participants: List[SplitParticipantOut]

    class Config:
        from_attributes = True
