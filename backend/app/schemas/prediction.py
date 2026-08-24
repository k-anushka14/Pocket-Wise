from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class CategoryPrediction(BaseModel):
    category: str
    current_spent: Decimal
    projected_spent: Decimal


class SpendingPrediction(BaseModel):
    days_elapsed: int
    days_remaining: int
    current_month_spent: Decimal
    projected_month_total: Decimal
    total_budgeted: Optional[Decimal]
    projected_overrun: Optional[Decimal]
    category_predictions: List[CategoryPrediction]
