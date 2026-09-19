from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    cf_profile,
    analytics,
    skill_gap,
    recommendations,
    ai_coach,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(cf_profile.router, prefix="/cf", tags=["Codeforces Profile"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(skill_gap.router, prefix="/skill-gap", tags=["Skill Gap"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(ai_coach.router, prefix="/ai-coach", tags=["AI Coach"])
