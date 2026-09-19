from typing import List, Dict, Any
from pydantic import BaseModel


class ActionPlanStep(BaseModel):
    step: int
    focus_area: str
    action: str
    target_problem_rating: int


class AICoachReviewResponse(BaseModel):
    handle: str
    current_rating: int
    summary: str
    tactical_advice: List[str]
    strengths_assessment: List[str]
    weaknesses_assessment: List[str]
    action_plan: List[ActionPlanStep]
