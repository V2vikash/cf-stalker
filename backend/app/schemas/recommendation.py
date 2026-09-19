from typing import List, Optional
from pydantic import BaseModel


class RecommendedProblemItem(BaseModel):
    problem_id: str
    contest_id: Optional[int] = None
    index: str
    name: str
    rating: Optional[int] = None
    recommendation_type: str  # SWEET_SPOT, WEAK_TAG_DRILL, CONTEST_UPSOLVE
    reason: str
    tags: List[str]


class RecommendationResponse(BaseModel):
    handle: str
    total_recommendations: int
    recommendations: List[RecommendedProblemItem]
