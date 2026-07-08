from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Uploads bytes under `key` and returns the storage key (not a public URL)."""

    @abstractmethod
    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Returns a short-lived, authenticated URL for downloading `key`."""
