from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models.cf_profile import CFProfile
from app.db.models.sync_job import SyncJob
from app.schemas.cf_profile import CFProfileResponse, SyncStatusResponse
from app.tasks.sync_user import sync_user_profile_task

router = APIRouter()


@router.post("/profile/{handle}", response_model=SyncStatusResponse)
async def trigger_profile_sync(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Trigger background ingestion and analysis for a Codeforces handle."""
    clean_handle = handle.strip()
    if not clean_handle:
        raise HTTPException(status_code=400, detail="Handle cannot be empty.")

    # Find or create profile
    stmt = select(CFProfile).where(CFProfile.handle == clean_handle)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        profile = CFProfile(handle=clean_handle)
        db.add(profile)
        await db.flush()

    # Create SyncJob audit record
    job = SyncJob(
        cf_profile_id=profile.id,
        job_type="USER_FULL_SYNC",
        status="PENDING"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Trigger Celery async task
    sync_user_profile_task.delay(clean_handle, str(job.id))

    return SyncStatusResponse(
        handle=clean_handle,
        status="PENDING",
        sync_job_id=str(job.id),
    )


@router.get("/sync-status/{job_id}", response_model=SyncStatusResponse)
async def get_sync_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Poll sync status for an ongoing background sync job."""
    stmt = select(SyncJob, CFProfile).join(CFProfile, SyncJob.cf_profile_id == CFProfile.id).where(SyncJob.id == job_id)
    res = await db.execute(stmt)
    row = res.first()

    if not row:
        raise HTTPException(status_code=404, detail="Sync job not found")

    job, profile = row
    return SyncStatusResponse(
        handle=profile.handle,
        status=job.status,
        sync_job_id=str(job.id),
        error_message=job.error_message,
    )
