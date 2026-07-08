import tempfile

from app.services.storage import get_storage_backend


async def download_to_temp_file(key: str, suffix: str) -> str:
    """Downloads via a signed URL so a temporary local file exists for
    Playwright's `set_input_files`, which needs a filesystem path.
    """
    storage = get_storage_backend()
    signed_url = await storage.get_signed_url(key)

    import httpx

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(signed_url)
        resp.raise_for_status()

    fd, path = tempfile.mkstemp(suffix=suffix)
    with open(fd, "wb") as f:
        f.write(resp.content)
    return path
