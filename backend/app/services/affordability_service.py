"""
Pure "Can I afford this?" logic. No DB access -- takes numbers already
computed elsewhere and returns a verdict + plain-English explanation.
Deterministic by design (per spec: "give a clear explanation instead
of simply saying yes/no", not an AI guess).
"""
from decimal import Decimal
from typing import Optional, List, Literal

Verdict = Literal["yes", "risky", "no"]


def calculate_after_purchase_balance(balance: Decimal, amount: Decimal) -> Decimal:
    return balance - amount


def is_over_budget_after_purchase(
    spent: Decimal, budget_amount: Decimal, purchase_amount: Decimal
) -> bool:
    return (spent + purchase_amount) > budget_amount


def estimate_goal_delay_days(purchase_amount: Decimal, amount_per_week: Optional[Decimal]) -> int:
    """
    How many extra days the purchase would push back a goal's deadline,
    assuming you keep contributing at the same weekly pace. 0 if there's
    no active pace to compare against (no deadline, already complete, etc).
    """
    if not amount_per_week or amount_per_week <= 0:
        return 0
    weeks_delay = purchase_amount / amount_per_week
    return int((weeks_delay * 7).to_integral_value(rounding="ROUND_CEILING"))


def evaluate_affordability(
    current_balance: Decimal,
    purchase_amount: Decimal,
    upcoming_recurring_total: Decimal,
    budget_context: Optional[dict] = None,   # {"category": str, "spent": Decimal, "amount": Decimal}
    goal_context: Optional[dict] = None,      # {"name": str, "amount_per_week": Decimal}
) -> dict:
    after_balance = calculate_after_purchase_balance(current_balance, purchase_amount)

    explanation: List[str] = []
    verdict: Verdict = "yes"

    if after_balance < 0:
        verdict = "no"
        explanation.append(
            f"This would take your balance to ₹{after_balance:,.0f} -- below zero."
        )
        return {
            "verdict": verdict,
            "after_purchase_balance": after_balance,
            "budget_overspend": False,
            "goal_delay_days": 0,
            "explanation": explanation,
        }

    if after_balance < upcoming_recurring_total:
        verdict = "risky"
        explanation.append(
            f"You have ₹{upcoming_recurring_total:,.0f} in upcoming recurring expenses due this month, "
            f"and only ₹{after_balance:,.0f} would be left after this purchase."
        )

    budget_overspend = False
    if budget_context:
        budget_overspend = is_over_budget_after_purchase(
            budget_context["spent"], budget_context["amount"], purchase_amount
        )
        if budget_overspend:
            verdict = "risky"
            category_label = budget_context["category"].replace("_", " ").title()
            over_by = (budget_context["spent"] + purchase_amount) - budget_context["amount"]
            explanation.append(
                f"This would put you ₹{over_by:,.0f} over your {category_label} budget for the month."
            )

    goal_delay_days = 0
    if goal_context:
        goal_delay_days = estimate_goal_delay_days(purchase_amount, goal_context.get("amount_per_week"))
        if goal_delay_days > 0:
            verdict = "risky"
            explanation.append(
                f"Your \"{goal_context['name']}\" goal could be delayed by approximately {goal_delay_days} day{'s' if goal_delay_days != 1 else ''}."
            )

    if not explanation:
        explanation.append("This fits comfortably within your current balance and commitments.")

    return {
        "verdict": verdict,
        "after_purchase_balance": after_balance,
        "budget_overspend": budget_overspend,
        "goal_delay_days": goal_delay_days,
        "explanation": explanation,
    }
