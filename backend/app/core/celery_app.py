from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cf_stalker_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for big user sync tasks
)

# Optional periodic schedules
celery_app.conf.beat_schedule = {
    "sync-problem-archive-daily": {
        "task": "app.tasks.sync_problems.sync_problem_archive_task",
        "schedule": 86400.0,  # Every 24 hours
    },
}
