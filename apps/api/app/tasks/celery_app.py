from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "job_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.job_scan_tasks",
        "app.tasks.resume_tasks",
        "app.tasks.application_tasks",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=15 * 60,
    worker_max_tasks_per_child=200,
)

celery_app.conf.beat_schedule = {
    "scan-jobs-every-interval": {
        "task": "app.tasks.job_scan_tasks.scan_all_sources",
        "schedule": settings.job_scan_interval_minutes * 60,
    },
}
