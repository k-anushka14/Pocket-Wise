import uuid
from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, Text
from app.database.types import GUID
from sqlalchemy.sql import func

from app.database.session import Base


class Income(Base):
    __tablename__ = "income"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    source = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    is_recurring = Column(Boolean, nullable=False, default=False)
    frequency = Column(String, nullable=True)  # weekly | monthly | yearly, only if is_recurring
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
