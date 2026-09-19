import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Codeforces submission ID
    cf_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cf_profiles.id", ondelete="CASCADE"), nullable=False
    )
    problem_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    creation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., OK, WRONG_ANSWER
    pass_test_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_consumed_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_consumed_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relationships
    profile: Mapped["CFProfile"] = relationship("CFProfile", back_populates="submissions")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="submissions")

    __table_args__ = (
        Index("idx_submission_profile_time", "cf_profile_id", "creation_time"),
        Index("idx_submission_verdict", "cf_profile_id", "verdict"),
    )
