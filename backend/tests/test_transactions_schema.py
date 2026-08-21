"""
Pure schema-validation tests -- no DB or running server needed, so these
run instantly and catch data-shape bugs before they ever hit Postgres.
"""
import pytest
from pydantic import ValidationError
from datetime import date

from app.schemas.transaction import TransactionCreate
from app.schemas.income import IncomeCreate


def test_transaction_rejects_negative_amount():
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount=-50,
            category="food",
            date=date.today(),
            payment_method="upi",
            type="want",
        )


def test_transaction_rejects_unknown_category():
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount=100,
            category="not_a_real_category",
            date=date.today(),
            payment_method="upi",
            type="want",
        )


def test_transaction_accepts_valid_payload():
    txn = TransactionCreate(
        amount=450,
        category="food",
        description="Pizza with friends",
        date=date.today(),
        payment_method="upi",
        type="want",
    )
    assert txn.amount == 450
    assert txn.category == "food"


def test_income_frequency_requires_recurring_flag():
    with pytest.raises(ValidationError):
        IncomeCreate(
            amount=8000,
            source="pocket_money",
            date=date.today(),
            is_recurring=False,
            frequency="monthly",
        )


def test_income_accepts_valid_recurring_payload():
    income = IncomeCreate(
        amount=8000,
        source="pocket_money",
        date=date.today(),
        is_recurring=True,
        frequency="monthly",
    )
    assert income.is_recurring is True
