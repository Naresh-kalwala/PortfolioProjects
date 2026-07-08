import hashlib
import re


def compute_dedupe_hash(title: str, company: str, location: str | None) -> str:
    """Normalizes title/company/location so the same posting cross-listed on
    multiple boards (e.g. a Greenhouse job also mirrored on the company
    site) collapses to one record instead of being stored twice.
    """
    normalize = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
    key = f"{normalize(title)}|{normalize(company)}|{normalize(location)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
