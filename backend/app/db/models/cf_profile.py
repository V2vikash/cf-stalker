import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class CFProfile(Base):
    __tablename__ = "cf_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    handle: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_rank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="profiles")
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission", back_populates="profile", cascade="all, delete-orphan"
    )
    contest_stats: Mapped[list["UserContestStat"]] = relationship(
        "UserContestStat", back_populates="profile", cascade="all, delete-orphan"
    )
    topic_stats: Mapped[list["UserTopicStat"]] = relationship(
        "UserTopicStat", back_populates="profile", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[list["UserSkillGap"]] = relationship(
        "UserSkillGap", back_populates="profile", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="profile", cascade="all, delete-orphan"
    )
    ai_insights: Mapped[list["AIInsight"]] = relationship(
        "AIInsight", back_populates="profile", cascade="all, delete-orphan"
    )
    sync_jobs: Mapped[list["SyncJob"]] = relationship(
        "SyncJob", back_populates="profile", cascade="all, delete-orphan"
    )
