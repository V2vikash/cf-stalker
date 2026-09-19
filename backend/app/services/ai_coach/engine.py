import json
import httpx
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models.cf_profile import CFProfile
from app.db.models.analytics import UserSkillGap, AIInsight
from app.services.analytics.engine import AnalyticsEngine
from app.schemas.ai_coach import AICoachReviewResponse, ActionPlanStep


class AICoachEngine:
    """Engine for generating structured AI performance reviews based on user data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_review(self, profile: CFProfile) -> AICoachReviewResponse:
        # Build analytical context payload
        analytics = AnalyticsEngine(self.db)
        overview = await analytics.get_profile_overview(profile)
        contests = await analytics.get_contest_analytics(profile)

        # Get weak tags
        w_stmt = select(UserSkillGap.tag).where(
            UserSkillGap.cf_profile_id == profile.id,
            UserSkillGap.classification == "WEAKNESS",
        )
        w_res = await self.db.execute(w_stmt)
        weak_tags = list(w_res.scalars().all())

        # Get strong tags
        s_stmt = select(UserSkillGap.tag).where(
            UserSkillGap.cf_profile_id == profile.id,
            UserSkillGap.classification == "STRENGTH",
        )
        s_res = await self.db.execute(s_stmt)
        strong_tags = list(s_res.scalars().all())

        rating = profile.rating or 1200

        # Construct structured payload for LLM
        context_payload = {
            "handle": profile.handle,
            "rating": rating,
            "max_rating": profile.max_rating or rating,
            "volatility": overview.volatility,
            "accuracy": overview.overall_accuracy,
            "weak_tags": weak_tags,
            "strong_tags": strong_tags,
            "total_contests": contests.total_contests,
            "best_rank": contests.best_rank,
        }

        # Attempt calling LLM provider if valid API key is present
        if settings.LLM_API_KEY and settings.LLM_API_KEY != "mock-key" and settings.LLM_API_KEY != "your-api-key-here":
            try:
                review_dict = await self._call_llm(context_payload)
                return AICoachReviewResponse(**review_dict)
            except Exception:
                pass  # Fallback to analytical template generation

        # Deterministic analytical coach review based on real context payload
        return self._generate_rule_based_review(context_payload)

    def _generate_rule_based_review(self, payload: Dict[str, Any]) -> AICoachReviewResponse:
        rating = payload["rating"]
        handle = payload["handle"]
        weak_tags = payload["weak_tags"]
        strong_tags = payload["strong_tags"]
        volatility = payload["volatility"]

        weak_summary = ", ".join(weak_tags[:3]) if weak_tags else "Advanced Algorithms"
        strong_summary = ", ".join(strong_tags[:3]) if strong_tags else "Basic Math & Implementation"

        summary = (
            f"Performance Audit for @{handle} (Rating: {rating}). "
            f"Your submission accuracy is {payload['accuracy']}% across {payload['total_contests']} contests. "
            f"Rating volatility stands at {volatility}."
        )

        tactical_advice = [
            f"Prioritize solving problems in '{weak_summary}' to eliminate rating leakage.",
            f"Your current practice sweet spot is rating range [{rating + 50} - {rating + 200}].",
            "Focus on speed optimization during the first 30 minutes of Div2/Div3 contests to reduce penalty.",
        ]

        strengths_assessment = [
            f"Demonstrated proficiency in {strong_summary}.",
            f"Achieved peak rank of #{payload['best_rank'] or 'N/A'} in official Codeforces contests.",
        ]

        weaknesses_assessment = [
            f"Identified rating delta deficit in topic: {weak_summary}.",
            f"High rating volatility ({volatility}) indicates inconsistency in penalty management under pressure.",
        ]

        action_plan = [
            ActionPlanStep(
                step=1,
                focus_area=weak_tags[0] if weak_tags else "Implementation",
                action="Solve 5 targeted problems in this tag without looking at editorial before 40 minutes.",
                target_problem_rating=rating + 100,
            ),
            ActionPlanStep(
                step=2,
                focus_area="Contest Upsolving",
                action="Upsolve problem C or D from your last attended contest.",
                target_problem_rating=rating + 150,
            ),
            ActionPlanStep(
                step=3,
                focus_area="Speed & Accuracy Drill",
                action="Participate in a virtual contest simulation focusing on zero wrong-submission penalty.",
                target_problem_rating=rating,
            ),
        ]

        return AICoachReviewResponse(
            handle=handle,
            current_rating=rating,
            summary=summary,
            tactical_advice=tactical_advice,
            strengths_assessment=strengths_assessment,
            weaknesses_assessment=weaknesses_assessment,
            action_plan=action_plan,
        )

    async def _call_llm(self, context_payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"You are a elite Competitive Programming Coach. Analyze this user statistics payload:\n"
            f"{json.dumps(context_payload, indent=2)}\n\n"
            f"Return a strict JSON object matching the keys: handle, current_rating, summary, "
            f"tactical_advice (array of strings), strengths_assessment (array of strings), "
            f"weaknesses_assessment (array of strings), action_plan (array of objects with step, focus_area, action, target_problem_rating)."
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
