from datetime import date

from app.services.no_spend_service import calculate_no_spend_days


def test_no_spend_all_days_spent():
    spend_dates = {date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3)}
    result = calculate_no_spend_days(spend_dates, date(2026, 8, 1), date(2026, 8, 3))
    assert result["count"] == 0
    assert result["longest_streak"] == 0


def test_no_spend_all_days_free():
    result = calculate_no_spend_days(set(), date(2026, 8, 1), date(2026, 8, 5))
    assert result["count"] == 5
    assert result["longest_streak"] == 5


def test_no_spend_mixed_streak():
    # spent on the 2nd only -> no-spend streaks are [1st] and [3rd,4th,5th]
    spend_dates = {date(2026, 8, 2)}
    result = calculate_no_spend_days(spend_dates, date(2026, 8, 1), date(2026, 8, 5))
    assert result["count"] == 4
    assert result["longest_streak"] == 3


def test_no_spend_invalid_range_returns_zero():
    result = calculate_no_spend_days(set(), date(2026, 8, 10), date(2026, 8, 1))
    assert result == {"count": 0, "longest_streak": 0}
