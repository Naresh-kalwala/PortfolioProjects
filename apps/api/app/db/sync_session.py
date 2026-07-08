"""Celery workers use a plain synchronous SQLAlchemy session — Celery's
task model is thread/process based, not asyncio-native, so mixing in the
API's async engine per task would mean spinning up a new event loop per
task anyway. Async I/O (AI calls, HTTP connectors) inside a task is run via
`asyncio.run(...)` instead.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")

sync_engine = create_engine(_sync_database_url, pool_pre_ping=True, future=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)
