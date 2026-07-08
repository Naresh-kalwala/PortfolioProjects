"""Clerk-based authentication.

Verifies the Clerk-issued session JWT sent by the Next.js frontend using
Clerk's JWKS endpoint, so the API never has to see Clerk's secret key on
every request (only for the JWKS fetch, which is cached).
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings

_bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict[str, Any] = {"keys": None, "fetched_at": 0.0}
_JWKS_TTL_SECONDS = 3600


async def _get_jwks() -> dict[str, Any]:
    now = time.time()
    if _jwks_cache["keys"] and now - _jwks_cache["fetched_at"] < _JWKS_TTL_SECONDS:
        return _jwks_cache["keys"]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.clerk_jwks_url)
        resp.raise_for_status()
        jwks = resp.json()

    _jwks_cache["keys"] = jwks
    _jwks_cache["fetched_at"] = now
    return jwks


async def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """FastAPI dependency: verifies the Clerk JWT and returns its claims."""

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = await _get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
        if key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer,
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if not claims.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

    return claims


async def get_current_user_id(claims: dict[str, Any] = Depends(get_current_claims)) -> str:
    return claims["sub"]
