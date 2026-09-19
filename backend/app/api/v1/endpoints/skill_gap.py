from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models.cf_profile import CFProfile
from app.schemas.skill_gap import SkillGapMatrixResponse
from app.services.skill_gap.engine import SkillGapEngine

router = APIRouter()


@router.get("/matrix/{handle}", response_model=SkillGapMatrixResponse)
async def get_skill_gap_matrix(
    handle: str,
    db: AsyncSession = Depends(get_db)
):
    """Get topic skill gap analysis and classifications for handle."""
    stmt = select(CFProfile).where(CFProfile.handle == handle)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Codeforces profile '{handle}' not found or not synced yet.",
        )

    engine = SkillGapEngine(db)
    return await engine.get_skill_gap_matrix(profile)
