from datetime import datetime

from sqlalchemy import Integer, Float, Boolean, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PromotionSuggestion(Base):
    __tablename__ = "promotion_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    coach_id: Mapped[int] = mapped_column(ForeignKey("coaches.id"), nullable=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    auto_suggested: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="suggested")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ArchivedStudent(Base):
    __tablename__ = "archived_students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_student_id: Mapped[int] = mapped_column(Integer, nullable=False)
    archive_year: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
