from decimal import Decimal

from app.services.affordability_service import (
    calculate_after_purchase_balance, is_over_budget_after_purchase,
    estimate_goal_delay_days, evaluate_affordability,
)


def test_after_purchase_balance():
    assert calculate_after_purchase_balance(Decimal("5200"), Decimal("2500")) == Decimal("2700")


def test_over_budget_detection():
    assert is_over_budget_after_purchase(Decimal("1800"), Decimal("2000"), Decimal("500")) is True
    assert is_over_budget_after_purchase(Decimal("1000"), Decimal("2000"), Decimal("500")) is False


def test_goal_delay_zero_without_pace():
    assert estimate_goal_delay_days(Decimal("1000"), None) == 0
    assert estimate_goal_delay_days(Decimal("1000"), Decimal("0")) == 0


def test_goal_delay_rounds_up():
    # 1000 / 700 per week = 1.43 weeks -> 10 days (ceiling)
    assert estimate_goal_delay_days(Decimal("1000"), Decimal("700")) == 10


def test_evaluate_affordability_cannot_afford():
    result = evaluate_affordability(
        current_balance=Decimal("1000"), purchase_amount=Decimal("2000"),
        upcoming_recurring_total=Decimal("0"),
    )
    assert result["verdict"] == "no"
    assert result["after_purchase_balance"] < 0


def test_evaluate_affordability_comfortable_yes():
    result = evaluate_affordability(
        current_balance=Decimal("10000"), purchase_amount=Decimal("500"),
        upcoming_recurring_total=Decimal("0"),
    )
    assert result["verdict"] == "yes"


def test_evaluate_affordability_risky_recurring():
    result = evaluate_affordability(
        current_balance=Decimal("3000"), purchase_amount=Decimal("2500"),
        upcoming_recurring_total=Decimal("1000"),
    )
    assert result["verdict"] == "risky"
    assert result["after_purchase_balance"] == Decimal("500")


def test_evaluate_affordability_risky_budget_overspend():
    result = evaluate_affordability(
        current_balance=Decimal("10000"), purchase_amount=Decimal("500"),
        upcoming_recurring_total=Decimal("0"),
        budget_context={"category": "shopping", "spent": Decimal("900"), "amount": Decimal("1000")},
    )
    assert result["verdict"] == "risky"
    assert result["budget_overspend"] is True


def test_evaluate_affordability_risky_goal_delay():
    result = evaluate_affordability(
        current_balance=Decimal("10000"), purchase_amount=Decimal("1000"),
        upcoming_recurring_total=Decimal("0"),
        goal_context={"name": "Goa Trip", "amount_per_week": Decimal("700")},
    )
    assert result["verdict"] == "risky"
    assert result["goal_delay_days"] > 0
    assert any("Goa Trip" in e for e in result["explanation"])


def test_evaluate_affordability_no_negative_gives_no_explanation_beyond_shortfall():
    result = evaluate_affordability(
        current_balance=Decimal("100"), purchase_amount=Decimal("500"),
        upcoming_recurring_total=Decimal("0"),
    )
    assert result["verdict"] == "no"
    assert len(result["explanation"]) == 1
