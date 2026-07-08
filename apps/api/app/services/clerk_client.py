"""Clerk Backend API client — used only for the one thing the session JWT
itself doesn't reliably carry: Clerk's default session token claims are
minimal (`sub`, `sid`, `iss`, ...) and do NOT include the user's email
unless a custom JWT template is configured. Rather than require every
deployment to hand-configure a template, fall back to asking Clerk's
Backend API for the user's primary email on first sign-in.
"""

from __future__ import annotations

import httpx

from app.core.config import settings

_BASE_URL = "https://api.clerk.com/v1"


async def fetch_user_email(clerk_user_id: str) -> str | None:
    if not settings.clerk_secret_key:
        return None

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{_BASE_URL}/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        primary_id = data.get("primary_email_address_id")
        for entry in data.get("email_addresses", []):
            if entry.get("id") == primary_id:
                return entry.get("email_address")
        return None
