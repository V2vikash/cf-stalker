from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CFProfileResponse(BaseModel):
    id: UUID
    handle: str
    rating: Optional[int] = None
    max_rating: Optional[int] = None
    rank: Optional[str] = None
    max_rank: Optional[str] = None
    avatar: Optional[str] = None
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    handle: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    sync_job_id: Optional[str] = None
    error_message: Optional[str] = None
