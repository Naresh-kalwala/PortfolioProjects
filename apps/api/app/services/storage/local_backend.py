"""Filesystem storage for local development, so `docker compose up` works
end-to-end with zero cloud credentials. Not for production use — signed
URLs here are just static file paths with no expiry or access control.
"""

import time
from pathlib import Path

from app.services.storage.base import StorageBackend

_MEDIA_ROOT = Path("/app/media") if Path("/app").exists() else Path("./media")


class LocalStorageBackend(StorageBackend):
    def __init__(self) -> None:
        _MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        path = _MEDIA_ROOT / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        # No real signing — the /media static mount serves these directly.
        # A cache-busting query param keeps this honest about not being a
        # real expiring URL.
        return f"/media/{key}?t={int(time.time())}"
