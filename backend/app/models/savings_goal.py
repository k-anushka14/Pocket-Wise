import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime
from app.database.types import GUID
from sqlalchemy.sql import func

from app.database.session import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)

    name = Column(String, nullable=False)
    target_amount = Column(Numeric(10, 2), nullable=False)
    current_amount = Column(Numeric(10, 2), nullable=False, default=0)
    deadline = Column(Date, nullable=True)
    priority = Column(String, nullable=False, default="medium")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
