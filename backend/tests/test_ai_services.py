"""
Tests for the AI service layer. Because these test pure logic in the
AI modules, we stub the pydantic Settings so we don't need a real .env.
"""
import os, sys
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Stub out env vars so pydantic-settings doesn't require a real .env
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "placeholder")
os.environ.setdefault("SUPABASE_JWT_SECRET", "placeholder")
os.environ.setdefault("DATABASE_URL", "postgresql://placeholder")
os.environ.setdefault("GEMINI_API_KEY", "placeholder")

from app.services.ai.categorizer import categorize_expense
from app.services.ai.assistant import build_summary, ask_assistant, FALLBACK_RESPONSE


def test_categorizer_unavailable_returns_none():
    with patch("app.services.ai.categorizer.client_available", return_value=False):
        assert categorize_expense("Pizza with friends ₹450") is None


def test_categorizer_accepts_valid_ai_response():
    mock_json = '{"category": "food", "type": "want", "amount": 450, "confidence": "high"}'
    with patch("app.services.ai.categorizer.client_available", return_value=True):
        with patch("app.services.ai.categorizer.generate", return_value=mock_json):
            result = categorize_expense("Pizza with friends for ₹450")
            assert result["category"] == "food"
            assert result["type"] == "want"
            assert result["amount"] == 450


def test_categorizer_sanitizes_invalid_category():
    mock_json = '{"category": "space_travel", "type": "want", "amount": null, "confidence": "low"}'
    with patch("app.services.ai.categorizer.client_available", return_value=True):
        with patch("app.services.ai.categorizer.generate", return_value=mock_json):
            result = categorize_expense("Bought something unusual")
            assert result["category"] == "other"


def test_categorizer_sanitizes_invalid_type():
    mock_json = '{"category": "food", "type": "luxury", "amount": null, "confidence": "low"}'
    with patch("app.services.ai.categorizer.client_available", return_value=True):
        with patch("app.services.ai.categorizer.generate", return_value=mock_json):
            result = categorize_expense("dinner")
            assert result["type"] == "want"


def test_categorizer_handles_unparseable_response():
    with patch("app.services.ai.categorizer.client_available", return_value=True):
        with patch("app.services.ai.categorizer.generate", return_value="sorry I can't do that"):
            result = categorize_expense("dinner")
            assert result is None


def test_categorizer_handles_generate_returning_none():
    with patch("app.services.ai.categorizer.client_available", return_value=True):
        with patch("app.services.ai.categorizer.generate", return_value=None):
            result = categorize_expense("dinner")
            assert result is None


def test_build_summary_includes_balance():
    ctx = {
        "remaining_balance": Decimal("3200"),
        "monthly_income": Decimal("8000"),
        "monthly_expenses": Decimal("4800"),
        "savings_rate_pct": 40.0,
        "health_score": 78,
        "wants_pct": 35.0,
        "days_remaining": 12,
        "recommended_daily": Decimal("266"),
        "top_categories": [{"category": "food", "amount": Decimal("1800")}],
        "overspent_budgets": [],
    }
    summary = build_summary(ctx)
    assert "3,200" in summary
    assert "40.0%" in summary


def test_build_summary_never_includes_sensitive_fields():
    ctx = {
        "remaining_balance": Decimal("1000"),
        "monthly_income": Decimal("5000"),
        "monthly_expenses": Decimal("4000"),
        "savings_rate_pct": 20.0,
        "health_score": 60,
        "wants_pct": 30.0,
        "days_remaining": 5,
        "recommended_daily": Decimal("200"),
        "top_categories": [],
        "overspent_budgets": [],
        "password": "secret123",
        "access_token": "bearer xyz",
        "user_id": "uuid-abc",
    }
    summary = build_summary(ctx)
    assert "secret123" not in summary
    assert "bearer xyz" not in summary
    assert "uuid-abc" not in summary


def test_assistant_unavailable_returns_fallback():
    with patch("app.services.ai.assistant.client_available", return_value=False):
        result = ask_assistant("Where am I spending the most?", {})
        assert result == FALLBACK_RESPONSE
