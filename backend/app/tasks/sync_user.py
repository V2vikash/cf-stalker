import asyncio
from datetime import datetime
from sqlalchemy import select
import structlog

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.db.models.cf_profile import CFProfile
from app.db.models.sync_job import SyncJob
from app.services.codeforces.ingestion import IngestionService

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.sync_user.sync_user_profile_task")
def sync_user_profile_task(handle: str, sync_job_id: str = None):
    """Celery background task to synchronize user profile, rating history, submissions, and topic stats."""
    return asyncio.run(_async_sync_user(handle, sync_job_id))


async def _async_sync_user(handle: str, sync_job_id: str = None):
    logger.info("Starting background user sync task", handle=handle, sync_job_id=sync_job_id)
    
    async with AsyncSessionLocal() as db:
        job = None
        if sync_job_id:
            job_stmt = select(SyncJob).where(SyncJob.id == sync_job_id)
            job_res = await db.execute(job_stmt)
            job = job_res.scalar_one_or_none()

        if job:
            job.status = "RUNNING"
            await db.commit()

        try:
            ingestion = IngestionService(db)
            profile = await ingestion.sync_cf_profile(handle)
            await ingestion.sync_user_contests(profile)
            await ingestion.sync_user_submissions(profile)
            await ingestion.compute_topic_aggregations(profile)

            if job:
                job.status = "COMPLETED"
                job.completed_at = datetime.utcnow()
                await db.commit()

            logger.info("Successfully completed user sync task", handle=handle)
            return {"status": "success", "handle": handle}

        except Exception as exc:
            logger.error("Failed background user sync task", handle=handle, error=str(exc))
            if job:
                job.status = "FAILED"
                job.error_message = str(exc)
                await db.commit()
            raise exc
