from decimal import Decimal

from app.services.insights_service import (
    budget_alerts, weekly_change_alert, needs_wants_insight,
    student_category_insights, generate_all_insights,
)


def test_budget_alert_warning():
    budgets = [{"category": "food", "percentage_used": 75, "status": "warning", "spent": Decimal("1500"), "amount": Decimal("2000")}]
    alerts = budget_alerts(budgets)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "warning"
    assert "75%" in alerts[0]["message"]


def test_budget_alert_overspent_shows_amount_over():
    budgets = [{"category": "shopping", "percentage_used": 145, "status": "overspent", "spent": Decimal("1450"), "amount": Decimal("1000")}]
    alerts = budget_alerts(budgets)
    assert "450" in alerts[0]["message"]
    assert alerts[0]["severity"] == "critical"


def test_budget_alert_normal_produces_nothing():
    budgets = [{"category": "food", "percentage_used": 40, "status": "normal", "spent": Decimal("400"), "amount": Decimal("1000")}]
    assert budget_alerts(budgets) == []


def test_weekly_change_alert_triggers_above_threshold():
    weekly = [{"label": "Week 1", "amount": Decimal("500")}, {"label": "Week 2", "amount": Decimal("700")}]
    alert = weekly_change_alert(weekly)
    assert alert is not None
    assert "40%" in alert["message"]


def test_weekly_change_alert_silent_below_threshold():
    weekly = [{"label": "Week 1", "amount": Decimal("500")}, {"label": "Week 2", "amount": Decimal("520")}]
    assert weekly_change_alert(weekly) is None


def test_weekly_change_alert_needs_two_weeks():
    assert weekly_change_alert([{"label": "Week 1", "amount": Decimal("500")}]) is None


def test_needs_wants_insight_triggers_above_threshold():
    insight = needs_wants_insight(Decimal("600"), Decimal("400"))
    assert insight is not None
    assert "40%" in insight["message"]


def test_needs_wants_insight_silent_below_threshold():
    assert needs_wants_insight(Decimal("900"), Decimal("100")) is None


def test_needs_wants_insight_handles_zero_total():
    assert needs_wants_insight(Decimal("0"), Decimal("0")) is None


def test_student_category_insight_triggers():
    spending = [{"category": "hostel", "amount": Decimal("3200")}, {"category": "food", "amount": Decimal("1000")}]
    insights = student_category_insights(spending)
    assert len(insights) == 1
    assert "Hostel" in insights[0]["message"]


def test_student_category_insight_ignores_non_watch_categories():
    spending = [{"category": "shopping", "amount": Decimal("5000")}]
    assert student_category_insights(spending) == []


def test_generate_all_insights_sorts_critical_first():
    budgets = [{"category": "food", "percentage_used": 75, "status": "warning", "spent": Decimal("1500"), "amount": Decimal("2000")}]
    spending = [{"category": "hostel", "amount": Decimal("3200")}, {"category": "food", "amount": Decimal("1000")}]
    result = generate_all_insights(budgets, [], Decimal("600"), Decimal("400"), spending)
    severities = [i["severity"] for i in result]
    assert severities == sorted(severities, key=lambda s: {"critical": 0, "warning": 1, "info": 2}[s])
