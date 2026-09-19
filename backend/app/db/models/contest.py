import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Contest(Base):
    __tablename__ = "contests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Codeforces Contest ID
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user_stats: Mapped[list["UserContestStat"]] = relationship(
        "UserContestStat", back_populates="contest"
    )


class UserContestStat(Base):
    __tablename__ = "user_contest_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    contest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    old_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    new_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_change: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="contest_stats")
    contest: Mapped["Contest"] = relationship("Contest", back_populates="user_stats")

    __table_args__ = (
        Index("idx_user_contest_profile_id", "cf_profile_id"),
    )
