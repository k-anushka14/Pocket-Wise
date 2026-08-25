"""
Rate limiting -- per-IP, in-memory (fine for a single-instance deployment;
swap the storage backend for Redis if this ever runs multi-instance).

Default limit applies globally. AI endpoints get a stricter limit since
they call a paid external API (Gemini) and are the most expensive/abusable
routes in the app.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
