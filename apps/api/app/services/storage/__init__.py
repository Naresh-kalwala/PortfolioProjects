from functools import lru_cache

from app.core.config import settings
from app.services.storage.base import StorageBackend


@lru_cache
def get_storage_backend() -> StorageBackend:
    if settings.storage_backend == "cloudinary":
        from app.services.storage.cloudinary_backend import CloudinaryStorageBackend

        return CloudinaryStorageBackend()

    from app.services.storage.s3_backend import S3StorageBackend

    return S3StorageBackend()


__all__ = ["StorageBackend", "get_storage_backend"]
