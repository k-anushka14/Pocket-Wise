import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey
from app.database.types import GUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.session import Base


class SplitExpense(Base):
    __tablename__ = "split_expenses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)

    description = Column(String, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    participants = relationship(
        "SplitParticipant", back_populates="split_expense", cascade="all, delete-orphan"
    )


class SplitParticipant(Base):
    __tablename__ = "split_participants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    split_expense_id = Column(GUID(), ForeignKey("split_expenses.id", ondelete="CASCADE"), nullable=False)

    person_name = Column(String, nullable=False)
    amount_owed = Column(Numeric(10, 2), nullable=False)
    direction = Column(String, nullable=False)  # owed_to_me | i_owe
    status = Column(String, nullable=False, default="pending")  # pending | paid

    split_expense = relationship("SplitExpense", back_populates="participants")
