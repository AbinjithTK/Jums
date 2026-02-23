"""Routes for /api/subscription/status — RevenueCat integration."""

import os

import httpx
from fastapi import APIRouter, Request

from app.models.responses import SubscriptionStatusResponse

router = APIRouter(prefix="/subscription", tags=["subscription"])

REVENUECAT_API_KEY = os.getenv("REVENUECAT_API_KEY", "")
REVENUECAT_BASE = "https://api.revenuecat.com/v1"


@router.get("/status")
async def get_subscription_status(request: Request) -> SubscriptionStatusResponse:
    """Check subscription status via RevenueCat server API."""
    user_id = request.state.user_id

    if not REVENUECAT_API_KEY:
        return SubscriptionStatusResponse()  # defaults: free, not pro

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{REVENUECAT_BASE}/subscribers/{user_id}",
                headers={"Authorization": f"Bearer {REVENUECAT_API_KEY}"},
                timeout=5.0,
            )
        if resp.status_code == 200:
            data = resp.json().get("subscriber", {})
            entitlements = data.get("entitlements", {})
            pro = entitlements.get("pro", {})
            if pro and pro.get("expires_date"):
                return SubscriptionStatusResponse(
                    plan="pro",
                    is_pro=True,
                    expires_at=pro["expires_date"],
                )
    except Exception:
        pass  # fail open — treat as free tier

    return SubscriptionStatusResponse()
