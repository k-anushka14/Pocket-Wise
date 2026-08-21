"""
App-specific user data. Supabase's own `auth.users` table (managed by
Supabase Auth) already stores email/password/etc -- we never touch that
table directly. This `profiles` table holds the extra fields PocketWise
needs, keyed by the same UUID Supabase Auth assigns to the user.
"""
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True)  # matches auth.users.id
    full_name = Column(String, nullable=True)
    college = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
