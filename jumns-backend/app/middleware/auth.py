"""Cognito JWT validation middleware.

Validates the Authorization: Bearer <token> header against the Cognito
User Pool JWKS endpoint.  On success, sets request.state.user_id to the
JWT 'sub' claim.  Skips auth for GET /health.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import Request
from jose import JWTError, jwk, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# ---------------------------------------------------------------------------
# Configuration — read from env vars (set by CDK), with dev defaults
# ---------------------------------------------------------------------------
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "us-east-1_Bn4GrzTdg")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "6v0sh32keeunk2e0j2sqlup6n")

JWKS_URL = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
    f"{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
)
ISSUER = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
)

# Module-level cache — survives across Lambda invocations in the same container
_jwks_cache: dict[str, Any] | None = None


def _get_jwks() -> dict[str, Any]:
    """Fetch JWKS from Cognito (cached on cold start)."""
    global _jwks_cache
    if _jwks_cache is None:
        resp = httpx.get(JWKS_URL, timeout=5.0)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def _find_key(token: str) -> dict[str, Any]:
    """Find the matching JWK for the token's kid header."""
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")
    keys = _get_jwks().get("keys", [])
    for key in keys:
        if key.get("kid") == kid:
            return key
    raise JWTError("No matching key found in JWKS")


def decode_token(token: str) -> dict[str, Any]:
    """Validate and decode a Cognito JWT, returning the claims dict."""
    signing_key = _find_key(token)
    public_key = jwk.construct(signing_key)
    claims = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=COGNITO_CLIENT_ID,
        issuer=ISSUER,
    )
    return claims


# Paths that skip authentication
_PUBLIC_PATHS = {"/health"}


class CognitoAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that validates Cognito JWTs on every request."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        # OPTIONS requests (CORS preflight) pass through
        if request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})

        token = auth_header[7:]  # strip "Bearer "
        try:
            claims = decode_token(token)
        except (JWTError, Exception):
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})

        user_id = claims.get("sub")
        if not user_id:
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})

        # Attach user_id to request state — all route handlers read from here
        request.state.user_id = user_id
        return await call_next(request)
