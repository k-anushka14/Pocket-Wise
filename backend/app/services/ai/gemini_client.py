"""
Thin wrapper around the Gemini API.
 
This is the ONLY file in the codebase that touches the Gemini SDK.
Every other AI feature (categorizer, assistant, affordability) calls
through here -- so if you ever want to swap Gemini for another provider,
this is the only file you change.
 
If GEMINI_API_KEY is not set the client is None; callers check
`client_available()` before calling `generate()` and return a graceful
fallback instead of crashing.
"""
import json
import re
from typing import Optional
 
try:
    import google.generativeai as genai
    _HAS_SDK = True
except ImportError:
    _HAS_SDK = False
 
from app.config import ai_settings
 
_client: Optional[object] = None
 
 
def _get_client():
    global _client
    if _client is not None:
        return _client
    if not _HAS_SDK or not ai_settings.gemini_api_key:
        return None
    genai.configure(api_key=ai_settings.gemini_api_key)
    _client = genai.GenerativeModel(ai_settings.gemini_model)
    return _client
 
 
def client_available() -> bool:
    return _get_client() is not None
 
 
def generate(prompt: str, temperature: float = 0.2) -> Optional[str]:
    """
    Send a prompt to Gemini and return the text response, or None on
    any error (network, quota, invalid key, etc.).
 
    All callers should handle None and fall back gracefully -- the
    expense tracker must stay functional even when AI is down.
    """
    client = _get_client()
    if client is None:
        return None
    try:
        response = client.generate_content(
            prompt,
            generation_config={"temperature": temperature},
        )
        return response.text
    except Exception:
        return None
 
 
def parse_json_response(text: str) -> Optional[dict]:
    """
    Gemini sometimes wraps JSON in markdown fences -- strip them and parse.
    Returns None if parsing fails rather than raising.
    """
    if text is None:
        return None
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        return None