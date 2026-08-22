from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

from app.schemas.dashboard import FinancialHealthOut, InsightItem
from app.schemas.transaction import TransactionOut


class MonthlyReport(BaseModel):
    month_label: str  # e.g. "August 2026"
    income: Decimal
    expenses: Decimal
    savings: Decimal
    savings_rate_pct: float
    top_category: Optional[str]
    largest_expense: Optional[TransactionOut]
    needs: Decimal
    wants: Decimal
    financial_health: FinancialHealthOut
    insights: List[InsightItem]
