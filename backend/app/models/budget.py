import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, UniqueConstraint
from app.database.types import GUID
from sqlalchemy.sql import func

from app.database.session import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        # One budget per category per month per user -- creating a second
        # "Food" budget for the same month should edit the existing one,
        # not create a conflicting duplicate.
        UniqueConstraint("user_id", "category", "month", name="uq_budget_user_category_month"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)

    category = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    month = Column(Date, nullable=False, index=True)  # always stored as the 1st of the month

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
