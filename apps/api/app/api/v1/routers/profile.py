from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_profile
from app.db.session import get_db
from app.models.user import UserProfile
from app.schemas.user import UserProfileRead, UserProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserProfileRead)
async def get_profile(profile: UserProfile = Depends(get_current_profile)):
    return profile


@router.put("", response_model=UserProfileRead)
async def update_profile(
    payload: UserProfileUpdate,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/push-subscription")
async def add_push_subscription(
    subscription: dict,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    subscriptions = list(profile.push_subscriptions or [])
    if subscription not in subscriptions:
        subscriptions.append(subscription)
    profile.push_subscriptions = subscriptions
    await db.commit()
    return {"status": "ok"}
