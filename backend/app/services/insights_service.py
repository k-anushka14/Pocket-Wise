"""
Pure, deterministic insight generation. Every message here is templated
from real numbers already computed elsewhere (budget status, category
totals, needs/wants split, weekly comparison) -- nothing is AI-generated,
so it's honest and fully unit-testable without a database.
"""
from decimal import Decimal
from typing import List, TypedDict, Optional


class Insight(TypedDict):
    type: str
    message: str
    severity: str  # info | warning | critical


# Categories where students specifically care about "what % of my spending
# is this eating up" -- called out per the product spec's Student Mode.
STUDENT_WATCH_CATEGORIES = {"hostel", "transport", "education"}


def budget_alerts(budgets: List[dict]) -> List[Insight]:
    """budgets: list of {category, percentage_used, status, spent, amount}"""
    alerts: List[Insight] = []
    for b in budgets:
        category_label = b["category"].replace("_", " ").title()
        if b["status"] == "warning":
            alerts.append({
                "type": "budget_warning",
                "message": f"⚠️ You've used {b['percentage_used']}% of your {category_label} budget.",
                "severity": "warning",
            })
        elif b["status"] == "critical":
            alerts.append({
                "type": "budget_critical",
                "message": f"🚨 You've used {b['percentage_used']}% of your {category_label} budget -- almost there.",
                "severity": "critical",
            })
        elif b["status"] == "overspent":
            over_by = b["spent"] - b["amount"]
            alerts.append({
                "type": "budget_overspent",
                "message": f"🚨 You exceeded your {category_label} budget by ₹{over_by:,.0f}.",
                "severity": "critical",
            })
    return alerts


def weekly_change_alert(weekly_spending: List[dict], threshold_pct: float = 20.0) -> Optional[Insight]:
    """weekly_spending: list of {label, amount}, oldest first, at least 2 entries."""
    if len(weekly_spending) < 2:
        return None
    prev = Decimal(str(weekly_spending[-2]["amount"]))
    latest = Decimal(str(weekly_spending[-1]["amount"]))
    if prev <= 0:
        return None
    change_pct = float((latest - prev) / prev * 100)
    if change_pct >= threshold_pct:
        return {
            "type": "weekly_increase",
            "message": f"📈 Your spending this week is {round(change_pct)}% higher than last week.",
            "severity": "warning",
        }
    return None


def needs_wants_insight(needs: Decimal, wants: Decimal, threshold_pct: float = 40.0) -> Optional[Insight]:
    total = needs + wants
    if total <= 0:
        return None
    wants_pct = float(wants / total * 100)
    if wants_pct >= threshold_pct:
        return {
            "type": "wants_high",
            "message": f"💡 {round(wants_pct)}% of your spending this month was on wants, not needs.",
            "severity": "info",
        }
    return None


def student_category_insights(spending_by_category: List[dict], threshold_pct: float = 25.0) -> List[Insight]:
    """spending_by_category: list of {category, amount}."""
    total = sum(Decimal(str(c["amount"])) for c in spending_by_category)
    if total <= 0:
        return []

    insights: List[Insight] = []
    icons = {"hostel": "🏠", "transport": "🚌", "education": "📚"}
    for c in spending_by_category:
        if c["category"] not in STUDENT_WATCH_CATEGORIES:
            continue
        amount = Decimal(str(c["amount"]))
        pct = float(amount / total * 100)
        if pct >= threshold_pct:
            label = c["category"].title()
            icon = icons.get(c["category"], "📌")
            insights.append({
                "type": "student_category",
                "message": f"{icon} {label} expenses are {round(pct)}% of your monthly spending.",
                "severity": "info",
            })
    return insights


def generate_all_insights(
    budgets: List[dict],
    weekly_spending: List[dict],
    needs: Decimal,
    wants: Decimal,
    spending_by_category: List[dict],
) -> List[Insight]:
    insights: List[Insight] = []
    insights.extend(budget_alerts(budgets))

    weekly = weekly_change_alert(weekly_spending)
    if weekly:
        insights.append(weekly)

    needs_wants = needs_wants_insight(needs, wants)
    if needs_wants:
        insights.append(needs_wants)

    insights.extend(student_category_insights(spending_by_category))

    # Critical/warning first so the most actionable alerts surface at the top.
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda i: severity_order.get(i["severity"], 3))
    return insights
