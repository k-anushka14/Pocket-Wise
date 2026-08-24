from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta
from decimal import Decimal
import uuid

from app.database.session import get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.models.achievement import Achievement, UserAchievement
from app.models.transaction import Transaction
from app.models.income import Income
from app.models.savings_goal import SavingsGoal
from app.schemas.achievement import AchievementOut
from app.services.achievements_service import evaluate_achievements, ACHIEVEMENT_CATALOG
from app.services.achievements_service import calculate_budget_safe_streak
from app.services.goal_service import calculate_goal_progress
from app.services.budget_queries import normalize_to_month_start, month_end
from app.services.period_queries import get_monthly_income, get_monthly_expenses, get_daily_category_spend, get_transaction_dates
from app.services.no_spend_service import calculate_no_spend_days
from sqlalchemy import func

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementOut])
def list_achievements(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluates current progress against every badge's condition and
    records any newly-earned ones. Already-earned badges are never
    revoked even if the underlying condition stops being true later
    (e.g. balance drops back below ₹500) -- an achievement is a moment,
    not a live status.
    """
    user_id = current_user.id
    today = date.today()
    month_start = normalize_to_month_start(today)

    # --- Gather the numbers each check needs
    total_income = db.execute(
        select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user_id)
    ).scalar_one()
    total_expenses = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id)
    ).scalar_one()
    total_savings = total_income - total_expenses

    monthly_income = get_monthly_income(db, user_id, month_start)
    monthly_expenses = get_monthly_expenses(db, user_id, month_start)
    savings_rate_pct = float((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0.0

    spend_dates = get_transaction_dates(db, user_id, month_start, today)
    no_spend_result = calculate_no_spend_days(spend_dates, month_start, today)

    goal_rows = db.execute(select(SavingsGoal).where(SavingsGoal.user_id == user_id)).scalars().all()
    goal_completion_flags = [g.current_amount >= g.target_amount for g in goal_rows]

    from app.models.budget import Budget
    budget_rows = db.execute(
        select(Budget).where(Budget.user_id == user_id, Budget.month == month_start)
    ).scalars().all()
    budget_dicts = [{"category": b.category, "amount": b.amount} for b in budget_rows]
    daily_spend = get_daily_category_spend(db, user_id, month_start, today)
    day_range = [month_start + timedelta(days=i) for i in range((today - month_start).days + 1)]
    budget_safe_streak = calculate_budget_safe_streak(budget_dicts, daily_spend, day_range)

    context = {
        "total_savings": total_savings,
        "savings_rate_pct": savings_rate_pct,
        "no_spend_count": no_spend_result["count"],
        "goal_completion_flags": goal_completion_flags,
        "budget_safe_streak": budget_safe_streak,
    }
    qualifies = evaluate_achievements(context)

    # --- Load catalog + what's already earned
    catalog_rows = db.execute(select(Achievement)).scalars().all()
    catalog_by_code = {a.code: a for a in catalog_rows}

    earned_rows = db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    ).scalars().all()
    earned_by_achievement_id = {e.achievement_id: e for e in earned_rows}

    # --- Award any newly-qualifying badges
    for code, does_qualify in qualifies.items():
        achievement = catalog_by_code.get(code)
        if not achievement:
            continue
        if does_qualify and achievement.id not in earned_by_achievement_id:
            new_earn = UserAchievement(id=uuid.uuid4(), user_id=user_id, achievement_id=achievement.id)
            db.add(new_earn)
            db.flush()
            earned_by_achievement_id[achievement.id] = new_earn
    db.commit()

    # --- Build response from the catalog, in a stable order
    results = []
    for badge in ACHIEVEMENT_CATALOG:
        achievement = catalog_by_code.get(badge["code"])
        earned_row = earned_by_achievement_id.get(achievement.id) if achievement else None
        results.append(AchievementOut(
            code=badge["code"],
            name=badge["name"],
            description=badge["description"],
            icon=badge["icon"],
            earned=earned_row is not None,
            earned_at=earned_row.earned_at if earned_row else None,
        ))
    return results
