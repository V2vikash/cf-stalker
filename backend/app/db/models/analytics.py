import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class UserTopicStat(Base):
    __tablename__ = "user_topic_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    solved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attempted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_rating_solved: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="topic_stats")

    __table_args__ = (
        Index("idx_user_topic_profile_tag", "cf_profile_id", "tag", unique=True),
    )


class UserSkillGap(Base):
    __tablename__ = "user_skill_gaps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    user_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    tag_effective_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    gap_delta: Mapped[int] = mapped_column(Integer, nullable=False)  # User Rating - Tag Effective Rating
    classification: Mapped[str] = mapped_column(String(50), nullable=False)  # WEAKNESS, BALANCED, STRENGTH
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="skill_gaps")

    __table_args__ = (
        Index("idx_user_skill_gap_profile_tag", "cf_profile_id", "tag", unique=True),
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    problem_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    recommendation_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # SWEET_SPOT, WEAK_TAG_DRILL, CONTEST_UPSOLVE
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="recommendations")


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # WEEKLY_REVIEW, CONTEST_TACTICAL
    content_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="ai_insights")
