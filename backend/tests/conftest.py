"""
Shared pytest fixtures for API-level integration tests.

Uses an in-memory SQLite DB (fast, zero setup) instead of a real Postgres
connection, made possible by the cross-database GUID column type. Auth is
faked via a dependency override -- these tests are NOT testing Supabase
JWT verification itself (that's covered separately in
test_auth_dependency.py with mocks); they're testing that routes do the
right thing once a user is authenticated.
"""
import os
import uuid
import pytest
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Stub env vars before any app module is imported, so pydantic-settings
# doesn't require a real .env in this sandbox.
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "placeholder")
os.environ.setdefault("SUPABASE_JWT_SECRET", "placeholder")
os.environ.setdefault("DATABASE_URL", "postgresql://placeholder")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ["TESTING"] = "1"

from app.database.session import Base, get_db
from app.auth.dependencies import get_current_user, CurrentUser
from app.main import app

TEST_USER_ID = str(uuid.uuid4())
OTHER_USER_ID = str(uuid.uuid4())


@pytest.fixture()
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(test_db):
    """
    A single TestClient whose "current user" is read per-request from an
    X-Test-User-Id header (defaulting to TEST_USER_ID). This -- not a
    second TestClient with its own override -- is how cross-user tests
    simulate a different user: app.dependency_overrides lives on the
    shared FastAPI app singleton, so two TestClient fixtures both trying
    to override get_current_user would stomp on each other's setting
    rather than being isolated per-client.
    """
    def override_get_db():
        yield test_db

    def override_get_current_user(request: Request):
        user_id = request.headers.get("X-Test-User-Id", TEST_USER_ID)
        return CurrentUser(id=user_id, email=f"{user_id}@example.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def other_user_headers():
    """Pass these headers on a request to simulate a second, different user."""
    return {"X-Test-User-Id": OTHER_USER_ID}
