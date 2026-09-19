from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.cf_profile import CFProfile
from app.db.models.analytics import UserSkillGap
from app.schemas.skill_gap import SkillGapMatrixResponse, SkillGapItem


class SkillGapEngine:
    """Engine for classifying user topic competencies into WEAKNESS, BALANCED, or STRENGTH."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_skill_gap_matrix(self, profile: CFProfile) -> SkillGapMatrixResponse:
        stmt = (
            select(UserSkillGap)
            .where(UserSkillGap.cf_profile_id == profile.id)
            .order_by(UserSkillGap.gap_delta.desc())
        )
        res = await self.db.execute(stmt)
        gap_rows = res.scalars().all()

        items: List[SkillGapItem] = []
        weaknesses = 0
        balanced = 0
        strengths = 0

        for sg in gap_rows:
            if sg.classification == "WEAKNESS":
                weaknesses += 1
            elif sg.classification == "STRENGTH":
                strengths += 1
            else:
                balanced += 1

            items.append(
                SkillGapItem(
                    tag=sg.tag,
                    user_rating=sg.user_rating,
                    tag_effective_rating=sg.tag_effective_rating,
                    gap_delta=sg.gap_delta,
                    classification=sg.classification,
                )
            )

        return SkillGapMatrixResponse(
            handle=profile.handle,
            overall_rating=profile.rating or 1200,
            weaknesses_count=weaknesses,
            balanced_count=balanced,
            strengths_count=strengths,
            gaps=items,
        )
