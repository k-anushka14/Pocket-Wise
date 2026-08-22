"""
Financial Health Score -- deterministic and fully explainable, per the
product spec ("transparent and deterministic rather than pretending AI
generated the score"). Every component below is pure math over numbers
computed elsewhere; no DB access here, so all of it is unit-testable.

Score = sum of 5 weighted components, each 0..its weight, weights sum to 100:
  Savings rate        -- weight 30
  Budget adherence     -- weight 25
  Wants ratio          -- weight 15
  Spending consistency -- weight 15
  Goal progress        -- weight 15
"""
from decimal import Decimal
from statistics import pstdev, mean
from typing import List, Optional, TypedDict


class HealthComponents(TypedDict):
    savings_rate: float
    budget_adherence: float
    wants_ratio: float
    spending_consistency: float
    goal_progress: float


def savings_rate_percent(income: Decimal, expenses: Decimal) -> float:
    if income <= 0:
        return 0.0
    return float((income - expenses) / income * 100)


def savings_rate_score(rate_pct: float, weight: float = 30, target_pct: float = 30) -> float:
    """Full weight at target_pct% saved or better; scales linearly below that; 0 if negative."""
    if rate_pct <= 0:
        return 0.0
    return round(min(rate_pct / target_pct, 1.0) * weight, 1)


def budget_adherence_score(budgets: List[dict], weight: float = 25) -> float:
    """budgets: list of {percentage_used}. No budgets set -> full credit (nothing violated)."""
    if not budgets:
        return weight
    credits = []
    for b in budgets:
        pct = b["percentage_used"]
        if pct <= 100:
            credits.append(1.0)
        else:
            # Lose credit proportional to how far over -- 200% used = 0 credit.
            credits.append(max(0.0, 1 - (pct - 100) / 100))
    return round(mean(credits) * weight, 1)


def wants_ratio_score(wants_pct: float, weight: float = 15, good: float = 30, bad: float = 70) -> float:
    if wants_pct <= good:
        return weight
    if wants_pct >= bad:
        return 0.0
    fraction = 1 - (wants_pct - good) / (bad - good)
    return round(fraction * weight, 1)


def spending_consistency_score(weekly_amounts: List[Decimal], weight: float = 15) -> float:
    """Lower week-to-week variability = higher score. Not enough data -> full credit."""
    values = [float(a) for a in weekly_amounts]
    if len(values) < 2 or mean(values) == 0:
        return weight
    coefficient_of_variation = pstdev(values) / mean(values)
    return round(max(0.0, 1 - coefficient_of_variation) * weight, 1)


def goal_progress_score(goal_progress_list: List[float], weight: float = 15) -> float:
    """No goals -> full credit (nothing to be behind on)."""
    if not goal_progress_list:
        return weight
    return round((mean(goal_progress_list) / 100) * weight, 1)


def calculate_financial_health_score(
    income: Decimal,
    expenses: Decimal,
    budgets: List[dict],
    wants_pct: float,
    weekly_amounts: List[Decimal],
    goal_progress_list: List[float],
) -> dict:
    rate_pct = savings_rate_percent(income, expenses)
    components: HealthComponents = {
        "savings_rate": savings_rate_score(rate_pct),
        "budget_adherence": budget_adherence_score(budgets),
        "wants_ratio": wants_ratio_score(wants_pct),
        "spending_consistency": spending_consistency_score(weekly_amounts),
        "goal_progress": goal_progress_score(goal_progress_list),
    }
    total = round(sum(components.values()))
    total = max(0, min(100, total))
    return {
        "score": total,
        "components": components,
        "savings_rate_pct": round(rate_pct, 1),
    }


def generate_health_explanations(
    score_result: dict,
    wants_pct: float,
    overspent_categories: List[str],
) -> dict:
    """Returns {"strengths": [...], "weaknesses": [...]} in plain language."""
    strengths, weaknesses = [], []
    rate = score_result["savings_rate_pct"]
    components = score_result["components"]

    if rate >= 20:
        strengths.append(f"You're saving {rate}% of your income this month.")
    elif rate < 10:
        weaknesses.append(f"You're only saving {rate}% of your income this month.")

    if components["budget_adherence"] >= 22:
        strengths.append("You're staying within most of your category budgets.")
    if overspent_categories:
        names = ", ".join(c.replace("_", " ").title() for c in overspent_categories)
        weaknesses.append(f"You've gone over budget in: {names}.")

    if wants_pct <= 30:
        strengths.append("Most of your spending this month went to needs, not wants.")
    elif wants_pct >= 50:
        weaknesses.append(f"{round(wants_pct)}% of your spending this month was on wants.")

    if components["goal_progress"] >= 12:
        strengths.append("You're making strong progress on your savings goals.")

    if not strengths:
        strengths.append("Keep logging your spending -- consistent tracking is the first step.")
    if not weaknesses:
        weaknesses.append("No major red flags this month -- keep it up.")

    return {"strengths": strengths, "weaknesses": weaknesses}
