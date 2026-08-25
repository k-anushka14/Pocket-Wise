"""
Tests for get_current_user (JWT verification). Mocks jwt.decode/JWKS
lookups directly -- these are NOT hitting a real Supabase project, they're
testing that our code handles each outcome (valid token, expired, tampered,
missing claim, network failure) correctly.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "placeholder")
os.environ.setdefault("SUPABASE_JWT_SECRET", "placeholder")
os.environ.setdefault("DATABASE_URL", "postgresql://placeholder")
os.environ.setdefault("GEMINI_API_KEY", "")

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.dependencies import get_current_user


def _creds(token="fake.jwt.token"):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_valid_hs256_token_returns_current_user():
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "HS256"}):
        with patch("app.auth.dependencies.jwt.decode", return_value={"sub": "user-123", "email": "a@b.com"}):
            user = get_current_user(_creds())
            assert user.id == "user-123"
            assert user.email == "a@b.com"


def test_valid_es256_token_uses_jwks(): 
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "ES256"}):
        with patch("app.auth.dependencies._jwks_client.get_signing_key_from_jwt", return_value=MagicMock(key="fake-key")):
            with patch("app.auth.dependencies.jwt.decode", return_value={"sub": "user-456", "email": None}):
                user = get_current_user(_creds())
                assert user.id == "user-456"


def test_expired_token_raises_401():
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "HS256"}):
        with patch("app.auth.dependencies.jwt.decode", side_effect=Exception("Signature has expired")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(_creds())
            assert exc_info.value.status_code == 401


def test_tampered_token_raises_401():
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "HS256"}):
        with patch("app.auth.dependencies.jwt.decode", side_effect=Exception("Signature verification failed")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(_creds())
            assert exc_info.value.status_code == 401


def test_token_missing_sub_claim_raises_401():
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "HS256"}):
        with patch("app.auth.dependencies.jwt.decode", return_value={"email": "a@b.com"}):  # no "sub"
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(_creds())
            assert exc_info.value.status_code == 401


def test_jwks_network_failure_raises_401_not_500():
    """A JWKS fetch failure (network down) must surface as a normal auth
    error, not an unhandled 500 -- covers the earlier real bug we hit
    (malformed SUPABASE_URL causing a DNS lookup failure)."""
    with patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"alg": "ES256"}):
        with patch("app.auth.dependencies._jwks_client.get_signing_key_from_jwt", side_effect=Exception("DNS failure")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(_creds())
            assert exc_info.value.status_code == 401
