from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models.cf_profile import CFProfile
from app.schemas.analytics import (
    ProfileOverviewResponse,
    ContestAnalyticsResponse,
    TopicAnalyticsResponse,
)
from app.services.analytics.engine import AnalyticsEngine

router = APIRouter()


async def _get_profile_or_404(handle: str, db: AsyncSession) -> CFProfile:
    stmt = select(CFProfile).where(CFProfile.handle == handle)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Codeforces profile '{handle}' not found or not synced yet.",
        )
    return profile


@router.get("/overview/{handle}", response_model=ProfileOverviewResponse)
async def get_profile_overview(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve profile overview metrics, rating stats, and volatility."""
    profile = await _get_profile_or_404(handle, db)
    engine = AnalyticsEngine(db)
    return await engine.get_profile_overview(profile)


@router.get("/contests/{handle}", response_model=ContestAnalyticsResponse)
async def get_contest_analytics(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve contest rating trajectory and performance metrics."""
    profile = await _get_profile_or_404(handle, db)
    engine = AnalyticsEngine(db)
    return await engine.get_contest_analytics(profile)


@router.get("/topics/{handle}", response_model=TopicAnalyticsResponse)
async def get_topic_analytics(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve tag-wise performance metrics and difficulty distribution."""
    profile = await _get_profile_or_404(handle, db)
    engine = AnalyticsEngine(db)
    return await engine.get_topic_analytics(profile)
