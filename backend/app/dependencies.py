"""Shared FastAPI dependencies: auth, DB client."""
import logging
from fastapi import Header, HTTPException, status
from app.config import settings

logger = logging.getLogger("careerlens.auth")


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Require a valid session. Use on routes that touch persisted, user-owned data."""
    user = _resolve_user(authorization)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header.")
    return user


async def get_current_user_optional(authorization: str | None = Header(default=None)) -> dict | None:
    """
    Like get_current_user, but returns None instead of raising when there's
    no/invalid token — for routes that work for anonymous visitors (e.g. the
    demo resume upload flow, spec §34) but personalize/persist when signed in.
    """
    return _resolve_user(authorization)


def _resolve_user(authorization: str | None) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    return _verify_token_via_supabase(token)


def _verify_token_via_supabase(token: str) -> dict | None:
    """
    Verifies a Supabase access token by asking Supabase's own Auth API to
    resolve it to a user, rather than manually decoding the JWT locally
    against a shared secret.

    Why: Supabase has multiple JWT signing configurations across projects
    (legacy shared-secret HS256 vs. newer asymmetric per-project signing
    keys, plus the newer publishable/secret API key naming). Manually
    decoding with PyJWT requires guessing the right secret/algorithm for
    *this* project, which is fragile and fails silently. Asking Supabase
    to verify the token instead works regardless of which signing setup
    the project uses, since Supabase is the source of truth for its own
    tokens.
    """
    try:
        from supabase import create_client
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        response = client.auth.get_user(token)
        user = response.user if response else None
        if user is None:
            return None
        return {"id": user.id, "email": user.email}
    except Exception as e:
        logger.warning("Token verification failed: %s", e)
        return None
