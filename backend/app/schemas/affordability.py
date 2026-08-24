from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from app.schemas.enums import ExpenseCategory


class AffordabilityRequest(BaseModel):
    item_name: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0)
    category: Optional[ExpenseCategory] = None


class AffordabilityResponse(BaseModel):
    verdict: str  # yes | risky | no
    item_name: str
    amount: Decimal
    current_balance: Decimal
    after_purchase_balance: Decimal
    upcoming_recurring_total: Decimal
    explanation: List[str]
