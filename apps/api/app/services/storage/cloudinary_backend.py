import asyncio

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.core.config import settings
from app.services.storage.base import StorageBackend


class CloudinaryStorageBackend(StorageBackend):
    def __init__(self) -> None:
        cloudinary.config(cloudinary_url=settings.cloudinary_url)

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            data,
            public_id=key,
            resource_type="raw",
            overwrite=True,
        )
        return result["public_id"]

    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        url, _ = cloudinary.utils.cloudinary_url(
            key, resource_type="raw", sign_url=True, type="authenticated"
        )
        return url
