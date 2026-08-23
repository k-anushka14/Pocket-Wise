"""
AI expense categorizer.

Takes a natural-language description like "Bought pizza with friends for ₹450"
and returns the most likely category, type (need/want), and the amount if it
can be found in the text.

If AI is unavailable, returns None so the caller can leave it to the user.
"""
from typing import Optional

from app.services.ai.gemini_client import client_available, generate, parse_json_response

# The exact enum values the backend and frontend both know about.
VALID_CATEGORIES = [
    "food", "cafe", "transport", "education", "shopping", "entertainment",
    "hostel", "recharge", "subscriptions", "personal_care", "health",
    "gifts", "groceries", "other",
]

CATEGORIZE_PROMPT = """You are a personal finance assistant for an Indian college student.

Analyze this expense description and return ONLY a JSON object (no markdown, no explanation):

Description: "{description}"

Return exactly:
{{
  "category": one of {categories},
  "type": "need" or "want",
  "amount": number or null,
  "confidence": "high" or "low"
}}

Rules:
- food/cafe = eating out or drinks; groceries = cooking ingredients
- education = textbooks, courses, fees
- needs = rent, food, transport, medicine, education essentials
- wants = entertainment, cafe, shopping, subscriptions for leisure
- amount: extract from description only if clearly stated (e.g. ₹450, Rs 450, 450 rupees); otherwise null
"""


def categorize_expense(description: str) -> Optional[dict]:
    """
    Returns dict with keys: category, type, amount, confidence
    or None if AI is unavailable or response was unparseable.
    """
    if not client_available():
        return None

    prompt = CATEGORIZE_PROMPT.format(
        description=description,
        categories=str(VALID_CATEGORIES),
    )
    raw = generate(prompt, temperature=0.1)
    result = parse_json_response(raw)

    if result is None:
        return None

    # Validate -- never trust AI output unconditionally.
    if result.get("category") not in VALID_CATEGORIES:
        result["category"] = "other"
    if result.get("type") not in ("need", "want"):
        result["type"] = "want"

    return result
