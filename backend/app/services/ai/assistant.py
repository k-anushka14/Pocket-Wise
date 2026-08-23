"""
AI Financial Assistant.

Builds a minimal context from the user's real data (no passwords, no raw
transaction IDs -- only the aggregated summary numbers the user would
already see on their dashboard), then sends it to Gemini with their question.

If AI is unavailable, returns a static fallback message.
"""
from decimal import Decimal
from typing import List

from app.services.ai.gemini_client import client_available, generate

SYSTEM_CONTEXT = """You are PocketWise, a friendly and practical financial assistant for an Indian college student.

You have access to the user's financial summary below. Use it to give specific, actionable answers.
Always respond in 2-4 sentences. Use ₹ for amounts. Be encouraging but honest.

USER FINANCIAL SUMMARY:
{summary}

USER QUESTION: {question}

Respond in plain text, no markdown headers or bullet points unless listing steps.
"""

FALLBACK_RESPONSE = (
    "I'm not able to reach the AI service right now. "
    "Check your dashboard for a breakdown of your spending and budget status — "
    "those numbers tell the same story without AI."
)


def build_summary(data: dict) -> str:
    """
    Converts only the aggregated numbers from the dashboard into a short
    text summary. Never includes: passwords, tokens, raw IDs, or any
    field that isn't already shown to the user in their own dashboard.
    """
    lines = [
        f"Balance: ₹{data.get('remaining_balance', 0):,.0f}",
        f"Monthly income: ₹{data.get('monthly_income', 0):,.0f}",
        f"Monthly expenses: ₹{data.get('monthly_expenses', 0):,.0f}",
        f"Savings rate: {data.get('savings_rate_pct', 0):.1f}%",
        f"Financial health score: {data.get('health_score', 0)}/100",
        f"Wants as % of spending: {data.get('wants_pct', 0):.1f}%",
        f"Days remaining in month: {data.get('days_remaining', 0)}",
        f"Recommended daily spend: ₹{data.get('recommended_daily', 0):,.0f}",
    ]

    if data.get("top_categories"):
        cats = ", ".join(
            f"{c['category'].replace('_', ' ')} ₹{c['amount']:,.0f}"
            for c in data["top_categories"][:4]
        )
        lines.append(f"Top spending categories this month: {cats}")

    if data.get("overspent_budgets"):
        lines.append(f"Over-budget categories: {', '.join(data['overspent_budgets'])}")

    return "\n".join(lines)


def ask_assistant(question: str, financial_context: dict) -> str:
    if not client_available():
        return FALLBACK_RESPONSE

    summary = build_summary(financial_context)
    prompt = SYSTEM_CONTEXT.format(summary=summary, question=question)
    response = generate(prompt, temperature=0.4)
    return response if response else FALLBACK_RESPONSE
