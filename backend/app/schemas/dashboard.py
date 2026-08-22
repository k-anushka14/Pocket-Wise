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


class NeedsWantsSummary(BaseModel):
    needs: Decimal
    wants: Decimal
    wants_percentage: float


class InsightItem(BaseModel):
    type: str
    message: str
    severity: str  # info | warning | critical


class HealthScoreComponents(BaseModel):
    savings_rate: float
    budget_adherence: float
    wants_ratio: float
    spending_consistency: float
    goal_progress: float


class FinancialHealthOut(BaseModel):
    score: int
    components: HealthScoreComponents
    savings_rate_pct: float
    strengths: List[str]
    weaknesses: List[str]


class NoSpendDaysOut(BaseModel):
    count: int
    longest_streak: int


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
    needs_vs_wants: NeedsWantsSummary
    insights: List[InsightItem]
    financial_health: FinancialHealthOut
    no_spend_days: NoSpendDaysOut
