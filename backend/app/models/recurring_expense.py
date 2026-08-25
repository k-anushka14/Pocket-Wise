import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime
from app.database.types import GUID
from sqlalchemy.sql import func

from app.database.session import Base


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)

    name = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)  # weekly | monthly | yearly
    next_due_date = Column(Date, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
