import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False, index=True)
    payment_method = Column(String, nullable=False)
    type = Column(String, nullable=False)  # need | want
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
