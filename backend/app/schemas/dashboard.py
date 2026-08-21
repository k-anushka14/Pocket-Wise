from pydantic import BaseModel
from decimal import Decimal
from typing import List

from app.schemas.transaction import TransactionOut
from app.schemas.budget import BudgetOut


class CategoryAmount(BaseModel):
    category: str
    amount: Decimal


class PeriodAmount(BaseModel):
    label: str
    amount: Decimal


class DailySpendingLimit(BaseModel):
    days_remaining: int
    remaining_balance: Decimal
    recommended_daily_spending: Decimal


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    remaining_balance: Decimal
    total_savings: Decimal
    spending_by_category: List[CategoryAmount]
    monthly_spending: List[PeriodAmount]
    weekly_spending: List[PeriodAmount]
    recent_transactions: List[TransactionOut]
    budgets: List[BudgetOut]
    daily_spending_limit: DailySpendingLimit
