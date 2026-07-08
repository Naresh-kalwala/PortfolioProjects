from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_claims
from app.db.session import get_db
from app.models.user import UserProfile


async def get_current_profile(
    claims: dict[str, Any] = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Just-in-time provisions a `UserProfile` row the first time a Clerk
    user calls the API, keyed off the verified Clerk user id.
    """
    clerk_user_id = claims["sub"]
    result = await db.execute(select(UserProfile).where(UserProfile.clerk_user_id == clerk_user_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = UserProfile(
            clerk_user_id=clerk_user_id,
            email=claims.get("email") or f"{clerk_user_id}@placeholder.local",
            full_name=claims.get("name"),
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile
