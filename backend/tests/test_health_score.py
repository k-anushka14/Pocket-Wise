from decimal import Decimal

from app.services.health_score_service import (
    savings_rate_percent, savings_rate_score, budget_adherence_score,
    wants_ratio_score, spending_consistency_score, goal_progress_score,
    calculate_financial_health_score, generate_health_explanations,
)


def test_savings_rate_percent_basic():
    assert savings_rate_percent(Decimal("10000"), Decimal("6240")) == 37.6


def test_savings_rate_percent_zero_income():
    assert savings_rate_percent(Decimal("0"), Decimal("500")) == 0.0


def test_savings_rate_score_full_at_target():
    assert savings_rate_score(30, weight=30, target_pct=30) == 30.0


def test_savings_rate_score_negative_is_zero():
    assert savings_rate_score(-10, weight=30) == 0.0


def test_budget_adherence_no_budgets_full_credit():
    assert budget_adherence_score([], weight=25) == 25


def test_budget_adherence_all_within_limit():
    budgets = [{"percentage_used": 50}, {"percentage_used": 80}]
    assert budget_adherence_score(budgets, weight=25) == 25.0


def test_budget_adherence_penalizes_overspend():
    budgets = [{"percentage_used": 200}]  # 100% over -> 0 credit
    assert budget_adherence_score(budgets, weight=25) == 0.0


def test_wants_ratio_score_good_zone():
    assert wants_ratio_score(20, weight=15, good=30, bad=70) == 15


def test_wants_ratio_score_bad_zone():
    assert wants_ratio_score(80, weight=15, good=30, bad=70) == 0.0


def test_spending_consistency_insufficient_data_full_credit():
    assert spending_consistency_score([Decimal("500")], weight=15) == 15


def test_spending_consistency_perfectly_even_full_credit():
    assert spending_consistency_score([Decimal("500")] * 4, weight=15) == 15.0


def test_goal_progress_no_goals_full_credit():
    assert goal_progress_score([], weight=15) == 15


def test_goal_progress_scales_with_average():
    assert goal_progress_score([100.0, 100.0], weight=15) == 15.0
    assert goal_progress_score([0.0, 0.0], weight=15) == 0.0


def test_overall_score_strong_finances():
    result = calculate_financial_health_score(
        income=Decimal("10000"),
        expenses=Decimal("5000"),  # 50% savings rate
        budgets=[{"percentage_used": 40}],
        wants_pct=20,
        weekly_amounts=[Decimal("1200")] * 4,
        goal_progress_list=[80.0],
    )
    assert result["score"] >= 85


def test_overall_score_weak_finances():
    result = calculate_financial_health_score(
        income=Decimal("10000"),
        expenses=Decimal("9800"),  # barely saving
        budgets=[{"percentage_used": 180}],
        wants_pct=85,
        weekly_amounts=[Decimal("500"), Decimal("2000"), Decimal("300"), Decimal("3000")],
        goal_progress_list=[5.0],
    )
    assert result["score"] <= 40


def test_score_never_exceeds_100_or_goes_negative():
    result = calculate_financial_health_score(
        income=Decimal("10000"), expenses=Decimal("0"), budgets=[],
        wants_pct=0, weekly_amounts=[], goal_progress_list=[100.0],
    )
    assert 0 <= result["score"] <= 100


def test_explanations_flag_overspent_categories():
    score_result = calculate_financial_health_score(
        income=Decimal("10000"), expenses=Decimal("9500"),
        budgets=[{"percentage_used": 150}], wants_pct=60,
        weekly_amounts=[Decimal("1000")], goal_progress_list=[],
    )
    explanations = generate_health_explanations(score_result, wants_pct=60, overspent_categories=["shopping"])
    assert any("Shopping" in w for w in explanations["weaknesses"])


def test_explanations_always_return_something():
    score_result = calculate_financial_health_score(
        income=Decimal("10000"), expenses=Decimal("3000"),
        budgets=[], wants_pct=15, weekly_amounts=[Decimal("750")] * 4, goal_progress_list=[90.0],
    )
    explanations = generate_health_explanations(score_result, wants_pct=15, overspent_categories=[])
    assert len(explanations["strengths"]) > 0
    assert len(explanations["weaknesses"]) > 0
