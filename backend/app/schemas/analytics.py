from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ProfileOverviewResponse(BaseModel):
    handle: str
    current_rating: Optional[int] = None
    max_rating: Optional[int] = None
    rank: Optional[str] = None
    max_rank: Optional[str] = None
    avatar: Optional[str] = None
    volatility: float  # Standard deviation of rating changes
    contests_attended: int
    total_solved: int
    total_submissions: int
    overall_accuracy: float


class ContestStatItem(BaseModel):
    contest_id: int
    name: str
    rank: int
    old_rating: int
    new_rating: int
    rating_change: int


class ContestAnalyticsResponse(BaseModel):
    handle: str
    total_contests: int
    best_rank: Optional[int] = None
    max_positive_delta: int
    max_negative_delta: int
    contests: List[ContestStatItem]


class TagStatItem(BaseModel):
    tag: str
    solved_count: int
    attempted_count: int
    max_rating_solved: Optional[int] = None
    accuracy: float


class TopicAnalyticsResponse(BaseModel):
    handle: str
    difficulty_distribution: Dict[int, int]  # e.g., {800: 15, 1200: 42, 1600: 10}
    tags: List[TagStatItem]
