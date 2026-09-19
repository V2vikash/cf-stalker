from typing import List
from pydantic import BaseModel


class SkillGapItem(BaseModel):
    tag: str
    user_rating: int
    tag_effective_rating: int
    gap_delta: int
    classification: str  # WEAKNESS, BALANCED, STRENGTH


class SkillGapMatrixResponse(BaseModel):
    handle: str
    overall_rating: int
    weaknesses_count: int
    balanced_count: int
    strengths_count: int
    gaps: List[SkillGapItem]
