from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models.cf_profile import CFProfile
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation.engine import RecommendationEngine

router = APIRouter()


@router.get("/daily/{handle}", response_model=RecommendationResponse)
async def get_daily_recommendations(
    handle: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve personalized daily problem recommendations for handle."""
    stmt = select(CFProfile).where(CFProfile.handle == handle)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Codeforces profile '{handle}' not found or not synced yet.",
        )

    engine = RecommendationEngine(db)
    return await engine.get_daily_recommendations(profile, limit=limit)
