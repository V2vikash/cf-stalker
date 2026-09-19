from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models.cf_profile import CFProfile
from app.schemas.ai_coach import AICoachReviewResponse
from app.services.ai_coach.engine import AICoachEngine

router = APIRouter()


@router.post("/review/{handle}", response_model=AICoachReviewResponse)
async def generate_ai_coach_review(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate an AI-powered performance coaching review for handle."""
    stmt = select(CFProfile).where(CFProfile.handle == handle)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Codeforces profile '{handle}' not found or not synced yet.",
        )

    engine = AICoachEngine(db)
    return await engine.generate_review(profile)
