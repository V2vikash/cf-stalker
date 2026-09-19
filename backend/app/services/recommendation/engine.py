from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.cf_profile import CFProfile
from app.db.models.problem import Problem, ProblemTag
from app.db.models.submission import Submission
from app.db.models.analytics import UserSkillGap
from app.schemas.recommendation import RecommendationResponse, RecommendedProblemItem


class RecommendationEngine:
    """Engine for generating personalized, multi-bucket problem practice recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_recommendations(
        self, profile: CFProfile, limit: int = 10
    ) -> RecommendationResponse:
        user_rating = profile.rating or 1200

        # Solved problem IDs to exclude
        s_stmt = select(Submission.problem_id).where(
            Submission.cf_profile_id == profile.id, Submission.verdict == "OK"
        )
        s_res = await self.db.execute(s_stmt)
        solved_ids = set(s_res.scalars().all())

        # Weak tags for the user
        w_stmt = select(UserSkillGap.tag).where(
            UserSkillGap.cf_profile_id == profile.id,
            UserSkillGap.classification == "WEAKNESS",
        )
        w_res = await self.db.execute(w_stmt)
        weak_tags = set(w_res.scalars().all())

        # Target rating ranges
        sweet_min = user_rating + 50
        sweet_max = user_rating + 250

        # Query candidate problems
        p_stmt = (
            select(Problem)
            .where(
                Problem.rating >= sweet_min,
                Problem.rating <= sweet_max,
                Problem.id.notin_(solved_ids) if solved_ids else True,
            )
            .order_by(Problem.contest_id.desc())
            .limit( limit * 3 )
        )
        p_res = await self.db.execute(p_stmt)
        candidate_problems = p_res.scalars().all()

        recommendations: List[RecommendedProblemItem] = []

        for prob in candidate_problems:
            if len(recommendations) >= limit:
                break

            # Fetch tags for problem
            t_stmt = select(ProblemTag.tag).where(ProblemTag.problem_id == prob.id)
            t_res = await self.db.execute(t_stmt)
            tags = list(t_res.scalars().all())

            # Check if matches weak tags
            has_weak_tag = any(t in weak_tags for t in tags)

            if has_weak_tag:
                rec_type = "WEAK_TAG_DRILL"
                matching_tag = next(t for t in tags if t in weak_tags)
                reason = f"Targeted drill for identified weakness in '{matching_tag}' at rating {prob.rating}."
            else:
                rec_type = "SWEET_SPOT"
                reason = f"Optimal challenge problem in your practice sweet spot ({prob.rating} rating)."

            recommendations.append(
                RecommendedProblemItem(
                    problem_id=prob.id,
                    contest_id=prob.contest_id,
                    index=prob.index,
                    name=prob.name,
                    rating=prob.rating,
                    recommendation_type=rec_type,
                    reason=reason,
                    tags=tags,
                )
            )

        return RecommendationResponse(
            handle=profile.handle,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
        )
