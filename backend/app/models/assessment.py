from datetime import datetime

from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PhysicalAssessment(Base):
    __tablename__ = "physical_assessments"
    __table_args__ = (
        UniqueConstraint("student_id", "week_number", "year", name="uq_assessment_student_week_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    speed_score: Mapped[float] = mapped_column(Float, default=0.0)
    strength_score: Mapped[float] = mapped_column(Float, default=0.0)
    endurance_score: Mapped[float] = mapped_column(Float, default=0.0)
    agility_score: Mapped[float] = mapped_column(Float, default=0.0)
    flexibility_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
