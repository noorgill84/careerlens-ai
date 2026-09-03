"""Shared FastAPI dependencies: auth, DB client."""
from fastapi import Header, HTTPException, status
from app.config import settings


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Require a valid session. Use on routes that touch persisted, user-owned data."""
    payload = _decode_token(authorization)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header.")
    return {"id": payload.get("sub"), "email": payload.get("email")}


async def get_current_user_optional(authorization: str | None = Header(default=None)) -> dict | None:
    """
    Like get_current_user, but returns None instead of raising when there's
    no/invalid token — for routes that work for anonymous visitors (e.g. the
    demo resume upload flow, spec §34) but personalize/persist when signed in.
    """
    return _decode_token(authorization)


def _decode_token(authorization: str | None) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    try:
        import jwt  # PyJWT
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        return payload
    except ImportError:
        raise HTTPException(status_code=500, detail="Auth library not installed on server.")
    except Exception:
        return None
