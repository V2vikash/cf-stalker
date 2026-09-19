import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(
        String(100), primary_key=True
    )  # e.g., "1900_A"
    contest_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    index: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    points: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    tags: Mapped[list["ProblemTag"]] = relationship(
        "ProblemTag", back_populates="problem", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission", back_populates="problem"
    )


class ProblemTag(Base):
    __tablename__ = "problem_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    problem_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # Relationships
    problem: Mapped["Problem"] = relationship("Problem", back_populates="tags")

    __table_args__ = (
        Index("idx_problem_tag_lookup", "tag", "problem_id"),
    )
